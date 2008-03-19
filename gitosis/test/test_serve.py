from nose.tools import eq_ as eq
from gitosis.test.util import assert_raises

import os
from ConfigParser import RawConfigParser

from gitosis import serve
from gitosis import repository

from gitosis.test import util

def test_bad_newLine():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.CommandMayNotContainNewlineError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='ev\nil',
        )
    eq(str(e), 'Command may not contain newline')
    assert isinstance(e, serve.ServingError)

def test_bad_nospace():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnknownCommandError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='git-upload-pack',
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, serve.ServingError)

def test_bad_command():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnknownCommandError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="evil 'foo'",
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, serve.ServingError)

def test_bad_unsafeArguments():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnsafeArgumentsError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='git-upload-pack /evil/attack',
        )
    eq(str(e), 'Arguments to command look dangerous')
    assert isinstance(e, serve.ServingError)

def test_bad_unsafeArguments_dotdot():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnsafeArgumentsError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='git-upload-pack something/../evil',
        )
    eq(str(e), 'Arguments to command look dangerous')
    assert isinstance(e, serve.ServingError)

def test_bad_forbiddenCommand_read():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.ReadAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_bad_forbiddenCommand_write_noAccess():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.ReadAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    # error message talks about read in an effort to make it more
    # obvious that jdoe doesn't have *even* read access
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_bad_forbiddenCommand_write_readAccess():
    cfg = RawConfigParser()
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    e = assert_raises(
        serve.WriteAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(str(e), 'Repository write access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_simple_read():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    got = serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(got, "git-upload-pack '%s/foo.git'" % tmp)

def test_simple_write():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    got = serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(got, "git-receive-pack '%s/foo.git'" % tmp)

def test_push_inits_if_needed():
    # a push to a non-existent repository (but where config authorizes
    # you to do that) will create the repository on the fly
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo.git', 'HEAD'))

def test_push_inits_if_needed_haveExtension():
    # a push to a non-existent repository (but where config authorizes
    # you to do that) will create the repository on the fly
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo.git'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo.git', 'HEAD'))

def test_push_inits_subdir_parent_missing():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo/bar')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo/bar.git'",
        )
    eq(os.listdir(repositories), ['foo'])
    foo = os.path.join(repositories, 'foo')
    util.check_mode(foo, 0750, is_dir=True)
    eq(os.listdir(foo), ['bar.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo', 'bar.git', 'HEAD'))

def test_push_inits_subdir_parent_exists():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    foo = os.path.join(repositories, 'foo')
    # silly mode on purpose; not to be touched
    os.mkdir(foo, 0751)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo/bar')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo/bar.git'",
        )
    eq(os.listdir(repositories), ['foo'])
    util.check_mode(foo, 0751, is_dir=True)
    eq(os.listdir(foo), ['bar.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo', 'bar.git', 'HEAD'))

def test_push_inits_if_needed_existsWithExtension():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    os.mkdir(os.path.join(repositories, 'foo.git'))
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    # it should *not* have HEAD here as we just mkdirred it and didn't
    # create it properly, and the mock repo didn't have anything in
    # it.. having HEAD implies serve ran git init, which is supposed
    # to be unnecessary here
    eq(os.listdir(os.path.join(repositories, 'foo.git')), [])

def test_push_inits_no_stdout_spam():
    # git init has a tendency to spew to stdout, and that confuses
    # e.g. a git push
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    old_stdout = os.dup(1)
    try:
        new_stdout = os.tmpfile()
        os.dup2(new_stdout.fileno(), 1)
        serve.serve(
            cfg=cfg,
            user='jdoe',
            command="git-receive-pack 'foo'",
            )
    finally:
        os.dup2(old_stdout, 1)
        os.close(old_stdout)
    new_stdout.seek(0)
    got = new_stdout.read()
    new_stdout.close()
    eq(got, '')
    eq(os.listdir(repositories), ['foo.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo.git', 'HEAD'))

def test_push_inits_sets_description():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'description', 'foodesc')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    path = os.path.join(repositories, 'foo.git', 'description')
    assert os.path.exists(path)
    got = util.readFile(path)
    eq(got, 'foodesc\n')

def test_push_inits_updates_projects_list():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'gitweb', 'yes')
    os.mkdir(os.path.join(repositories, 'gitosis-admin.git'))
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(
        sorted(os.listdir(repositories)),
        sorted(['foo.git', 'gitosis-admin.git']),
        )
    path = os.path.join(generated, 'projects.list')
    assert os.path.exists(path)
    got = util.readFile(path)
    eq(got, 'foo.git\n')

def test_push_inits_sets_export_ok():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'yes')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    path = os.path.join(repositories, 'foo.git', 'git-daemon-export-ok')
    assert os.path.exists(path)

