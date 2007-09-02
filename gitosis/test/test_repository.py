from nose.tools import eq_ as eq

import os
import subprocess

from gitosis import repository

from gitosis.test.util import mkdir, maketemp, readFile, check_mode

def check_bare(path):
    # we want it to be a bare repository
    assert not os.path.exists(os.path.join(path, '.git'))

def test_init_simple():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path)
    check_mode(path, 0750, is_dir=True)
    check_bare(path)

def test_init_exist_dir():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    mkdir(path, 0710)
    check_mode(path, 0710, is_dir=True)
    repository.init(path)
    # my weird access mode is preserved
    check_mode(path, 0710, is_dir=True)
    check_bare(path)

def test_init_exist_git():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path)
    repository.init(path)
    check_mode(path, 0750, is_dir=True)
    check_bare(path)

def test_init_templates():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    templatedir = os.path.join(
        os.path.dirname(__file__),
        'mocktemplates',
        )
    repository.init(path, template=templatedir)
    repository.init(path)
    got = readFile(os.path.join(path, 'no-confusion'))
    eq(got, 'i should show up\n')
    check_mode(
        os.path.join(path, 'hooks', 'post-update'),
        0755,
        is_file=True,
        )
    got = readFile(os.path.join(path, 'hooks', 'post-update'))
    eq(got, '#!/bin/sh\n# i can override standard templates\n')
    # standard templates are there, too
    assert os.path.isfile(os.path.join(path, 'hooks', 'pre-rebase'))

def test_export_simple():
    tmp = maketemp()
    git_dir = os.path.join(tmp, 'repo.git')
    repository.init(path=git_dir)
    repository.fast_import(
        git_dir=git_dir,
        committer='John Doe <jdoe@example.com>',
        commit_msg="""\
Reverse the polarity of the neutron flow.

Frobitz the quux and eschew obfuscation.
""",
        files=[
            ('foo', 'content'),
            ('bar/quux', 'another'),
            ],
        )
    export = os.path.join(tmp, 'export')
    repository.export(git_dir=git_dir, path=export)
    eq(sorted(os.listdir(export)),
       sorted(['foo', 'bar']))
    eq(readFile(os.path.join(export, 'foo')), 'content')
    eq(os.listdir(os.path.join(export, 'bar')), ['quux'])
    eq(readFile(os.path.join(export, 'bar', 'quux')), 'another')
    child = subprocess.Popen(
        args=['git', 'cat-file', 'commit', 'HEAD'],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        close_fds=True,
        env=dict(GIT_DIR=git_dir),
        )
    got = child.stdout.read().splitlines()
    returncode = child.wait()
    if returncode != 0:
        raise RuntimeError('git exit status %d' % returncode)
    eq(got[0].split(None, 1)[0], 'tree')
    eq(got[1].rsplit(None, 2)[0],
       'author John Doe <jdoe@example.com>')
    eq(got[2].rsplit(None, 2)[0],
       'committer John Doe <jdoe@example.com>')
    eq(got[3], '')
    eq(got[4], 'Reverse the polarity of the neutron flow.')
    eq(got[5], '')
    eq(got[6], 'Frobitz the quux and eschew obfuscation.')
    eq(got[7:], [])
