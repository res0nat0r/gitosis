==========================================================
 ``gitosis`` -- software for hosting ``git`` repositories
==========================================================

Example configuration:

.. include:: example.conf
   :literal:

group -> list of repos

/usr/local/bin/git-shell-enforce-directory

check that the user account (e.g. ``git``) looks valid

ssh keys

regenerate authorized_keys, only touching lines that look safe

allow skipping .git suffix

git-daemon-export-ok

