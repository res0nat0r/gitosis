from nose.tools import eq_ as eq

import os
from ConfigParser import RawConfigParser
from cStringIO import StringIO

from gitosis import init, repository, run_hook
from gitosis.test.util import maketemp, readFile

def test_post_update_simple():
    tmp = maketemp()
    repos = os.path.join(tmp, 'repositories')
    os.mkdir(repos)
    admin_repository = os.path.join(repos, 'gitosis-admin.git')
    pubkey = (
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost')
    user = 'theadmin'
    init.init_admin_repository(
        git_dir=admin_repository,
        pubkey=pubkey,
        user=user,
        )
    repository.init(path=os.path.join(repos, 'forweb.git'))
    repository.init(path=os.path.join(repos, 'fordaemon.git'))
    repository.fast_import(
        git_dir=admin_repository,
        committer='John Doe <jdoe@example.com>',
        commit_msg="""\
stuff
""",
        parent='refs/heads/master^0',
        files=[
            ('gitosis.conf', """\
[gitosis]

[group gitosis-admin]
members = theadmin
writable = gitosis-admin

[repo fordaemon]
daemon = yes

[repo forweb]
gitweb = yes
owner = John Doe
description = blah blah
"""),
            ('keydir/jdoe.pub',
             'ssh-somealgo '
             +'0123456789ABCDEFBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
             +'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
             +'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
             +'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB= jdoe@host.example.com'),
            ],
        )
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', repos)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    ssh = os.path.join(tmp, 'ssh')
    os.mkdir(ssh)
    cfg.set(
        'gitosis',
        'ssh-authorized-keys-path',
        os.path.join(ssh, 'authorized_keys'),
        )
    run_hook.post_update(
        cfg=cfg,
        git_dir=admin_repository,
        )
    got = readFile(os.path.join(repos, 'forweb.git', 'description'))
    eq(got, 'blah blah\n')
    got = os.listdir(generated)
    eq(got, ['projects.list'])
    got = readFile(os.path.join(generated, 'projects.list'))
    eq(
        got,
        """\
forweb.git John+Doe
""",
        )
    got = os.listdir(os.path.join(repos, 'fordaemon.git'))
    assert 'git-daemon-export-ok' in got, \
        "git-daemon-export-ok not created: %r" % got
    got = os.listdir(ssh)
    eq(got, ['authorized_keys'])
    got = readFile(os.path.join(ssh, 'authorized_keys')).splitlines(True)
    assert 'command="gitosis-serve jdoe",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty ssh-somealgo 0123456789ABCDEFBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB= jdoe@host.example.com\n' in got, \
        "SSH authorized_keys line for jdoe not found: %r" % got
