"""
Implements an abstraction to the database.
"""
import sqlite3
import pyres.episode as mod_episode
import pyres.utils as utils

class PodcastDatabase(object):
    """ Class to encapsulate access to database """
    def __init__(self, file_name):
        if not file_name:
            raise AttributeError()

        self.connection = sqlite3.connect(file_name)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        # test to ensure that the main podcasts table exists
        # Create it if not
        try:
            self.connection.execute("CREATE TABLE podcasts (name text, url " \
                                    "text)")
        except sqlite3.OperationalError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_type:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()

    def add_podcast(self, name, url):
        """Add a new podcast url to the database and set up a table to track
           episodes.
        """
        if not name or not url:
            raise AttributeError()

        with self.connection:
            cursor = self.connection.cursor()

            # make sure this podcast isn't already there
            cursor.execute("Select * from podcasts where name = ?", (name, ))
            check1 = cursor.fetchone()
            if check1 is not None:
                return  # already exists

            cursor.execute("INSERT INTO podcasts VALUES (?, ?)", (name, url))
            cursor.execute("CREATE TABLE '%s' (date text, title text, file "
                           "text, url text, state integer)" % name)

    def add_new_episode_data(self, table, episode):
        """Add the episode data if not already present.  If the episode is
        present, do nothing.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * from '%s' where date = '%s'" % \
                           (table, episode.date))
            check1 = cursor.fetchone()
            if check1 is None:
                cursor.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, ?)" % \
                               table, episode.as_list())
                print("Added %s" % episode.title)

    def find_episodes_to_download(self, table):
        """Return a list of (url, filename) tuples for each file to be
        downloaded.
        """
        episodes = list()
        with self.connection:
            cursor = self.connection.cursor()
            for row in cursor.execute("SELECT * from '%s' where " \
                                      "state = 0" % table):
                row_list = list(row)
                episodes.append(
                    mod_episode.Episode(date=utils.string_to_date(row_list[0]),
                                        title=row_list[1],
                                        file_name=row_list[2], url=row_list[3],
                                        state=row_list[4]))
        return episodes


    def _update_state(self, table, title, state):
        """

        :param cur:
        :param table:
        :param title:
        :param state:
        """
        with self.connection:
            self.connection.execute("UPDATE '%s' SET state=? where title = ?" \
                                    % table, (state, title))


    def mark_episode_downloaded(self, table, episode):
        """

        :param cur:
        :param table:
        :param title:
        """
        print("in mark with %s %s" % (table, episode.title))
        self._update_state(table, episode.title, 1)


    def delete_podcast(self, name):
        """Delete a podcast from the main table.  Also drops the episode table
           for this podcast.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM podcasts WHERE name='%s'" % name)
            cursor.execute("DROP TABLE '%s'" % name)


    def get_podcast_names(self):
        """Return a list of podcasts
        """
        names = list()
        with self.connection:
            cursor = self.connection.cursor()
            for name in cursor.execute('SELECT name FROM podcasts ORDER BY '
                                       'name'):
                names.append(name)
        return names


    def show_podcasts(self):
        """Display information from database.
        """
        names = self.get_podcast_names()
        with self.connection:
            cursor = self.connection.cursor()
            for name in names:
                print
                print name
                for podcast in cursor.execute("SELECT * FROM '%s'" % name):
                    print podcast


if __name__ == "__main__":
    print "Not Implemented"
