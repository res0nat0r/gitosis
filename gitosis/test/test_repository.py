from nose.tools import eq_ as eq

import os
import subprocess
import random

from gitosis import repository

from gitosis.test.util import (
    mkdir,
    maketemp,
    readFile,
    writeFile,
    check_mode,
    assert_raises,
    )

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
    os.umask(0022)
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
    # Git doesn't create missing hooks
    #assert os.path.isfile(os.path.join(path, 'hooks', 'pre-rebase'))

def test_init_default_templates():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path)
    hook_path = os.path.join(path, 'hooks', 'post-receive')
    check_mode(
        hook_path,
        0755,
        is_file=True,
        )
    got = readFile(hook_path)
    eq(got, '#!/bin/sh\nset -e\ngit-update-server-info\ngitosis-run-hook update-mirrors')
    

def test_init_environment():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    mockbindir = os.path.join(tmp, 'mockbin')
    os.mkdir(mockbindir)
    mockgit = os.path.join(mockbindir, 'git')
    writeFile(mockgit, '''\
#!/bin/sh
set -e
# git wrapper for gitosis unit tests
printf '%s' "$GITOSIS_UNITTEST_COOKIE" >"$(dirname "$0")/../cookie"

# strip away my special PATH insert so system git will be found
PATH="${PATH#*:}"

exec git "$@"
''')
    os.chmod(mockgit, 0755)
    magic_cookie = '%d' % random.randint(1, 100000)
    good_path = os.environ['PATH']
    try:
        os.environ['PATH'] = '%s:%s' % (mockbindir, good_path)
        os.environ['GITOSIS_UNITTEST_COOKIE'] = magic_cookie
        repository.init(path)
    finally:
        os.environ['PATH'] = good_path
        os.environ.pop('GITOSIS_UNITTEST_COOKIE', None)
    eq(
        sorted(os.listdir(tmp)),
        sorted([
                'mockbin',
                'cookie',
                'repo.git',
                ]),
        )
    got = readFile(os.path.join(tmp, 'cookie'))
    eq(got, magic_cookie)

def test_fast_import_environment():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path=path)
    mockbindir = os.path.join(tmp, 'mockbin')
    os.mkdir(mockbindir)
    mockgit = os.path.join(mockbindir, 'git')
    writeFile(mockgit, '''\
#!/bin/sh
set -e
# git wrapper for gitosis unit tests
printf '%s' "$GITOSIS_UNITTEST_COOKIE" >"$(dirname "$0")/../cookie"

# strip away my special PATH insert so system git will be found
PATH="${PATH#*:}"

exec git "$@"
''')
    os.chmod(mockgit, 0755)
    magic_cookie = '%d' % random.randint(1, 100000)
    good_path = os.environ['PATH']
    try:
        os.environ['PATH'] = '%s:%s' % (mockbindir, good_path)
        os.environ['GITOSIS_UNITTEST_COOKIE'] = magic_cookie
        repository.fast_import(
            git_dir=path,
            commit_msg='foo initial bar',
            committer='Mr. Unit Test <unit.test@example.com>',
            files=[
                ('foo', 'bar\n'),
                ],
            )
    finally:
        os.environ['PATH'] = good_path
        os.environ.pop('GITOSIS_UNITTEST_COOKIE', None)
    eq(
        sorted(os.listdir(tmp)),
        sorted([
                'mockbin',
                'cookie',
                'repo.git',
                ]),
        )
    got = readFile(os.path.join(tmp, 'cookie'))
    eq(got, magic_cookie)

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
        args=[
            'git',
            '--git-dir=%s' % git_dir,
            'cat-file',
            'commit',
            'HEAD',
            ],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        close_fds=True,
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

def test_export_environment():
    tmp = maketemp()
    git_dir = os.path.join(tmp, 'repo.git')
    mockbindir = os.path.join(tmp, 'mockbin')
    os.mkdir(mockbindir)
    mockgit = os.path.join(mockbindir, 'git')
    writeFile(mockgit, '''\
#!/bin/sh
set -e
# git wrapper for gitosis unit tests
printf '%s\n' "$GITOSIS_UNITTEST_COOKIE" >>"$(dirname "$0")/../cookie"

# strip away my special PATH insert so system git will be found
PATH="${PATH#*:}"

exec git "$@"
''')
    os.chmod(mockgit, 0755)
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
    magic_cookie = '%d' % random.randint(1, 100000)
    good_path = os.environ['PATH']
    try:
        os.environ['PATH'] = '%s:%s' % (mockbindir, good_path)
        os.environ['GITOSIS_UNITTEST_COOKIE'] = magic_cookie
        repository.export(git_dir=git_dir, path=export)
    finally:
        os.environ['PATH'] = good_path
        os.environ.pop('GITOSIS_UNITTEST_COOKIE', None)
    got = readFile(os.path.join(tmp, 'cookie'))
    eq(
        got,
        # export runs git twice
        '%s\n%s\n' % (magic_cookie, magic_cookie),
        )

def test_has_initial_commit_fail_notAGitDir():
    tmp = maketemp()
    e = assert_raises(
        repository.GitRevParseError,
        repository.has_initial_commit,
        git_dir=tmp)
    eq(str(e), 'rev-parse failed: exit status 128')

def test_has_initial_commit_no():
    tmp = maketemp()
    repository.init(path=tmp)
    got = repository.has_initial_commit(git_dir=tmp)
    eq(got, False)

def test_has_initial_commit_yes():
    tmp = maketemp()
    repository.init(path=tmp)
    repository.fast_import(
        git_dir=tmp,
        commit_msg='fakecommit',
        committer='John Doe <jdoe@example.com>',
        files=[],
        )
    got = repository.has_initial_commit(git_dir=tmp)
    eq(got, True)

def test_has_initial_commit_environment():
    tmp = maketemp()
    git_dir = os.path.join(tmp, 'repo.git')
    mockbindir = os.path.join(tmp, 'mockbin')
    os.mkdir(mockbindir)
    mockgit = os.path.join(mockbindir, 'git')
    writeFile(mockgit, '''\
#!/bin/sh
set -e
# git wrapper for gitosis unit tests
printf '%s' "$GITOSIS_UNITTEST_COOKIE" >"$(dirname "$0")/../cookie"

# strip away my special PATH insert so system git will be found
PATH="${PATH#*:}"

exec git "$@"
''')
    os.chmod(mockgit, 0755)
    repository.init(path=tmp)
    repository.fast_import(
        git_dir=tmp,
        commit_msg='fakecommit',
        committer='John Doe <jdoe@example.com>',
        files=[],
        )
    magic_cookie = '%d' % random.randint(1, 100000)
    good_path = os.environ['PATH']
    try:
        os.environ['PATH'] = '%s:%s' % (mockbindir, good_path)
        os.environ['GITOSIS_UNITTEST_COOKIE'] = magic_cookie
        got = repository.has_initial_commit(git_dir=tmp)
    finally:
        os.environ['PATH'] = good_path
        os.environ.pop('GITOSIS_UNITTEST_COOKIE', None)
    eq(got, True)
    got = readFile(os.path.join(tmp, 'cookie'))
    eq(got, magic_cookie)

def test_fast_import_parent():
    tmp = maketemp()
    path = os.path.join(tmp, 'repo.git')
    repository.init(path=path)
    repository.fast_import(
        git_dir=path,
        commit_msg='foo initial bar',
        committer='Mr. Unit Test <unit.test@example.com>',
        files=[
            ('foo', 'bar\n'),
            ],
        )
    repository.fast_import(
        git_dir=path,
        commit_msg='another',
        committer='Sam One Else <sam@example.com>',
        parent='refs/heads/master^0',
        files=[
            ('quux', 'thud\n'),
            ],
        )
    export = os.path.join(tmp, 'export')
    repository.export(
        git_dir=path,
        path=export,
        )
    eq(sorted(os.listdir(export)),
       sorted(['foo', 'quux']))

def test_mirror():
    tmp = maketemp()
    main_path = os.path.join(tmp, 'main.git')
    mirror_path = os.path.join(tmp, 'mirror.git')
    repository.init(path=main_path, template=False)
    repository.init(path=mirror_path, template=False)
    repository.fast_import(
        git_dir=main_path,
        commit_msg='foo initial bar',
        committer='Mr. Unit Test <unit.test@example.com>',
        files=[
            ('foo', 'bar\n'),
            ],
        )
    repository.mirror(main_path, mirror_path)
    export = os.path.join(tmp, 'export')
    repository.export(
        git_dir=mirror_path,
        path=export,
        )
    eq(os.listdir(export),
       ['foo'])