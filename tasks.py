""" Task definitions for invoke command line utility for building, testing and
    releasing markplates. """
import colorama
from invoke import run
from invoke import task
from invoke import exceptions
import pytest
import setuptools
import sys

PROJECT_FILES = [
    'pyres',
    'tests',
    'tasks.py',
    'setup.py',
]


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
    if (res.exited):
        print_red("Failed linting!")
        raise exceptions.Exit()
    else:
        print_green("Linting passed.")


@task(lint)
def newtest(c):
    print("IN NEW TEST")


@task
def test(c):
    pytest.main(
        [
            "--cov=markplates",
            "--cov-report=term-missing",
            "--cov-report=term:skip-covered",
            "tests",
        ]
    )


@task
def build(c):
    setuptools.sandbox.run_setup("setup.py", ["clean", "bdist_wheel"])


@task
def tox(c):
    run("tox")


@task
def release(c):
    print("coming soon!")


@task
def format(c):
    run("black -l 80 markplates")
    run("black -l 80 tests")
    run("black -l 80 tasks.py")


@task
def clean(c, bytecode=False, test=False, extra=""):
    patterns = ["build/", "dist/", "markplates.egg-info/"]
    if bytecode:
        patterns.append("__pycache__/")
        patterns.append("markplates/__pycache__/")
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