===========
 TODO list
===========

- guard against *.pub files named -foo.pub or foo;bar.pub

- gitweb doesn't understand mappings, just visible/no,
  physical and logical path are always the same

  - maybe remove the whole mapping feature for good?

- use groups somehow to reduce typing for ``gitweb = yes``

- detect when repo actually ends in ``.git`` for ``projects.list``
  (otherwise gitweb won't see it)

- ConfigParser does not guarantee ordering, rewrite all unit tests to
  assume sorted, fix code to sort
