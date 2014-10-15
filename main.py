"""
Test Program, I think.
"""
import argparse
import pyres.rss
import time

def cmd_string_to_date(date_string):
    """ Convert a formatted string into a date."""
    return time.strptime(date_string, "%x")

# JHA TODO add subcommands for different stages
def parse_command_line():
    parser = argparse.ArgumentParser(description='Pyres podcast manager.')
    parser.add_argument('-d', '--database-dump', action='store_true',
                        help="print contents of database and exit")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="print debug output while processing")
    parser.add_argument('-a', '--add-url', action='store',
                        help="URL of podcast to add")
    parser.add_argument('--start-date', action='store',
                        type=cmd_string_to_date,
                        help="date before first podcast to download")
    parser.add_argument('-w', '--download', action='store_true',
                        help="Download episodes to mp3 player")
    parser.add_argument('-u', '--update', action='store_true',
                        help="update the list of podcasts to download")
    parser.add_argument('--convert-database', action='store_true',
                        help="debug utility to convert database when mistakes"
                        " were made")


    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_command_line()
    pyres = pyres.rss.RssFeed()
    if args.database_dump:
        pyres.display_database()
    elif args.add_url:
        pyres.add_url(args.add_url, args.start_date)
    elif args.download:
        pyres.download_to_player()
    elif args.update:
        pyres.update_download_list()
    elif args.convert_database:
        pyres.convert_database()
    else:
        pyres.process_rss_feeds()
