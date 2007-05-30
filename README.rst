==========================================================
 ``gitosis`` -- software for hosting ``git`` repositories
==========================================================

group -> list of repos

/usr/local/bin/git-shell-enforce-directory

check that the user account (e.g. ``git``) looks valid

ssh keys

regenerate authorized_keys, only touching lines that look safe

allow skipping .git suffix

git-daemon-export-ok

Example configuration::

	[gitosis]

	[group NAME]
	members = jdoe wsmith @anothergroup
	writable = foo bar baz/thud
	readonly = xyzzy
	map writable visiblename = actualname
	map readonly visiblename = actualname

	[repo foo]
	description = blah blah
	daemon-ok = no

	[gitweb]
	homelink = http://example.com/
