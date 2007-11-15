#!/usr/bin/python
from setuptools import setup, find_packages
import os

def _subdir_contents(path):
    for toplevel in os.listdir(path):
        toplevel_path = os.path.join(path, toplevel)
        if not os.path.isdir(toplevel_path):
            continue
        for dirpath, dirnames, filenames in os.walk(toplevel_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if not full_path.startswith(path+'/'):
                    raise RuntimeError()
                yield full_path[len(path)+1:]
def subdir_contents(path):
    return list(_subdir_contents(path))

setup(
    name = "gitosis",
    version = "0.2",
    packages = find_packages(),

    author = "Tommi Virtanen",
    author_email = "tv@eagain.net",
    description = "software for hosting git repositories",
    long_description = """

Manage git repositories, provide access to them over SSH, with tight
access control and not needing shell accounts.

gitosis aims to make hosting git repos easier and safer. It manages
multiple repositories under one user account, using SSH keys to
identify users. End users do not need shell accounts on the server,
they will talk to one shared account that will not let them run
arbitrary commands.

""".strip(),
    license = "GPL",
    keywords = "git scm version-control ssh",
    url = "http://eagain.net/software/gitosis/",

    entry_points = {
        'console_scripts': [
            'gitosis-serve = gitosis.serve:Main.run',
            'gitosis-run-hook = gitosis.run_hook:Main.run',
            'gitosis-init = gitosis.init:Main.run',
            ],
        },

    package_data = {
        # this seems to be the only way to convince setuptools
        # to include things recursively
        'gitosis.templates': subdir_contents('gitosis/templates'),
    },

    # templates need to be a real directory, for git init
    zip_safe=False,

    install_requires=[
        # setuptools 0.6a9 will have a non-executeable post-update
        # hook, this will make gitosis-admin settings not update
        # (fixed in 0.6c5, maybe earlier)
        'setuptools>=0.6c5',
        ],
    )

