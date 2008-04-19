from nose.tools import eq_ as eq

import logging
from ConfigParser import RawConfigParser

from gitosis import access

def test_write_no_simple():
    cfg = RawConfigParser()
    eq(access.haveAccess(config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       None)

def test_write_yes_simple():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'writable', 'foo/bar')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       ('repositories', 'foo/bar'))

def test_write_no_simple_wouldHaveReadonly():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'readonly', 'foo/bar')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       None)

def test_write_yes_map():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map writable foo/bar', 'quux/thud')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       ('repositories', 'quux/thud'))

def test_write_no_map_wouldHaveReadonly():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map readonly foo/bar', 'quux/thud')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       None)

def test_read_no_simple():
    cfg = RawConfigParser()
    eq(access.haveAccess(config=cfg, user='jdoe', mode='readonly', path='foo/bar'),
       None)

def test_read_yes_simple():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'readonly', 'foo/bar')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='readonly', path='foo/bar'),
       ('repositories', 'foo/bar'))

def test_read_yes_simple_wouldHaveWritable():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'writable', 'foo/bar')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='readonly', path='foo/bar'),
       None)

def test_read_yes_map():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map readonly foo/bar', 'quux/thud')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='readonly', path='foo/bar'),
       ('repositories', 'quux/thud'))

def test_read_yes_map_wouldHaveWritable():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map writable foo/bar', 'quux/thud')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='readonly', path='foo/bar'),
       None)

def test_read_yes_all():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', '@all')
    cfg.set('group fooers', 'readonly', 'foo/bar')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='readonly', path='foo/bar'),
       ('repositories', 'foo/bar'))

def test_base_global_absolute():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', '/a/leading/path')
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map writable foo/bar', 'baz/quux/thud')
    eq(access.haveAccess(
        config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       ('/a/leading/path', 'baz/quux/thud'))

def test_base_global_relative():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', 'some/relative/path')
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map writable foo/bar', 'baz/quux/thud')
    eq(access.haveAccess(
        config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       ('some/relative/path', 'baz/quux/thud'))

def test_base_global_relative_simple():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', 'some/relative/path')
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'readonly', 'foo xyzzy bar')
    eq(access.haveAccess(
        config=cfg, user='jdoe', mode='readonly', path='xyzzy'),
       ('some/relative/path', 'xyzzy'))

def test_base_global_unset():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'readonly', 'foo xyzzy bar')
    eq(access.haveAccess(
        config=cfg, user='jdoe', mode='readonly', path='xyzzy'),
       ('repositories', 'xyzzy'))

def test_base_local():
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'repositories', 'some/relative/path')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'map writable foo/bar', 'baz/quux/thud')
    eq(access.haveAccess(
        config=cfg, user='jdoe', mode='writable', path='foo/bar'),
       ('some/relative/path', 'baz/quux/thud'))

def test_dotgit():
    # a .git extension is always allowed to be added
    cfg = RawConfigParser()
    cfg.add_section('group fooers')
    cfg.set('group fooers', 'members', 'jdoe')
    cfg.set('group fooers', 'writable', 'foo/bar')
    eq(access.haveAccess(config=cfg, user='jdoe', mode='writable', path='foo/bar.git'),
       ('repositories', 'foo/bar'))
