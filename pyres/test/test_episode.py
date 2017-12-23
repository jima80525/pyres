""" Test the Episode module """
import time
import pytest
import pyres.episode


class TestEpisode(object):
    """ test the open functionality """

    def test_all_params(self):
        """ set all parameters """
        assert self
        episode = pyres.episode.Episode(
            date=time.localtime(),
            title='title',
            url='url',
            podcast='podcast',
            size=1234,
            state=1,
            # one of these two required
            base_path='base_path',
            file_name='file_name'
        )
        assert episode
        elements = episode.as_list()
        assert 'title' in elements
        assert 'url' in elements
        # podcast is not returned in list
        # assert 'podcast' in elements
        assert 1234 in elements
        assert 1 in elements
        assert None not in elements
        # base_path is used to create file name element - file_name is ignored
        # assert 'base_path' in elements
        assert 'file_name' not in elements

    def test_no_file_name_params(self):
        """ set all parameters """
        assert self
        with pytest.raises(Exception):
            pyres.episode.Episode(
                date=time.localtime(),
                title='title',
                url='url',
                podcast='podcast',
                size=1234,
                state=1,
                # one of these two required
                # base_path='base_path',
                # file_name='file_name'
            )

    def test_file_name(self):
        """ set all parameters """
        assert self
        episode = pyres.episode.Episode(
            date=time.localtime(),
            title='title',
            url='url',
            podcast='podcast',
            size=1234,
            state=1,
            # one of these two required
            # base_path='base_path',
            file_name='file_name'
        )
        assert episode
        elements = episode.as_list()
        assert 'title' in elements
        assert 'url' in elements
        # podcast is not returned in list
        # assert 'podcast' in elements
        assert 1234 in elements
        assert 1 in elements
        assert None not in elements
        # file name is copied directly if base_path not specified
        # assert 'base_path' in elements
        assert 'file_name' in elements

    def test_no_state_no_size_set(self):
        """ create episode without specifying state or size """
        assert self
        episode = pyres.episode.Episode(
            date=time.localtime(),
            title='title',
            url='url',
            podcast='podcast',
            # one of these two required
            # base_path='base_path',
            file_name='file_name'
        )
        assert episode
        elements = episode.as_list()
        assert 'title' in elements
        assert 'url' in elements
        # podcast is not returned in list
        # assert 'podcast' in elements
        assert None in elements  # no size specified
        assert 0 in elements  # default state
        # file name is copied directly if base_path not specified
        # assert 'base_path' in elements
        assert 'file_name' in elements
        assert episode.state == 0
        assert not episode.size
