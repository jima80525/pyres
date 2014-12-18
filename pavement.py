# -*- coding: utf-8 -*-
""" File to drive paver scripts """

from __future__ import print_function

import sys

# Import parameters from the setup file.
sys.path.append('.')
from setup import (
    setup_dict, _lint, _test)

from paver.easy import options, task, consume_args
from paver.setuputils import install_distutils_tasks

options(setup=setup_dict)

install_distutils_tasks()


@task
def lint():
    # This refuses to format properly when running `paver help' unless
    # this ugliness is used.
    ('Perform PEP8 style check, run PyFlakes, and run McCabe complexity '
     'metrics on the code.')
    raise SystemExit(_lint())


@task
@consume_args
def run(args):
    """Run the package's main script. All arguments are passed to it."""
    # The main script expects to get the called executable's name as
    # argv[0]. However, paver doesn't provide that in args. Even if it did (or
    # we dove into sys.argv), it wouldn't be useful because it would be paver's
    # executable. So we just pass the package name in as the executable name,
    # since it's close enough. This should never be seen by an end user
    # installing through Setuptools anyway.
    from pyres.main import main
    raise SystemExit(main(args))


@task
def add_sciam():
    """ Test adding a scientific american podcast """
    # see notes in run task above
    from pyres.main import main
    arg = ['add', 'http://rss.sciam.com/sciam/60secsciencepodcast',
           '--start-date', '10/25/14']
    main(arg)
    arg = ['add', 'http://rss.sciam.com/sciam/60-second-psych',
           '--start-date', '09/20/14']
    raise SystemExit(main(arg))


@task
def add_serial():
    """ Test adding the serial podcast """
    # see notes in run task above
    from pyres.main import main
    arg = ['add', 'http://feeds.serialpodcast.org/serialpodcast',
           '--start-date', '01/01/14']
    raise SystemExit(main(arg))


@task
def test():
    """Run the unit tests."""
    raise SystemExit(_test())
