import os
import subprocess

from gitosis import util

def init(
    path,
    template=None,
    _git=None,
    ):
    if _git is None:
        _git = 'git'

    util.mkdir(path, 0750)
    args = [_git, 'init']
    if template is not None:
        args.append('--template=%s' % template)
    env = {}
    env.update(os.environ)
    env['GIT_DIR'] = '.'
    returncode = subprocess.call(
        args=args,
        cwd=path,
        close_fds=True,
        env=env,
        )
    if returncode != 0:
        raise RuntimeError(
            ("Command '%r' returned non-zero exit status %d"
             % (args, returncode)),
            )
