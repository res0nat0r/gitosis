"""
Enforce git-shell to only serve allowed by access control policy.
directory. The client should refer to them without any extra directory
prefix. Repository names are forced to match ALLOW_RE.
"""

import logging

import sys, os, optparse, re
from ConfigParser import RawConfigParser

from gitosis import access
from gitosis import repository

def die(msg):
    print >>sys.stderr, '%s: %s' % (sys.argv[0], msg)
    sys.exit(1)

def getParser():
    parser = optparse.OptionParser(
        usage='%prog [--config=FILE] USER',
        description='Allow restricted git operations under DIR',
        )
    parser.set_defaults(
        config=os.path.expanduser('~/.gitosis.conf'),
        )
    parser.add_option('--config',
                      metavar='FILE',
                      help='read config from FILE',
                      )
    return parser

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
    """Access denied"""

class WriteAccessDenied(AccessDenied):
    """Write access denied"""

class ReadAccessDenied(AccessDenied):
    """Read access denied"""

def serve(
    cfg,
    user,
    command,
    ):
    if '\n' in command:
        raise CommandMayNotContainNewlineError()

    verb, args = command.split(None, 1)

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

    if (not os.path.exists(newpath)
        and verb in COMMANDS_WRITE):
        # it doesn't exist on the filesystem, but the configuration
        # refers to it, we're serving a write request, and the user is
        # authorized to do that: create the repository on the fly
        assert not newpath.endswith('.git'), \
            'git extension should have been stripped: %r' % newpath
        repopath = '%s.git' % newpath
        repository.init(path=repopath)

    # put the verb back together with the new path
    newcmd = "%(verb)s '%(newpath)s'" % dict(
        verb=verb,
        newpath=newpath,
        )
    return newcmd

def main():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('gitosis.serve.main')
    os.umask(0022)

    parser = getParser()
    (options, args) = parser.parse_args()
    try:
        (user,) = args
    except ValueError:
        parser.error('Missing argument USER.')

    cmd = os.environ.get('SSH_ORIGINAL_COMMAND', None)
    if cmd is None:
        die("Need SSH_ORIGINAL_COMMAND in environment.")

    log.debug('Got command %(cmd)r' % dict(
        cmd=cmd,
        ))

    cfg = RawConfigParser()
    try:
        conffile = file(options.config)
    except (IOError, OSError), e:
        # I trust the exception has the path.
        die("Unable to read config file: %s." % e)
    try:
        cfg.readfp(conffile)
    finally:
        conffile.close()

    os.chdir(os.path.expanduser('~'))

    try:
        newcmd = serve(
            cfg=cfg,
            user=user,
            command=cmd,
            )
    except ServingError, e:
        die(str(e))

    log.debug('Serving %s', newcmd)
    os.execvpe('git-shell', ['git-shell', '-c', newcmd], {})
    die("Cannot execute git-shell.")
