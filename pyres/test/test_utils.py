""" Test the utils package """
import pytest
import errno
import pyres.utils
from mock import patch
from mock import Mock


class TestMkdir(object):
    """ Test the mkdir_p function"""

    @patch('pyres.utils.os.makedirs')
    def test_dir_creation(self, mkdir):
        """  make sure the os funtion is called with the directory name """
        assert self
        pyres.utils.mkdir_p("fred")
        mkdir.assert_called_once_with("fred")

    @patch('pyres.utils.os.makedirs')
    @patch('pyres.utils.os.path.isdir')
    def test_dir_exists(self, isdir, mkdir):
        """  make sure no exception is raised on "directory exists" """
        assert self
        # mock mkdir to raise OSError exception with errno set accordingly
        my_error = OSError()
        my_error.errno = errno.EEXIST
        mkdir.side_effect = my_error
        isdir.return_value = True

        pyres.utils.mkdir_p("fred")
        mkdir.assert_called_once_with("fred")

    @patch('pyres.utils.os.makedirs')
    @patch('pyres.utils.os.path.isdir')
    def test_file_exists(self, isdir, mkdir):
        """  make sure exception is raised on if path specified is a file """
        assert self
        # mock mkdir to raise OSError exception with errno set accordingly
        my_error = OSError()
        my_error.errno = errno.EEXIST
        mkdir.side_effect = my_error
        isdir.return_value = False

        pytest.raises(OSError, pyres.utils.mkdir_p, 'fred')

    @patch('pyres.utils.os.makedirs')
    @patch('pyres.utils.os.path.isdir')
    def test_bad_errno(self, isdir, mkdir):
        """  make sure exception is raised on if errno is not EEXIST """
        assert self
        # mock mkdir to raise OSError exception with errno set accordingly
        my_error = OSError()
        my_error.errno = errno.ENOENT
        mkdir.side_effect = my_error
        isdir.return_value = True

        pytest.raises(OSError, pyres.utils.mkdir_p, 'fred')


class TestCleanName(object):
    """ Test the clean_name function.  This function removes the following
    characters from the input string:
       / : * % ? " < > | '
    """

    def test_empty_string(self):
        """ Tests that empty string doesn't crash """
        assert self
        test_string = ""
        pyres.utils.clean_name(test_string)
        assert test_string == ""

    def test_none_rasies(self):
        """ Passing in None should raise an exception """
        assert self
        pytest.raises(AttributeError, pyres.utils.clean_name, None)

    def test_starting_chars(self):
        """ test invalid chars at start of string """
        assert self
        base_string = "this is a string"

        result = pyres.utils.clean_name("///" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name(":::" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name("***" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name("%%%" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name("???" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name('"""' + base_string)
        assert result == base_string
        result = pyres.utils.clean_name("<<<" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name(">>>" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name("|||" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name("'''" + base_string)
        assert result == base_string
        result = pyres.utils.clean_name(r"\/:*%?\"<>|'" + r"\/:*%?\"<>|'" +
                                        r"\/:*%?\"<>|'" + base_string)
        assert result == base_string

    def test_ending_chars(self):
        """ test invalid chars at end of string """
        assert self
        base_string = "this is a string"

        result = pyres.utils.clean_name(base_string + "///")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + ":::")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + "***")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + "%%%")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + "???")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + '"""')
        assert result == base_string
        result = pyres.utils.clean_name(base_string + "<<<")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + ">>>")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + "|||")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + "'''")
        assert result == base_string
        result = pyres.utils.clean_name(base_string + r"\/:*%?\"<>|'" +
                                        r"\/:*%?\"<>|'" + r"\/:*%?\"<>|'")
        assert result == base_string

    def test_mixed_chars(self):
        """ test invalid chars at end of string """
        assert self
        result = pyres.utils.clean_name(r"t|h'i*s is a \"s?tri>ng<")
        assert result == "this is a string"


class TestAudioConversion(object):
    """ Test function which does the fixup.  This is fairly lame as we're
    mocking out the two calls it makes.  """
    def test_none_raises(self):
        """ makes sure that passing in none fails """
        assert self
        pytest.raises(AttributeError, pyres.utils.fixup_mp3_file, None)

    @patch('pyres.utils.AudioSegment')
    def test_audio_convert(self, audio_mock):
        """ pass"""
        assert self
        song_mock = Mock()
        audio_mock.from_mp3.return_value = song_mock

        pyres.utils.fixup_mp3_file("fred")
        audio_mock.from_mp3.assert_called_once_with('fred')
        song_mock.export.assert_called_once_with('fred', format='mp3')


class TestAcroname(object):
    """ Test function which produces a three-letter acronym from the podcast
    name.  There are several special cases for this function which are tested
    below. """
    def test_none_raises(self):
        """ makes sure that passing in none fails """
        assert self
        pytest.raises(TypeError, pyres.utils.acroname, None)

    def test_one_word_name(self):
        """ A one-word name should just take the first three letters of the
        word if there are that many. """
        assert self
        result = pyres.utils.acroname("ABCDE")
        assert result == "ABC"
        result = pyres.utils.acroname("ABCD")
        assert result == "ABC"
        result = pyres.utils.acroname("ABC")
        assert result == "ABC"
        result = pyres.utils.acroname("AB")
        assert result == "AB"
        result = pyres.utils.acroname("A")
        assert result == "A"
        result = pyres.utils.acroname("")
        assert result == ""

    def test_two_work_name(self):
        """ A two-word name should take the first two letters of the first word
        (if there are that many) and only one letter from the second. """
        assert self
        result = pyres.utils.acroname("ABCDE ZYX")
        assert result == "ABZ"
        result = pyres.utils.acroname("ABCD ZYX")
        assert result == "ABZ"
        result = pyres.utils.acroname("ABC ZYX")
        assert result == "ABZ"
        result = pyres.utils.acroname("AB ZYX")
        assert result == "ABZ"
        result = pyres.utils.acroname("A ZYX")
        assert result == "AZ"

    def test_three_work_name(self):
        """ A three-word name should take the first letter of each word. """
        assert self
        result = pyres.utils.acroname("always buy corn downtown")
        assert result == "abc"
        result = pyres.utils.acroname("always buy corn")
        assert result == "abc"

    def test_special_cases(self):
        """ There are two specials.  One for NPR podcasts - we strip that word
        off.  The second is for Scientific American podcasts.  We trim those,
        too. """
        assert self
        result = pyres.utils.acroname("NPR always buy corn downtown")
        assert result == "abc"
        result = pyres.utils.acroname("Scientific American Podcast always "
                                      "buy corn downtown")
        assert result == "abc"
