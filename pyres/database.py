"""
Implements an abstraction to the database.
"""
from __future__ import print_function
import sqlite3
import sys
import logging
import time
import pyres.episode as mod_episode
import pyres.utils as utils


class PodcastDatabase(object):
    """ Class to encapsulate access to database """
    def __init__(self, file_name):
        if not file_name:
            raise AttributeError()

        self.connection = sqlite3.connect(file_name)
        self.connection.text_factory = str
        self.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        # test to ensure that the main podcasts table exists
        # Create it if not
        try:
            self.cursor.execute("CREATE TABLE podcasts (name text, "
                                "url text unique, needsfix bool, "
                                "throttle int)")
        except sqlite3.OperationalError:
            pass
        # check to see if we're on the proper database version, if not, update
        try:
            cursor = self.cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            current_version = 1
            if version != current_version:
                print("=================================")
                print("CONVERTING DATABASE TO NEW FORMAT")
                print("=================================")
                self.convert_to_new_version(version, current_version)
                cursor = self.cursor.execute("PRAGMA user_version = %s" %
                                             current_version)

        except sqlite3.OperationalError:
            print("Failed reading database version or doing conversion")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_type:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def add_podcast(self, name, url, throttle):
        """Add a new podcast url to the database and set up a table to track
           episodes.
        """
        if not name or not url:
            raise AttributeError()

        # make sure this podcast isn't already there
        if len(list(self.cursor.execute("Select * from podcasts where name = "
                                        "?", (name, )))):
            return  # already exists

        try:
            self.cursor.execute("INSERT INTO podcasts VALUES (?, ?, 0, ?)",
                                (name, url, throttle))
            self.cursor.execute("CREATE TABLE '%s' (date text, title text unique, "
                                "file text, url text, size integer, state integer)"
                                % name)
        except sqlite3.IntegrityError as e:
            print("failed to insert %s:%s" % (name, e))

    def add_new_episode_data(self, table, episode):
        """Add the episode data if not already present.  If the episode is
        present, do nothing.
        """
        if not episode.date or not episode.title or not episode.url:
            # not using %s formats for last three in case they are None
            print("Got a bad episode from %s server, will not add: (date, "
                  "title, url):" % table, episode.date, episode.title,
                  episode.url)
            return False

        try:
            self.cursor.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, ?, ?)"
                                % table, episode.as_list())
            logging.debug("Added %s", episode.title)
            return True
        except sqlite3.IntegrityError:
            # Fresh air is giving me duplicate titles for some reason. The
            # table will throw on a duplicate name.  We'll ignore it for now.
            # Would be good to figure out what's going on there
            return True

    def find_episodes_to_download(self, table):
        """ returns a list of episodes read to download """
        return self.find_episodes(table, 0)

    def find_episodes_to_copy(self, table):
        """ returns a list of episodes read to copy to mp3 player """
        return self.find_episodes(table, 1)

    def find_episodes(self, table, state):
        """Return a list of (url, filename) tuples for each file to be
        downloaded.
        """
        episodes = list()
        for row in self.cursor.execute("SELECT * from '%s' where "
                                       "state = %s" % (table, state)):
            row_list = list(row)
            episodes.append(
                mod_episode.Episode(date=utils.string_to_date(row_list[0]),
                                    title=row_list[1], podcast=table,
                                    file_name=row_list[2], url=row_list[3],
                                    size=row_list[4], state=row_list[5]))
        return episodes

    def _update_size(self, table, title, size):
        """ change state of podcast """
        logging.debug("In update size with %s %s %d", table, title, size)
        self.cursor.execute("UPDATE '%s' SET size=? where title = ?" % table,
                            (size, title))

    def _update_state(self, table, title, state):
        """ change state of podcast """
        self.cursor.execute("UPDATE '%s' SET state=? where title = ?" % table,
                            (state, title))

    def mark_episode_downloaded(self, episode):
        """ update state to downloaded and update size """
        logging.debug("in mark with %s %s", episode.podcast, episode.title)
        self._update_state(episode.podcast, episode.title, 1)
        self._update_size(episode.podcast, episode.title, episode.size)

    def mark_episode_on_mp3_player(self, episode):
        """ update state to downloaded and update size """
        logging.debug("in on player : %s %s", episode.podcast, episode.title)
        self._update_state(episode.podcast, episode.title, 2)

    def mark_podcast_for_fixups(self, name):
        """ update flag on podcast to indicate it needs fixup """
        self.cursor.execute("SELECT name from  'podcasts' where name = '%s'"
                            % (name))
        check1 = self.cursor.fetchone()
        if check1:
            self.cursor.execute("UPDATE 'podcasts' SET needsfix=1 where name "
                                "= '%s'" % (name))
        else:
            raise sqlite3.OperationalError

    def does_podcast_need_fixup(self, name):
        """ Checks database to see if this podcast needs fixups. """
        self.cursor.execute("SELECT needsfix from 'podcasts' where name = "
                            "'%s'" % (name))
        check1 = self.cursor.fetchone()
        return bool(check1[0])

    def delete_podcast(self, name):
        """Delete a podcast from the main table.  Also drops the episode table
           for this podcast.
        """
        self.cursor.execute("DELETE FROM podcasts WHERE name='%s'" % name)
        self.cursor.execute("DROP TABLE '%s'" % name)

    def get_podcast_urls(self):
        """Return a list of urls.  Goes through the table list and produces a
        list of [name, url] tuples.  Walks this list and produces a list of
        [url, latest_date] tuples from the podcast tables specified by names.
        I suspect someone better at SQL than I could get this in a single
        query, but this will work quickly enough for the small data sets I'm
        expecting.
        """
        urls = list()
        tuples = list()
        urls = list(self.cursor.execute('SELECT url,name,throttle FROM '
                                        'podcasts ORDER BY name'))
        for _tuple in urls:
            url = _tuple[0]
            name = _tuple[1]
            throttle = _tuple[2]
            dates = list(self.cursor.execute("Select date from '%s' ORDER BY "
                                             "date DESC" % name))
            if len(dates):
                latest_date = utils.string_to_date(dates[0][0])
            else:
                latest_date = time.gmtime()
            tuples.append([url, throttle, latest_date])
        return tuples

    def get_podcast_names(self):
        """Return a list of podcasts
        """
        names = list()
        for name in self.cursor.execute('SELECT name FROM podcasts ORDER BY '
                                        'name'):
            names.append(name[0])
        return names

    def convert_to_new_version(self, old_version, current_version):
        """ Do an automatic database conversion. """
        if old_version != 0:
            print("Unrecognized old version in database conversion",
                  old_version)
            sys.exit()
        if current_version != 1:
            print("Unrecognized current version in database conversion",
                  current_version)
            sys.exit()

        # now set it to maxsize for each podcast
        urls = list(self.cursor.execute('SELECT * FROM podcasts ORDER BY '
                                        'name'))
        self.cursor.execute("DROP TABLE 'podcasts'")
        self.cursor.execute("CREATE TABLE podcasts (name text, "
                            "url text unique, needsfix bool, throttle int)")
        for _tuple in urls:
            self.cursor.execute("INSERT INTO podcasts VALUES (?, ?, 0, ?)",
                                (_tuple[0], _tuple[1], sys.maxsize))

    def show_all_episodes(self):
        """Display information from database.
        """
        names = self.get_podcast_names()

        for name in names:
            print("%s (%s)" % (name, self.does_podcast_need_fixup(name)))
            for row in self.cursor.execute("SELECT * FROM '%s'" % name):
                row_list = list(row)
                print(row_list[0], row_list[1], row_list[5],)
                if row_list[3]:
                    print("URL OK")
            print()  # extra line to separate podcasts

    def show_podcasts(self):
        """ show entries in the podcasts table """
        urls = list(self.cursor.execute('SELECT * FROM podcasts ORDER BY '
                                        'name'))

        for _tuple in urls:
            print(_tuple)

    def show_names(self):
        """ show names of podcasts in the podcasts table """
        urls = list(self.cursor.execute('SELECT name FROM podcasts ORDER BY '
                                        'name'))

        for _tuple in urls:
            print(_tuple[0])
