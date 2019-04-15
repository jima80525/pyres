#!/usr/bin/env python3.7
""" Manage downloading episodes to filesystem.  """
import asks
import time
import tqdm
import trio

asks.init("trio")


class Downloader:
    """ Manage the download of a single URL to a specified file. """

    def __init__(self):
        self.failed_files = list()
        self.successful_files = list()

    async def download_site(self, episode, overall_bar, position):
        url, filename = episode
        name = url.replace("/", " ").split()[-1]
        try:
            async with await asks.get(url, stream=True) as req:
                file_size = int(req.headers["Content-Length"])
                progbar = tqdm.tqdm(total=file_size, position=position, desc=name)
                with open(filename, "wb") as podcast_file:
                    async for chunk in req.body:
                        progbar.update(len(chunk))
                        podcast_file.write(chunk)
                progbar.close()
                self.successful_files.append(name)
        except Exception:
            self.failed_files.append(name)
            progbar = tqdm.tqdm(total=1, position=position, desc=f"{name} - ERROR")
            progbar.update(1)
            progbar.close()
        finally:
            overall_bar.update(1)

    async def download_all_files(self, sites):
        progbar = tqdm.tqdm(total=len(sites), position=0, desc="total files")
        progbar.update(0)
        async with trio.open_nursery() as nursery:
            for index, episode in enumerate(sites, start=1):
                nursery.start_soon(self.download_site, episode, progbar, index)

        progbar.close()

    def download_episodes(self, sites):
        trio.run(self.download_all_files, sites)
        return self.successful_files, self.failed_files


if __name__ == "__main__":
    sites = [
        ("http://thehistoryofrome.com/lib/audio/1-in-the-beginning.mp3", "one.mp3"),
        (
            "http://thehistoryofrome.com/lib/audio/2-youthful-indiscretions.mp3",
            "two.mp3",
        ),
        (
            "http://jdflakdsjfistorye.com/lib/audio/2-youthful-indiscretions.mp3",
            "three.mp3",
        ),
        ("http://www.jython.org", "four.mp3"),
        ("http://olympus.realpython.org/dice", "five.mp3"),
    ]
    t1 = time.time()
    passed, failed = Downloader().download_episodes(sites)
    skip = "\n" * len(sites)
    duration = time.time() - t1
    print(f"{skip}code took to run {duration}")
    print("failed", failed)
    print("passed", passed)
