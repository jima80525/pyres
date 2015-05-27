""" Test the rss module """
import time
import pytest
from pyres.rss import add_episodes_from_feed
from mock import patch
from mock import Mock


@pytest.fixture
def basicfeed():
    """ Provide a simple feed  """
    test_feed = {
        'channel': {
            'title': u'99% Invisible',
        },
        'items': [{
            'published': u'Wed, 20 May 2015 04:47:53 +0000',
            'title': u'165- The Nutshell Studies',
            'links': [
                {
                    'href': u'http://www.podtrac.com/pts/redirect.mp3/'
                    'media.blubrry.com/99percentinvisible/cdn.99percen'
                    'tinvisible.org/wp-content/uploads/165-The-Nutshe'
                    'll-Studies.mp3',
                    'type': u'audio/mpeg'
                }
            ],
        }, ],
    }
    return test_feed


class TestRss(object):
    """ test the rss module """

    def test_rss_bad_url(self):
        """ Tests calling an invalid url """
        assert self
        # bad url gives None
        name, added = add_episodes_from_feed(None, 'a', 'bdir', time.gmtime())
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_bad_channel_data(self, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test simple url and that it got through - missing channel field
        should result in None being returned. """
        assert self
        # set up the mock for feedparser
        del basicfeed['channel']
        feedparser.return_value = basicfeed

        # call the function
        name, added = add_episodes_from_feed(None, 'a', 'bdir', time.gmtime())

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_bad_title(self, feedparser,
                           basicfeed):  # pylint: disable=W0621
        """  test simple url and that it got through - missing channel field
        should result in None being returned. """
        assert self
        # set up the mock for feedparser
        del basicfeed['channel']['title']
        feedparser.return_value = basicfeed

        # call the function
        name, added = add_episodes_from_feed(None, 'a', 'bdir', time.gmtime())

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_no_items(self, feedparser,
                          basicfeed):  # pylint: disable=W0621
        """  test simple url and that it got through - missing channel field
        should result in None being returned. """
        assert self
        # set up the mock for feedparser
        del basicfeed['items']
        feedparser.return_value = basicfeed

        # call the function
        name, added = add_episodes_from_feed(None, 'a', 'bdir', time.gmtime())

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_bad_episode_date(self, mkdir, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no date. """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem

        # set up the mode for feedparser
        basicfeed['items'][0]['published'] = "not a valid date"
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        # I want this to raise and kill the program to know if we need to
        # strengthen the date parsing routine.  So far it has been good
        pytest.raises(ValueError, add_episodes_from_feed, database, 'a',
                      'bdir', None)

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_no_episode_date(self, mkdir, feedparser,
                                 basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no date. """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem

        # set up the mode for feedparser
        del basicfeed['items'][0]['published']
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir', None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_no_episode_title(self, mkdir, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no title. """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem

        # set up the mode for feedparser
        del basicfeed['items'][0]['title']
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir', None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_no_episode_links(self, mkdir, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no title. """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem

        # set up the mode for feedparser
        del basicfeed['items'][0]['links']
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir', None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_episode_links_no_audio(self, mkdir, feedparser,
                                        basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no link with audio. """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem

        # set up the mode for feedparser
        basicfeed['items'][0]['links'][0]['type'] = u'video'
        feedparser.return_value = basicfeed

        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir', None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_episode_links_no_hrd(self, mkdir, feedparser,
                                      basicfeed):  # pylint: disable=W0621
        """  test result if an episode has audio link with no href tag. """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem

        # set up the mode for feedparser
        del basicfeed['items'][0]['links'][0]['href']
        feedparser.return_value = basicfeed

        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        pytest.raises(KeyError, add_episodes_from_feed, database, 'a', 'bdir',
                      time.gmtime())

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_get_full_url(self, mkdir, feedparser,
                              basicfeed):  # pylint: disable=W0621
        """  test that the right info is pulled from feed """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem
        # set up the mode for feedparser
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir', None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert name == u'99 Invisible'
        assert added == 1

        # test database mock - note the "add new episode data" call takes a
        # complex structure.  I don't really want to test that here
        database.add_podcast.assert_called_once_with(u'99 Invisible', "a")
        assert database.add_new_episode_data.call_count == 1

    @patch('pyres.rss.feedparser.parse')
    @patch('pyres.filemanager.utils.mkdir_p')
    def test_rss_no_database(self, mkdir, feedparser,
                             basicfeed):  # pylint: disable=W0621
        """  attempt to add to a nil database """
        assert self
        assert mkdir  # mocking so we don't actually modify filesystem
        # set up the mode for feedparser
        feedparser.return_value = basicfeed

        # call the routine - it should raise - invalid database is an internal
        # error
        pytest.raises(AttributeError, add_episodes_from_feed, None, 'a',
                      'bdir', time.gmtime())
