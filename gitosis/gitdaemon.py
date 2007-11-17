import errno
import logging
import os

from ConfigParser import NoSectionError, NoOptionError

log = logging.getLogger('gitosis.gitdaemon')

from gitosis import util

def export_ok_path(repopath):
    p = os.path.join(repopath, 'git-daemon-export-ok')
    return p

def allow_export(repopath):
    p = export_ok_path(repopath)
    file(p, 'a').close()

def deny_export(repopath):
    p = export_ok_path(repopath)
    try:
        os.unlink(p)
    except OSError, e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise

def _extract_reldir(topdir, dirpath):
    if topdir == dirpath:
        return '.'
    prefix = topdir + '/'
    assert dirpath.startswith(prefix)
    reldir = dirpath[len(prefix):]
    return reldir

def set_export_ok(config):
    repositories = util.getRepositoryDir(config)

    try:
        global_enable = config.getboolean('gitosis', 'daemon')
    except (NoSectionError, NoOptionError):
        global_enable = False
    log.debug(
        'Global default is %r',
        {True: 'allow', False: 'deny'}.get(global_enable),
        )

    def _error(e):
        if e.errno == errno.ENOENT:
            pass
        else:
            raise e

    for (dirpath, dirnames, filenames) \
            in os.walk(repositories, onerror=_error):
        # oh how many times i have wished for os.walk to report
        # topdir and reldir separately, instead of dirpath
        reldir = _extract_reldir(
            topdir=repositories,
            dirpath=dirpath,
            )

        log.debug('Walking %r, seeing %r', reldir, dirnames)

        to_recurse = []
        repos = []
        for dirname in dirnames:
            if dirname.endswith('.git'):
                repos.append(dirname)
            else:
                to_recurse.append(dirname)
        dirnames[:] = to_recurse

        for repo in repos:
            name, ext = os.path.splitext(repo)
            if reldir != '.':
                name = os.path.join(reldir, name)
            assert ext == '.git'
            try:
                enable = config.getboolean('repo %s' % name, 'daemon')
            except (NoSectionError, NoOptionError):
                enable = global_enable

            if enable:
                log.debug('Allow %r', name)
                allow_export(os.path.join(dirpath, repo))
            else:
                log.debug('Deny %r', name)
                deny_export(os.path.join(dirpath, repo))
