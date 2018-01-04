===================================
 Pyres podcast subscription manager .. image:: https://travis-ci.org/jima80525/pyres.svg?branch=master
    :target: https://travis-ci.org/jima80525/pyres
===================================

This project provides a simple podcast subscription manager which pulls podcasts
from the web and copies them to an MP3 player.

It has been developed for and only used on a Coby MP3 play with USB connection
and designed around the author's use model, which is far simpler than what is
supported by something like itunes.  It manages rss subscriptions, downloading
new episodes to the host system for storage and then transfers all of the
downloaded episodes to the mp3 player in a single batch.  The podcasts are all
put into a single directory and are written in chronological order so that the
player sees them in that order.

See "Development" below for more features that will be coming for this tool.

Project Setup
=============

Instructions
------------

Download the package and type ./setup.py install.
Running 'pyres' will invoke the app.  Use --help to see list of options.  Pyres
starts with an empty database so you'll need to add new podcasts to see it do
much of anything.

Supported Python Versions
=========================

Python Project Template supports the following versions out of the box:

* CPython 2.7

Licenses
========

The code which makes up this Python project template is licensed under the
MIT/X11 license. Feel free to use it in your free software/open-source or
proprietary projects.

+------------------------+----------------------------------+
|Project                 |License                           |
+========================+==================================+
|Python itself           |Python Software Foundation License|
+------------------------+----------------------------------+
|argparse (now in stdlib)|Python Software Foundation License|
+------------------------+----------------------------------+
|Sphinx                  |Simplified BSD License            |
+------------------------+----------------------------------+
|Paver                   |Modified BSD License              |
+------------------------+----------------------------------+
|colorama                |Modified BSD License              |
+------------------------+----------------------------------+
|flake8                  |MIT/X11 License                   |
+------------------------+----------------------------------+
|mock                    |Modified BSD License              |
+------------------------+----------------------------------+
|pytest                  |MIT/X11 License                   |
+------------------------+----------------------------------+
|tox                     |MIT/X11 License                   |
+------------------------+----------------------------------+
|pydub                   |MIT/X11 License                   |
+------------------------+----------------------------------+

Issues
======

Please report any bugs or requests that you have using the GitHub issue tracker!

Development
===========
See the TODO file for ongoing development list.

Authors
=======
* Jim Anderson
