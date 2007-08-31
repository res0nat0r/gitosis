import errno
import os
import subprocess

def _mkdir(*a, **kw):
    try:
        os.mkdir(*a, **kw)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

def init(
    path,
    template=None,
    _git=None,
    ):
    if _git is None:
        _git = 'git'

    _mkdir(path, 0750)
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
