"""
Enforce git-shell to only serve allowed by access control policy.
directory. The client should refer to them without any extra directory
prefix. Repository names are forced to match ALLOW_RE.
"""

import logging

import sys, os, re

from gitosis import access
from gitosis import repository
from gitosis import gitweb
from gitosis import gitdaemon
from gitosis import app
from gitosis import util

ALLOW_RE = re.compile("^'(?P<path>[a-zA-Z0-9][a-zA-Z0-9@._-]*(/[a-zA-Z0-9][a-zA-Z0-9@._-]*)*)'$")

COMMANDS_READONLY = [
    'git-upload-pack',
    ]

COMMANDS_WRITE = [
    'git-receive-pack',
    ]

class ServingError(Exception):
    """Serving error"""

    def __str__(self):
        return '%s' % self.__doc__

class CommandMayNotContainNewlineError(ServingError):
    """Command may not contain newline"""

class UnknownCommandError(ServingError):
    """Unknown command denied"""

class UnsafeArgumentsError(ServingError):
    """Arguments to command look dangerous"""

class AccessDenied(ServingError):
    """Access denied to repository"""

class WriteAccessDenied(AccessDenied):
    """Repository write access denied"""

class ReadAccessDenied(AccessDenied):
    """Repository read access denied"""

def serve(
    cfg,
    user,
    command,
    ):
    if '\n' in command:
        raise CommandMayNotContainNewlineError()

    try:
        verb, args = command.split(None, 1)
    except ValueError:
        # all known commands take one argument; improve if/when needed
        raise UnknownCommandError()

    if (verb not in COMMANDS_WRITE
        and verb not in COMMANDS_READONLY):
        raise UnknownCommandError()

    match = ALLOW_RE.match(args)
    if match is None:
        raise UnsafeArgumentsError()

    path = match.group('path')

    # write access is always sufficient
    newpath = access.haveAccess(
        config=cfg,
        user=user,
        mode='writable',
        path=path)

    if newpath is None:
        # didn't have write access

        newpath = access.haveAccess(
            config=cfg,
            user=user,
            mode='readonly',
            path=path)

        if newpath is None:
            raise ReadAccessDenied()

        if verb in COMMANDS_WRITE:
            # didn't have write access and tried to write
            raise WriteAccessDenied()

    (topdir, relpath) = newpath
    assert not relpath.endswith('.git'), \
           'git extension should have been stripped: %r' % relpath
    repopath = '%s.git' % relpath
    fullpath = os.path.join(topdir, repopath)
    if (not os.path.exists(fullpath)
        and verb in COMMANDS_WRITE):
        # it doesn't exist on the filesystem, but the configuration
        # refers to it, we're serving a write request, and the user is
        # authorized to do that: create the repository on the fly

        # create leading directories
        p = topdir
        for segment in repopath.split(os.sep)[:-1]:
            p = os.path.join(p, segment)
            util.mkdir(p, 0750)

        repository.init(path=fullpath)
        gitweb.set_descriptions(
            config=cfg,
            )
        generated = util.getGeneratedFilesDir(config=cfg)
        gitweb.generate_project_list(
            config=cfg,
            path=os.path.join(generated, 'projects.list'),
            )
        gitdaemon.set_export_ok(
            config=cfg,
            )

    # put the verb back together with the new path
    newcmd = "%(verb)s '%(path)s'" % dict(
        verb=verb,
        path=fullpath,
        )
    return newcmd

class Main(app.App):
    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] USER')
        parser.set_description(
            'Allow restricted git operations under DIR')
        return parser

    def handle_args(self, parser, cfg, options, args):
        try:
            (user,) = args
        except ValueError:
            parser.error('Missing argument USER.')

        log = logging.getLogger('gitosis.serve.main')
        os.umask(0022)

        cmd = os.environ.get('SSH_ORIGINAL_COMMAND', None)
        if cmd is None:
            log.error('Need SSH_ORIGINAL_COMMAND in environment.')
            sys.exit(1)

        log.debug('Got command %(cmd)r' % dict(
            cmd=cmd,
            ))

        os.chdir(os.path.expanduser('~'))

        try:
            newcmd = serve(
                cfg=cfg,
                user=user,
                command=cmd,
                )
        except ServingError, e:
            log.error('%s', e)
            sys.exit(1)

        log.debug('Serving %s', newcmd)
        os.execvp('git-shell', ['git-shell', '-c', newcmd])
        log.error('Cannot execute git-shell.')
        sys.exit(1)
