""" Test the utils package """
#import os
#import time
import pyres.metadata
#from mock import patch


class TestUtils(object):
    """ Test for each individual utility function """

    def test_one(self):
        """  this is merely here to satisfy my anal-retentive freakishness to
        maximize test coverage numbers. """
        assert self
        assert pyres.metadata.package

    def test_two(self):
        """  see note above """
        assert self
        assert pyres.metadata.authors_string
