import unittest
import os
import stat
from pyres import db

def _MakeFile(file_name):
	"""
		_MakeFile(file_name): makes an empty file.
	"""
	file = open(file_name, 'w')
	file.write('')
	file.close()

class OpenTests(unittest.TestCase):

    def testNewDB(self):
        conn, cur = db.open_podcasts('newdb.db')
        self.failUnless(conn)
        self.failUnless(cur)
        db.close_podcasts(conn)
        os.remove('newdb.db')

    def testExistingDB(self):
        db_name = 'existing.db'
        _MakeFile(db_name)
        conn, cur = db.open_podcasts(db_name)
        self.failUnless(conn)
        self.failUnless(cur)
        db.close_podcasts(conn)

    def testReadOnlyFile(self):
        try:
            db_name = 'rofile.db'
            _MakeFile(db_name)
            os.chmod(db_name, stat.S_IREAD)
            self.assertRaises(Exception, db.open_podcasts, db_name)
        except:
            pass
        os.chmod(db_name, stat.S_IWRITE)
        os.remove(db_name)

    def testOpenParams(self):
        self.assertRaises(AttributeError, db.open_podcasts, None)

class CloseTests(unittest.TestCase):

    def testWithOpen(self):
        db_name = 'existing.db'
        _MakeFile(db_name)
        conn, cur = db.open_podcasts(db_name)
        self.failUnless(conn)
        self.failUnless(cur)
        db.close_podcasts(conn)

    def testWithoutOpen(self):
        self.assertRaises(AttributeError, db.close_podcasts, None)

class AddPCTests(unittest.TestCase):
    def setUp(self):
        self.db_name = 'add_test.db'
        _MakeFile(self.db_name)
        self.conn, self.cur = db.open_podcasts(self.db_name)
        self.failUnless(self.conn)
        self.failUnless(self.cur)

    def tearDown(self):
        db.close_podcasts(self.conn)

    def testNormalAdd(self):
        db.add_podcast(self.cur, 'name1', 'url1', 'here')
        db.add_podcast(self.cur, 'name2', 'url2', 'here')
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' in names)
        self.failUnless('name2' in names)

    def testAddNameTwice(self):
        db.add_podcast(self.cur, 'name1', 'url1', 'here')
        self.assertRaises(Exception, db.add_podcast, self.cur, 'name1', 'url2', 'here')
        # makes sure the names is still there only once
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' in names)
        self.failUnless(len(names) == 1)

    def testAddParams(self):
        self.assertRaises(AttributeError, db.add_podcast, None, 'name1', 'url1', 'here')
        self.assertRaises(AttributeError, db.add_podcast, self.cur, None, 'url1', 'here')
        self.assertRaises(AttributeError, db.add_podcast, self.cur, 'name1', None, 'here')
        # JHA TODO - when rest of params for podcast are defined, add tests here
        #db.add_podcast(self.cur, None, 'url1', 'here')
        names = db.get_podcast_names(self.cur)
        self.failUnless(len(names) == 0)

class DeletePCTests(unittest.TestCase):
    def setUp(self):
        self.db_name = 'add_test.db'
        _MakeFile(self.db_name)
        self.conn, self.cur = db.open_podcasts(self.db_name)
        self.failUnless(self.conn)
        self.failUnless(self.cur)

    def tearDown(self):
        db.close_podcasts(self.conn)

    def testDeleteFromEmpty(self):
        self.assertRaises(Exception, db.delete_podcast, self.cur, 'name1')

    def testAddThenDelete(self):
        db.add_podcast(self.cur, 'name1', 'url1', 'here')
        db.add_podcast(self.cur, 'name2', 'url2', 'here')
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' in names)
        self.failUnless('name2' in names)
        self.failUnless(len(names) == 2)

        # now delete name1
        db.delete_podcast(self.cur, 'name1')
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' not in names)
        self.failUnless('name2' in names)
        self.failUnless(len(names) == 1)

        # now delete name2
        db.delete_podcast(self.cur, 'name2')
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' not in names)
        self.failUnless('name2' not in names)
        self.failUnless(len(names) == 0)

    def testNormalAdd(self):
        # add name1
        db.add_podcast(self.cur, 'name1', 'url1', 'here')
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' in names)
        self.failUnless(len(names) == 1)

        # now delete it
        db.delete_podcast(self.cur, 'name1')
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' not in names)
        self.failUnless(len(names) == 0)

        # now delete it again
        self.assertRaises(Exception, db.delete_podcast, self.cur, 'name1')
        # just a sanity check here
        names = db.get_podcast_names(self.cur)
        self.failUnless('name1' not in names)
        self.failUnless(len(names) == 0)

def main():
    unittest.main()

if __name__ == '__main__':
    main()

