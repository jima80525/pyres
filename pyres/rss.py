"""
Tool to download and manage podcasts.
"""
import feedparser
import os
import logging
import time
import pyres.database
import pyres.download
import pyres.episode
import pyres.utils as utils

class RssFeed(object):
    """ Class to manage rss feeds """
    def __init__(self, base_dir="Files"):
        self.base_dir = base_dir

    def process_feed(self, url):
        """
        Pull down the rss feed and add return episodes
        """
        feed = feedparser.parse(url)
        podcast_name = feed['channel']['title']
        podcast_path_name = os.path.join(self.base_dir,
                                         utils.clean_name(podcast_name))

        # create the podcast directory as long as we're here
        utils.mkdir_p(podcast_path_name)

        episodes = list()
        for feed_data in feed["items"]:
            raw_date = feed_data['published']
            # remove last word from published date - it's a timezone
            # and we don't really care about the timezone as most feeds are
            # likely to remain with the same timezone and we're only using dates
            # for ordering.
            raw_date = raw_date.rsplit(' ', 1)[0]
            date = time.strptime(raw_date, "%a, %d %b %Y %X")
            try:
                title = feed_data['title'].encode('cp1252', 'replace')
                link = None
                for k in feed_data["links"]:
                    if 'audio' in k['type']:
                        link = k['href'] or link
                episodes.append(pyres.episode.Episode(base_path=\
                                                      podcast_path_name,
                                                      date=date, title=title,
                                                      url=link))

            except KeyError:
                logging.error("Failed processing feed title")
                raise
        return podcast_name, episodes

    def add_episodes_from_feed(self, database, url, start_date=None):
        """ Add episodes from url into database. """
        name, episodes = self.process_feed(url)

        # adds table for podcast - likely to exist already
        database.add_podcast(name, url)

        # for each podcast in this feed - add it to databse
        for episode in episodes:
            # when comparing,  date None is always the least
            if start_date < episode.date:
                logging.debug("Adding %s", utils.date_as_string(episode.date))
                database.add_new_episode_data(name, episode)

    @staticmethod
    def display_database():
        """ debug routine to display the database """
        with pyres.database.PodcastDatabase('rss.db') as database:
            database.show_podcasts()

    def add_url(self, url, start_date):
        """ add a new podcast to the system """
        logging.debug("in add url with %s %s", url, start_date)
        with pyres.database.PodcastDatabase('rss.db') as database:
            self.add_episodes_from_feed(database, url, start_date)

    # TODO - * then need a "copy to mp3 player and mark state as copied"
    # TODO - * then a "remove from mp3 player and harddrive and mark state as
    #        heard"
    @staticmethod
    def process_rss_feeds():
        """ Main routine for program """
        with pyres.database.PodcastDatabase('rss.db') as database:

            podcasts = database.get_podcast_names()

            for podcast in podcasts:
                episodes = database.find_episodes_to_download(podcast)
                print "----------------------------------------"
                print podcast
                print "----------------------------------------"
                downloader = pyres.download.PodcastDownloader(episodes)
                downloader.download_url_list()
                for episode in downloader.return_successful_files():
                    database.mark_episode_downloaded(podcast, episode)
                    print episode.file_name

if __name__ == "__main__":
    FEED = RssFeed()
    exit(FEED.process_rss_feeds())
