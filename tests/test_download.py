import pytest  # noqa: F401
import pyres.download


@pytest.fixture
def episodes():
    """ Provide a list of episodes to download """
    return [
        (
            "http://thehistoryofrome.com/lib/audio/1-in-the-beginning.mp3",
            "one.mp3",
        ),
        (
            "http://thehistoryofrome.com/lib/audio/2-youthful-indiscretions.mp3",
            "two.mp3",
        ),
        # (
        # "http://jdflakdsjfistorye.com/lib/audio/2-youthful-indiscretions.mp3",
        # "three.mp3",
        # ),
        # ("http://www.jython.org", "four.mp3"),
        # ("http://olympus.realpython.org/dice", "five.mp3"),
    ]


class TestClass(object):
    def test_one(self, episodes):
        print("ONE")
        x = "this"
        assert "h" in x
        for e in episodes:
            print(e)
        passed, failed = pyres.download.Downloader().download_episodes(episodes)
        print(f"passed {passed}")
        print(f"failed {failed}")
        # assert False

    def test_two(self):
        print("TWO")
        x = "hello"
        assert "l" in x
        # assert hasattr(x, 'check')
