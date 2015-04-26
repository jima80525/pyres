"""
Implements an abstraction to the database.
"""
import sqlite3
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
        self.cursor = self.connection.cursor()
        # test to ensure that the main podcasts table exists
        # Create it if not
        try:
            self.connection.execute("CREATE TABLE podcasts (name text, "
                                    "url text unique, needsfix bool)")
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

            cursor.execute("INSERT INTO podcasts VALUES (?, ?, 0)", (name, url))
            cursor.execute("CREATE TABLE '%s' (date text, title text unique, "
                           "file text, url text, size integer, state integer)"
                           % name)

    def add_new_episode_data(self, table, episode):
        """Add the episode data if not already present.  If the episode is
        present, do nothing.
        """
        if not episode.date or not episode.title or not episode.url:
            print("Got a bad episode from server, will not add:", episode.date,
                  episode.title, episode.url)
            return False
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * from '%s' where title = '%s'" %
                           (table, episode.title))
            check1 = cursor.fetchone()
            if check1 is None:
                try:
                    cursor.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, ?, ?)"
                                   % table, episode.as_list())
                    logging.debug("Added %s", episode.title)
                    return True
                except:
                    # Fresh air is giving me duplicate titles for some reason
                    # The table will throw on a duplicate name.  We'll ignore
                    # it for now.  Would be good to figure out what's going
                    # on there
                    pass

            else:
                logging.debug("Didn't add %s as it was already there!",
                              episode.title)
                return False

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
        with self.connection:
            cursor = self.connection.cursor()
            for row in cursor.execute("SELECT * from '%s' where "
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
        with self.connection:
            self.connection.execute("UPDATE '%s' SET size=? where title = ?"
                                    % table, (size, title))

    def _update_state(self, table, title, state):
        """ change state of podcast """
        with self.connection:
            self.connection.execute("UPDATE '%s' SET state=? where title = ?"
                                    % table, (state, title))

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
        with self.connection:
            self.connection.execute("UPDATE 'podcasts' SET needsfix=1 where "
                                    "name = '%s'" % (name))

    def does_podcast_need_fixup(self, name):
        """ Checks database to see if this podcast needs fixups. """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT needsfix from 'podcasts' where name = '%s'" \
                           % (name))
            check1 = cursor.fetchone()
            return bool(check1[0])

    def delete_podcast(self, name):
        """Delete a podcast from the main table.  Also drops the episode table
           for this podcast.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM podcasts WHERE name='%s'" % name)
            cursor.execute("DROP TABLE '%s'" % name)

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
        with self.connection:
            cursor = self.connection.cursor()
            urls = list(cursor.execute('SELECT url,name FROM podcasts '
                                       'ORDER BY name'))
            for _tuple in urls:
                url = _tuple[0]
                name = _tuple[1]
                cursor.execute("Select date from '%s' ORDER BY date DESC" %
                               name)
                check1 = cursor.fetchone()
                if check1 is not None:
                    latest_date = utils.string_to_date(check1[0])
                else:
                    latest_date = time.gmtime()
                tuples.append([url, latest_date])
        return tuples

    def get_podcast_names(self):
        """Return a list of podcasts
        """
        names = list()
        with self.connection:
            cursor = self.connection.cursor()
            for name in cursor.execute('SELECT name FROM podcasts ORDER BY '
                                       'name'):
                names.append(name[0])
        return names

    def show_podcasts(self, names_only):
        """Display information from database.
        """
        names = self.get_podcast_names()

        with self.connection:
            cursor = self.connection.cursor()
            for name in names:
                cursor.execute("SELECT needsfix from 'podcasts' where name "
                               "= '%s'" % (name))
                check1 = cursor.fetchone()
                print("%s (%s)" % (name, self.does_podcast_need_fixup(name)))
                if not names_only:
                    for row in cursor.execute("SELECT * FROM '%s'" % name):
                        row_list = list(row)
                        print row_list[0], row_list[1], row_list[5],
                        if row_list[3]:
                            print "URL OK"
                        else:
                            print "BAD URL"
                    print # extra line to separate podcasts

    def clean_table_of_dups(self, name):
        """ gets all episodes from a table, only keeping unique dates.  Then
        drops the table and re-creates it with only unique data. """
        uniques = dict()
        with self.connection:
            cursor = self.connection.cursor()
            for row in cursor.execute("SELECT * FROM '%s'" % name):
                row_list = list(row)
                print row_list[0], row_list[1], row_list[5]
                if not row_list[0] in uniques:
                    uniques[row_list[0]] = row_list
            print
            for key in uniques:
                print key, uniques[key][1]

            # now drop that table entirely!
            cursor.execute("DROP TABLE '%s'" % name)
            # and re-create it
            cursor.execute("CREATE TABLE '%s' (date text, title text unique, "
                           "file text, url text, size integer, state integer)"
                           % name)

            for key in uniques:
                cursor.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, ?, ?)" %
                               name, uniques[key])

    def convert_tables(self):
        """ Utility to change format of the podcast tables. """
        # JHA this  returned names, too podcasts = self.jima_get_podcast_urls()
        #for _tuple in sorted(podcasts):
            #print "%-49s" % (_tuple[1])
            #self.clean_table_of_dups(_tuple[1])

        #name = 'NPR Fresh Air'
        #name = 'How To Do Everything'
        #name = 'TED Radio Hour'
        #name = 'This American Life'
        #name = 'Wait Wait... Dont Tell Me!'
        #self.clean_table_of_dups(name)
        #pass
        # use old version of string to date function
        #utils.string_to_date = lambda x: time.strptime(x, "%x:%X")
        #######################################################################
        # Walk through podcasts table, adding field
        with self.connection:
            cursor = self.connection.cursor()
            urls = list(cursor.execute('SELECT * FROM podcasts ORDER BY name'))

            #casts = list()
            for _tuple in urls:
                name = _tuple[0]
                url = _tuple[1]
                flag = _tuple[2]
                print flag, name
            #print urls
            #cursor.execute("DROP TABLE 'podcasts'")
            #self.connection.execute("CREATE TABLE podcasts (name text, "
                                    #"url text unique, needsfix bool)")
            #for _tuple in urls:
                #url = _tuple[0]
                #name = _tuple[1]
                #cursor.execute("INSERT INTO podcasts VALUES (?, ?, 0)",
                               #(name, url))

        #######################################################################
        # Print names of podcasts
        #names = self.get_podcast_names()
        #for name in names:
            #print name

        #######################################################################
        # Code below here will read all tables and allow conversion of field
        # values in individual podcasts
        #names = self.get_podcast_names()
        #print names

        #with self.connection:
            #cursor = self.connection.cursor()
            #for name in names:
                #newtable = list()
                #print "----------------------------------------"
                #print name
                #print "----------------------------------------"
                #for row in cursor.execute("SELECT * FROM '%s'" % name):
                    # right now we're converting date from mm/dd/yy to
                    # yyyy/mm/dd to it sorts correctly
                    #row_list = list(row)
                    #row_list.append(0)
                    #newtable.append(row_list)
                #print newtable
                #cursor.execute("DROP TABLE '%s'" % name)
                #cursor.execute("CREATE TABLE '%s' (date text, "
                               #"title text unique, file text, url text, "
                               #"size integer, state integer, convert integer)"
                           #% name)
                #for podcast in newtable:
                    #cursor.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, ?" \
                                   #", ?, ?)" % name, podcast)

if __name__ == "__main__":
    print "Not Implemented"
