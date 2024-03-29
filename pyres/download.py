"""
Manage downloading episodes to filesystem.
"""
from __future__ import print_function
from six.moves.urllib_request import urlopen
from six.moves.urllib_error import URLError
from six.moves import queue
import time
import os
import requests
import threading


########################################################################
class Downloader(threading.Thread):
    """Threaded File Downloader"""

    # ----------------------------------------------------------------------
    def __init__(self, task_id, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = in_queue
        self.out_queue = out_queue
        self.task_id = task_id
        self.name = "task %d" % task_id

    # ----------------------------------------------------------------------
    def run(self):
        while True:
            episode = self.queue.get()
            self.download_file(episode)
            self.queue.task_done()

    # ----------------------------------------------------------------------
    def send_error(self, episode, name, message):
        """ Utility to put an error message in the out_queue """
        episode.error_msg = "%s:%s" % (name, message)
        self.send_status(0, episode)

    def send_status(self, downloaded_current, episode):
        """ Utility to put an error message in the out_queue """
        self.out_queue.put((self.task_id, downloaded_current, episode))

    # ----------------------------------------------------------------------
    def download_file(self, episode):
        """ Download and write the file to disc """
        # open the url
        try:
            r = requests.get(episode.url, stream=True)
        except URLError as err:
            self.send_error(episode, episode.url, err)
            return

        # check http status for success (2xx)
        http_status = r.status_code
        if (200 > http_status) or (299 < http_status):
            self.send_error(episode, episode.url,
                            "HTTP STATUS: %s" % http_status)
            return

        episode.size = int(r.headers["Content-Length"])
        total = 0
        try:
            with open(episode.file_name, "wb") as podcast_file:
                for block in r.iter_content(1024):
                    if not block:
                        break
                    total = total + len(block)
                    podcast_file.write(block)
                    self.send_status(total, episode)
        except requests.exceptions.RequestException as e:  # This will catch ONLY Requests exceptions
            print('REQUESTS ERROR:')
            print(e)  # This should tell you more details about the error
            self.send_error(episode, episode.file_name, e)
        except IOError as err:
            self.send_error(episode, episode.file_name, err)


########################################################################
class DisplayStatus(object):
    """console progress indicator for multiple threads"""

    # ----------------------------------------------------------------------
    def __init__(self, number_threads, number_files):
        self.num = number_threads
        self.total_files = number_files
        self.displays = list()
        self.displays = [["", 0, 0] for _ in range(self.num)]
        self.successful_file_count = 0
        self.progress_string = "  0:%3s " % self.total_files

    def increment_success(self):
        """ Update the count and header string of successful files. """
        self.successful_file_count += 1
        self.progress_string = r"%3s:%3s " % (self.successful_file_count,
                                              self.total_files)

    def finish(self, failed_files):
        """ Close out status """
        print()  # get us off status line
        if not failed_files:
            print("Successfully downloaded %s files" %
                  self.successful_file_count)
        else:
            print("Downloaded %s files of which %s failed" %
                  (self.total_files, len(failed_files)))
            print("Failed files:")
            for episode in failed_files:
                print("\t%s" % episode.file_name)

    def update(self, task_id, amt_read, episode):
        """ Update display status.  JHA More info here """
        # update the info from this task
        if episode:
            (_, file_name) = os.path.split(episode.file_name)
            self.displays[task_id][0] = file_name[0:8] + file_name[12:]
            self.displays[task_id][1] = amt_read
            self.displays[task_id][2] = episode.size

        # now display all of them
        display_str = self.progress_string
        for counter in range(0, self.num):
            if self.displays[counter][2]:
                pct = float(self.displays[counter][1] *
                            100/self.displays[counter][2])
            else:
                pct = 0.0
            tmp_str = r"%10s:%7d/%7d  [%2.0f%%]  " % \
                (self.displays[counter][0][0:11], self.displays[counter][1],
                 self.displays[counter][2], pct)
            display_str = display_str + tmp_str

        display_str = display_str + chr(8)*(len(display_str)+1)
        print(display_str, end='')


# ----------------------------------------------------------------------
class PodcastDownloader(object):
    """ download the podcasts to disk. """
    def __init__(self, episodes):
        self.episodes = episodes
        self.num_threads = min(3, len(episodes))
        self.queue = queue.Queue()
        self.out_queue = queue.Queue()
        self.status = DisplayStatus(self.num_threads, len(episodes))
        self.failed_files = []
        self.successful_files = []

    def download_url_list(self):
        """
        Downloads each of the episodes passed in using a thread pool to
        download in parallel.
        """
        # create a thread pool and give them a queue
        for thread_number in range(self.num_threads):
            the_thread = Downloader(thread_number, self.queue, self.out_queue)
            the_thread.setDaemon(True)
            the_thread.start()

        # give the queue some data
        for episode in self.episodes:
            self.queue.put(episode)

        while self.queue.unfinished_tasks or self.out_queue.unfinished_tasks:
            if self.out_queue.empty():
                time.sleep(1)
            else:
                (task_id, current_size, episode) = self.out_queue.get(True, 1)

                # if total length is 0, there was an error
                if episode.error_msg:
                    self.failed_files.append(episode)
                    # update our UI
                    self.status.update(task_id, current_size, None)
                else:
                    if current_size == episode.size:
                        # if length read is total length - save name
                        self.successful_files.append(episode)
                        self.status.increment_success()
                    # update our UI
                    self.status.update(task_id, current_size, episode)

                self.out_queue.task_done()

        # wait for the queue to finish
        self.queue.join()
        self.status.finish(self.failed_files)

    def return_failed_files(self):
        """ get the list of files that failed to download """
        return self.failed_files

    def return_successful_files(self):
        """ get the list of files that downloaded successfully """
        return self.successful_files
