""" Test the main package """
import pytest
import six
import sys
import os
import shutil
import sqlite3
import time
import pyres.main
from mock import patch
from mock import Mock
import argparse

# For some reason, one of the mocks is getting called an extra time in python
# 2.7 (python 3 seems to do the expected number) this helps hack around that
if six.PY2:
    PYTHON2_ADDON = 1
else:
    PYTHON2_ADDON = 0


@pytest.fixture
def newplayer(request):
    """ Provide a new, non-existent directory to act as player """
    player_name = 'test_mp3_player'

    def fin():
        """ remove the file after use """
        try:
            shutil.rmtree(player_name)
        except OSError:
            pass  # OK if file doesn't exist

    request.addfinalizer(fin)
    return player_name


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


class TestParseCmdLine(object):
    """ Test the parse_command_line function"""

    @patch('pyres.main.argparse._sys.exit')
    def test_no_args(self, exit_mock):
        """  call with no command line args results in sys.exit being called"""
        assert self
        sys.argv = ['test', ]
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 0 + PYTHON2_ADDON

    @patch('pyres.main.argparse._sys.exit')
    def test_bad_main_args(self, exit_mock):
        """  exit is called with bad args to main processor """
        assert self
        sys.argv = ['test', '-xyz', ]
        exit_mock.call_count = 0  # reset call count
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 1 + PYTHON2_ADDON

        # test with valid global options but no subcommand
        exit_mock.call_count = 0  # reset call count
        sys.argv = ['test', '-v', ]
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 0 + PYTHON2_ADDON
        exit_mock.call_count = 0  # reset call count
        sys.argv = ['test', '-b', ]
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 0 + PYTHON2_ADDON
        exit_mock.call_count = 0  # reset call count
        sys.argv = ['test', '-d', 'fred', ]
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 0 + PYTHON2_ADDON

        # finally confirm that -d throws without additional, required arg
        sys.argv = ['test', '-d', ]
        pytest.raises(TypeError, pyres.main.parse_command_line)

    @patch('pyres.main.argparse._sys.exit')
    def test_bad_main_command(self, exit_mock):
        """  exit is called with unknown subcommand """
        assert self
        sys.argv = ['test', 'xyz', ]
        pytest.raises(TypeError, pyres.main.parse_command_line)
        assert exit_mock.call_count == 1

    def util_base_args(self, arglist):
        """ test -v -b and -d options on given command line.  Assumes that
        these options are not in the arglist provided. """
        assert self

        # -v off
        sys.argv = arglist[:]
        results = pyres.main.parse_command_line()
        assert results.database == 'rss.db'
        assert not results.no_backup
        assert not results.verbose
        # -v on
        sys.argv = arglist[:]
        sys.argv.append('-v')
        results = pyres.main.parse_command_line()
        assert results.database == 'rss.db'
        assert not results.no_backup
        assert results.verbose

        # -b off
        sys.argv = arglist[:]
        print(sys.argv)
        results = pyres.main.parse_command_line()
        assert results.database == 'rss.db'
        assert not results.no_backup
        assert not results.verbose
        # -b on
        sys.argv = arglist[:]
        sys.argv.append('-b')
        results = pyres.main.parse_command_line()
        assert results.database == 'rss.db'
        assert results.no_backup
        assert not results.verbose

        # -d off
        sys.argv = arglist[:]
        print(sys.argv)
        results = pyres.main.parse_command_line()
        assert results.database == 'rss.db'
        assert not results.no_backup
        assert not results.verbose
        # -d on
        sys.argv = arglist[:]
        sys.argv.append('-d')
        sys.argv.append('newdb.db')
        results = pyres.main.parse_command_line()
        assert results.database == 'newdb.db'
        assert not results.no_backup
        assert not results.verbose

    @patch('pyres.main.argparse._sys.exit')
    def test_delete_command(self, exit_mock):
        """  delete subcommand """
        assert self
        # delete command requires a podcast name
        sys.argv = ['test', 'delete', ]
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 1 + PYTHON2_ADDON

        exit_mock.call_count = 0
        sys.argv = ['test', 'delete', 'podcast', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'delete'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.delete_podcast  # too white-boxy?
        assert results.name == 'podcast'
        assert not results.no_backup
        assert not results.verbose
        self.util_base_args(sys.argv)

    @patch('pyres.main.argparse._sys.exit')
    def test_add_command(self, exit_mock):
        """  add subcommand """
        def util_add_tester(base_dir, max_update, start_date, url):
            """ utility to help cut down tedious code """
            assert self

            results = pyres.main.parse_command_line()
            assert results.command == 'add'
            assert results.database == 'rss.db'
            assert results.func == pyres.main.add_url  # too white-boxy?

            assert results.base_dir == base_dir
            assert results.max_update == max_update
            if start_date:
                assert results.start_date == time.strptime(start_date, "%x")
            else:
                assert not results.start_date
            assert results.url == url
            assert not results.no_backup
            assert not results.verbose

        assert self
        # add command requires a url name as positional param
        sys.argv = ['test', 'add', ]
        pyres.main.parse_command_line()
        assert exit_mock.call_count == 1 + PYTHON2_ADDON

        # test command with no optional params
        sys.argv = ['test', 'add', 'url', ]
        util_add_tester('Files', sys.maxsize, None, 'url')

        # test base args
        self.util_base_args(sys.argv)

        # confirm individual optiions, --base-dir
        sys.argv = ['test', 'add', 'url', '--base-dir=bdir', ]
        util_add_tester('bdir', sys.maxsize, None, 'url')

        # confirm individual optiions, --start-date
        sys.argv = ['test', 'add', 'url', '--start-date', '04/17/15', ]
        util_add_tester('Files', sys.maxsize, '04/17/15', 'url')

        # confirm bad input for start time throws
        sys.argv = ['test', 'add', 'url', '--start-date', 'this is bad', ]
        pytest.raises(TypeError, pyres.main.parse_command_line)

        # confirm individual optiions, --max_update
        sys.argv = ['test', 'add', 'url', '--max-update', '15', ]
        util_add_tester('Files', '15', None, 'url')

    def test_update_command(self):
        """  update subcommand """
        assert self
        # test command with no optional params
        sys.argv = ['test', 'update', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'update'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.update_download_list
        assert results.base_dir == 'Files'
        assert not results.no_backup
        assert not results.verbose

        # test base args
        self.util_base_args(sys.argv)

        # test command with basedir option
        sys.argv = ['test', 'update', '--base-dir=bdir', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'update'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.update_download_list
        assert results.base_dir == 'bdir'
        assert not results.no_backup
        assert not results.verbose

    def test_process_command(self):
        """  process subcommand """
        assert self
        # test command with no optional params
        sys.argv = ['test', 'process', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'process'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.process_rss_feeds
        assert not results.no_backup
        assert not results.verbose

        # test base args
        self.util_base_args(sys.argv)

    def test_download_command(self):
        """  download subcommand """
        assert self
        # test command with no optional params
        sys.argv = ['test', 'download', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'download'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.download_to_player
        assert not results.mp3_player
        assert not results.no_backup
        assert not results.verbose

        # test base args
        self.util_base_args(sys.argv)

        # test command with mp3 player option
        sys.argv = ['test', 'download', '--mp3-player=newplayer', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'download'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.download_to_player
        assert results.mp3_player == 'newplayer'
        assert not results.no_backup
        assert not results.verbose

    def test_audiobook_command(self):
        """  audiobook subcommand """
        assert self
        # test command with no optional params
        sys.argv = ['test', 'audiobook', '--dir=dir', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'audiobook'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.manage_audiobook
        assert not results.mp3_player
        assert results.dir == 'dir'
        assert not results.no_backup
        assert not results.verbose

        # test base args
        self.util_base_args(sys.argv)

        # test command with mp3 player option
        sys.argv = ['test', 'audiobook', '--dir=dir',
                    '--mp3-player=newplayer', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'audiobook'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.manage_audiobook
        assert results.mp3_player == 'newplayer'
        assert results.dir == 'dir'
        assert not results.no_backup
        assert not results.verbose

    def test_database_command(self):
        """  database subcommand """
        assert self
        # test command with no optional params
        sys.argv = ['test', 'database', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'database'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.debug_database
        assert not results.all
        assert not results.no_backup
        assert not results.verbose

        # test base args
        self.util_base_args(sys.argv)

        # test command with mp3 player option
        sys.argv = ['test', 'database', '-a', ]
        results = pyres.main.parse_command_line()
        assert results.command == 'database'
        assert results.database == 'rss.db'
        assert results.func == pyres.main.debug_database
        assert results.all
        assert not results.no_backup
        assert not results.verbose


class TestMain(object):
    """ Test the main function"""
    @patch('pyres.main.logging')
    def test_verbose(self, log_mock):
        """ call with and without verbose option set to ensure logging is set
        correctly """
        assert self
        sys.argv = ['test', 'process', ]
        results = pyres.main.parse_command_line()
        results.func = Mock()

        with patch('pyres.main.parse_command_line') as mock_parse:
            mock_parse.return_value = results
            pyres.main.main()

        assert results.func.call_count == 1
        assert log_mock.basicConfig.assert_not_called

        results.verbose = True

        with patch('pyres.main.parse_command_line') as mock_parse:
            mock_parse.return_value = results
            pyres.main.main()

        assert results.func.call_count == 2
        assert log_mock.basicConfig.call_count == 1

    @patch('pyres.main.backup_database')
    def test_no_backup(self, backup_mock):
        """  exit is called with bad args to main processor """
        assert self
        sys.argv = ['test', 'process', ]
        results = pyres.main.parse_command_line()
        results.func = Mock()

        with patch('pyres.main.parse_command_line') as mock_parse:
            mock_parse.return_value = results
            pyres.main.main()
        assert results.func.call_count == 1
        assert backup_mock.assert_not_called

        results.no_backup = True

        with patch('pyres.main.parse_command_line') as mock_parse:
            mock_parse.return_value = results
            pyres.main.main()

        assert results.func.call_count == 2
        assert backup_mock.call_count == 1

    @patch('pyres.main.shutil.copyfile')
    @patch('pyres.main.os.path.isfile')
    def test_no_database_file(self, isfile, copyfile):
        """ Test to make sure we don't try to create a back up of the database
        file if one doesn't exist"""
        assert self
        isfile.return_value = False

        sys.argv = ['test', 'process', ]
        results = pyres.main.parse_command_line()
        results.func = Mock()

        with patch('pyres.main.parse_command_line') as mock_parse:
            mock_parse.return_value = results
            pyres.main.main()
        assert results.func.call_count == 1
        assert copyfile.assert_not_called


class TestDebugDatabase(object):
    """ Test the debug database function"""
    def test_show_all(self, emptyfile):  # pylint: disable=W0621
        """ call debug_database with show all flag set to true """
        assert self
        with patch('pyres.main.PodcastDatabase.show_all_episodes') as show_all:
            with patch('pyres.main.PodcastDatabase.show_podcasts') \
                    as show_podcasts:
                # set up the arguments
                args = argparse.Namespace()
                args.all = True
                args.database = emptyfile

                # call the routine
                pyres.main.debug_database(args)

                # test that we called the right things
                show_all.assert_called_once_with()
                assert not show_podcasts.call_count

    def test_show_not_all(self, emptyfile):  # pylint: disable=W0621
        """ call debug_database with show all flag set to false """
        assert self
        with patch('pyres.main.PodcastDatabase.show_all_episodes') as show_all:
            with patch('pyres.main.PodcastDatabase.show_podcasts') \
                    as show_podcasts:
                # set up the arguments
                args = argparse.Namespace()
                args.all = False
                args.database = emptyfile

                # call the routine
                pyres.main.debug_database(args)

                # test that we called the right things
                show_podcasts.assert_called_once_with()
                assert not show_all.call_count


def test_audiobook(newplayer):  # pylint: disable=W0621
    """ Test audiobook mgmt function """
    with patch('pyres.main.FileManager.copy_audiobook') as copy_mock:
        # set up the arguments
        args = argparse.Namespace()
        args.dir = "test_dir"
        args.mp3_player = newplayer

        # call the routine
        pyres.main.manage_audiobook(args)

        # test that we called the right things
        print(copy_mock.call_count)
        copy_mock.assert_called_once_with('test_dir')


class TestDownload(object):
    """ Test the download to player function"""
    def test_no_podcasts(self, emptyfile):  # pylint: disable=W0621
        """ call download with no podcasts in the database"""
        assert self
        with patch('pyres.main.PodcastDatabase.mark_episode_on_mp3_player') \
                as mark_episode:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                # set up the patch to return an empty list
                get_names.return_value = []

                # set up the arguments
                args = argparse.Namespace()
                args.database = emptyfile

                # call the routine
                pyres.main.download_to_player(args)

                # test that we called the right things
                get_names.assert_called_once_with()
                assert mark_episode.call_count == 0

    def test_one_podcast_no_episodes(self, emptyfile):  # pylint: disable=W0621
        """ one podcast but no episodes to download """
        assert self
        with patch('pyres.main.PodcastDatabase.find_episodes_to_copy') \
                as to_copy:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                # set up the patch to return an empty list
                get_names.return_value = ['podcast', ]
                to_copy.return_value = []

                # set up the arguments
                args = argparse.Namespace()
                args.database = emptyfile

                # call the routine
                pyres.main.download_to_player(args)

                # test that we called the right things
                get_names.assert_called_once_with()
                to_copy.assert_called_once_with('podcast')

    @patch('pyres.main.FileManager.copy_episodes_to_player')
    def test_one_podcast_two_episodes(self, copier,
                                      emptyfile,  # pylint: disable=W0621
                                      newplayer):  # pylint: disable=W0621
        """ one podcast with two episodes to download """
        assert self
        with patch('pyres.main.PodcastDatabase.find_episodes_to_copy') \
                as to_copy:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                with patch('pyres.main.PodcastDatabase.'
                           'mark_episode_on_mp3_player') as mark_eps:
                    # set up the patch to return an empty list
                    get_names.return_value = ['podcast', ]
                    episode_list = ['ep1', 'ep2', ]
                    to_copy.return_value = episode_list

                    # set up the arguments
                    args = argparse.Namespace()
                    args.database = emptyfile
                    args.mp3_player = newplayer

                    # call the routine
                    pyres.main.download_to_player(args)

                    # test that we called the right things
                    get_names.assert_called_once_with()
                    to_copy.assert_called_once_with('podcast')
                    copier.assert_called_once_with(episode_list)
                    assert mark_eps.call_count == 2

    @patch('pyres.main.FileManager.copy_episodes_to_player')
    def test_two_podcasts_two_episodes(self, copier,
                                       emptyfile,  # pylint: disable=W0621
                                       newplayer):  # pylint: disable=W0621
        """ two podcast with two episodes each to download """
        assert self
        with patch('pyres.main.PodcastDatabase.find_episodes_to_copy') \
                as to_copy:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                with patch('pyres.main.PodcastDatabase.'
                           'mark_episode_on_mp3_player') as mark_eps:
                    # set up the patch to return an empty list
                    get_names.return_value = ['podcast1', 'podcast2', ]
                    episode_list = ['ep1', 'ep2', ]
                    to_copy.side_effect = (episode_list, episode_list)

                    # set up the arguments
                    args = argparse.Namespace()
                    args.database = emptyfile
                    args.mp3_player = newplayer

                    # call the routine
                    pyres.main.download_to_player(args)

                    # test that we called the right things
                    get_names.assert_called_once_with()
                    assert to_copy.call_count == 2
                    list_to_copy = episode_list
                    list_to_copy.extend(episode_list)
                    copier.assert_called_once_with(list_to_copy)
                    assert mark_eps.call_count == 4


class TestProcess(object):
    """ Test the process rss feeds function"""
    def test_no_podcasts(self, emptyfile):  # pylint: disable=W0621
        """ call download with no podcasts in the database"""
        assert self
        with patch('pyres.main.PodcastDatabase.mark_episode_on_mp3_player') \
                as mark_episode:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                # set up the patch to return an empty list
                get_names.return_value = []

                # set up the arguments
                args = argparse.Namespace()
                args.database = emptyfile

                # call the routine
                pyres.main.process_rss_feeds(args)

                # test that we called the right things
                get_names.assert_called_once_with()
                assert mark_episode.call_count == 0

    def test_one_podcast_no_episodes(self, emptyfile):  # pylint: disable=W0621
        """ one podcast but no episodes to download """
        assert self
        with patch('pyres.main.PodcastDatabase.find_episodes_to_download') \
                as to_download:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                # set up the patch to return an empty list
                get_names.return_value = ['podcast', ]
                to_download.return_value = []

                # set up the arguments
                args = argparse.Namespace()
                args.database = emptyfile

                # call the routine
                pyres.main.process_rss_feeds(args)

                # test that we called the right things
                get_names.assert_called_once_with()
                to_download.assert_called_once_with('podcast')

    @patch('pyres.main.PodcastDownloader.return_successful_files')
    def test_one_podcast_two_episodes(self, downloader,
                                      emptyfile,  # pylint: disable=W0621
                                      newplayer):  # pylint: disable=W0621
        """ one podcast with two episodes to download """
        assert self

        class FakeEpisode(object):  # pylint: disable=too-few-public-methods
            """ Simple mock for episodes """
            def __init__(self, file_name, podcast):
                self.file_name = file_name
                self.podcast = podcast

        with patch('pyres.main.PodcastDatabase.find_episodes_to_download') \
                as to_download:
            with patch('pyres.main.PodcastDatabase.get_podcast_names') as \
                    get_names:
                with patch('pyres.main.PodcastDatabase.'
                           'mark_episode_downloaded') as mark_eps:
                    with patch('pyres.main.PodcastDownloader.'
                               'download_url_list') as download_list:
                        assert download_list
                        # set up the patch to return an empty list
                        get_names.return_value = ['podcast1', ]
                        episode_list = [FakeEpisode('ep1', 'podcast1'),
                                        FakeEpisode('ep2', 'podcast1'), ]
                        to_download.return_value = episode_list
                        downloader.return_value = episode_list

                        # set up the arguments
                        args = argparse.Namespace()
                        args.database = emptyfile
                        args.mp3_player = newplayer

                        # call the routine
                        pyres.main.process_rss_feeds(args)

                        # test that we called the right things
                        get_names.assert_called_once_with()
                        to_download.assert_called_once_with('podcast1')
                        downloader.assert_called_once_with()
                        assert mark_eps.call_count == 2


class TestMainDelete(object):
    """ Test the delete_podcast function"""
    def test_no_podcasts(self, emptyfile):  # pylint: disable=W0621
        """ call delete with no podcasts in the database"""
        assert self
        # set up the arguments
        args = argparse.Namespace()
        args.name = "not_there"
        args.database = emptyfile

        # call the routine
        pytest.raises(sqlite3.OperationalError, pyres.main.delete_podcast,
                      args)

    def test_call(self, emptyfile):  # pylint: disable=W0621
        """ call delete with patch to catch delete call"""
        assert self
        with patch('pyres.main.PodcastDatabase.delete_podcast') as delete:
            # set up the arguments
            args = argparse.Namespace()
            args.name = "podcast_name"
            args.database = emptyfile

            # call the routine
            pyres.main.delete_podcast(args)

            assert delete.called_once_with(args.name)


class TestAddUrl(object):
    """ Test the add_url function"""
    def test_no_episodes(self, emptyfile):  # pylint: disable=W0621
        """ call add url with no episodes found """
        assert self
        # set up the arguments
        args = argparse.Namespace()
        args.database = emptyfile
        args.url = "url"
        args.base_dir = "base_dir"
        args.max_update = "1"
        args.start_date = None

        # call the routine
        pyres.main.add_url(args)

    def test_episode_with_start_date(self, emptyfile):  # pylint: disable=W0621
        """ call add_url with a start date """
        assert self
        with patch('pyres.main.pyres.rss.add_episodes_from_feed') as add_ep:
            # set up the arguments
            args = argparse.Namespace()
            args.database = emptyfile
            args.url = "url"
            args.base_dir = "base_dir"
            args.max_update = "1"
            args.start_date = time.strptime("04/17/15", "%x")

            add_ep.return_value = "name", 1

            # call the routine
            pyres.main.add_url(args)

            assert add_ep.call_count == 1

    def test_episode_no_start_date(self, emptyfile):  # pylint: disable=W0621
        """ call add_url without a start date """
        assert self
        with patch('pyres.main.pyres.rss.add_episodes_from_feed') as add_ep:
            # set up the arguments
            args = argparse.Namespace()
            args.database = emptyfile
            args.url = "url"
            args.base_dir = "base_dir"
            args.max_update = "1"
            args.start_date = None

            add_ep.return_value = "name", 1

            # call the routine
            pyres.main.add_url(args)

            assert add_ep.call_count == 1


class TestUpdate(object):
    """ Test the update_download_list function"""
    """
    with PodcastDatabase(args.database) as _database:
        podcasts = _database.get_podcast_urls()
        total_added = 0
        for _tuple in podcasts:
            name, added = pyres.rss.add_episodes_from_feed(_database,
                                                           _tuple[0],
                                                           args.base_dir,
                                                           int(_tuple[1]),
                                                           _tuple[2])
            if added:
                total_added += added
                print("%-50s: %3d episodes since %s" %
                      (name, added, utils.date_as_string(_tuple[2])))
        print
        print("There are a total of %d episodes to be updated." %
              (total_added))

    """
    def test_no_podcasts(self, emptyfile):  # pylint: disable=W0621
        """ call update with no podcasts found """
        assert self
        # set up the arguments
        args = argparse.Namespace()
        args.database = emptyfile
        args.base_dir = "base_dir"

        # call the routine
        pyres.main.update_download_list(args)

    def test_update_with_one(self, emptyfile):  # pylint: disable=W0621
        """ call add_url with a an episode to add """
        assert self
        with patch('pyres.main.PodcastDatabase.get_podcast_urls') as get_pod:
            with patch('pyres.main.pyres.rss.add_episodes_from_feed') as add_e:
                # set up the arguments
                args = argparse.Namespace()
                args.database = emptyfile
                args.base_dir = "base_dir"

                add_e.return_value = "name", 1
                get_pod.return_value = ((0, 1,
                                         time.strptime("04/17/15", "%x")), )

                # call the routine
                pyres.main.update_download_list(args)

                assert add_e.call_count == 1
