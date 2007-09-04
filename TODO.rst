===========
 TODO list
===========

- let me have ~git{,/repositories} owned by root:root

- gitosis-lint: check that the user account (e.g. ``git``) looks valid

- gitosis-create-repositories: create repos mentioned in config if
  they don't exist

- git-daemon-export-ok

- guard against *.pub files named -foo.pub or foo;bar.pub

- gitweb doesn't understand mappings, just visible/no,
  physical and logical path are always the same

  - maybe remove the whole mapping feature for good?

  - maybe create symlink trees to make mappings visible in filesystem?

- use groups somehow to reduce typing for ``gitweb = yes``

- detect when repo actually ends in ``.git`` for ``projects.list``
  (otherwise gitweb won't see it)

- unit test projects.list generation in run-hook

- ConfigParser does not guarantee ordering, rewrite all unit tests to
  assume sorted, fix code to sort

- test with ssh://

- write description to a file, make REPO.git/description symlink to it
  if it doesn't exist (thus not overwriting local changes)

- gitweb knows about cloneurl, handle like description

- gitweb knows about README.html, figure out how to generate from e.g.
  README.rst in gitosis.git

- make gitosis-gitweb output a gitweb.conf file too

- need to chgrp repositories www-data to make them accessible by gitweb

- allow using git-cvsserver?

- move from log.foo("bar" % quux) to log.foo("bar",  quux)

- can't trust "~"::

	[0 tv@musti ~]$ sudo python -c 'import os; print os.path.expanduser("~")'
	/home/tv
	[0 tv@musti ~]$ sudo -H python -c 'import os; print os.path.expanduser("~")'
	/root

- command line options

  - gitosis init --repositories=
  - gitosis init --config= (or whatever the option is elsewhere)
  - gitosis init --home= (for testing)
  - gitosis init --admin=username[@host]

- gitosis-run-hook has to be in PATH and PYTHONPATH before you can
  push to gitosis-admin.git

- make generated gitosis.conf read-only to discourage editing

- maybe postprocess gitosis.conf to have a "# DO NOT EDIT" header?

- setuptools 0.6a9 will have a non-executeable post-update hook,
  this will make gitosis-admin settings not update
  (fixed in 0.6c5, maybe earlier)

- git enhancement: "git init" should output to stderr, not to stdout
