#!/usr/bin/env python3
import datetime
import peewee as pw

DATABASE = pw.SqliteDatabase(None)


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
    size = pw.IntegerField(null=True)
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
        # JHA TODO figure out how to use it as a stand-alone object

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

    def show_podcasts(self):
        """ show entries in the podcasts table """
        query = Podcast.select().order_by(Podcast.name)
        for podcast in query:
            print(podcast.name, podcast.throttle, podcast.url)

    def add_podcast(self, name, url, throttle):
        if not name or not url:
            raise AttributeError()

        try:
            podcast = Podcast(
                name=name,
                url=url,
                throttle=throttle,
                last_update=datetime.datetime.now(),
            )
            podcast.save()
        except Exception:
            print(f"Failed adding {name}. Podcast with same url exists.")

        return podcast

    def delete_podcast(self, name):
        if not name:
            raise AttributeError()

        try:
            podcast = Podcast.select().where(Podcast.name == name).get()
        except Exception:
            raise AttributeError()

        podcast.delete_instance()

    def add_new_episode_data(self, podcast_name, title, date, url):
        if not podcast_name or not title or not date or not url:
            raise AttributeError()

        try:
            # fred = datetime.datetime.now()
            podcast = Podcast.select().where(Podcast.name == podcast_name).get()
            episode = Episode(
                podcast=podcast,
                title="title",
                date=date,
                file="",
                size=0,
                state=0,
                url=url,
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

    def find_episodes_to_download(self, table):
        return self.find_episodes(table, 0)

    def get_podcast_names(self):
        """Return a list of podcasts."""
        podcasts = Podcast.select().order_by(Podcast.name)
        return [podcast.name for podcast in podcasts]

    def get_podcast_urls(self):
        # """ Returns a list of [url, latest_date] tuples for each podcast """
        podcasts = Podcast.select().order_by(Podcast.name)
        return [
            (podcast.url, podcast.throttle, podcast.last_update)
            for podcast in podcasts
        ]

    def mark_episode_downloaded(self, episode):
        episode.state = 1
        episode.save()

    def mark_episode_on_mp3_player(self, episode):
        episode.state = 2
        episode.save()

    def update_size(self, episode, size):
        episode.size = size
        episode.save()


    def mark_episode_on_mp3_player(self, episode):
        episode.state = 2
        episode.save()


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
