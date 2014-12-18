""" Test test """
#import unittest
import os
#import stat
#import pyres.database
from pyres.database import PodcastDatabase


def _make_file(file_name):
    """ _make_file(file_name): makes an empty file.  """
    _file = open(file_name, 'w')
    _file.write('')
    _file.close()


# content of test_tmpdir.py
def test_needsfiles(tmpdir):
    """ Testing pytest """
    print tmpdir
    print "passed new assert"

    #assert 0


class TestOpen(object):
    """ test the open functionality """

    def test_new_db(self):
        """ create a new database """
        assert self
        with PodcastDatabase('newdb.db') as _database:
            assert _database

        os.remove('newdb.db')

    def test_existing_db(self):
        """ open an existing database """
        assert self
        myx = "hello"
        assert 'h' in myx
        #assert 'm' in myx
        #assert hasattr(myx, 'check')
        db_name = 'existing.db'
        _make_file(db_name)
        with PodcastDatabase(db_name) as _database:
            assert _database
        os.remove(db_name)

    #def testReadOnlyFile(self):
        #try:
            #db_name = 'rofile.db'
            #_make_file(db_name)
            #os.chmod(db_name, stat.S_IREAD)
            #self.assertRaises(Exception, pyres.db.open_podcasts, db_name)
        #except:
            #pass
        #os.chmod(db_name, stat.S_IWRITE)
        #os.remove(db_name)

    #def testOpenParams(self):
        #self.assertRaises(AttributeError, pyres.db.open_podcasts, None)


#class CloseTests(unittest.TestCase):

    #def testWithOpen(self):
        #db_name = 'existing.db'
        #_make_file(db_name)
        #conn, cur = pyres.db.open_podcasts(db_name)
        #self.failUnless(conn)
        #self.failUnless(cur)
        #pyres.db.close_podcasts(conn)

    #def testWithoutOpen(self):
        #self.assertRaises(AttributeError, pyres.db.close_podcasts, None)


#class AddPCTests(unittest.TestCase):
    #def setUp(self):
        #self.db_name = 'add_test.db'
        #_make_file(self.db_name)
        #self.conn, self.cur = pyres.db.open_podcasts(self.db_name)
        #self.failUnless(self.conn)
        #self.failUnless(self.cur)

    #def tearDown(self):
        #pyres.db.close_podcasts(self.conn)

    #def testNormalAdd(self):
        #pyres.db.add_podcast(self.cur, 'name1', 'url1', 'here')
        #pyres.db.add_podcast(self.cur, 'name2', 'url2', 'here')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' in names)
        #self.failUnless('name2' in names)

    #def testAddNameTwice(self):
        #pyres.db.add_podcast(self.cur, 'name1', 'url1', 'here')
        #self.assertRaises(Exception, pyres.db.add_podcast, self.cur, 'name1',
                          #'url2', 'here')
        ## makes sure the names is still there only once
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' in names)
        #self.failUnless(len(names) == 1)

    #def testAddParams(self):
        #self.assertRaises(AttributeError, pyres.db.add_podcast, None, 'name1',
                          #'url1', 'here')
        #self.assertRaises(AttributeError, pyres.db.add_podcast, self.cur,
                            #None,
                          #'url1', 'here')
        #self.assertRaises(AttributeError, pyres.db.add_podcast, self.cur,
                          #'name1', None, 'here')
        ##pyres.db.add_podcast(self.cur, None, 'url1', 'here')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless(len(names) == 0)


#class DeletePCTests(unittest.TestCase):
    #def setUp(self):
        #self.db_name = 'add_test.db'
        #_make_file(self.db_name)
        #self.conn, self.cur = pyres.db.open_podcasts(self.db_name)
        #self.failUnless(self.conn)
        #self.failUnless(self.cur)

    #def tearDown(self):
        #pyres.db.close_podcasts(self.conn)

    #def testDeleteFromEmpty(self):
        #self.assertRaises(Exception, pyres.db.delete_podcast, self.cur,
                          #'name1')

    #def testAddThenDelete(self):
        #pyres.db.add_podcast(self.cur, 'name1', 'url1', 'here')
        #pyres.db.add_podcast(self.cur, 'name2', 'url2', 'here')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' in names)
        #self.failUnless('name2' in names)
        #self.failUnless(len(names) == 2)

        ## now delete name1
        #pyres.db.delete_podcast(self.cur, 'name1')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' not in names)
        #self.failUnless('name2' in names)
        #self.failUnless(len(names) == 1)

        ## now delete name2
        #pyres.db.delete_podcast(self.cur, 'name2')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' not in names)
        #self.failUnless('name2' not in names)
        #self.failUnless(len(names) == 0)

    #def testNormalAdd(self):
        ## add name1
        #pyres.db.add_podcast(self.cur, 'name1', 'url1', 'here')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' in names)
        #self.failUnless(len(names) == 1)

        ## now delete it
        #pyres.db.delete_podcast(self.cur, 'name1')
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' not in names)
        #self.failUnless(len(names) == 0)

        ## now delete it again
        #self.assertRaises(Exception, pyres.db.delete_podcast, self.cur,
                          #'name1')
        ## just a sanity check here
        #names = pyres.db.get_podcast_names(self.cur)
        #self.failUnless('name1' not in names)
        #self.failUnless(len(names) == 0)


## content of test_sample.py
#def func(x):
    #return x + 1


#def test_answer():
    #assert func(3) == 5
