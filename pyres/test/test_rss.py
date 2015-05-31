""" Test the rss module """
import sys
import os
import time
import pytest
from pyres.rss import add_episodes_from_feed
from pyres.database import PodcastDatabase
import pyres.utils
from mock import patch
from mock import Mock


@pytest.fixture
def emptyfile(request):
    """ Provide a new, empty database file """
    file_name = 'newdb.db'
    _file = open(file_name, 'w')
    _file.write('')
    _file.close()

    def fin():
        """ remove the file after use """
        os.remove(file_name)

    request.addfinalizer(fin)
    return file_name


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


@pytest.fixture
def largefeed():
    """ Provide a larger feed  """
    test_feed = {
        'channel': {
            'title': u'99% Invisible',
        },
        'items': [
            {
                'published': u'Tue, 19 May 2015 04:47:53 +0000',
                'title': u'1 - title one',
                'links': [
                    {
                        'href': u'Link 1',
                        'type': u'audio/mpeg'
                    }
                ],
            },
            {
                'published': u'Wed, 20 May 2015 04:47:53 +0000',
                'title': u'2 - title 2',
                'links': [
                    {
                        'href': u'Link 2',
                        'type': u'audio/mpeg'
                    }
                ],
            },
            {
                'published': u'Thu, 21 May 2015 04:47:53 +0000',
                'title': u'3 - title 3',
                'links': [
                    {
                        'href': u'Link 3',
                        'type': u'audio/mpeg'
                    }
                ],
            },
            {
                'published': u'Fri, 22 May 2015 04:47:53 +0000',
                'title': u'4 - title 4',
                'links': [
                    {
                        'href': u'Link 4',
                        'type': u'audio/mpeg'
                    }
                ],
            },
        ],
    }
    return test_feed


class TestRss(object):
    """ test the rss module """

    def test_rss_bad_url(self):
        """ Tests calling an invalid url """
        assert self
        # bad url gives None
        name, added = add_episodes_from_feed(None, 'a', 'bdir', sys.maxsize,
                                             None)
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
        name, added = add_episodes_from_feed(None, 'a', 'bdir', sys.maxsize,
                                             None)

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
        name, added = add_episodes_from_feed(None, 'a', 'bdir', sys.maxsize,
                                             None)

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
        name, added = add_episodes_from_feed(None, 'a', 'bdir', sys.maxsize,
                                             None)

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_bad_episode_date(self, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no date. """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

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
                      'bdir', sys.maxsize,
                      None)

    @patch('pyres.rss.feedparser.parse')
    def test_rss_no_episode_date(self, feedparser,
                                 basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no date. """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # set up the mode for feedparser
        del basicfeed['items'][0]['published']
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir',
                                             sys.maxsize, None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_no_episode_title(self, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no title. """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # set up the mode for feedparser
        del basicfeed['items'][0]['title']
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir',
                                             sys.maxsize, None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_no_episode_links(self, feedparser,
                                  basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no title. """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # set up the mode for feedparser
        del basicfeed['items'][0]['links']
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir',
                                             sys.maxsize, None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_episode_links_no_audio(self, feedparser,
                                        basicfeed):  # pylint: disable=W0621
        """  test result if an episode has no link with audio. """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # set up the mode for feedparser
        basicfeed['items'][0]['links'][0]['type'] = u'video'
        feedparser.return_value = basicfeed

        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir',
                                             sys.maxsize, None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert not name
        assert not added

    @patch('pyres.rss.feedparser.parse')
    def test_rss_episode_links_no_hrd(self, feedparser,
                                      basicfeed):  # pylint: disable=W0621
        """  test result if an episode has audio link with no href tag. """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # set up the mode for feedparser
        del basicfeed['items'][0]['links'][0]['href']
        feedparser.return_value = basicfeed

        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        pytest.raises(KeyError, add_episodes_from_feed, database, 'a', 'bdir',
                      sys.maxsize, None)

    @patch('pyres.rss.feedparser.parse')
    def test_rss_get_full_url(self, feedparser,
                              basicfeed):  # pylint: disable=W0621
        """  test that the right info is pulled from feed """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p
        # set up the mode for feedparser
        feedparser.return_value = basicfeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir',
                                             sys.maxsize, None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert name == u'99 Invisible'
        assert added == 1

        # test database mock - note the "add new episode data" call takes a
        # complex structure.  I don't really want to test that here
        database.add_podcast.assert_called_once_with(u'99 Invisible', "a",
                                                     sys.maxsize)
        assert database.add_new_episode_data.call_count == 1

    @patch('pyres.rss.feedparser.parse')
    def test_rss_no_database(self, feedparser,
                             basicfeed):  # pylint: disable=W0621
        """  attempt to add to a nil database """
        assert self
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p
        # set up the mode for feedparser
        feedparser.return_value = basicfeed

        # call the routine - it should raise - invalid database is an internal
        # error
        pytest.raises(AttributeError, add_episodes_from_feed, None, 'a',
                      'bdir', sys.maxsize, None)

    @patch('pyres.rss.feedparser.parse')
    @pytest.mark.parametrize("throttle, expected", [
        (sys.maxsize, 4), (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 4),
    ])
    def test_rss_throttle(self, feedparser, throttle, expected,
                          largefeed):  # pylint: disable=W0621
        """  Test that throttle function works """
        assert self

        # set up the mode for feedparser
        feedparser.return_value = largefeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir', throttle,
                                             None)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        assert name == u'99 Invisible'
        assert added == expected

        # test database mock - note the "add new episode data" call takes a
        # complex structure.  I don't really want to test that here
        database.add_podcast.assert_called_once_with(u'99 Invisible', "a",
                                                     throttle)
        assert database.add_new_episode_data.call_count == expected

    @patch('pyres.rss.feedparser.parse')
    @pytest.mark.parametrize("start_date, expected", [
        # the largefeed fixture has four episodes, one on each day starting
        # on 5/19/2015 through 5/22/2015
        ("2015/04/19", 4), ("2015/05/19", 4), ("2015/05/20", 3),
        ("2015/05/21", 2), ("2015/05/22", 1), ("2015/05/23", 0),
    ])
    def test_rss_start_date(self, feedparser, start_date, expected,
                            largefeed):  # pylint: disable=W0621
        """  Test that throttle function works """
        assert self

        # set up the mode for feedparser
        feedparser.return_value = largefeed
        # set up a mock for the database so we don't need to actually write one
        database = Mock()
        database.add_new_episode_data.return_value = True
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # convert the date string to the internally used date time
        date = time.strptime(start_date, "%Y/%m/%d")

        # call the routine
        name, added = add_episodes_from_feed(database, 'a', 'bdir',
                                             sys.maxsize, date)

        # check the feedparser mock
        feedparser.assert_called_once_with('a')
        if expected:
            assert name == u'99 Invisible'
        assert added == expected

        # test database mock - note the "add new episode data" call takes a
        # complex structure.  I don't really want to test that here
        if expected:
            database.add_podcast.assert_called_once_with(u'99 Invisible', "a",
                                                         sys.maxsize)
            assert database.add_new_episode_data.call_count == expected

    @patch('pyres.rss.feedparser.parse')
    def test_rss_start_date_with_db(self, feedparser,
                                    largefeed,  # pylint: disable=W0621
                                    emptyfile):  # pylint: disable=W0621
        """  Test that throttle function works in conjunction with start date
        """
        assert self

        # set up the mode for feedparser
        feedparser.return_value = largefeed
        pyres.utils.mkdir_p = Mock()  # set up a mock for utils.mkdir_p

        # convert the date string to the internally used date time
        date = time.strptime('2015/4/19', "%Y/%m/%d")
        #("2015/04/19", 4), ("2015/05/19", 4), ("2015/05/20", 3),

        with PodcastDatabase(emptyfile) as _database:
            assert _database

            # call the routine
            name, added = add_episodes_from_feed(_database, 'a', 'bdir', 2,
                                                 date)

            # check the feedparser mock
            feedparser.assert_called_once_with('a')
            assert name == u'99 Invisible'
            assert added == 2

            # test database - ask it how many episodes it has ready.  It should
            # be two
            to_download = _database.find_episodes_to_download(u'99 Invisible')
            assert len(to_download) == 2

            # now call add_episodes again - this should pull another two
            # episodes but with a bug I was seeing, it only added one to the
            # database - use the date of the second podcast to as the start
            # date
            name, added = add_episodes_from_feed(_database, 'a', 'bdir', 2,
                                                 to_download[1].date)

            # check the feedparser mock - only check number added this time
            assert added == 2

            # test database - ask it how many episodes it has ready.  It should
            # be
            to_download = _database.find_episodes_to_download(u'99 Invisible')
            assert len(to_download) == 4
