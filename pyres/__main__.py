#!/usr/bin/env python3
""" Manage podcasts. """
from .main import pyres
from .consts import BASEDATE  # noqa f841

if __name__ == "__main__":
    pyres.main(prog_name=__package__)
