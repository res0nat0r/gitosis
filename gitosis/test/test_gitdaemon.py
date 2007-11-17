from nose.tools import eq_ as eq

import os
from ConfigParser import RawConfigParser

from gitosis import gitdaemon
from gitosis.test.util import maketemp, writeFile

def exported(path):
    assert os.path.isdir(path)
    p = gitdaemon.export_ok_path(path)
    return os.path.exists(p)

def test_git_daemon_export_ok_repo_missing():
    # configured but not created yet; before first push
    tmp = maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'yes')
    gitdaemon.set_export_ok(config=cfg)
    assert not os.path.exists(os.path.join(tmp, 'foo'))
    assert not os.path.exists(os.path.join(tmp, 'foo.git'))

def test_git_daemon_export_ok_repo_missing_parent():
    # configured but not created yet; before first push
    tmp = maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo/bar')
    cfg.set('repo foo/bar', 'daemon', 'yes')
    gitdaemon.set_export_ok(config=cfg)
    assert not os.path.exists(os.path.join(tmp, 'foo'))

def test_git_daemon_export_ok_allowed():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    os.mkdir(path)
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'yes')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), True)

def test_git_daemon_export_ok_allowed_already():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    os.mkdir(path)
    writeFile(gitdaemon.export_ok_path(path), '')
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'yes')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), True)

def test_git_daemon_export_ok_denied():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    os.mkdir(path)
    writeFile(gitdaemon.export_ok_path(path), '')
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'no')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), False)

def test_git_daemon_export_ok_denied_already():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    os.mkdir(path)
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'no')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), False)

def test_git_daemon_export_ok_subdirs():
    tmp = maketemp()
    foo = os.path.join(tmp, 'foo')
    os.mkdir(foo)
    path = os.path.join(foo, 'bar.git')
    os.mkdir(path)
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo/bar')
    cfg.set('repo foo/bar', 'daemon', 'yes')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), True)

def test_git_daemon_export_ok_denied_default():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    os.mkdir(path)
    writeFile(gitdaemon.export_ok_path(path), '')
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), False)

def test_git_daemon_export_ok_denied_even_not_configured():
    # repositories not mentioned in config also get touched; this is
    # to avoid security trouble, otherwise we might expose (or
    # continue to expose) old repositories removed from config
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    os.mkdir(path)
    writeFile(gitdaemon.export_ok_path(path), '')
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(path), False)

def test_git_daemon_export_ok_allowed_global():
    tmp = maketemp()

    for repo in [
        'foo.git',
        'quux.git',
        'thud.git',
        ]:
        path = os.path.join(tmp, repo)
        os.mkdir(path)

    # try to provoke an invalid allow
    writeFile(gitdaemon.export_ok_path(os.path.join(tmp, 'thud.git')), '')

    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.set('gitosis', 'daemon', 'yes')
    cfg.add_section('repo foo')
    cfg.add_section('repo quux')
    # same as default, no effect
    cfg.set('repo quux', 'daemon', 'yes')
    cfg.add_section('repo thud')
    # this is still hidden
    cfg.set('repo thud', 'daemon', 'no')
    gitdaemon.set_export_ok(config=cfg)
    eq(exported(os.path.join(tmp, 'foo.git')), True)
    eq(exported(os.path.join(tmp, 'quux.git')), True)
    eq(exported(os.path.join(tmp, 'thud.git')), False)
