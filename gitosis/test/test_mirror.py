from nose.tools import eq_ as eq, ok_ as ok

from ConfigParser import RawConfigParser

from gitosis import mirror, repository
from gitosis.test.util import maketemp
import os

def get_config():
    cfg = RawConfigParser()
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'mirrors', '/var/bar /var/baz')
    return cfg

def test_get_mirrors():
    cfg = get_config()
    cfg.add_section('mirror github')
    cfg.set('mirror github', 'repos', 'foo bar')
    cfg.set('mirror github', 'uri', 'git@github.com:res0nat0r/%s.git')
    mirrors = list(mirror.get_mirrors(cfg, 'foo'))
    ok('/var/bar' in mirrors)
    ok('/var/baz' in mirrors)
    ok('git@github.com:res0nat0r/foo.git' in mirrors)
    eq(3, len(mirrors))
    
    mirrors = list(mirror.get_mirrors(cfg, 'bar'))
    ok('git@github.com:res0nat0r/bar.git' in mirrors)
    eq(1, len(mirrors))

def test_get_mirrors_with_all():
    cfg = get_config()
    mirrors = list(mirror.get_mirrors(cfg, 'baz'))
    eq(0, len(mirrors))
    
    cfg.add_section('mirror github')
    cfg.set('mirror github', 'repos', '@all')
    cfg.set('mirror github', 'uri', 'git@github.com:res0nat0r/%s.git')
    mirrors = list(mirror.get_mirrors(cfg, 'baz'))
    ok('git@github.com:res0nat0r/baz.git' in mirrors)
    eq(1, len(mirrors))
    
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