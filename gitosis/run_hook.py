"""
Perform gitosis actions for a git hook.
"""

import errno
import logging
import optparse
import os
import sys
import shutil

from ConfigParser import RawConfigParser

from gitosis import repository
from gitosis import ssh
from gitosis import gitweb

log = logging.getLogger('gitosis.run_hook')

def die(msg):
    log.error(msg)
    sys.exit(1)

def getParser():
    parser = optparse.OptionParser(
        usage='%prog HOOK',
        description='Perform gitosis actions for a git hook',
        )
    parser.set_defaults(
        config=os.path.expanduser('~/.gitosis.conf'),
        )
    parser.add_option('--config',
                      metavar='FILE',
                      help='read config from FILE',
                      )
    return parser

def post_update(cfg):
    try:
        shutil.rmtree('gitosis-export')
    except OSError, e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise
    repository.export(git_dir='.', path='gitosis-export')
    os.rename('gitosis-export/gitosis.conf', 'gitosis.conf')
    gitweb.generate(config=cfg, path='projects.list')
    ssh.writeAuthorizedKeys(
        path=os.path.expanduser('~/.ssh/authorized_keys'),
        keydir='gitosis-export/keydir',
        )

def main():
    logging.basicConfig(level=logging.INFO)
    os.umask(0022)

    parser = getParser()
    (options, args) = parser.parse_args()
    try:
        (hook,) = args
    except ValueError:
        parser.error('Missing argument HOOK.')

    cfg = RawConfigParser()
    try:
        conffile = file(options.config)
    except (IOError, OSError), e:
        if e.errno == errno.ENOENT:
            # not existing is ok
            pass
        else:
            # I trust the exception has the path.
            die("Unable to read config file: %s." % e)
    else:
        try:
            cfg.readfp(conffile)
        finally:
            conffile.close()

    git_dir = os.environ.get('GIT_DIR')
    if git_dir is None:
        die('Must have GIT_DIR set in enviroment.')
    os.chdir(git_dir)
    os.environ['GIT_DIR'] = '.'

    if hook == 'post-update':
        log.info('Running hook %s', hook)
        post_update(cfg)
        log.info('Done.')
    else:
        log.warning('Ignoring unknown hook: %r', hook)
        return 0
