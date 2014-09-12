"""
Tool to download and manage podcasts.
"""
import feedparser
#import urllib2
#import shutil
#import urlparse
import os
import time
import pyres.db
import pyres.download
import errno


def mkdir_p(_path):
    """
    create a directory and all parent directires.  Does not raise
    exception if directory already exists.
    """
    try:
        print _path
        _path = _path.replace(":", "_")
        print _path
        os.makedirs(_path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(_path):
            pass
        else:
            raise


def process_feed(url):
    """

    :rtype : [string, list]
    """
    feed = feedparser.parse(url)
    podcast_name = feed['channel']['title']

    podcasts = list()
    for feed_data in feed["items"]:
        raw_date = feed_data['published']
        # remove last word from published date - it's a timezone
        # and we don't really care about the timezone as most feeds are
        # likely to be with the same timezone and we're only using dates
        # for ordering.
        raw_date = raw_date.rsplit(' ', 1)[0]
        date = time.strptime(raw_date, "%a, %d %b %Y %X")
        try:
            title = feed_data['title'].encode('cp1252', 'replace')
            #published = feed_data['published']  # jha unused - might need it?
            link = None
            for k in feed_data["links"]:
                if 'audio' in k['type']:
                    link = k['href'] or link
            podcasts.append((date, title, link))
        except KeyError:
            print "Failed processing feed title"
            raise
    return podcast_name, podcasts


URLS = (
    "http://rss.sciam.com/sciam/60-second-psych",
     #"http://thehistoryofbyzantium.wordpress.com/feed/",
)


def date_to_string(_date):
    """ Convert a date field into a string """
    return time.strftime("%x:%X", _date)


def string_to_date(date_string):
    """ Convert a formatted string into a date."""
    return time.strptime(date_string, "%x:%X")


def add_episodes_from_feed(cur, url):
    """ Add episodes from url into database. """
    name, podcasts = process_feed(url)

    # adds table for podcast - likely to exist already
    pyres.db.add_podcast(cur, name, url, "")

    # for each podcast in this feed - add it to databse
    for podcast in podcasts:
        pyres.db.add_new_episode_data(cur, name, date_to_string(podcast[0]),
                                      podcast[1], podcast[2])

def display_database():
    """ debug routine to display the database """
    conn, cur = pyres.db.open_podcasts('rss.db')
    pyres.db.show_podcasts(cur)
    pyres.db.close_podcasts(conn)


def add_url(url, start_date):
    """ add a new podcast to the system """
    print("in add url with %s %s" % (url, start_date))
    # if there is no cursor passed in, this was requested from the command line
    # open the database here.  If there was a cursor, then conn will stay None
    # and we won't close it
    #connection = None
    #if not cursor:
        #connection, cursor = pyres.db.open_podcasts('rss.db')
    #for url in URLS:
        #add_episodes_from_feed(cursor, url)
    #if connection:
        #pyres.db.close_podcasts(connection)
    #print "done In add defaults"

def add_default_urls_to_database(cursor = None):
    """ Debug routine to add a set of test urls to the database """
    print "In add defaults"
    # if there is no cursor passed in, this was requested from the command line
    # open the database here.  If there was a cursor, then conn will stay None
    # and we won't close it
    connection = None
    if not cursor:
        connection, cursor = pyres.db.open_podcasts('rss.db')
    for url in URLS:
        add_episodes_from_feed(cursor, url)
    if connection:
        pyres.db.close_podcasts(connection)
    print "done In add defaults"

#JHA - TODO
# - redo db.py to make it a class - it can hold cur and conn!
# * first lines here can be moved into a "add urls to db" command.
# * the need a "find episodes to download"
# * need to create a "add new url" function to replace first with outside url
# * then need a "copy to mp3 player and mark state as copied"
# * then a "remove from mp3 player and harddrive and mark state as heard"
def process_rss_feeds():
    """ Main routine for program """
    connection, cur = pyres.db.open_podcasts('rss.db')

    add_default_urls_to_database(cur)

    podcasts = pyres.db.get_podcast_names(cur)
    base_file_directory = "Files\\"

    to_mark = True
    for podcast in podcasts:
        # get the path and make sure it exists
        pathname = base_file_directory + podcast
        pathname = pathname.replace(':', '_')
        mkdir_p(pathname)

        episodes = pyres.db.find_episodes_to_download(cur, podcast, pathname)
        print "----------------------------------------"
        print podcast
        print "----------------------------------------"
        print "about to download"
        #pyres.download.download_url_list(episodes)
        #print "done"

    pyres.db.close_podcasts(connection)

def dummy():
        for episode in episodes:
            if to_mark:
                print "HERE IS EPISODE"
                print episode
                print "THERE IS WAS"
                #fname = "%s\\%s.mp3"%(pathname, episode[1])
                #f = list(episode)
                #f.append(fname)
                #print "jima"
                #print f
                #print "past"
                toget = (episode,)
                pyres.download.download_url_list(toget)

                #pyres.db.mark_episode_downloaded(cur, podcast, episode[1])
                #print episode, "MARKED"
                to_mark = False
                #else:
                #print episode


#feed = feedparser.parse(python_wiki_rss_url)

#for t in feed["items"]:
    # print "\nNEW ITEM\n"
    # #   print t["title"]
    # print t["published_parsed"]
    # #print t["link"]
    # #print
    # #   print t["pheedo_origenclosurelink"]
    # #print
    # #print t["links"]
    # #print
    # for k in t["links"]:
    #     if 'audio' in k['type']:
    #         print "this is the link:" + k['href']
if __name__ == "__main__":
    exit(process_rss_feeds())
