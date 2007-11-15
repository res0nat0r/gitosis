import os
import re
import subprocess
import sys

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
    if _git is None:
        _git = 'git'

    util.mkdir(path, 0750)
    args = [
        _git,
        '--git-dir=.',
        'init',
        ]
    if template is not None:
        args.append('--template=%s' % template)
    returncode = subprocess.call(
        args=args,
        cwd=path,
        stdout=sys.stderr,
        close_fds=True,
        )
    if returncode != 0:
        raise GitInitError('exit status %d' % returncode)


class GitFastImportError(GitError):
    """git fast-import failed"""
    pass

def fast_import(
    git_dir,
    commit_msg,
    committer,
    files,
    ):
    """
    Create an initial commit.
    """
    init(path=git_dir)
    child = subprocess.Popen(
        args=['git', 'fast-import', '--quiet', '--date-format=now'],
        cwd=git_dir,
        stdin=subprocess.PIPE,
        close_fds=True,
        env=dict(GIT_DIR=git_dir),
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
    # it's a literal prefix for git, a trailing slash is needed to
    # extract to the subdirectory
    path = os.path.join(path, '')
    returncode = subprocess.call(
        args=['git', 'read-tree', 'HEAD'],
        close_fds=True,
        env=dict(GIT_DIR=git_dir),
        )
    if returncode != 0:
        raise GitReadTreeError('exit status %d' % returncode)
    returncode = subprocess.call(
        args=[
            'git',
            'checkout-index',
            '-a',
            '-f',
            '--prefix=%s' % path,
            ],
        close_fds=True,
        env=dict(GIT_DIR=git_dir),
        )
    if returncode != 0:
        raise GitCheckoutIndexError('exit status %d' % returncode)

class GitHasInitialCommitError(GitError):
    """Check for initial commit failed"""

class GitRevParseError(GitError):
    """rev-parse failed"""

def has_initial_commit(git_dir):
    child = subprocess.Popen(
        args=['git', 'rev-parse', 'HEAD'],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        close_fds=True,
        env=dict(GIT_DIR='.'),
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
