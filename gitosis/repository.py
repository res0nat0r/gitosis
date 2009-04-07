import stat
import errno
import os
import re
import subprocess
import sys

from pkg_resources import resource_filename
from gitosis import util

class GitError(Exception):
    """git failed"""

    def __str__(self):
        return '%s: %s' % (self.__doc__, ': '.join(self.args))

class GitInitError(Exception):
    """git init failed"""

def init(
    path,
    template=None,
    _git=None,
    ):
    """
    Create a git repository at C{path} (if missing).

    Leading directories of C{path} must exist.

    @param path: Path of repository create.

    @type path: str

    @param template: Template directory, to pass to C{git init}.

    @type template: str
    """
    if _git is None:
        _git = 'git'

    if template is None:
        template = resource_filename('gitosis.templates', 'default')


    util.mkdir(path, 0750)
    args = [
        _git,
        '--git-dir=.',
        'init',
        ]
        
    hooks = []
    if template:
        args.append('--template=%s' % template)
        template_hooks_dir = os.path.join(template, 'hooks')
        if os.path.isdir(template_hooks_dir):
            hooks = os.listdir(template_hooks_dir)

    returncode = subprocess.call(
        args=args,
        cwd=path,
        stdout=sys.stderr,
        close_fds=True,
        )
    if returncode != 0:
        raise GitInitError('exit status %d' % returncode)
    
    hooks_dir = os.path.join(path, 'hooks')
    if not os.path.exists(hooks_dir):
        hooks_dir = os.path.join(path, '.git', 'hooks')
    if not os.path.exists(hooks_dir):
        raise
    for hook in hooks:
        os.chmod(
            os.path.join(hooks_dir, hook),
            0755)


class GitFastImportError(GitError):
    """git fast-import failed"""
    pass

def fast_import(
    git_dir,
    commit_msg,
    committer,
    files,
    parent=None,
    ):
    """
    Create an initial commit.
    """
    child = subprocess.Popen(
        args=[
            'git',
            '--git-dir=.',
            'fast-import',
            '--quiet',
            '--date-format=now',
            ],
        cwd=git_dir,
        stdin=subprocess.PIPE,
        close_fds=True,
        )
    files = list(files)
    for index, (path, content) in enumerate(files):
        child.stdin.write("""\
blob
mark :%(mark)d
data %(len)d
%(content)s
""" % dict(
            mark=index+1,
            len=len(content),
            content=content,
            ))
    child.stdin.write("""\
commit refs/heads/master
committer %(committer)s now
data %(commit_msg_len)d
%(commit_msg)s
""" % dict(
            committer=committer,
            commit_msg_len=len(commit_msg),
            commit_msg=commit_msg,
            ))
    if parent is not None:
        assert not parent.startswith(':')
        child.stdin.write("""\
from %(parent)s
""" % dict(
                parent=parent,
                ))
    for index, (path, content) in enumerate(files):
        child.stdin.write('M 100644 :%d %s\n' % (index+1, path))
    child.stdin.close()
    returncode = child.wait()
    if returncode != 0:
        raise GitFastImportError(
            'git fast-import failed', 'exit status %d' % returncode)

class GitExportError(GitError):
    """Export failed"""
    pass

class GitReadTreeError(GitExportError):
    """git read-tree failed"""

class GitCheckoutIndexError(GitExportError):
    """git checkout-index failed"""

def export(git_dir, path):
    try:
        os.mkdir(path)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise
    returncode = subprocess.call(
        args=[
            'git',
            '--git-dir=%s' % git_dir,
            'read-tree',
            'HEAD',
            ],
        close_fds=True,
        )
    if returncode != 0:
        raise GitReadTreeError('exit status %d' % returncode)
    # jumping through hoops to be compatible with git versions
    # that don't have --work-tree=
    env = {}
    env.update(os.environ)
    env['GIT_WORK_TREE'] = '.'
    returncode = subprocess.call(
        args=[
            'git',
            '--git-dir=%s' % os.path.abspath(git_dir),
            'checkout-index',
            '-a',
            '-f',
            ],
        cwd=path,
        close_fds=True,
        env=env,
        )
    if returncode != 0:
        raise GitCheckoutIndexError('exit status %d' % returncode)

class GitHasInitialCommitError(GitError):
    """Check for initial commit failed"""

class GitRevParseError(GitError):
    """rev-parse failed"""

def has_initial_commit(git_dir):
    child = subprocess.Popen(
        args=[
            'git',
            '--git-dir=.',
            'rev-parse',
            'HEAD',
            ],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        close_fds=True,
        )
    got = child.stdout.read()
    returncode = child.wait()
    if returncode != 0:
        raise GitRevParseError('exit status %d' % returncode)
    if got == 'HEAD\n':
        return False
    elif re.match('^[0-9a-f]{40}\n$', got):
        return True
    else:
        raise GitHasInitialCommitError('Unknown git HEAD: %r' % got)


class GitPushMirrorException(GitError):
    """push --mirror failed"""

def mirror(git_dir, remote):
    returncode = subprocess.call(
        args=[
            'git',
            '--git-dir=%s' % git_dir,
            'push',
            '--mirror',
            remote,
            ],
        cwd=git_dir,
        close_fds=True
        )
    if returncode != 0:
        raise GitPushMirrorException('exit status %d' % returncode)