"""
Utility functions shared by pyres tool
"""
import os
import time
import errno

def mkdir_p(_path):
    """
    create a directory and all parent directires.  Does not raise
    exception if directory already exists.
    """
    try:
        _path = _path.replace(":", "_")
        os.makedirs(_path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(_path):
            pass
        else:
            raise

def clean_name(value, deletechars=r"\/:*%?\"<>|'"):
    """ remove bad character from possible file name component """
    for letter in deletechars:
        value = value.replace(letter, '')
    return value

def string_to_date(date_string):
    """ Convert a formatted string into a date."""
    return time.strptime(date_string, "%x:%X")

def date_as_string(value):
    """ Convert a date field into a string """
    return time.strftime("%x:%X", value)

def acroname(name):
    """ Returns a three letter acronym given a podcast title """
    word_list = name.split()

    # first, trim npr label from some podcasts
    if ('NPR' == word_list[0]):
        word_list = word_list[1:]

    if (name.startswith("Scientific American Podcast")):
        word_list = word_list[3:]

    if (len(word_list) == 0):
        result = ""
    elif (len(word_list) == 1):
        result = word_list[0][:3]
    elif (len(word_list) == 2):
        result = word_list[0][:2] + word_list[1][0]
    else:
        fullacro = ''.join(e[0] for e in word_list)
        result = fullacro[:3]
    return result

if __name__ == "__main__":
    print "Not Implemented"
