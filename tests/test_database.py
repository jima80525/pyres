""" Test test """
from __future__ import print_function
import os
import sys
import stat

import datetime
import peewee
import pytest
from pyres.database import PodcastDatabase
import pyres.database 

# import pyres.episode
# from mock import patch

# this is coupled into at least one test
_FILLED_TABLE_NAME = "filled_table"


@pytest.fixture
def emptyfile(request):
    """ Provide a new, empty database file """
    file_name = "newdb.db"
    _file = open(file_name, "w")
    _file.write("")
    _file.close()

    def fin():
        """ remove the file after use """
        os.remove(file_name)

    request.addfinalizer(fin)
    return file_name


@pytest.fixture
def filledfile(emptyfile):  # pylint: disable=W0621

    """ Tests for add episode data function """
    # get a fixed date
    assert emptyfile
    date = datetime.datetime.strptime("2015/4/19", "%Y/%m/%d")
    with PodcastDatabase(emptyfile) as db:
        assert db
        db.add_podcast(_FILLED_TABLE_NAME, "url", sys.maxsize)
        # add a valid episode
        add_and_check(db, _FILLED_TABLE_NAME, "title", date, "link")
        date = datetime.datetime.strptime("2015/4/20", "%Y/%m/%d")
        add_and_check(db, _FILLED_TABLE_NAME, "title2", date, "link2", 2)

    return emptyfile


def add_and_check(database, table_name, name, date, url, expected=1):
    """ utility to add episode and ensure there is a known number of episodes for that
    podcast """
    database.show_all_episodes()
    ep = database.add_new_episode_data(table_name, name, date, url)
    assert ep
    eps = database.find_episodes_to_download(table_name)
    assert len(eps) == expected
    eps = database.find_episodes_to_copy(table_name)
    assert len(eps) == 0


class TestOpen(object):
    """ test the open functionality """

    def test_new_db(self):
        """ create a new database """
        assert self
        db_name = "newdb.db"
        with PodcastDatabase(db_name) as _database:
            assert _database
        os.remove(db_name)

    def test_existing_db(self, emptyfile):  # pylint: disable=W0621
        """ open an existing database """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            _database.add_podcast("name", "url", sys.maxsize)

    def test_read_only_file(self, emptyfile):  # pylint: disable=W0621
        """ Test opening a read-only database file """
        assert self
        os.chmod(emptyfile, stat.S_IREAD)
        with pytest.raises(peewee.OperationalError):
            PodcastDatabase(emptyfile)
        os.chmod(emptyfile, stat.S_IWRITE)

    def test_empty_params(self):
        """ Testing no parameters to open"""
        assert self
        with pytest.raises(AttributeError):
            PodcastDatabase(None)

    def test_commit(self, emptyfile):  # pylint: disable=W0621
        """ Test that changes are committed to the database """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast("name", "url", sys.maxsize)

            # make sure the names is still there only once
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert "name" in names

        # end the with block and re-open the database
        with PodcastDatabase(emptyfile) as _database:
            # make sure the names is still there only once
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert "name" in names


class TestAddPodcast(object):
    """ test adding podcasts to database """

    def test_add_name_twice(self, emptyfile):  # pylint: disable=W0621
        """ Add the same podcast two times.  This covers adding it a single
            time as well.
        """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast("name", "url", sys.maxsize)
            # _database.add_podcast("name", "url", sys.maxsize)

            # make sure the names is still there only once
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert "name" in names

    def test_add_parameters(self, emptyfile):  # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            pytest.raises(
                AttributeError, _database.add_podcast, None, "url", sys.maxsize
            )
            pytest.raises(
                AttributeError, _database.add_podcast, "name", None, sys.maxsize
            )

            names = _database.get_podcast_names()
            assert len(names) == 0

    def test_throttle_rate(self, emptyfile):  # pylint: disable=W0621
        """ Make sure throttle rate is stored and returned correctly """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast("maxsize", "urlmax", sys.maxsize)
            _database.add_podcast("two", "url2", 2)
            _database.add_podcast("three", "url3", 3)
            names = _database.get_podcast_urls()
            assert len(names) == 3
            added1 = False
            added2 = False
            added3 = False
            for _tuple in names:
                url = _tuple[0]
                throttle = _tuple[1]  # don't care about startdate which is [2]
                if "urlmax" in url:
                    assert throttle == sys.maxsize
                    added1 = True
                if "url2" in url:
                    assert throttle == 2
                    added2 = True
                if "url3" in url:
                    assert throttle == 3
                    added3 = True
            assert added1
            assert added2
            assert added3


class TestDeletePodcast(object):
    """ Test the delete_podcast function"""

    def test_deleting_bad_podcast(self, emptyfile):  # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            pytest.raises(
                ValueError, _database.delete_podcast, None
            )
            pytest.raises(
                ValueError, _database.delete_podcast, "name"
            )

    def test_add_then_delete(self, emptyfile):  # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        assert emptyfile
        table_name = "podcast_name"
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast(table_name, "url", sys.maxsize)
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert table_name in names
            _database.delete_podcast(table_name)
            names = _database.get_podcast_names()
            assert len(names) == 0
            pytest.raises(
                ValueError, _database.delete_podcast, table_name
            )

    def test_add_episode_then_delete(self, emptyfile):  # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        assert emptyfile
        table_name = "podcast_name"
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast(table_name, "url", sys.maxsize)
            add_and_check(_database, table_name, "title1", datetime.datetime.now(), "link1", 1)
            add_and_check(_database, table_name, "title2", datetime.datetime.now(), "link2", 2)
            _database.delete_podcast(table_name)


class TestAddEpisode(object):
    """ Test the add_episode routine """

    def test_add_bad_episode(self, emptyfile):  # pylint: disable=W0621
        """ test bad add episode calls """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            # test bad params
            pytest.raises(
                AttributeError, _database.add_new_episode_data, None, None, None, None
            )
            pytest.raises(
                AttributeError, _database.add_new_episode_data, "table", None, None, None
            )
            pytest.raises(
                AttributeError, _database.add_new_episode_data, None, "episode", None, None
            )
            pytest.raises(
                AttributeError, _database.add_new_episode_data, None, None, "date", None
            )
            pytest.raises(
                AttributeError, _database.add_new_episode_data, None, None, None, "url"
            )

            _database.add_podcast("table", "url", sys.maxsize)
            # real episode with bad table name
            pytest.raises(
                ValueError,
                _database.add_new_episode_data,
                "tle",
                "title",
                datetime.datetime.now(),
                "link"
            )

    def test_add_episode(self, emptyfile):  # pylint: disable=W0621
        """ Tests for add episode data function """
        assert self
        table_name = "name"
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            _database.add_podcast(table_name, "url", sys.maxsize)
            # add a valid episode
            add_and_check(_database, table_name, "title", datetime.datetime.now(), "link")
            # add it again - make sure there's only one
            pytest.raises(
                ValueError, add_and_check, _database, table_name, "title", datetime.datetime.now(), "link"
            )


class TestState(object):
    """ test functions to modify state and sort based on state """

    @staticmethod
    def check_download_and_copy_counts(database, download, copy):
        """ Utility to check expected counts"""
        to_download = database.find_episodes_to_download(_FILLED_TABLE_NAME)
        assert len(to_download) == download
        eps = database.find_episodes_to_copy(_FILLED_TABLE_NAME)
        assert len(eps) == copy

    def test_add_without_state(self, filledfile):  # pylint: disable=W0621
        """ test that un-modified episodes are in 'to be downloaded' state """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database

            # start with two to download, none to copy
            self.check_download_and_copy_counts(_database, 2, 0)

            # get the list to download
            episodes = _database.find_episodes_to_download(_FILLED_TABLE_NAME)

            # 'download' one and see counts change
            _database.mark_episode_downloaded(episodes[0])
            self.check_download_and_copy_counts(_database, 1, 1)

            # 'download' the other and see counts change
            _database.mark_episode_downloaded(episodes[1])
            self.check_download_and_copy_counts(_database, 0, 2)

            # now copy them to the mp3 player and watch counts
            # 'copy' one and see counts change
            _database.mark_episode_on_mp3_player(episodes[0])
            self.check_download_and_copy_counts(_database, 0, 1)

            # 'download' the other and see counts change
            _database.mark_episode_on_mp3_player(episodes[1])
            self.check_download_and_copy_counts(_database, 0, 0)

    def test_bad_params(self, filledfile):  # pylint: disable=W0621
        """ send bad values to state change functions """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database
            # need to pass in an actual episode
            pytest.raises(
                AttributeError, _database.mark_episode_downloaded, None
            )
            pytest.raises(
                AttributeError, _database.mark_episode_on_mp3_player, None
            )


class TestGetUrls(object):
    """ test the Get Urls method """

    def test_on_empty_file(self, emptyfile):  # pylint: disable=W0621
        """  tests function against an empty database """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            names = _database.get_podcast_urls()
            assert len(names) == 0

    def test_on_full_file(self, filledfile):  # pylint: disable=W0621
        """  tests function against an full database """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database
            names = _database.get_podcast_urls()
            assert len(names) == 1

    def test_on_podcast_no_episode(self, emptyfile):  # pylint: disable=W0621
        """ tests on a podcast without episodes """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            _database.add_podcast(_FILLED_TABLE_NAME, "url", sys.maxsize)
            names = _database.get_podcast_urls()
            assert len(names) == 1


class TestShowMethods(object):
    """ test the debug show methods
        JHA 5/31/15 - not thrilled with these as they are very white-boxy.
        THey know too much about the output format, which might change without
        dramatically altering the functionality.  Might change to simply count
        number of lines returns?  Or that something was returned?  Might be
        thinking about this too much. """

    def test_show_podcasts(self, capsys, filledfile):  # pylint: disable=W0621
        """  tests the show_podcasts function """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database
            _database.show_podcasts()
            out, _ = capsys.readouterr()
            assert out.startswith("Podcast details")

    def test_show_episodes(self, capsys, filledfile):  # pylint: disable=W0621
        """  tests the show_all_episodes function """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database
            _database.show_all_episodes()
            out, _ = capsys.readouterr()
            print("out is", out)
            print("over and out")
            assert (
                out.startswith("Podcast details in database:\n"
                "  *  filled_table")
            )
