""" Test the download module - mock out urllib2 """
import pytest
import time
from mock import patch
from mock import Mock
from mock import mock_open
import urllib2
from pyres.download import PodcastDownloader
import pyres.episode


@pytest.fixture
def episode():
    """ Provide a episode to download """
    return pyres.episode.Episode(base_path='path', date=time.localtime(),
                                 title='title', url='link',
                                 podcast='podcast_name')


@pytest.fixture
def urllib_mock():
    """ Mocks out the urllib urlopen command with general, working values """
    urllib2.urlopen = Mock()
    urllib2.urlopen.return_value = Mock()
    urllib2.urlopen.return_value.getcode.return_value = 200
    # create the metadata object - this needs to have enough metadata for the
    # downloader to get the content length
    meta = Mock()
    meta.getheaders.return_value = ["20", ]
    urllib2.urlopen.return_value.info.return_value = meta
    return urllib2.urlopen


class TestOpen(object):
    """ test the Get Urls method """
    def test_bad_url(self, episode):  # pylint: disable=W0621
        """  tests opening bad url """
        assert self
        # mock out open to raise an error
        urllib2.urlopen = Mock(side_effect=urllib2.URLError("test"))
        downloader = PodcastDownloader([episode])
        downloader.download_url_list()
        failed = downloader.return_failed_files()
        assert len(failed) == 1
        worked = downloader.return_successful_files()
        assert len(worked) == 0

    def test_bad_status(self, episode, urllib_mock):  # pylint: disable=W0621
        """ Test website returning bad status """
        assert self
        # change mock to return a 404
        urllib_mock.return_value.getcode.return_value = 404

        downloader = PodcastDownloader([episode])
        downloader.download_url_list()
        failed = downloader.return_failed_files()
        assert len(failed) == 1
        worked = downloader.return_successful_files()
        assert len(worked) == 0

    def test_fileio_error(self, episode, urllib_mock):  # pylint: disable=W0621
        """  test writing to filesystem failure """
        assert self
        # need to assert this as it's all configured for this test
        assert urllib_mock

        # path in the given episode fails to open, cause IO error
        downloader = PodcastDownloader([episode])
        downloader.download_url_list()
        failed = downloader.return_failed_files()
        assert len(failed) == 1
        worked = downloader.return_successful_files()
        assert len(worked) == 0

    def test_file_write(self, episode, urllib_mock):  # pylint: disable=W0621
        """  test writing to filesystem successfully """
        assert self
        # now make sure the read of the metadata works
        urllib_mock.return_value.read = Mock(
            side_effect=["aaaaaaaaaaaaaaaaaaaa", None])

        mock_file = mock_open()
        with patch('pyres.download.open', mock_file, create=True):
            downloader = PodcastDownloader([episode])
            downloader.download_url_list()
        failed = downloader.return_failed_files()
        assert len(failed) == 0
        worked = downloader.return_successful_files()
        assert len(worked) == 1
        handle = mock_file()
        assert handle.write.called_once()
