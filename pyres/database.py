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
    url = pw.TextField(unique=False)

    def get_state_label(self):
        return dict(self.state_choices)[self.state]


class PodcastDatabase(object):
    def __init__(self, file_name):
        if not file_name:
            raise AttributeError()

        DATABASE.init(file_name)

        print("in init")
        DATABASE.connect()
        DATABASE.create_tables([Podcast, Episode])
        print("leaving init")
        # JHA TODO figure out how to use it as a stand-alone object

    def __enter__(self):
        print("in enter")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_type:
            print("COMMITTING")
            DATABASE.commit()
        else:
            print("ROLLING BACK")
            DATABASE.rollback()

        DATABASE.close()
        print("in exit")

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
            podcast = Podcast.select().where(name == name).get()
            print("got new podcast", podcast)
        return podcast

    def add_new_episode_data(self, podcast, title, file, size, url):
        try:
            print(f"adding {title} with url={url}")
            episode = Episode(
                podcast=podcast,
                title=title,
                date=datetime.datetime.now(),
                file=file,
                size=size,
                state=1,
                url=url,
            )
            episode.save()
            print("JIMA TEST")
            for ep in Episode.select():
                print(ep.title)
            print("JIMA END TEST")
            return episode
        except Exception:
            print(
                f"Failed adding episode {title}. Episode with same url exists."
            )


def populate():
    with PodcastDatabase("new_rss.db") as db:
        tal = db.add_podcast("This American Life", "url", 0)
        two = db.add_podcast("two name", "twourl", 2)
        db.add_new_episode_data(two, "two ep1", "two file1", 13, "two url1")
        db.add_new_episode_data(two, "two ep2", "two file2", 13, "two url2")
        db.add_new_episode_data(tal, "tal ep1", "tal file1", 13, "tal url1")
        db.add_new_episode_data(tal, "tal ep2", "tal file2", 13, "tal url2")
        db.add_new_episode_data(tal, "tal ep3", "tal file3", 13, "tal url3")
        db.add_new_episode_data(tal, "tal ep5", "tal file4", 14, "tal url7")


if __name__ == "__main__":
    populate()
    with PodcastDatabase("new_rss.db") as db:
        #     print("inside cm")
        db.show_all_episodes()
        # db.show_names()
        # db.show_podcasts()

"""
    def find_episodes_to_copy(self, table):
    def find_episodes_to_download(self, table):
    def find_episodes(self, table, state):
    def mark_episode_downloaded(self, episode):
    def mark_episode_on_mp3_player(self, episode):
    def _update_size(self, table, title, size):
    def _update_state(self, table, title, state):
    def get_podcast_urls(self):
    def delete_podcast(self, name):
    def get_podcast_names(self):
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
