"""
Implements an abstraction to the database.
"""
import sqlite3

def open_podcasts(filename):
    '''Opens connection to database.
       '''
    if not filename:
        raise AttributeError()
    conn = sqlite3.connect(filename)
    conn.text_factory = str
    cur = conn.cursor()
    # test to ensure that the main podcasts table exists
    # Create table
    try:
        cur.execute('''CREATE TABLE podcasts (name text, url text, what real)''')
    except:
        pass # ok if it exists - JHA TODO be more explicit in what we're
             # catching
    return conn, cur

# Create table
#c.execute('''CREATE TABLE podcasts (name text, url text, what real)''')

def add_podcast(cur, name, url, what):
    '''Add a new podcast url to the database and set up a table to track
       episodes.
    '''
    if not name or not url:
        raise AttributeError()

    # make sure this podcast isn't already there
    cur.execute("Select * from podcasts where name = ?", (name, ))
    check1 = cur.fetchone()
    if check1 is not None:
        raise Exception()

    cur.execute("INSERT INTO podcasts VALUES (?, ?, ?)",
          (name, url, what))
    cur.execute("CREATE TABLE '%s' (date text, title text, file text, url "
          "text, state integer)"%name)

def add_new_episode_data(cur, table, date, title, file, url):
    '''Add the episode data if not already present.  If the episode is present,
    do nothing.
    '''
    cur.execute("SELECT * from '%s' where date = '%s'" % (table, date))
    check1 = cur.fetchone()
    if check1 is None:
        print("Added %s" % title)
        cur.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?, 0)"%table,
          (date, title, file, url))
        print("after add")


def delete_podcast(cur, name):
    '''Delete a podcast from the main table.  Also drops the episode table
       for this podcast.
    '''
    cur.execute("DELETE FROM podcasts WHERE name='%s'"%name)
    cur.execute("DROP TABLE '%s'"%name)

def close_podcasts(conn):
    '''Close the handle to the database.
    '''
    # Save (commit) the changes
    conn.commit()
    conn.close()

def get_podcast_names(cur):
    '''Return a list of podcasts
    '''
    names = list()
    for row in cur.execute('SELECT * FROM podcasts ORDER BY name'):
        names.append(row[0])
    return names

def show_podcasts(cur):
    '''Display information from database.
    '''
    # jha this can probably be done in one call with a clever join.
    # Not tonight.
    names = list()
    for name in cur.execute('SELECT name FROM podcasts ORDER BY name'):
        names.append(name)
    for name in names:
        print
        print name
        for pc in cur.execute("SELECT * FROM '%s'"% name):
            print pc



if __name__ == "__main__":
    CONNECTION, CURSOR = open_podcasts('example.db')
    #show_podcasts(CURSOR)
    #add_podcast(CURSOR, 'pc1', u"pc1url", 19)
    delete_podcast(CURSOR, 'pc1')
    close_podcasts(CONNECTION)

