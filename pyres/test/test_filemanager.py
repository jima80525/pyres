""" Test the Filemanager module """
import os
import time
import pyres.filemanager
from mock import patch


class TestFilemanager(object):
    """ test the open functionality """

    def test_create(self, tmpdir):
        """  just call the cstor for the object """
        assert self
        filemgr = pyres.filemanager.FileManager(base_dir=tmpdir.dirname)
        assert filemgr.does_filesystem_exist()

    @patch('shutil.copyfile')
    def test_copy(self, mock_copy):   # pylint: disable=W0621
        """  copy files correctly """
        assert self
        episodes = [
            pyres.episode.Episode(
                date=time.localtime(),
                title='title',
                url='url',
                podcast='podcast',
                size=1234,
                state=1,
                # one of these two required
                base_path='base_path',
                file_name='file_name'
            ),
            pyres.episode.Episode(
                date=time.gmtime(),  # use gm time to get a different value
                title='title',
                url='url',
                podcast='podcast',
                size=1234,
                state=1,
                # one of these two required
                base_path='base_path',
                file_name='file_name2'
            )
        ]

        copy_base = 'copy_base'
        filemgr = pyres.filemanager.FileManager(base_dir=copy_base)
        assert filemgr

        filemgr.copy_episodes_to_player(episodes)
        assert mock_copy.called
        assert mock_copy.call_count == 2

    @patch('shutil.copyfile')
    @patch('pyres.filemanager.utils.mkdir_p')
    @patch('pyres.filemanager.os.walk')
    def test_audiobook_copy(self, os_walk, mkdir_p,
                            copyfile):   # pylint: disable=W0621
        """  test simple file copy """
        assert self
        assert mkdir_p  # to appease pylint
        os_walk.return_value = [
            ('/foo', ['bar', ], ('baz',)),
            ('/foo/bar', [], ('spam', 'eggs')),
        ]
        copy_base = 'copy_base'
        filemgr = pyres.filemanager.FileManager(base_dir=copy_base)
        filemgr.copy_audiobook("source")
        assert copyfile.called
        print copyfile.call_args_list
        assert copyfile.call_count == 3
        assert copyfile.any_call('/foo/baz')
        assert copyfile.any_call('/foo/bar/spam')
        assert copyfile.any_call('/foo/bar/eggs')

    @patch('shutil.copyfile')
    @patch('pyres.filemanager.utils.mkdir_p')
    @patch('pyres.filemanager.os.walk')
    def test_audiobook_name(self, os_walk, mkdir_p,
                            copyfile):   # pylint: disable=W0621
        """  test that names with numbers are converted correctly """
        assert self
        assert mkdir_p  # to appease pylint

        def single_file(filename, expected):
            """ Test a single file """
            os_walk.return_value = [
                # if os.walk returns a root with leading /, os.path.join
                # doesn't add the filemanager base_dir to the path.  This
                # makes it a bit easier to write these tests
                ('/foo', [], (filename,)),
            ]
            filemgr.copy_audiobook("source")
            copyfile.assert_called_with(os.path.join('/foo', filename),
                                        os.path.join('/foo', expected))

        copy_base = 'copy_base'
        filemgr = pyres.filemanager.FileManager(base_dir=copy_base)
        assert filemgr
        # one digit
        single_file('1one', '01one')
        single_file('o1ne', 'o01ne')
        single_file('one1', 'one01')

        # two digits
        single_file('11two', '11two')
        single_file('t11wo', 't11wo')
        single_file('two11', 'two11')

        # three digits
        single_file('123three', '123three')
        single_file('th123ree', 'th123ree')
        single_file('three123', 'three123')

        # mp3 extension not changed
        single_file('1baz.mp3', '01baz.mp3')
        single_file('b1az.mp3', 'b01az.mp3')
        single_file('baz1.mp3', 'baz01.mp3')

        # test multiple substitutions
        single_file('1b1a1z.1mp3', '01b01a01z.01mp3')
        #print copyfile.call_args_list

    @patch('shutil.copyfile')
    @patch('pyres.filemanager.utils.mkdir_p')
    @patch('pyres.filemanager.os.walk')
    def test_audiobook_dest_dir(self, os_walk, mkdir_p,
                                copyfile):   # pylint: disable=W0621
        """  test that the dest dir parameters is used correctly """
        assert self
        assert mkdir_p  # to appease pylint

        copy_base = 'copy_base'
        filemgr = pyres.filemanager.FileManager(base_dir=copy_base)
        assert filemgr
        os_walk.return_value = [
            ('source', [], ("wilma",)),
        ]
        filemgr.copy_audiobook("source", "dest")
        print copyfile.call_args_list
        copyfile.assert_called_with(os.path.join('source', 'wilma'),
                                    os.path.join('copy_base', 'dest', 'source',
                                                 'wilma'))

    @patch('shutil.copyfile')
    @patch('pyres.filemanager.utils.mkdir_p')
    @patch('pyres.filemanager.os.walk')
    def test_audiobook_deep_dir(self, os_walk, mkdir_p,
                                copyfile):   # pylint: disable=W0621
        """  test that directory structures are preserved """
        assert self
        assert mkdir_p  # to appease pylint

        copy_base = 'copy_base'
        filemgr = pyres.filemanager.FileManager(base_dir=copy_base)
        assert filemgr
        os_walk.return_value = [
            # see note above about leading slashes on top level directory
            ('/first', ['second', ], ("wilma",)),
            ('/first/second', ['third', ], ("wilma",)),
            ('/first/second/third', ['', ], ("wilma", "fred")),
        ]
        filemgr.copy_audiobook("source")
        copyfile.assert_any_call(os.path.join('/first', 'wilma'),
                                 os.path.join('/first', 'wilma'))
        copyfile.assert_any_call(os.path.join('/first/second', 'wilma'),
                                 os.path.join('/first/second', 'wilma'))
        copyfile.assert_any_call(os.path.join('/first/second/third', 'wilma'),
                                 os.path.join('/first/second/third', 'wilma'))
        copyfile.assert_any_call(os.path.join('/first/second/third', 'fred'),
                                 os.path.join('/first/second/third', 'fred'))
