from nose.tools import eq_ as eq
from gitosis.test.util import assert_raises, maketemp

import os
from ConfigParser import RawConfigParser

from gitosis import init
from gitosis import repository

from gitosis.test import util

def test_ssh_extract_user_simple():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost')
    eq(got, 'fakeuser@fakehost')

def test_ssh_extract_user_domain():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost.example.com')
    eq(got, 'fakeuser@fakehost.example.com')

def test_ssh_extract_user_domain_dashes():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@ridiculously-long.example.com')
    eq(got, 'fakeuser@ridiculously-long.example.com')

def test_ssh_extract_user_underscore():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake_user@example.com')
    eq(got, 'fake_user@example.com')

def test_ssh_extract_user_dot():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake.u.ser@example.com')
    eq(got, 'fake.u.ser@example.com')

def test_ssh_extract_user_dash():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake.u-ser@example.com')
    eq(got, 'fake.u-ser@example.com')

def test_ssh_extract_user_no_at():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser')
    eq(got, 'fakeuser')

def test_ssh_extract_user_caps():
    got = init.ssh_extract_user(
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= Fake.User@Domain.Example.Com')
    eq(got, 'Fake.User@Domain.Example.Com')

def test_ssh_extract_user_bad():
    e = assert_raises(
        init.InsecureSSHKeyUsername,
        init.ssh_extract_user,
        'ssh-somealgo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= ER3%#@e%')
    eq(str(e), "Username contains not allowed characters: 'ER3%#@e%'")

def test_init_admin_repository():
    tmp = maketemp()
    admin_repository = os.path.join(tmp, 'admin.git')
    pubkey = (
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost')
    user = 'jdoe'
    init.init_admin_repository(
        git_dir=admin_repository,
        pubkey=pubkey,
        user=user,
        )
    eq(os.listdir(tmp), ['admin.git'])
    hook = os.path.join(
        tmp,
        'admin.git',
        'hooks',
        'post-update',
        )
    util.check_mode(hook, 0755, is_file=True)
    got = util.readFile(hook).splitlines()
    assert 'gitosis-run-hook post-update' in got
    export_dir = os.path.join(tmp, 'export')
    repository.export(git_dir=admin_repository,
                      path=export_dir)
    eq(sorted(os.listdir(export_dir)),
       sorted(['gitosis.conf', 'keydir']))
    eq(os.listdir(os.path.join(export_dir, 'keydir')),
       ['jdoe.pub'])
    got = util.readFile(
        os.path.join(export_dir, 'keydir', 'jdoe.pub'))
    eq(got, pubkey)
    # the only thing guaranteed of initial config file ordering is
    # that [gitosis] is first
    got = util.readFile(os.path.join(export_dir, 'gitosis.conf'))
    got = got.splitlines()[0]
    eq(got, '[gitosis]')
    cfg = RawConfigParser()
    cfg.read(os.path.join(export_dir, 'gitosis.conf'))
    eq(sorted(cfg.sections()),
       sorted([
        'gitosis',
        'group gitosis-admin',
        ]))
    eq(cfg.items('gitosis'), [])
    eq(sorted(cfg.items('group gitosis-admin')),
       sorted([
        ('writable', 'gitosis-admin'),
        ('members', 'jdoe'),
        ]))
