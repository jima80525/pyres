"""
Test Program, I think.
"""
import argparse
import pyres.rss
import time

def cmd_string_to_date(date_string):
    """ Convert a formatted string into a date."""
    #return time.strptime(date_string, "%m/%d/%y")
    return time.strptime(date_string, "%x")

def parse_command_line():
    parser = argparse.ArgumentParser(description='Pyres podcast manager.')
    parser.add_argument('-d', '--database-dump', action='store_true',
                        help="print contents of database and exit")
    parser.add_argument('--default-urls', action='store_true',
                        help="add default podcasts to database for testing")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="print debug output while processing")
    parser.add_argument('-a', '--add-url', action='store',
                        help="URL of podcast to add")
    parser.add_argument('--start-date', action='store',
                        type=cmd_string_to_date,
                        help="date before first podcast to download")


    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_command_line()
    # JHA TODO get logging working with verbose flag
    if args.database_dump:
        pyres.rss.display_database()
    elif args.default_urls:
        pyres.rss.add_default_urls_to_database()
    elif args.add_url:
        pyres.rss.add_url(args.add_url, args.start_date)
    else:
        pyres.rss.process_rss_feeds()
