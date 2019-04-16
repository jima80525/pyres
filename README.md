# Pyres podcast subscription manager

> A tool for tracking your podcasts and putting them on your mp3 player.

[![travis-ci](https://travis-ci.org/jima80525/pyres.svg?branch=master)](https://travis-ci.org/jima80525/pyres)

This project provides a simple podcast subscription manager which pulls podcasts from the web and copies them to an MP3 player.

It has been developed for and only used on a Coby MP3 play with USB connection and is currently designed around the author's use model, which is far simpler than what is supported by something like itunes.  It manages rss subscriptions, downloading new episodes to the host system for storage and then transfers all of the downloaded episodes to the mp3 player in a single batch.  The podcasts are all put into a single directory and are written in chronological order so that the player sees them in that order.

See "Development" below for more features that will be coming for this tool.

## Project Setup

### Instructions

Download the package and type ./setup.py install.

Running 'pyres' will invoke the app.  Use --help to see list of options.  Pyres starts with an empty database so you'll need to add new podcasts to see it do much of anything.

### Supported Python Versions

* CPython > 3.6

## Issues

Please report any bugs or requests that you have using the GitHub issue tracker!

## Development

## Contributors

* Jim Anderson
