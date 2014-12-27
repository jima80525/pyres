""" Test test """
import os
import stat
import pytest
import sqlite3
import time
from pyres.database import PodcastDatabase
import pyres.episode

# this is coupled into at least one test
_FILLED_TABLE_NAME = 'filled_table'


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
def filledfile(emptyfile):  # pylint: disable=W0621

    """ Tests for add episode data function """
    episode = pyres.episode.Episode(base_path='path',
                                    date=time.localtime(),
                                    title='title', url='link',
                                    podcast=_FILLED_TABLE_NAME)
    with PodcastDatabase(emptyfile) as _database:
        assert _database
        _database.add_podcast(_FILLED_TABLE_NAME, 'url')
        # add a valid episode
        add_and_check(_database, _FILLED_TABLE_NAME, episode)
        episode.title = 'title2'
        add_and_check(_database, _FILLED_TABLE_NAME, episode, 2)

    return emptyfile


def add_and_check(database, table_name, episode, expected=1):
    """ utility to add episode and ensure there is a single episode for that
    podcast """
    database.add_new_episode_data(table_name, episode)
    eps = database.find_episodes_to_download(table_name)
    assert len(eps) == expected
    eps = database.find_episodes_to_copy(table_name)
    assert len(eps) == 0


class TestOpen(object):
    """ test the open functionality """

    def test_envreading(self, monkeypatch):
        """ laksjdd"""
        assert self
        monkeypatch.setitem(os.environ, 'ENV1', 'myval')
        val = os.environ['ENV1']
        assert val == "myval"

    def test_new_db(self):
        """ create a new database """
        assert self
        db_name = 'newdb.db'
        with PodcastDatabase(db_name) as _database:
            assert _database
        os.remove(db_name)

    def test_existing_db(self, emptyfile):  # pylint: disable=W0621
        """ open an existing database """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            _database.add_podcast('name', 'url')

    def test_read_only_file(self, emptyfile):  # pylint: disable=W0621
        """ Test opening a read-only database file """
        assert self
        os.chmod(emptyfile, stat.S_IREAD)
        with pytest.raises(sqlite3.OperationalError):
            with PodcastDatabase(emptyfile) as _database:
                assert _database
                _database.add_podcast('name', 'url')
        os.chmod(emptyfile, stat.S_IWRITE)

    def test_empty_params(self):
        """ Testing no parameters to open"""
        assert self
        with pytest.raises(AttributeError):
            with PodcastDatabase(None):
                pass


class TestAddPodcast(object):
    """ test adding podcasts to database """
    def test_add_name_twice(self, emptyfile):   # pylint: disable=W0621
        """ Add the same podcast two times.  This covers adding it a single
            time as well.
        """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast('name', 'url')
            _database.add_podcast('name', 'url')

            # make sure the names is still there only once
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert 'name' in names

    def test_add_parameters(self, emptyfile):   # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            pytest.raises(AttributeError, _database.add_podcast, None, 'url')
            pytest.raises(AttributeError, _database.add_podcast, 'name', None)

            names = _database.get_podcast_names()
            assert len(names) == 0


class TestDeletePodcast(object):
    """ Test the delete_podcast function"""
    def test_deleting_bad_podcast(self, emptyfile):   # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            pytest.raises(sqlite3.OperationalError, _database.delete_podcast,
                          None)
            pytest.raises(sqlite3.OperationalError, _database.delete_podcast,
                          "name")

    def test_add_then_delete(self, emptyfile):   # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        assert emptyfile
        table_name = "podcast_name"
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast(table_name, 'url')
            names = _database.get_podcast_names()
            assert len(names) == 1
            assert table_name in names
            _database.delete_podcast(table_name)
            names = _database.get_podcast_names()
            assert len(names) == 0
            pytest.raises(sqlite3.OperationalError, _database.delete_podcast,
                          table_name)

    def test_add_episode_then_delete(self, emptyfile):  # pylint: disable=W0621
        """ test setting bad parameters on add command """
        assert self
        assert emptyfile
        table_name = "podcast_name"
        with PodcastDatabase(emptyfile) as _database:
            _database.add_podcast(table_name, 'url')
            episode1 = pyres.episode.Episode(base_path='path',
                                             date=time.localtime(),
                                             title='title1', url='link1',
                                             podcast=table_name)
            episode2 = pyres.episode.Episode(base_path='path',
                                             date=time.localtime(),
                                             title='title2', url='link2',
                                             podcast=table_name)
            add_and_check(_database, table_name, episode1, 1)
            add_and_check(_database, table_name, episode2, 2)
            _database.delete_podcast(table_name)


class TestAddEpisode(object):
    """ Test the add_episode routine """
    def test_add_bad_episode(self, emptyfile):    # pylint: disable=W0621
        """ test bad add episode calls """
        assert self
        with PodcastDatabase(emptyfile) as _database:
            # test bad params
            pytest.raises(AttributeError, _database.add_new_episode_data, None,
                          None)
            pytest.raises(AttributeError, _database.add_new_episode_data,
                          'table', None)
            pytest.raises(AttributeError, _database.add_new_episode_data, None,
                          'episode')

            # test episode as string
            pytest.raises(AttributeError, _database.add_new_episode_data,
                          'table', 'episode')

            # episode as string with actual table
            _database.add_podcast('table', 'url')
            pytest.raises(AttributeError, _database.add_new_episode_data,
                          'table', 'episode')

            # real episode with bad table name
            episode = pyres.episode.Episode(base_path='path',
                                            date=time.localtime(),
                                            title='title', url='link',
                                            podcast='podcast_name')
            pytest.raises(sqlite3.OperationalError,
                          _database.add_new_episode_data, 'tle', episode)

    def test_add_episode(self, emptyfile):    # pylint: disable=W0621
        """ Tests for add episode data function """
        episode = pyres.episode.Episode(base_path='path',
                                        date=time.localtime(),
                                        title='title', url='link',
                                        podcast='podcast_name')
        assert self
        table_name = 'name'
        with PodcastDatabase(emptyfile) as _database:
            assert _database
            _database.add_podcast(table_name, 'url')
            # add a valid episode
            add_and_check(_database, table_name, episode)
            # add it again - make sure there's only one
            add_and_check(_database, table_name, episode)

            # now add an ill-formed episode - should not be added
            save = episode.date
            episode.date = None
            add_and_check(_database, table_name, episode)
            episode.date = save

            save = episode.title
            episode.title = None
            add_and_check(_database, table_name, episode)
            episode.title = save

            save = episode.url
            episode.url = None
            add_and_check(_database, table_name, episode)
            episode.url = save


class TestState(object):
    """ test functions to modify state and sort based on state """
    @staticmethod
    def check_download_and_copy_counts(database, download, copy):
        """ Utility to check expected counts"""
        to_download = database.find_episodes_to_download(
            _FILLED_TABLE_NAME)
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
            episodes = _database.find_episodes_to_download(
                _FILLED_TABLE_NAME)

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

    def test_bad_params(self, filledfile):    # pylint: disable=W0621
        """ send bad values to state change functions """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database
            # need to pass in an actual episode
            pytest.raises(AttributeError, _database.mark_episode_downloaded,
                          None)
            pytest.raises(AttributeError, _database.mark_episode_on_mp3_player,
                          None)

            # marking episodes that do not exist is ignored
            self.check_download_and_copy_counts(_database, 2, 0)
            episode = pyres.episode.Episode(base_path='path',
                                            date=time.localtime(),
                                            title='new_title', url='link',
                                            podcast=_FILLED_TABLE_NAME)
            _database.mark_episode_downloaded(episode)
            _database.mark_episode_on_mp3_player(episode)
            self.check_download_and_copy_counts(_database, 2, 0)


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
        """  tests function against an empty database """
        assert self
        with PodcastDatabase(filledfile) as _database:
            assert _database
            names = _database.get_podcast_urls()
            assert len(names) == 1
