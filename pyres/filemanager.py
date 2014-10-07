"""
manages the files on the mp3 player
"""
import os
import logging
import shutil
import pyres.utils as utils

class FileManager(object):
    """ Class to manage filesystem on mp3 player """
    def __init__(self, base_dir="TestFiles"):
        self.base_dir = os.path.join(base_dir, "podcasts")
        utils.mkdir_p(self.base_dir)

    def does_filesystem_exist(self):
        """ Tests for existance """
        return os.path.exists(self.base_dir)

    def copy_files_to_player(self, episodes):
        """ Copies the episodes to the mp3 player """
        total = len(episodes)
        counter = 0
        for episode in sorted(episodes, key=lambda x: x.date):
            (_, tail) = os.path.split(episode.file_name)
            newfile = os.path.join(self.base_dir, tail)
            shutil.copyfile(episode.file_name, newfile)
            counter += 1
            logging.debug("copied %s to %s", episode.file_name, newfile)
            print("%2d/%d: copied %s to %s" % (counter, total,
                                              episode.file_name, newfile))


# TODO - * then need a "copy to mp3 player and mark state as copied"
# TODO - * then a "remove from mp3 player and harddrive and mark state as
#          heard"
# need utils:
    # walk directory tree
    # parsing xml file with current status - does it have 'i've listened to
    # this' info?
    #
# simple functionality:
    # get list of files in state 1
    # copy them to specified path
    # mark them as moved

if __name__ == "__main__":
    FSYS = FileManager()