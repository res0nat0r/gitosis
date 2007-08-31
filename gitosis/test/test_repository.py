from nose.tools import eq_ as eq

import os
import stat
import shutil

from gitosis import repository

from gitosis.test.util import mkdir, maketemp, writeFile, readFile

def check_bare(path):
    # we want it to be a bare repository
    assert not os.path.exists(os.path.join(path, '.git'))

def test_init_simple():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path)
    st = os.stat(path)
    assert stat.S_ISDIR(st.st_mode)
    eq(stat.S_IMODE(st.st_mode), 0750)
    check_bare(path)

def test_init_exist_dir():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    mkdir(path)
    repository.init(path)
    st = os.stat(path)
    assert stat.S_ISDIR(st.st_mode)
    eq(stat.S_IMODE(st.st_mode), 0750)
    check_bare(path)

def test_init_exist_git():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path)
    repository.init(path)
    st = os.stat(path)
    assert stat.S_ISDIR(st.st_mode)
    eq(stat.S_IMODE(st.st_mode), 0750)
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
    st = os.stat(os.path.join(path, 'hooks', 'post-update'))
    assert stat.S_ISREG(st.st_mode)
    eq('%04o'%stat.S_IMODE(st.st_mode), '%04o'%0755)
    got = readFile(os.path.join(path, 'hooks', 'post-update'))
    eq(got, '#!/bin/sh\n# i can override standard templates\n')
    # standard templates are there, too
    assert os.path.isfile(os.path.join(path, 'hooks', 'pre-rebase'))
