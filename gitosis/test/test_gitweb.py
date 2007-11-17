from nose.tools import eq_ as eq

import os
from ConfigParser import RawConfigParser
from cStringIO import StringIO

from gitosis import gitweb
from gitosis.test.util import mkdir, maketemp, readFile

def test_projectsList_empty():
    cfg = RawConfigParser()
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
''')

def test_projectsList_repoDenied():
    cfg = RawConfigParser()
    cfg.add_section('repo foo/bar')
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
''')

def test_projectsList_noOwner():
    cfg = RawConfigParser()
    cfg.add_section('repo foo/bar')
    cfg.set('repo foo/bar', 'gitweb', 'yes')
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
foo%2Fbar
''')

def test_projectsList_haveOwner():
    cfg = RawConfigParser()
    cfg.add_section('repo foo/bar')
    cfg.set('repo foo/bar', 'gitweb', 'yes')
    cfg.set('repo foo/bar', 'owner', 'John Doe')
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
foo%2Fbar John+Doe
''')

def test_projectsList_multiple():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.add_section('repo foo/bar')
    cfg.set('repo foo/bar', 'owner', 'John Doe')
    cfg.set('repo foo/bar', 'gitweb', 'yes')
    cfg.add_section('repo quux')
    cfg.set('repo quux', 'gitweb', 'yes')
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
quux
foo%2Fbar John+Doe
''')

def test_projectsList_multiple_globalGitwebYes():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'gitweb', 'yes')
    cfg.add_section('repo foo/bar')
    cfg.set('repo foo/bar', 'owner', 'John Doe')
    cfg.add_section('repo quux')
    # same as default, no effect
    cfg.set('repo quux', 'gitweb', 'yes')
    cfg.add_section('repo thud')
    # this is still hidden
    cfg.set('repo thud', 'gitweb', 'no')
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
quux
foo%2Fbar John+Doe
''')

def test_projectsList_reallyEndsWithGit():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    mkdir(path)
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'gitweb', 'yes')
    got = StringIO()
    gitweb.generate_project_list_fp(
        config=cfg,
        fp=got)
    eq(got.getvalue(), '''\
foo.git
''')

def test_projectsList_path():
    tmp = maketemp()
    path = os.path.join(tmp, 'foo.git')
    mkdir(path)
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'gitweb', 'yes')
    projects_list = os.path.join(tmp, 'projects.list')
    gitweb.generate_project_list(
        config=cfg,
        path=projects_list)
    got = readFile(projects_list)
    eq(got, '''\
foo.git
''')
