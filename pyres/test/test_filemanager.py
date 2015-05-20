""" Test the Filemanager module """
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

    #def test_copy(self, tmpdir, filelist):   # pylint: disable=W0621
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
