"""
Class representing a single episode of a podcast
"""
import os
import logging
import pyres.utils as utils


# pylint: disable-msg=R0902
class Episode(object):
    """ Class to encapsulate a single episode """
    def __init__(self, **kwargs):
        self.date = kwargs['date']
        self.title = kwargs['title']
        self.url = kwargs['url']
        self.podcast = kwargs['podcast']
        # set file size and error_msg to None at first
        self.error_msg = None
        if 'size' in kwargs:
            self.size = kwargs['size']
        else:
            self.size = None
        if 'state' in kwargs:
            self.state = kwargs['state']
        else:
            self.state = 0

        if 'base_path' in kwargs:
            # create file name
            postfix = utils.acroname(kwargs['podcast'])
            self.file_name = os.path.join(kwargs['base_path'],
                                          utils.clean_name(
                                              utils.date_as_string(self.date))
                                          + postfix + ".mp3")
        elif 'file_name' in kwargs:
            self.file_name = kwargs['file_name']
        else:
            raise Exception("No path or filename specified for episode %s" %
                            kwargs['title'])

    def as_list(self):
        """
        Return all fields of object as a list. Handy for inserting into
        database.
        """
        return (utils.date_as_string(self.date), self.title, self.file_name,
                self.url, self.size, self.state)

    def debug_display(self):
        """ Print current info of episode to logging """
        logging.debug(self.as_list())


if __name__ == "__main__":
    print "Not Implemented"
