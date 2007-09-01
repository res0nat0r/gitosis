from nose.tools import eq_ as eq

import os
import shutil

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
    if os.path.exists(path):
        shutil.rmtree(path)
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
