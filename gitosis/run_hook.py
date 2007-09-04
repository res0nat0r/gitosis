"""
Perform gitosis actions for a git hook.
"""

import errno
import logging
import os
import sys
import shutil

from gitosis import repository
from gitosis import ssh
from gitosis import gitweb
from gitosis import app

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

class Main(app.App):
    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] HOOK')
        parser.set_description(
            'Perform gitosis actions for a git hook')
        return parser

    def handle_args(self, parser, cfg, options, args):
        try:
            (hook,) = args
        except ValueError:
            parser.error('Missing argument HOOK.')

        log = logging.getLogger('gitosis.run_hook')
        os.umask(0022)

        git_dir = os.environ.get('GIT_DIR')
        if git_dir is None:
            log.error('Must have GIT_DIR set in enviroment')
            sys.exit(1)
        os.chdir(git_dir)
        os.environ['GIT_DIR'] = '.'

        if hook == 'post-update':
            log.info('Running hook %s', hook)
            post_update(cfg)
            log.info('Done.')
        else:
            log.warning('Ignoring unknown hook: %r', hook)
