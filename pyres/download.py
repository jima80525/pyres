#!/usr/bin/env python3.7
""" Manage downloading episodes to filesystem.  """
import time
import asks
import tqdm
import trio


class Downloader:
    """ Manage the download of a single URL to a specified file. """

    def __init__(self):
        self.failed_files = list()
        self.successful_files = list()

    async def _download_site(self, episode, progbar, overall_bar):
        url, filename = episode
        name = url.replace("/", " ").split()[-1]
        try:
            async with await asks.get(url, stream=True) as req:
                file_size = int(req.headers["Content-Length"])
                with open(filename, "wb") as podcast_file:
                    async for chunk in req.body:
                        progbar.update(100 * len(chunk) / file_size)
                        podcast_file.write(chunk)
                self.successful_files.append(url)
            progbar.update(1)
            progbar.set_description(f"{name} = COMPLETE")
        except Exception as ex:
            self.failed_files.append(name + str(ex))
            progbar.set_description(f"{name} - ERROR")
            progbar.update(100)
        finally:
            progbar.close()
            overall_bar.update(1)

    async def _download_all_files(self, sites):
        progbar = tqdm.tqdm(total=len(sites), position=0, desc="total files")
        progbar.update(0)
        async with trio.open_nursery() as nursery:
            for index, episode in enumerate(sites, start=1):
                name = episode[0].replace("/", " ").split()[-1]
                bar = tqdm.tqdm(total=100, position=index, desc=name)
                nursery.start_soon(self._download_site, episode, bar, progbar)
        progbar.close()

    def download_episodes(self, sites):
        trio.run(self._download_all_files, sites)
        return self.successful_files, self.failed_files


if __name__ == "__main__":
    sites = [
        # (
        # "http://thehistoryofrome.com/lib/audio/1-in-the-beginning.mp3",
        # "one.mp3",
        # ),
        (
            "https://traffic.libsyn.com/historyofrome/"
            "167-_Exploiting_the_Opportunity.mp3",
            "two.mp3",
        ),
        # (
        # 'https://traffic.libsyn.com/historyofrome/166-_As_Long_As_Shes_Nice_to_Look_At.mp3',
        # "three.mp3",
        # ),
        # ("http://olympus.realpython.org/dice", "five.mp3"),
        # ("http://olympus.realpython.org/dice", "aive.mp3"),
        # ("http://olympus.realpython.org/dice", "bive.mp3"),
        # ("http://olympus.realpythn.org/dice", "cive.mp3"),
    ]
    t1 = time.time()
    passed, failed = Downloader().download_episodes(sites)
    skip = "\n" * len(sites)
    duration = time.time() - t1
    print(f"{skip}code took to run {duration}")
    print("failed", failed)
    print("passed", passed)
