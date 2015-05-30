"""
Tool to download and manage podcasts.
"""
import feedparser
import os
import logging
import time
from pyres.episode import Episode
import pyres.utils as utils


def __process_feed(url, base_dir, start_date):
    """ Pull down the rss feed and add return episodes """
    feed = feedparser.parse(url)

    # some feeds have ill formed entries.  Skip them if they
    # don't have a channel or a title or items
    if 'items' not in feed or 'channel' not in feed or \
       'title' not in feed['channel']:
        return None, None

    # get name and clean out any characters we don't like before we start
    # using it.
    podcast_name = feed['channel']['title']
    podcast_name = utils.clean_name(podcast_name)

    # now we can use it for the path
    podcast_path_name = os.path.join(base_dir, podcast_name)

    # create the podcast directory as long as we're here
    utils.mkdir_p(podcast_path_name)

    episodes = __process_items(feed, podcast_path_name, podcast_name,
                               start_date)

    return podcast_name, episodes


def __process_items(feed, podcast_path_name, podcast_name, start_date):
    """ Walk the list of items and return the list of episodes generated """

    episodes = list()
    for feed_data in feed["items"]:
        if 'published' not in feed_data or 'title' not in feed_data:
            continue  # only pull episodes that have dates

        raw_date = feed_data['published']
        # remove last word from published date - it's a timezone
        # and we don't really care about the timezone as most feeds are
        # likely to remain with the same timezone and we're only using
        # dates for ordering.
        raw_date = raw_date.rsplit(' ', 1)[0]
        date = time.strptime(raw_date, "%a, %d %b %Y %X")
        # when comparing,  date None is always the least
        if start_date > date:
            continue
        try:
            # make sure as end up with only ascii in the titles.  Not great
            # for international users, but I"m currently only listening to
            # english language podcasts.  We'll need something better here
            # to support other character sets.
            title = feed_data['title'].encode('ascii', 'replace')
            # titles with single quotes (') provide an extra challenge for
            # SQL entries.
            title = title.replace("'", "''")
            link = None
            if 'links' in feed_data:
                for k in feed_data["links"]:
                    if 'type' in k and 'audio' in k['type']:
                        link = k['href'] or link
                if link:
                    # the memory palace and a few other podcasts have
                    # ocassionally published videos.  My player doesn't
                    # support them, and the above code ends up without a
                    # valid link for them.  Skip them without an error
                    episodes.append(Episode(base_path=podcast_path_name,
                                            date=date, title=title,
                                            url=link, podcast=podcast_name))
        except KeyError:
            logging.error("Failed processing feed title")
            raise
    return episodes


def add_episodes_from_feed(database, url, base_dir, throttle, start_date=None):
    """ Add episodes from url into database. """
    name, episodes = __process_feed(url, base_dir, start_date)
    if not name or not episodes:
        return None, 0

    # adds table for podcast - likely to exist already
    database.add_podcast(name, url, throttle)

    episodes_added = 0
    # sort the episodes so we get the oldest ones first - this is needed for
    # feeds for which we have a throttle value
    episodes.sort(key=lambda x: x.date, reverse=False)

    # get either all of the episodes or the throttle limit
    for index in range(0, min(throttle, len(episodes))):
        logging.debug("Adding %s", utils.date_as_string(episodes[index].date))
        if database.add_new_episode_data(name, episodes[index]):
            episodes_added += 1
    return name, episodes_added

if __name__ == "__main__":
    print "NOT IMPLEMENTED"
