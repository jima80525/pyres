""" Test the metadata file """
import pyres.metadata


class TestMetadata(object):
    """ Test for metadata file """

    def test_one(self):
        """  this is merely here to satisfy my anal-retentive freakishness to
        maximize test coverage numbers. """
        assert self
        assert pyres.metadata.package

    def test_two(self):
        """  see note above """
        assert self
        assert pyres.metadata.authors_string
