# Contribution guide and Code of CONDUCT

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Bug reports

When [reporting a bug](<https://github.com/jima80525/pyres/issues>) please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Documentation improvements

Pyres 3 could always use more documentation, whether as part of the official
Pyres 3 docs, in docstrings, or even on the web in blog posts, articles, and
such.

## Feature requests and feedback

The best way to send feedback is to file an issue in the [github issues](https://github.com/jima80525/pyres/issues) section.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that code contributions are welcome :)

## Development

To set up `pyres` for local development:

1. Fork [pyres](<https://github.com/jima80525/pyres>)
   (look for the "Fork" button).
1. Clone your fork locally::

    git clone git@github.com:your_name_here/pyres.git

1. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

1. When you're done making changes, run all the checks, doc builder and spell checker with [tox](<http://tox.readthedocs.io/en/latest/install.html>) one command::

    tox

1. Commit your changes and push your branch to GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

1. Submit a pull request through the GitHub website.

## Pull Request Guidelines

If you need some code review or feedback while you're developing the code just make the pull request.

For merging, you should:

1. Include passing tests (run tox).
1. Update documentation when there's new API, functionality etc.
1. Add yourself to the `Authors` section in the `README.md`.

> If you don't have all the necessary python versions available locally you can rely on Travis - it will [run the tests](<https://travis-ci.org/jima80525/pyres/pull_requests>) for each change you add in the pull request.
It will be slower though ...

## Tips

To run a subset of tests::

    tox -e envname -- pytest -k test_myfeature

To run all the test environments in *parallel* (you need to ``pip install detox``)::

    detox
