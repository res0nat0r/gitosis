from nose.tools import eq_ as eq

from ConfigParser import RawConfigParser

from gitosis import mirror, repository
from gitosis.test.util import maketemp
import os

def get_config():
    cfg = RawConfigParser()
    cfg.add_section('repo foo')
    return cfg

def test_get_mirrors():
    cfg = get_config()
    cfg.set('repo foo', 'mirrors', '/var/bar /var/baz')
    mirrors = mirror.get_mirrors(cfg, 'foo')
    eq('/var/bar', mirrors.next())
    eq('/var/baz', mirrors.next())
    
def test_get_git_name():
    eq('foo', mirror.get_git_name('/home/git/repository', '/home/git/repository/foo.git'))
    
def test_push_mirrors():
    tmp = maketemp()
    foo_path = os.path.join(tmp, 'foo.git')
    bar_path = os.path.join(tmp, 'bar.git')
    baz_path = os.path.join(tmp, 'baz.git')
    repository.init(path=foo_path, template=False)
    repository.init(path=bar_path, template=False)
    repository.init(path=baz_path, template=False)
    repository.fast_import(
        git_dir=foo_path,
        commit_msg='foo initial bar',
        committer='Mr. Unit Test <unit.test@example.com>',
        files=[
            ('foo', 'bar\n'),
            ],
        )
    cfg = get_config()
    cfg.set('repo foo', 'mirrors', ' '.join([bar_path,baz_path]))
    mirror.push_mirrors(cfg, foo_path)
    export_bar = os.path.join(tmp, 'export_bar')
    export_baz = os.path.join(tmp, 'export_baz')
    repository.export(
        git_dir=bar_path,
        path=export_bar,
        )
    repository.export(
        git_dir=baz_path,
        path=export_baz,
        )
    eq(os.listdir(export_bar),
       ['foo'])
    eq(os.listdir(export_baz),
       ['foo'])