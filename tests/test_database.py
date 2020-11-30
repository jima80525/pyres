""" Test test """
import dateutil
import os
import sys
import stat

# import datetime
import peewee
import pytest
from pyres.consts import BASEDATE
from pyres.database import (
    PodcastDatabase,
    PodcastExistsException,
    PodcastDoesNotExistException,
)
from pyres.rss import EpData

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
def episodes(request):
    eps = []
    for index in range(3):
        date = BASEDATE + dateutil.relativedelta.relativedelta(days=index)
        episode = EpData(date, f"title{index}", f"link{index}")
        eps.append(episode)
    return eps


@pytest.fixture
def bad_episodes(request):
    date = BASEDATE
    return [
        EpData(None, "t", "l"),
        EpData(date, None, "l"),
        EpData(date, "t", None),
    ]


@pytest.fixture
def filledfile(emptyfile, episodes):  # pylint: disable=W0621
    """ Tests for add episode data function """
    # get a fixed date
    with PodcastDatabase(emptyfile) as _database:
        assert _database
        _database.add_podcast(_FILLED_TABLE_NAME, "url", sys.maxsize)
        # add a valid episode
        add_and_check(_database, _FILLED_TABLE_NAME, episodes[0])
        add_and_check(_database, _FILLED_TABLE_NAME, episodes[1], 2)

    return emptyfile


def add_and_check(database, table_name, episode, expected=1):
    """ utility to add episode and ensure there is a single episode for that
    podcast """
    assert database.add_new_episode_data(table_name, episode)
    eps = database.find_episodes_to_download()
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
        # PodcastDatabase(emptyfile)
        os.chmod(emptyfile, stat.S_IWRITE)

    def test_empty_params(self):
        """ Testing no parameters to open"""
        assert self
        with pytest.raises(AttributeError):
            PodcastDatabase(None)

    def test_rollback(self, filledfile):  # pylint: disable=W0621
        """ Test that an exception raised inside a 'with' clause causes a
        rollback of the database. """
        assert self
        # first add podcast with one episode
        with PodcastDatabase(filledfile) as _database:
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert _FILLED_TABLE_NAME in names
            episodes = _database.find_episodes_to_download()
            assert len(episodes) == 2
        # now add one but throw exception in the with block
        with pytest.raises(Exception):
            with PodcastDatabase(filledfile) as _database:
                # make one of the episodes as downloaded
                _database.mark_episode_downloaded(episodes[0])
                new_list = _database.find_episodes_to_download()
                # confirm that we now think there's only 1 left to download
                assert len(new_list) == 1
                # raise the exception to roll us back
                raise Exception

        # end the with block and re-open the database
        with PodcastDatabase(filledfile) as _database:
            # should still have 2 to download
            new_list = _database.find_episodes_to_download()
            assert len(new_list) == 2

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
            pytest.raises(
                PodcastExistsException,
                _database.add_podcast,
                "name",
                "url",
                sys.maxsize,
            )

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
            pytest.raises(AttributeError, _database.delete_podcast, None)
            pytest.raises(
                PodcastDoesNotExistException, _database.delete_podcast, "name"
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
                PodcastDoesNotExistException,
                _database.delete_podcast,
                table_name,
            )

    def test_add_episode_then_delete(
        self, emptyfile, episodes
    ):  # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        assert emptyfile
        table_name = "podcast_name"
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast(table_name, "url", sys.maxsize)
            add_and_check(_database, table_name, episodes[0], 1)
            add_and_check(_database, table_name, episodes[1], 2)
            _database.delete_podcast(table_name)


class TestAddEpisode(object):
    """ Test the add_episode routine """

    def test_add_bad_episode(
        self, emptyfile, episodes
    ):  # pylint: disable=W0621
        """ test bad add episode calls """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            # test bad params
            pytest.raises(
                AttributeError, _database.add_new_episode_data, None, None
            )
            pytest.raises(
                AttributeError, _database.add_new_episode_data, "table", None
            )
            pytest.raises(
                AttributeError, _database.add_new_episode_data, None, "episode"
            )

            # test episode as string
            pytest.raises(
                AttributeError,
                _database.add_new_episode_data,
                "table",
                "episode",
            )

            # episode as string with actual table
            _database.add_podcast("table", "url", sys.maxsize)
            pytest.raises(
                AttributeError,
                _database.add_new_episode_data,
                "table",
                "episode",
            )

            # real episode with bad table name
            pytest.raises(
                AttributeError,
                _database.add_new_episode_data,
                "tle",
                episodes[0],
            )

    def test_add_episode(self, emptyfile, episodes, bad_episodes):
        """ Tests for add episode data function """
        table_name = "name"
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            _database.add_podcast(table_name, "url", sys.maxsize)
            # add a valid episode
            add_and_check(_database, table_name, episodes[0])
            # add it again - make sure there's only one
            pytest.raises(
                AttributeError,
                _database.add_new_episode_data,
                table_name,
                episodes[0],
            )

            for bad in bad_episodes:
                pytest.raises(
                    AttributeError,
                    _database.add_new_episode_data,
                    table_name,
                    bad,
                )


"""
JHA TODO add:
class TestState(object):
class TestGetUrls(object):
class TestShowMethods(object): ????
"""
