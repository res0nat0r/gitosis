#!/usr/bin/python
from setuptools import setup, find_packages
setup(
    name = "gitosis",
    version = "0.1",
    packages = find_packages(),

    author = "Tommi Virtanen",
    author_email = "tv@eagain.net",
    description = "software for hosting git repositories",
    license = "GPL",
    keywords = "git scm version-control ssh",
    url = "http://eagain.net/software/gitosis/",

    entry_points = {
        'console_scripts': [
            'gitosis-ssh = gitosis.ssh:main',
            'gitosis-serve = gitosis.serve:main',
            'gitosis-gitweb = gitosis.gitweb:main',
            'gitosis-run-hook = gitosis.run_hook:main',
            'gitosis-init = gitosis.init:main',
            ],
        },
    )
