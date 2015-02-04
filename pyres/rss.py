"""
Tool to download and manage podcasts.
"""
import feedparser
import os
import logging
import time
from pyres.episode import Episode
import pyres.utils as utils


class RssFeed(object):
    """ Class to manage rss feeds """
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def process_feed(self, url):
        """
        Pull down the rss feed and add return episodes
        """
        feed = feedparser.parse(url)

        # some feeds have ill formed entries.  Skip them if they
        # don't have a channel or a title
        if 'channel' not in feed or 'title' not in feed['channel']:
            return None, None

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
            # likely to remain with the same timezone and we're only using
            # dates for ordering.
            raw_date = raw_date.rsplit(' ', 1)[0]
            date = time.strptime(raw_date, "%a, %d %b %Y %X")
            try:
                title = feed_data['title'].encode('cp1252', 'replace')
                # titles with single quotes (') provide an extra challenge for
                # SQL entries.
                title = title.replace("'", "''")
                link = None
                if 'links' in feed_data:
                    for k in feed_data["links"]:
                        if 'type' in k and 'audio' in k['type']:
                            link = k['href'] or link
                    episodes.append(Episode(base_path=podcast_path_name,
                                            date=date, title=title, url=link,
                                            podcast=podcast_name))
            except KeyError:
                logging.error("Failed processing feed title")
                raise
        return podcast_name, episodes

    def add_episodes_from_feed(self, database, url, start_date=None):
        """ Add episodes from url into database. """
        name, episodes = self.process_feed(url)
        if not name or not episodes:
            return None, None

        # adds table for podcast - likely to exist already
        database.add_podcast(name, url)

        episodes_added = 0
        # for each podcast in this feed - add it to databse
        for _episode in episodes:
            # when comparing,  date None is always the least
            if start_date < _episode.date:
                logging.debug("Adding %s", utils.date_as_string(_episode.date))
                database.add_new_episode_data(name, _episode)
                episodes_added += 1
        return name, episodes_added

if __name__ == "__main__":
    print "NOT IMPLEMENTED"
