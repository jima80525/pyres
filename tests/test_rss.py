""" Test the rss module """
import dateutil.parser
import dateutil.utils
import sys
import pytest
from pyres.rss import get_episode_list, SiteData
from mock import patch


@pytest.fixture
def basicfeed():
    """ Provide a simple feed  """
    test_feed = {
        "channel": {"title": u"99% Invisible"},
        "items": [
            {
                "published": u"Wed, 20 May 2015 04:47:53 +0000",
                "title": u"165- The Nutshell Studies",
                "links": [
                    {
                        "href": u"http://www.podtrac.com/pts/redirect.mp3/"
                        "media.blubrry.com/99percentinvisible/cdn.99percen"
                        "tinvisible.org/wp-content/uploads/165-The-Nutshe"
                        "ll-Studies.mp3",
                        "type": u"audio/mpeg",
                    }
                ],
            }
        ],
    }
    return test_feed


@pytest.fixture
def largefeed():
    """ Provide a larger feed  """
    test_feed = {
        "channel": {"title": u"99% Invisible"},
        "items": [
            {
                "published": u"Tue, 19 May 2015 04:47:53 +0000",
                "title": u"1 - title one",
                "links": [{"href": u"Link 1", "type": u"audio/mpeg"}],
            },
            {
                "published": u"Wed, 20 May 2015 04:47:53 +0000",
                "title": u"2 - title 2",
                "links": [{"href": u"Link 2", "type": u"audio/mpeg"}],
            },
            {
                "published": u"Thu, 21 May 2015 04:47:53 +0000",
                "title": u"3 - title 3",
                "links": [{"href": u"Link 3", "type": u"audio/mpeg"}],
            },
            {
                "published": u"Fri, 22 May 2015 04:47:53 +0000",
                "title": u"4 - title 4",
                "links": [{"href": u"Link 4", "type": u"audio/mpeg"}],
            },
        ],
    }
    return test_feed


@pytest.fixture
def site():
    start_date = dateutil.parser.parse("1/1/1970")
    start_date = dateutil.utils.default_tzinfo(start_date, dateutil.tz.UTC)
    return SiteData(url="a", throttle=10, start_date=start_date)


class TestRss(object):
    """ test the rss module """

    def test_rss_bad_url(self, site):
        """ Tests calling an invalid url """
        # bad data gives None
        name, episodes = get_episode_list("", site)
        # def get_episode_list(url, throttle, start_date):
        # def add_episodes_from_feed(database, url, base_dir, throttle,
        #                            start_date=None):

        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_bad_channel_data(self, feedparser, basicfeed, site):
        """  test simple url and that it got through - missing channel field
        should result in None being returned. """
        # set up the mock for feedparser
        del basicfeed["channel"]
        feedparser.return_value = basicfeed

        # call the function
        name, episodes = get_episode_list("noop", site)

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_bad_title(self, feedparser, basicfeed, site):
        """  test simple url and that it got through - missing channel field
        should result in None being returned. """
        # set up the mock for feedparser
        del basicfeed["channel"]["title"]
        feedparser.return_value = basicfeed

        # call the function
        name, episodes = get_episode_list("noop", site)

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_no_items(self, feedparser, basicfeed, site):
        """  test simple url and that it got through - missing channel field
        should result in None being returned. """
        # set up the mock for feedparser
        del basicfeed["items"]
        feedparser.return_value = basicfeed

        # call the function
        name, episodes = get_episode_list("noop", site)

        # test that we were called correctly and that the return values are ok
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_bad_episode_date(self, feedparser, basicfeed, site):
        """  test result if an episode has no date. """

        # set up the mode for feedparser
        basicfeed["items"][0]["published"] = "not a valid date"
        feedparser.return_value = basicfeed

        # call the routine
        # I want this to raise and kill the program to know if we need to
        # strengthen the date parsing routine.  So far it has been good
        pytest.raises(
            dateutil.parser._parser.ParserError, get_episode_list, "noop", site
        )

    @patch("pyres.rss.feedparser.parse")
    def test_rss_no_episode_date(self, feedparser, basicfeed, site):
        """  test result if an episode has no date. """
        # set up the mode for feedparser
        del basicfeed["items"][0]["published"]
        feedparser.return_value = basicfeed

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_no_episode_title(self, feedparser, basicfeed, site):
        """  test result if an episode has no title. """
        # set up the mode for feedparser
        del basicfeed["items"][0]["title"]
        feedparser.return_value = basicfeed

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_no_episode_links(self, feedparser, basicfeed, site):
        """  test result if an episode has no title. """
        # set up the mode for feedparser
        del basicfeed["items"][0]["links"]
        feedparser.return_value = basicfeed

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_episode_links_no_audio(self, feedparser, basicfeed, site):
        """  test result if an episode has no link with audio. """

        # set up the mode for feedparser
        basicfeed["items"][0]["links"][0]["type"] = u"video"
        feedparser.return_value = basicfeed

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert not name
        assert not episodes

    @patch("pyres.rss.feedparser.parse")
    def test_rss_episode_links_no_hrd(self, feedparser, basicfeed, site):
        """  test result if an episode has audio link with no href tag. """

        # set up the mode for feedparser
        del basicfeed["items"][0]["links"][0]["href"]
        feedparser.return_value = basicfeed

        # call the routine
        pytest.raises(KeyError, get_episode_list, "noop", site)

    @patch("pyres.rss.feedparser.parse")
    def test_rss_get_full_url(self, feedparser, basicfeed, site):
        """  test that the right info is pulled from feed """
        # set up the mode for feedparser
        feedparser.return_value = basicfeed

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert name == u"99% Invisible"
        assert len(episodes) == 1
        assert episodes[0].title.decode("utf-8") == "165- The Nutshell Studies"

    @patch("pyres.rss.feedparser.parse")
    @pytest.mark.parametrize(
        "throttle, expected",
        [(sys.maxsize, 4), (1, 1), (2, 2), (3, 3), (4, 4), (5, 4)],
    )  # pylint: disable=too-many-arguments
    def test_rss_throttle(
        self, feedparser, throttle, expected, largefeed, site
    ):
        """  Test that throttle function works """

        # set up the mode for feedparser
        feedparser.return_value = largefeed

        # site.throttle = throttle
        site = SiteData(site.url, throttle, site.start_date)

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert name == u"99% Invisible"
        assert len(episodes) == expected

    @patch("pyres.rss.feedparser.parse")
    @pytest.mark.parametrize(
        "start, expected",
        [
            # the largefeed fixture has four episodes, one on each day starting
            # on 5/19/2015 through 5/22/2015
            ("2015/04/19", 4),
            ("2015/05/19", 4),
            ("2015/05/20", 3),
            ("2015/05/21", 2),
            ("2015/05/22", 1),
            ("2015/05/23", 0),
        ],
    )  # pylint: disable=too-many-arguments
    def test_rss_start_date(self, feedparser, start, expected, largefeed, site):
        """  Test that throttle function works """
        # set up the mode for feedparser
        feedparser.return_value = largefeed

        # convert the date string to the internally used date time
        date = dateutil.parser.parse(start)
        date = dateutil.utils.default_tzinfo(date, dateutil.tz.UTC)
        site = SiteData(site.url, site.throttle, date)

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        if expected:
            assert name == u"99% Invisible"
            assert len(episodes) == expected

    @patch("pyres.rss.feedparser.parse")
    def test_rss_start_date_with_db(self, feedparser, largefeed, site):
        """  Test that throttle function works in conjunction with start date
        """
        # set up the mode for feedparser
        feedparser.return_value = largefeed

        # convert the date string to the internally used date time
        date = dateutil.parser.parse("2015/4/19")
        date = dateutil.utils.default_tzinfo(date, dateutil.tz.UTC)
        site = SiteData(site.url, 2, date)

        # call the routine
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock
        feedparser.assert_called_once_with("noop")
        assert name == u"99% Invisible"
        assert episodes[0].title.decode("utf-8") == "1 - title one"
        assert len(episodes) == 2

        date = episodes[1].date
        site = SiteData(site.url, 2, date)

        # now call add_episodes again - this should pull another two
        # episodes but with a bug I was seeing, it only added one to the
        # database - use the date of the second podcast to as the start
        # date
        name, episodes = get_episode_list("noop", site)

        # check the feedparser mock - only check number added this time
        assert name == u"99% Invisible"
        assert episodes[0].title.decode("utf-8") == "3 - title 3"
        assert len(episodes) == 2
