"""
Created on 23 Mar 2009

@author: Damien Lebrun
"""
from ConfigParser import NoOptionError, NoSectionError
import os
import logging

from gitosis import repository
from gitosis import util


def push_mirrors(config, git_dir):
    log = logging.getLogger('gitosis.mirror.push')
    
    repository_dir = os.path.abspath(util.getRepositoryDir(config))
    git_dir = os.path.abspath(git_dir)
    git_name = get_git_name(repository_dir, git_dir)
    
    log.info('Updating %s\'s mirrors.' % git_name)
    
    for remote in get_mirrors(config, git_name):
        log.info('Updating %s.' % remote)
        repository.mirror(git_dir, remote)

        
def get_git_name(repository_dir, git_dir):
    if git_dir.startswith(repository_dir):
        git_name = git_dir[len(repository_dir):]
    else:
        git_name = os.path.split(git_dir)[1]
        
    git_name = git_name.strip(r'\/')     
    if git_name.endswith('.git'):
        git_name = git_name[:-4]
    return git_name

def get_mirrors(config, git_name):
    try:
        mirrors = config.get('repo %s' % git_name, 'mirrors')
        for mirror in mirrors.split():
            yield mirror
    except (NoSectionError, NoOptionError):
        pass