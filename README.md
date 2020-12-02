# Pyres podcast subscription manager

> A tool for tracking your podcasts and putting them on your mp3 player.

[![travis-ci](https://travis-ci.org/jima80525/pyres.svg?branch=master)](https://travis-ci.org/jima80525/pyres)

This project provides a simple podcast subscription manager which pulls podcasts from the web and copies them to an MP3 player.

It has been developed for and only used on a Coby MP3 play with USB connection and is currently designed around the author's use model, which is far simpler than what is supported by something like itunes.

It manages rss subscriptions, downloading new episodes to the host system for storage and then transfers all of the downloaded episodes to the mp3 player in a single batch.  The podcasts are all put into a single directory and are written in chronological order so that the player sees them in that order.

See "Development" below for more features that will be coming for this tool.

## Installation

### Stable release

To install Pyres, run this command in your terminal:

```bash
$ pip install pyres
```

This is the preferred method to install Pyres, as it will always install the most recent stable release.

### From sources

The sources for Pyres can be downloaded from the `Github repo`:

You can either clone the public repository:

```bash
$ git clone git://github.com/jima80525/pyres
```

Or download the `tarball`:

```bash
$ curl  -OL https://github.com/jima80525/pyres/tarball/master
```

Once you have a copy of the source, you can install it with:

```bash
$ python setup.py install
```

## Development

The development of pyres is done using `invoke` (which can be installed with pip). `invoke --list` will show you the available commands. `invoke test` will run the test suite.

The program can be run directly using `python -m pyres --help`

Pyres starts with an empty database so you'll need to add new podcasts to see it do much of anything.

### Supported Python Versions

* CPython > 3.6


## Todo List

Short Term Todos:

* Fix up format of TQDM progress bars while downloading
* test for click interface
* explore how to refactor top level to make unit tests less obnoxious
* get tox running
* get full CI running
* Update docs - look into sphinx and how it works
* add wiley
* add docs and possibly sphinx
* asyncio testing and use: https://www.roguelynn.com/words/asyncio-we-did-it-wrong/
* upload first release to pypi!!!

Features to be added:

* tracking and removing items from MP3 player
* managing a queue of audiobooks (filling player when possible)
* tests need to be expanded to cover more of the top level functions
* way to see how long each episode is - and how much time is being downloaded -
* maybe how much time in each state
* GUI

## Issues

Please report any bugs or requests that you have using the GitHub issue tracker!

## Contributors

* Jim Anderson

