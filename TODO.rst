===========
 TODO list
===========

- let me have ~git owned by root:root

- gitosis-lint: check that the user account (e.g. ``git``) looks valid

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

- gitweb knows about README.html, figure out how to generate from e.g.
  README.rst in gitosis.git

- need to chgrp repositories www-data to make them accessible by gitweb

- allow using git-cvsserver?
  - git-shell can now let users do cvs-compatible commits
  - ponder GIT_AUTHOR_NAME etc

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

- git enhancement: "git init" should output to stderr, not to stdout

- README says "when prompted", but those are INFO level log messages,
  not shown by default

- rename keydir to keys, with backwards compatibility

- get rid of username extraction from ssh key comment field, used only
  in gitosis-init
