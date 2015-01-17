"""
manages the files on the mp3 player
"""
import os
import logging
import shutil
import pyres.utils as utils


class FileManager(object):
    """ Class to manage filesystem on mp3 player """
    #def __init__(self, base_dir="TestFiles"):
    def __init__(self, base_dir="/media/jima/549C-9E8D/"):
        self.base_dir = os.path.join(base_dir, "podcasts")
        utils.mkdir_p(self.base_dir)

    def does_filesystem_exist(self):
        """ Tests for existence  - this is unused, but it's a placeholder to
        keep lint happy until I add the management of files on the mp3 player -
        removing and copying audio books.  It might not make sense to keep this
        as a class. """
        return os.path.exists(self.base_dir)

    def copy_files_to_player(self, episodes):
        """ Copies the episodes to the mp3 player """
        total = len(episodes)
        counter = 0
        for episode in sorted(episodes, key=lambda x: x.date):
            episode.file_name = episode.file_name.replace('\\', '/')
            (_, tail) = os.path.split(episode.file_name)
            newfile = os.path.join(self.base_dir, tail)

            logging.debug("copying %s to %s", episode.file_name, newfile)
            shutil.copyfile(episode.file_name, newfile)

            # keeping win verson around for the time being
            #if sys.platform == 'win32':
                #logging.debug('xcopy /Q "%s" "%s" > '
                              #'tmp_pyres_file_do_not_use',
                              #episode.file_name, self.base_dir)
                #os.system('xcopy /Y /Q "%s" "%s" > tmp_pyres_file_do_not_use'
                          #% (episode.file_name, self.base_dir))
                #os.remove("tmp_pyres_file_do_not_use")
            #else:
                #logging.debug("copying %s to %s", episode.file_name, newfile)
                #shutil.copyfile(episode.file_name, newfile)

            counter += 1
            logging.debug("copied %s to %s", episode.file_name, newfile)
            print("%2d/%d: copied %s to %s" % (counter, total,
                                               episode.file_name, newfile))
if __name__ == "__main__":
    FSYS = FileManager()
