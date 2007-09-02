from nose.tools import eq_ as eq
from gitosis.test.util import assert_raises

from ConfigParser import RawConfigParser

from gitosis import serve

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

def test_bad_forbiddenCommand_read():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.ReadAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(str(e), 'Read access denied')
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
    eq(str(e), 'Read access denied')
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
    eq(str(e), 'Write access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_simple_read():
    cfg = RawConfigParser()
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    got = serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(got, "git-upload-pack 'repositories/foo'")

def test_simple_write():
    cfg = RawConfigParser()
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    got = serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(got, "git-receive-pack 'repositories/foo'")
