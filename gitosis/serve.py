"""
Enforce git-shell to only serve repositories in the given
directory. The client should refer to them without any directory
prefix. Repository names are forced to match ALLOW.
"""

import logging; logging.basicConfig(level=logging.DEBUG)

import sys, os, optparse, re
from ConfigParser import RawConfigParser

from gitosis import access

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

ALLOW_RE = re.compile("^(?P<command>git-(?:receive|upload)-pack) '(?P<path>[a-zA-Z][a-zA-Z0-9@._-]*(/[a-zA-Z][a-zA-Z0-9@._-]*)*)'$")

COMMANDS_READONLY = [
    'git-upload-pack',
    ]

COMMANDS_WRITE = [
    'git-receive-pack',
    ]

def main():
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

    if '\n' in cmd:
        die("Command may not contain newlines.")

    match = ALLOW_RE.match(cmd)
    if match is None:
        die("Command to run looks dangerous")

    cfg = RawConfigParser()
    cfg.read(options.config)

    os.chdir(os.path.expanduser('~'))

    command = match.group('command')
    if (command not in COMMANDS_WRITE
        and command not in COMMANDS_READONLY):
        die("Unknown command denied.")

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
            die("Access denied.")

        if command in COMMANDS_WRITE:
            # didn't have write access and tried to write
            die("Write access denied.")

    # put the command back together with the new path
    newcmd = "%(command)s '%(newpath)s'" % dict(
        command=command,
        newpath=newpath,
        )
    os.execve('/usr/bin/git-shell', ['git-shell', '-c', newcmd], {})
    die("Cannot execute git-shell.")
