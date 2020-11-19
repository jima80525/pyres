"""
Tool to download and manage podcasts.
"""
import collections
import dateutil.parser
import dateutil.utils
import feedparser
import logging
import asks
import tqdm
import trio

EpData = collections.namedtuple("EpData", ["date", "title", "link"])
SiteData = collections.namedtuple("SiteData", ["url", "throttle", "start_date"])


def process_feed(data, start_date):
    """ Pull down the rss feed and return episodes """
    feed = feedparser.parse(data)

    # some feeds have ill formed entries.  Skip them if they
    # don't have a channel or a title or items
    if (
        "items" not in feed
        or "channel" not in feed
        or "title" not in feed["channel"]
    ):
        return None, None

    podcast_name = feed["channel"]["title"]
    episodes = []
    for feed_data in feed["items"]:
        ep = __process_item(feed_data, start_date)
        if ep:
            episodes.append(ep)

    # sort the episodes so we get the oldest ones first - this is needed for
    # feeds for which we have a throttle value
    episodes.sort(key=lambda x: x.date, reverse=False)

    return podcast_name, episodes


def __process_item(feed_data, start_date):
    """ Walk the list of items and return the list of episodes generated """
    if (
        "published" not in feed_data
        or "title" not in feed_data
        or "links" not in feed_data
    ):
        return None  # only pull episodes that have dates

    date = dateutil.parser.parse(feed_data["published"])
    if start_date >= date:
        return None
    try:
        # make sure as end up with only ascii in the titles. Not great for
        # international users, but I"m currently only listening to english
        # language podcasts. We'll need something better here to support other
        # character sets.
        # JHA TODO - does Peewee handle this escaping?
        title = feed_data["title"].encode("ascii", "replace")
        # titles with single quotes provide an extra challenge for SQL entries.
        title = title.replace("'".encode("utf-8"), "''".encode("utf-8"))
        # there can be multiple links to a single episode. We only want the
        # audio one. If there are multiple, take the last one.
        link = None
        for kk in feed_data["links"]:
            if "type" in kk and "audio" in kk["type"]:
                link = kk["href"] or link
        if link:
            # the memory palace and a few other podcasts have ocassionally
            # published videos. My player doesn't support them, and the above
            # code ends up without a valid link for them. Silently kip them.
            return EpData(date, title, link)
    except KeyError:
        logging.error("Failed processing feed")
        raise
    return None


def get_episode_list(data, site):
    """ Build a list of episodes from the RSS data. """
    name, episodes = process_feed(data, site.start_date)
    if not name or not episodes:
        return None, None

    # limit to the first "throttle" values
    if site.throttle != 0:
        episodes = episodes[: site.throttle]

    return name, episodes


class RssDownloader:
    """ Manage the rss download and parsing """

    def __init__(self, sites: SiteData):
        self.failed_files = []
        self.results = {}
        self.sites = sites

    async def _download_site(self, site, overall_bar):
        try:
            async with await asks.get(site.url) as req:
                name, episodes = get_episode_list(req.content, site)
                if name and episodes:
                    self.results[name] = episodes
                else:
                    self.failed.append(site.url)
        except Exception as ex:
            self.failed_files.append(site.url + ":" + str(ex))
        finally:
            overall_bar.update(1)

    async def _download_all_sites(self):
        progbar = tqdm.tqdm(total=len(self.sites), position=0, desc="rss feeds")
        progbar.update(0)
        async with trio.open_nursery() as nursery:
            for site in self.sites:
                nursery.start_soon(self._download_site, site, progbar)
        progbar.close()

    def download_episodes(self):
        trio.run(self._download_all_sites)
        return self.results, self.failed_files


if __name__ == "__main__":
    # JHA TODO - this needs to be used in the CLI to set a TZ for the start date
    start_date = dateutil.parser.parse("1/1/1970")
    start_date = dateutil.utils.default_tzinfo(start_date, dateutil.tz.UTC)
    ss = SiteData("https://realpython.com/podcasts/rpp/feed", 10, start_date)
    x, y = RssDownloader([ss]).download_episodes()
    print(y)
    print(x)
