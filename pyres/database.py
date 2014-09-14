"""
Implements an abstraction to the database.
"""
import sqlite3

class PodcastDatabase(object):
    """ Class to encapsulate access to database """
    def __init__(self, file_name):
        print "incstor"
        if not file_name:
            raise AttributeError()

        self.connection = sqlite3.connect(file_name)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        # test to ensure that the main podcasts table exists
        # Create it if not
        try:
            self.cursor.execute("CREATE TABLE podcasts (name text, url " \
                                "text, what real)")
        except sqlite3.OperationalError:
            pass

    def __enter__(self):
        print "in enter"
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        print "in exit"
        self.connection.commit()
        self.connection.close()

    def add_podcast(self, name, url, what):
        """Add a new podcast url to the database and set up a table to track
           episodes.
        """
        if not name or not url:
            raise AttributeError()

        # make sure this podcast isn't already there
        self.cursor.execute("Select * from podcasts where name = ?", (name, ))
        check1 = self.cursor.fetchone()
        if check1 is not None:
            return  # already exists

        self.cursor.execute("INSERT INTO podcasts VALUES (?, ?, ?)",
                            (name, url, what))
        self.cursor.execute("CREATE TABLE '%s' (date text, title text, file "
                            "text, url text, state integer)" % name)


    def add_new_episode_data(self, table, date, title, url):
        """Add the episode data if not already present.  If the episode is
        present, do nothing.
        """
        filename = date.replace(":", "_").replace("/", "_")
        self.cursor.execute("SELECT * from '%s' where date = '%s'" % \
                            (table, date))
        check1 = self.cursor.fetchone()
        if check1 is None:
            print("Added %s" % title)
            self.cursor.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, 0)" % \
                                table, (date, title, filename, url))

    def find_episodes_to_download(self, table, path):
        """Return a list of (url, filename) tuples for each file to be
        downloaded.
        """
        episodes = list()
        assert isinstance(table, object)
        for row in self.cursor.execute("SELECT url, file from '%s' where " \
                                       "state = 0" % table):
            row_list = list(row)
            row_list.append("%s\\%s.mp3" % (path, row[1]))
            episodes.append(row_list)
        return episodes


    def _update_state(self, table, title, state):
        """

        :param cur:
        :param table:
        :param title:
        :param state:
        """
        self.cursor.execute("UPDATE '%s' SET state=? where title = ?" % table,
                            (state, title))


    def mark_episode_downloaded(self, table, title):
        """

        :param cur:
        :param table:
        :param title:
        """
        self._update_state(table, title, 1)


    def delete_podcast(self, name):
        """Delete a podcast from the main table.  Also drops the episode table
           for this podcast.
        """
        self.cursor.execute("DELETE FROM podcasts WHERE name='%s'" % name)
        self.cursor.execute("DROP TABLE '%s'" % name)


    def get_podcast_names(self):
        """Return a list of podcasts
        """
        names = list()
        for row in self.cursor.execute('SELECT * FROM podcasts ORDER BY name'):
            names.append(row[0])
        return names


    def show_podcasts(self):
        """Display information from database.
        """
        # jha this can probably be done in one call with a clever join.
        # Not tonight.
        names = list()
        for name in self.cursor.execute( \
            'SELECT name FROM podcasts ORDER BY name'):
            names.append(name)
        for name in names:
            print
            print name
            for podcast in self.cursor.execute("SELECT * FROM '%s'" % name):
                print podcast


if __name__ == "__main__":
    print "JHA TODO"
    #CONNECTION, CURSOR = open_podcasts('example.db')
    #show_podcasts(CURSOR)
    #add_podcast(CURSOR, 'pc1', u"pc1url", 19)
    #delete_podcast(CURSOR, 'pc1')
    #close_podcasts(CONNECTION)
