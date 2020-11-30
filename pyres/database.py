#!/usr/bin/env python3
import datetime
import peewee as pw
import dateutil
from .consts import BASEDATE, BASEDIR
from slugify import slugify
import pathlib

DATABASE = pw.SqliteDatabase(None)


def _make_date(strdate):
    return dateutil.utils.default_tzinfo(
        dateutil.parser.parse(strdate), dateutil.tz.UTC
    )


def _make_path(podcast, title):
    base_dir = pathlib.Path(BASEDIR)
    # create the directory for the stored files
    podcast_name = slugify(podcast)
    podcast_path_name = base_dir / podcast_name
    podcast_path_name.mkdir(exist_ok=True)
    filename = podcast_path_name / slugify(title)
    return str(filename) + ".mp3"


class PodcastExistsException(Exception):
    pass


class PodcastDoesNotExistException(Exception):
    pass


class BaseModel(pw.Model):
    class Meta:
        database = DATABASE


class Podcast(BaseModel):
    name = pw.TextField()
    throttle = pw.IntegerField(default=0)
    url = pw.TextField(unique=True)
    last_update = pw.DateTimeField(default=datetime.datetime.now())


class Episode(BaseModel):
    podcast = pw.ForeignKeyField(Podcast, backref="episodes")
    title = pw.TextField()
    date = pw.DateTimeField()
    file = pw.TextField(null=True)
    state_choices = ((0, "unknown"), (1, "downloaded"), (2, "on player"))
    state = pw.IntegerField(choices=state_choices)
    url = pw.TextField(unique=True)

    def get_state_label(self):
        return dict(self.state_choices)[self.state]


class PodcastDatabase(object):
    def __init__(self, file_name):
        if not file_name:
            raise AttributeError()

        DATABASE.init(file_name)
        DATABASE.connect()
        DATABASE.create_tables([Podcast, Episode])

    def __enter__(self):
        DATABASE.session_start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_type:
            DATABASE.session_commit()
        else:
            DATABASE.session_rollback()

        DATABASE.close()

    def show_names(self):
        print("Podcasts in database:")
        query = Podcast.select().order_by(Podcast.name)
        for podcast in query:
            print("  * ", podcast.name)

    def show_all_episodes(self):
        print("Podcast details in database:")
        query = Podcast.select().order_by(Podcast.name).prefetch(Episode)
        for podcast in query:
            print("  * ", podcast.name)
            for episode in podcast.episodes:
                print("      *", episode.title)

    def show_podcasts(self, all):
        """ show entries in the podcasts table """
        if all:
            return self.show_all_episodes()

        query = Podcast.select().order_by(Podcast.name)
        for podcast in query:
            print(f"'{podcast.name}' {podcast.throttle} {podcast.url}")

    def add_podcast(self, name, url, throttle):
        if not name or not url:
            raise AttributeError()

        try:
            podcast = Podcast(
                name=name, url=url, throttle=throttle, last_update=BASEDATE
            )
            podcast.save()
        except Exception:
            raise PodcastExistsException

        return podcast

    def delete_podcast(self, name):
        if not name:
            raise AttributeError()

        try:
            podcast_episodes = Podcast.select(Podcast.id).where(
                Podcast.name == name
            )
            Episode.delete().where(
                Episode.podcast_id.in_(podcast_episodes)
            ).execute()
            podcast = Podcast.select().where(Podcast.name == name).get()
            podcast.delete_instance()
        except Exception:
            raise PodcastDoesNotExistException

    # def add_new_episode_data(self, podcast_name, title, date, url):
    def add_new_episode_data(self, podcast_name, episode):
        if not podcast_name or not episode:
            raise AttributeError()

        try:
            podcast = Podcast.select().where(Podcast.name == podcast_name).get()
            last_date = _make_date(podcast.last_update)
            if episode.date > last_date:
                podcast.last_update = episode.date
                podcast.save()
            episode = Episode(
                podcast=podcast,
                title=episode.title,
                date=episode.date,
                file=_make_path(podcast.name, episode.title),
                state=0,
                url=episode.link,
            )
            episode.save()
            return episode
        except Exception:
            raise AttributeError()

    def find_episodes(self, table, state):
        episodes = list()
        for ep in Episode.select().join(Podcast).where(Episode.state == state):
            episodes.append(ep)

        return episodes

    def find_episodes_to_copy(self, table):
        return self.find_episodes(table, 1)

    def find_episodes_to_download(self):
        episodes = Episode.select().where(Episode.state == 0)
        return [(ep.url, ep.file) for ep in episodes]

    def get_podcast_names(self):
        """Return a list of podcasts."""
        podcasts = Podcast.select().order_by(Podcast.name)
        return [podcast.name for podcast in podcasts]

    def get_podcast_urls(self):
        # """ Returns a list of [url, latest_date] tuples for each podcast """
        podcasts = Podcast.select().order_by(Podcast.name)
        res = []
        for podcast in podcasts:
            date = _make_date(podcast.last_update)
            res.append((podcast.url, podcast.throttle, date))
        return res

    def mark_episode_downloaded(self, episode):
        ep = Episode.select().where(Episode.url == episode).get()
        ep.state = 1
        ep.save()

    def mark_episode_on_mp3_player(self, episode):
        ep = Episode.select().where(Episode.file == episode).get()
        ep.state = 2
        ep.save()


"""
JHA keeping this for time being until I get rest of system built around
the database layer. 07/07/2019
def populate():
    with PodcastDatabase("new_rss.db") as db:
        db.add_podcast("This American Life", "url", 0)
        db.add_podcast("two name", "twourl", 2)
        date = datetime.datetime.now()
        db.add_new_episode_data("two name", "two ep1", date, "two url1")
        db.add_new_episode_data("two name", "two ep2", date, "two url2")
        db.add_new_episode_data(
            "This American Life", "tal ep1", date, "tal url1"
        )
        db.add_new_episode_data(
            "This American Life", "tal ep2", date, "tal url2"
        )
        db.add_new_episode_data(
            "This American Life", "tal ep3", date, "tal url3"
        )
        db.add_new_episode_data(
            "This American Life", "tal ep5", date, "tal url7"
        )

if __name__ == "__main__":
    populate()
    with PodcastDatabase("new_rss.db") as db:
        db.show_all_episodes()
        # db.show_names()
        # db.show_podcasts()

    def find_episodes(self, table, state):
    def convert_to_new_version(self, old_version, current_version):

################################################################################
# list podcasts
DATABASE.connect()
for podcast in Podcast.select():
    print(podcast.name)

# Given a podcast name, list its episodes
for ep in Episode.select(Episode, Podcast).join(Podcast)
                                          .where(Podcast.name == "two name"):
    print(ep.title, ep.podcast.name)

################################################################################
# Given a podcast, list its episodes
ttt = Podcast.select().where(Podcast.name == "two name").get()
print(ttt.name)

for ep in Episode.select().join(Podcast).where(Episode.podcast == ttt):
    print(ep.title, ep.podcast.name)

################################################################################
# Get number of episodes for each podcast
query = (Podcast
         .select(Podcast, pw.fn.COUNT(Episode.id).alias('episode_count'))
         .join(Episode, pw.JOIN.LEFT_OUTER)
         .group_by(Podcast)
         .order_by(Podcast.name))

for podcast in query:
    print(podcast.name, podcast.episode_count, "episodes")

################################################################################
# list each episode for each podcast

query = Podcast.select().order_by(Podcast.name).prefetch(Episode)
for podcast in query:
    print(podcast.name)
    for episode in podcast.episodes:
        print("  *", episode.title)


DATABASE.close()


        """
