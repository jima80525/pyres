"""
Implements an abstraction to the database.
"""
import sqlite3


def open_podcasts(filename):
    """ Opens connection to database.
    :param filename: full path to the database file
       """
    if not filename:
        raise AttributeError()
    conn = sqlite3.connect(filename)
    conn.text_factory = str
    cur = conn.cursor()
    # test to ensure that the main podcasts table exists
    # Create it if not
    try:
        cur.execute("CREATE TABLE podcasts (name text, url text, what real)")
    except sqlite3.OperationalError:
        pass
    return conn, cur

def add_podcast(cur, name, url, what):
    """Add a new podcast url to the database and set up a table to track
       episodes.
    """
    if not name or not url:
        raise AttributeError()

    # make sure this podcast isn't already there
    cur.execute("Select * from podcasts where name = ?", (name, ))
    check1 = cur.fetchone()
    if check1 is not None:
        return  # already exists

    cur.execute("INSERT INTO podcasts VALUES (?, ?, ?)",
                (name, url, what))
    cur.execute("CREATE TABLE '%s' (date text, title text, file text, url "
                "text, state integer)" % name)


def add_new_episode_data(cur, table, date, title, url):
    """Add the episode data if not already present.  If the episode is present,
    do nothing.
    """
    filename = date.replace(":", "_").replace("/", "_")
    cur.execute("SELECT * from '%s' where date = '%s'" % (table, date))
    check1 = cur.fetchone()
    if check1 is None:
        print("Added %s" % title)
        cur.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, 0)" % table,
                    (date, title, filename, url))

def find_episodes_to_download(cur, table, path):
    """Return a list of (url, filename) tuples for each file to be downloaded.
    """
    episodes = list()
    assert isinstance(table, object)
    for row in cur.execute("SELECT url, file from '%s' where state = 0" % \
                           table):
        row_list = list(row)
        row_list.append("%s\\%s.mp3" % (path, row[1]))
        episodes.append(row_list)
    return episodes


def _update_state(cur, table, title, state):
    """

    :param cur:
    :param table:
    :param title:
    :param state:
    """
    cur.execute("UPDATE '%s' SET state=? where title = ?" % table,
                (state, title))


def mark_episode_downloaded(cur, table, title):
    """

    :param cur:
    :param table:
    :param title:
    """
    _update_state(cur, table, title, 1)


def delete_podcast(cur, name):
    """Delete a podcast from the main table.  Also drops the episode table
       for this podcast.
    """
    cur.execute("DELETE FROM podcasts WHERE name='%s'" % name)
    cur.execute("DROP TABLE '%s'" % name)


def close_podcasts(conn):
    """Close the handle to the database.
    """
    # Save (commit) the changes
    conn.commit()
    conn.close()


def get_podcast_names(cur):
    """Return a list of podcasts
    """
    names = list()
    for row in cur.execute('SELECT * FROM podcasts ORDER BY name'):
        names.append(row[0])
    return names


def show_podcasts(cur):
    """Display information from database.
    """
    # jha this can probably be done in one call with a clever join.
    # Not tonight.
    names = list()
    for name in cur.execute('SELECT name FROM podcasts ORDER BY name'):
        names.append(name)
    for name in names:
        print
        print name
        for podcast in cur.execute("SELECT * FROM '%s'" % name):
            print podcast


if __name__ == "__main__":
    CONNECTION, CURSOR = open_podcasts('example.db')
    #show_podcasts(CURSOR)
    #add_podcast(CURSOR, 'pc1', u"pc1url", 19)
    delete_podcast(CURSOR, 'pc1')
    close_podcasts(CONNECTION)
