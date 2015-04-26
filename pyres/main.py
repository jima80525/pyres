""" Manage podcasts. """
import argparse
import time
import shutil
import os
import sys
import logging
import pyres.utils as utils
from pyres.rss import RssFeed
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


def display_database(args):
    """ debug routine to display the database """
    with PodcastDatabase(args.database) as _database:
        _database.show_podcasts(args.names_only)


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
        feedmgr = RssFeed(args.base_dir)
        name, added = feedmgr.add_episodes_from_feed(_database, args.url,
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
        feedmgr = RssFeed(args.base_dir)
        podcasts = _database.get_podcast_urls()
        total_added = 0
        for _tuple in podcasts:
            name, added = feedmgr.add_episodes_from_feed(_database, _tuple[0],
                                                         _tuple[1])
            if added:
                total_added += added
                print("%-50s: %3d episodes since %s" %
                      (name, added, utils.date_as_string(_tuple[1])))
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
        downloader = PodcastDownloader(episodes)
        downloader.download_url_list()
        for episode in downloader.return_successful_files():
            if (_database.does_podcast_need_fixup(episode.podcast)):
                print "Fixing...",
                utils.fixup_mp3_file(episode.file_name)

            _database.mark_episode_downloaded(episode)
            print episode.file_name,


def download_to_player(args):
    """ copy episodes to mp3 player """
    with PodcastDatabase(args.database) as _database:
        filemgr = FileManager(args.mp3_player)
        podcasts = _database.get_podcast_names()

        episodes = list()
        for podcast in podcasts:
            new_episodes = _database.find_episodes_to_copy(podcast)
            if len(new_episodes) != 0:
                print "%-50s: %3d" % (podcast, len(new_episodes))
                episodes.extend(new_episodes)

        print
        print "Copying %d episodes to player" % len(episodes)

        # copy all the files in one list so they come out in date
        # order
        filemgr.copy_files_to_player(episodes)
        for episode in episodes:
            _database.mark_episode_on_mp3_player(episode)


def convert_database(args):
    """ debug routine to convert the database """
    with PodcastDatabase(args.database) as _database:
        # fix up the table for one podcast
        _database.convert_tables()


def parse_command_line(input_args):
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

    # Dump database command
    dump_parser = subparsers.add_parser('dump', help='Show contents of '
                                        'database', parents=[base])
    dump_parser.add_argument('-n', '--names-only', action='store_true',
                             help="only display podcast names")
    dump_parser.set_defaults(func=display_database)

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
    add_parser.set_defaults(func=add_url)

    # podcast flag_fixup command
    flag_fixup_parser = subparsers.add_parser('flag_fixup', help="mark flag on "
                                              "podcast indicating mp3 files "
                                              "need to be post-processed",
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
                                 default="/media/jima/EC57-25A1/",
                                 help='The path to the mp3 player including '
                                 'drive')
    download_parser.set_defaults(func=download_to_player)

    # debug conversion of database on general command
    convert_parser = subparsers.add_parser('convert', help="debug utility to "
                                           "convert database when mistakes "
                                           "were made", parents=[base])
    convert_parser.set_defaults(func=convert_database)

    args = parser.parse_args(input_args)
    return args


def main(input_args):
    """ Main entry point for pyres application """
    args = parse_command_line(input_args)

    # database backup is done before any operation by default
    if not args.no_backup:
        backup_database(args)

    # if verbose flag is set - turn logging level up
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("verbose set")

    args.func(args)


if __name__ == "__main__":
    main(sys.argv)
