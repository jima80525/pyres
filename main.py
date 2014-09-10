"""
Test Program, I think.
"""
import argparse
import pyres.rss

def parse_command_line():
    parser = argparse.ArgumentParser(description='Pyres podcast manager.')
    parser.add_argument('-d', '--database-dump', action='store_true',
                        help="print contents of database and exit")
    parser.add_argument('--default-urls', action='store_true',
                        help="add default podcasts to database for testing")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="print debug output while processing")

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_command_line()
    # JHA TODO get logging working with verbose flag
    if args.database_dump:
        pyres.rss.display_database()
    elif args.default_urls:
        pyres.rss.add_default_urls_to_database()
    else:
        pyres.rss.process_rss_feeds()
