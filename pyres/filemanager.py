"""
manages the files on the mp3 player
"""
import os
import re
import logging
import shutil
import pyres.utils as utils


def _double_digit_name(name):
    """ Makes all numbers two digit numbers by adding a leading 0 where
    necessary.  Three digit or longer numbers are unaffected. """
    # do a little clean up to start with
    name = name.rstrip().replace('\\', '/')
    name = name.rstrip('/')  # make sure we don't have trailing / chars
    # now pull of the trailing '3' on .mp3 filenames so we don't convert that
    mp3suffix = ''
    if name.endswith('mp3'):
        name = name[:-1]
        mp3suffix = '3'

    # the regex produces a empty string at the end, skip that or zfill will
    # expand it to 00.  Note we cannot just remove the last element from the
    # split as it does not always produce an empty element.  Joy
    elements = re.split(r'(\d+)', name)
    if elements[-1] == '':
        elements.pop()
    result = ""
    # this next section is a bit goofy.  We need to tell whether a given
    # element is a number (\d+) or not.  Only if it's a number do we want to do
    # the zfill on it.  Else a name like '1b1a1z.1mp3' ends up adding a zero to
    # the b a and z elements as well as the 1s. (in other words that string
    # ends up with '010b010a010z.01mp3' instead of '01b01a01z.01mp3')
    # It might be possible to be clever about the regex grouping on the split,
    # but that idea is escaping me presently.
    for element in elements:
        try:
            int(element)
        except ValueError:
            result += element
        else:
            result += element.zfill(2)
    result += mp3suffix
    return re.sub(' +', ' ', result)  # remove double spaces


class FileManager(object):
    """ Class to manage filesystem on mp3 player """
    def __init__(self, base_dir):
        # set default value for mp3 player
        #base_dir = base_dir or "TestFiles"
        base_dir = base_dir or "/media/jima/EC57-25A1/"
        print base_dir
        self.base_dir = base_dir
        utils.mkdir_p(self.base_dir)

    def does_filesystem_exist(self):
        """ Tests for existence  - this is unused in real code, but it's handy
        for unit tests.  It was originally added to keep lint happy. """
        return os.path.exists(self.base_dir)

    def copy_audiobook(self, source_dir, dest_dir=None):
        """ Main routine to convert and copy files to mp3 player """
        if not dest_dir:
            dest_dir = source_dir
            print "Copying audiobook from %s" % source_dir
        else:
            print "Coping audiobook from %s to %s" % (source_dir, dest_dir)

        for root, dirs, files in os.walk(source_dir):
            dirs.sort()
            for dir_name in dirs:
                full_dir = os.path.join(root, _double_digit_name(dir_name))
                utils.mkdir_p(os.path.join(self.base_dir, full_dir))
            for filename in sorted(files):
                file_name = os.path.join(root, filename)
                newfile = _double_digit_name(os.path.join(self.base_dir,
                                                          dest_dir, file_name))
                logging.debug("copying %s to %s", file_name, newfile)
                print "copying to %s" % (newfile)
                shutil.copyfile(file_name, newfile)

    def copy_episodes_to_player(self, episodes):
        """ Copies the episodes to the mp3 player """
        # make sure the podcast directory exists
        podcast_dir = os.path.join(self.base_dir, "podcasts_" +
                                   utils.current_date_time_as_string())
        utils.mkdir_p(podcast_dir)

        total = len(episodes)
        counter = 0
        for episode in sorted(episodes, key=lambda x: x.date):
            episode.file_name = episode.file_name.replace('\\', '/')
            (_, tail) = os.path.split(episode.file_name)
            newfile = os.path.join(podcast_dir, tail)

            logging.debug("copying %s to %s", episode.file_name, newfile)
            shutil.copyfile(episode.file_name, newfile)

            counter += 1
            logging.debug("copied %s to %s", episode.file_name, newfile)
            print("%2d/%d: copied %s to %s" % (counter, total,
                                               episode.file_name, newfile))
if __name__ == "__main__":
    FSYS = FileManager()
