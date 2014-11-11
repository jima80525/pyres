"""
Tool to download and manage podcasts.
"""
import feedparser
import os
import logging
import time
import shutil
import pyres.database
import pyres.download
import pyres.episode
import pyres.filemanager
import pyres.utils as utils

class RssFeed(object):
    """ Class to manage rss feeds """
    def __init__(self, base_dir="Files"):
        self.base_dir = base_dir
        self.database_name = 'rss.db'

    def process_feed(self, url):
        """
        Pull down the rss feed and add return episodes
        """
        feed = feedparser.parse(url)
        # get name and clean out any characters we don't like before we start
        # using it.
        podcast_name = feed['channel']['title']
        podcast_name = utils.clean_name(podcast_name)

        # now we can use it for the path
        podcast_path_name = os.path.join(self.base_dir, podcast_name)

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
                                                      url=link,
                                                      podcast=podcast_name))

            except KeyError:
                logging.error("Failed processing feed title")
                raise
        return podcast_name, episodes

    def add_episodes_from_feed(self, database, url, start_date=None):
        """ Add episodes from url into database. """
        name, episodes = self.process_feed(url)

        # adds table for podcast - likely to exist already
        database.add_podcast(name, url)

        episodes_added = 0
        # for each podcast in this feed - add it to databse
        for episode in episodes:
            # when comparing,  date None is always the least
            if start_date < episode.date:
                logging.debug("Adding %s", utils.date_as_string(episode.date))
                database.add_new_episode_data(name, episode)
                episodes_added += 1
        return name, episodes_added

    def convert_database(self):
        """ debug routine to convert the database """
        with pyres.database.PodcastDatabase(self.database_name) as database:
            database.convert_tables()

    def display_database(self):
        """ debug routine to display the database """
        with pyres.database.PodcastDatabase(self.database_name) as database:
            database.show_podcasts()

    def add_url(self, url, start_date):
        """ add a new podcast to the system """
        logging.debug("in add url with %s %s", url, start_date)
        with pyres.database.PodcastDatabase(self.database_name) as database:
            name, added = self.add_episodes_from_feed(database, url, start_date)
            if start_date:
                print("%-50s: %3d episodes since %s" % \
                      (name, added, utils.date_as_string(start_date)))
            else:
                print("%-50s: %3d episodes returned" % (name, added))

    def process_rss_feeds(self):
        """ Main routine for program """
        with pyres.database.PodcastDatabase(self.database_name) as database:

            podcasts = database.get_podcast_names()

            episodes = list()

            for podcast in podcasts:
                tmp_list = database.find_episodes_to_download(podcast)
                episodes += tmp_list
                if len(tmp_list) != 0:
                    print("%-50s: %3d episodes to download" % (podcast, len(tmp_list)))
            downloader = pyres.download.PodcastDownloader(episodes)
            downloader.download_url_list()
            for episode in downloader.return_successful_files():
                database.mark_episode_downloaded(episode)
                print episode.file_name

    def update_download_list(self):
        """ Queries each podcast website for new episodes to down load.  Adds
        these to the database.
        """
        with pyres.database.PodcastDatabase(self.database_name) as database:
            podcasts = database.get_podcast_urls()
            total_added = 0
            for _tuple in podcasts:
                name, added = self.add_episodes_from_feed(database, _tuple[0],
                                                          _tuple[1])
                if added:
                    total_added += added
                    print("%-50s: %3d episodes since %s" % \
                          (name, added, utils.date_as_string(_tuple[1])))
            print
            print("There are a total of %d episodes to be updated." %
                  (total_added))

    def download_to_player(self):
        """ copy episodes to mp3 player """
        with pyres.database.PodcastDatabase(self.database_name) as database:

            podcasts = database.get_podcast_names()
            filemgr = pyres.filemanager.FileManager()

            episodes = list()
            for podcast in podcasts:
                new_episodes = database.find_episodes_to_copy(podcast)
                if len(new_episodes) != 0:
                    print("%-50s: %3d" % (podcast, len(new_episodes)))
                    episodes.extend(new_episodes)

            print
            print("Copying %d episodes to player" % len(episodes))

            # copy all the files in one list so they come out in date
            # order
            filemgr.copy_files_to_player(episodes)
            for episode in episodes:
                database.mark_episode_on_mp3_player(episode)

    def backup_database(self):
        if os.path.isfile(self.database_name):
            utils.mkdir_p("BACKUP")
            suffix = utils.current_date_time_as_string()
            filename = os.path.join("BACKUP", self.database_name + "_" + suffix)
            shutil.copyfile(self.database_name, filename)
        else:
            logging.debug("No database file to back up")

if __name__ == "__main__":
    FEED = RssFeed()
    exit(FEED.process_rss_feeds())
