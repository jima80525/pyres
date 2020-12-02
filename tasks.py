""" Task definitions for invoke command line utility for building, testing and
    releasing pyres. """
import colorama
from invoke import run
from invoke import task
from invoke import exceptions
import pytest

# import setuptools
import sys

PROJECT_FILES = ["pyres", "tests", "tasks.py", "setup.py"]


def print_green(message):
    """Print a message indicating success in green color to STDOUT.
    :param message: the message to print
    :type message: :class:`str`
    """
    print(colorama.Fore.GREEN + message + colorama.Fore.RESET)


def print_red(message):
    """Print a message indicating failure in red color to STDERR.
    :param message: the message to print
    :type message: :class:`str`
    """
    print(colorama.Fore.RED + message + colorama.Fore.RESET, file=sys.stderr)


@task
def lint(c):
    """Run lint and return an exit code."""
    files = " ".join(PROJECT_FILES)
    res = run("flake8 --max-complexity=10 %s" % files, warn=True)
    if res.exited:
        print_red("Failed linting!")
        raise exceptions.Exit()
    else:
        print_green("Linting passed.")


@task
def retest(c):
    pytest.main(
        [
            "--lf",
            "--tb=short",
            # "--cov-report=term:skip-covered",
            "tests",
        ]
    )


@task
def test(c):
    pytest.main(
        [
            # "--cov-report=term-missing",
            # "--cov-report=term:skip-covered",
            "tests"
        ]
    )


# JHA TODO:
#     add task to run only a single test
#     add param to turn on -s for output of stdout all the time for pytest
#     add task to simply run the program with params
#     add task to add particular podcast
"""
@task
@consume_args
def run(args):
    # The main script expects to get the called executable's name as
    # argv[0]. However, paver doesn't provide that in args. Even if it did (or
    # we dove into sys.argv), it wouldn't be useful because it would be paver's
    # executable. So we just pass the package name in as the executable name,
    # since it's close enough. This should never be seen by an end user
    # installing through Setuptools anyway.
    # This is stuffed into sys.argv as setuptools calls entry points without
    # args.
    from pyres.main import main
    sys.argv = ['pyres']
    sys.argv.extend(args)
    raise SystemExit(main())
"""


"""
@task
def add_sciam():
    # see notes in run task above
    from pyres.main import main
    arg = ['add', 'http://rss.sciam.com/sciam/60secsciencepodcast',
           '--start-date', '05/01/15', '--max-update', '3']
           #'--start-date', '10/25/14', '--max-update', '3']
    #arg = ['add', 'http://rss.sciam.com/sciam/60secsciencepodcast',
           #'--start-date', '10/25/14']
    sys.argv = ['pyres']
    sys.argv.extend(arg)
    main()
    arg = ['add', 'http://rss.sciam.com/sciam/60-second-psych',
           '--start-date', '09/20/14']
    sys.argv = ['pyres']
    sys.argv.extend(arg)
    raise SystemExit()
"""


@task
def build(c):
    """ JHA Does not work currently """
    print("To be developed")
    # setuptools.sandbox.run_setup("setup.py", ["clean", "bdist_wheel"])


@task
def tox(c):
    run("tox")


@task
def format(c):
    for source in PROJECT_FILES:
        run(f"black -l 80 {source}")


@task
def clean(c, bytecode=False, test=False, extra=""):
    patterns = ["build/", "dist/", "pyres.egg-info/"]
    if bytecode:
        patterns.append("__pycache__/")
        patterns.append("pyres/__pycache__/")
        patterns.append("tests/__pycache__/")
    if test:
        patterns.append(".coverage")
        patterns.append(".pytest_cache/")
        patterns.append(".tox/")
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task
def distclean(c):
    clean(c, True, True)
