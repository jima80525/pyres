""" Manage podcasts. """
import argparse
import time
import shutil
import os
import sys
import logging
import pyres.utils as utils
import pyres.rss
from pyres.database import PodcastDatabase
from pyres.filemanager import FileManager
from pyres.download import PodcastDownloader


def cmd_string_to_date(date_string):
    """ Convert a formatted string into a date."""
    return time.strptime(date_string, "%x")


def backup_database(args):
    """ Save a copy of the database before modifying """
    if os.path.isfile(args.database):
        utils.mkdir_p("BACKUP")
        suffix = utils.current_date_time_as_string()
        filename = os.path.join("BACKUP", args.database + "_" + suffix)
        shutil.copyfile(args.database, filename)
    else:
        logging.debug("No database file to back up")


def delete_podcast(args):
    """ Delete a podcast from the database """
    with PodcastDatabase(args.database) as _database:
        _database.delete_podcast(args.name)


def flag_fixup_for_podcast(args):
    """ Mark a podcast as needing fixups """
    with PodcastDatabase(args.database) as _database:
        _database.mark_podcast_for_fixups(args.name)


def add_url(args):
    """ add a new podcast to the system """
    logging.debug("in add url with %s %s", args.url, args.start_date)
    with PodcastDatabase(args.database) as _database:
        name, added = pyres.rss.add_episodes_from_feed(_database, args.url,
                                                       args.base_dir,
                                                       int(args.max_update),
                                                       args.start_date)
        if not name or not added:
            print "Error: No episodes added"
        elif args.start_date:
            print("%-50s: %3d episodes since %s" %
                  (name, added, utils.date_as_string(args.start_date)))
        else:
            print "%-50s: %3d episodes returned" % (name, added)


def update_download_list(args):
    """ Queries each podcast website for new episodes to down load.  Adds
    these to the database.
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


def process_rss_feeds(args):
    """ download podcasts from web to computer - poorly named """
    with PodcastDatabase(args.database) as _database:

        podcasts = _database.get_podcast_names()

        episodes = list()

        for podcast in podcasts:
            tmp_list = _database.find_episodes_to_download(podcast)
            episodes += tmp_list
            if len(tmp_list) != 0:
                print("%-50s: %3d episodes to download" % (podcast,
                                                           len(tmp_list)))
        if episodes:
            downloader = PodcastDownloader(episodes)
            downloader.download_url_list()
            for episode in downloader.return_successful_files():
                if _database.does_podcast_need_fixup(episode.podcast):
                    print "Fixing ", episode.file_name
                    utils.fixup_mp3_file(episode.file_name)

                _database.mark_episode_downloaded(episode)
                print episode.file_name


def download_to_player(args):
    """ copy episodes to mp3 player """
    with PodcastDatabase(args.database) as _database:
        podcasts = _database.get_podcast_names()

        episodes = list()
        for podcast in podcasts:
            new_episodes = _database.find_episodes_to_copy(podcast)
            print podcast, new_episodes
            if len(new_episodes) != 0:
                print "%-50s: %3d" % (podcast, len(new_episodes))
                episodes.extend(new_episodes)

        if episodes:
            print
            print "Copying %d episodes to player" % len(episodes)

            # copy all the files in one list so they come out in date
            # order
            filemgr = FileManager(args.mp3_player)
            filemgr.copy_episodes_to_player(episodes)
            for episode in episodes:
                _database.mark_episode_on_mp3_player(episode)
        else:
            print
            print "No episodes to copy"


def manage_audiobook(args):
    """ Copies audiobook to mp3 player """
    filemgr = FileManager(args.mp3_player)
    filemgr.copy_audiobook(args.dir)


def debug_database(args):
    """ debug routine to examine the database """
    with PodcastDatabase(args.database) as _database:
        # fix up the table for one podcast
        if args.all:
            _database.show_all_episodes()
        else:
            _database.show_podcasts()


def parse_command_line():
    """ Manage command line options """
    # base args are shared with all subcommands
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument('-v', '--verbose', action='store_true',
                      help="print debug output while processing")
    base.add_argument('-b', '--no-backup', action='store_true',
                      help="do not create an auto-backup of the database")
    base.add_argument('-d', '--database', action='store', default='rss.db',
                      help="name of database file")

    parser = argparse.ArgumentParser(description='Pyres podcast manager.',
                                     parents=[base])

    # add subcommands
    subparsers = parser.add_subparsers(help='commands', dest='command')

    # delete podcast command
    delete_parser = subparsers.add_parser('delete', help='remove podcast from '
                                          'database', parents=[base])
    delete_parser.add_argument('name', action='store', help="the name of the "
                               "podcast to delete")
    delete_parser.set_defaults(func=delete_podcast)

    # Add new URL command
    add_parser = subparsers.add_parser('add', help='Add a new podcast',
                                       parents=[base])
    add_parser.add_argument('url', action='store', help='The URL of the'
                            'podcast to add')
    add_parser.add_argument('--start-date', action='store',
                            type=cmd_string_to_date, help="date before first "
                            "podcast to download (04/17/15, for example)")
    add_parser.add_argument('--base-dir', action='store', default='Files',
                            help='The local direction in which to store '
                            'podcasts')
    add_parser.add_argument('--max-update', action='store',
                            default=sys.maxsize, help='The maximum number of '
                            'episodes to download at one time.')
    add_parser.set_defaults(func=add_url)

    # podcast flag_fixup command
    flag_fixup_parser = subparsers.add_parser('flag_fixup', help="mark flag "
                                              "on podcast indicating mp3 files"
                                              " need to be post-processed",
                                              parents=[base])
    flag_fixup_parser.add_argument('name', action='store', help="the name of "
                                   "the podcast to flag for fixups")
    flag_fixup_parser.set_defaults(func=flag_fixup_for_podcast)

    # Update existing podcasts - download to from web to computer
    update_parser = subparsers.add_parser('update', help="update the list of "
                                          "podcasts to download",
                                          parents=[base])
    update_parser.add_argument('--base-dir', action='store', default='Files',
                               help='The local direction in which to store '
                               'podcasts')
    update_parser.set_defaults(func=update_download_list)

    # process existing podcasts - download to from web to computer
    process_parser = subparsers.add_parser('process', help="download podcasts "
                                           "from web to computer",
                                           parents=[base])
    process_parser.set_defaults(func=process_rss_feeds)

    # download podcasts - download from computer to mp3 player
    download_parser = subparsers.add_parser('download', help="Download "
                                            "episodes to mp3 player",
                                            parents=[base])
    download_parser.add_argument('--mp3-player', action='store',
                                 default=None, help='The path to the mp3 '
                                 'player including drive')
    download_parser.set_defaults(func=download_to_player)

    # transfer an audiobook to mp3 play in correct order
    # Player is very fussy about the directory order (it does not sort by name)
    # Copying them in in the correct order gets it to play in the right order!
    audiobook_parser = subparsers.add_parser('audiobook', help="update the "
                                             "list of podcasts to download",
                                             parents=[base])
    audiobook_parser.add_argument('--dir', action='store', required=True,
                                  help='The directory from which the '
                                  'audiobook will be copied.')
    audiobook_parser.add_argument('--mp3-player', action='store',
                                  default=None, help='The path to the mp3 '
                                  'player including drive')
    audiobook_parser.set_defaults(func=manage_audiobook)

    # debug conversion of database on general command
    database_parser = subparsers.add_parser('database', help="debug utility "
                                            "to examine database.",
                                            parents=[base])
    database_parser.add_argument('-a', '--all', action='store_true',
                                 help="show all episode data")
    database_parser.set_defaults(func=debug_database)

    args = parser.parse_args(sys.argv[1:])
    return args


def main():
    """ Main entry point for pyres application """
    args = parse_command_line()

    # database backup is done before any operation by default
    if not args.no_backup:
        backup_database(args)

    # if verbose flag is set - turn logging level up
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("verbose set")

    args.func(args)
