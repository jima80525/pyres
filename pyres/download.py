"""
Manage downloading episodes to filesystem.
"""
import urllib2
import Queue
import time
import threading

########################################################################
class Downloader(threading.Thread):
    """Threaded File Downloader"""

    #----------------------------------------------------------------------
    def __init__(self, task_id, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.task_id = task_id
        name = "task %d" % task_id
        self.name = name

    #----------------------------------------------------------------------
    def run(self):
        while True:
            url = self.queue.get()
            self.download_file(url)
            self.queue.task_done()

    #----------------------------------------------------------------------
    def send_error(self, name, message):
        """ Utility to put an error message in the out_queue """
        self.out_queue.put((self.task_id, "%s:%s" % (name, message), 0, 0))

    #----------------------------------------------------------------------
    def download_file(self, podcast):
        """ Download and write the file to disc """
        (url, name, fname) = podcast
        # open the url
        try:
            handle = urllib2.urlopen(url)
        except urllib2.URLError as err:
            self.send_error(url, err)
            return

        # check http status for success (2xx)
        http_status = handle.getcode()
        if (200 > http_status) or (299 < http_status):
            self.send_error(url, "HTTP STATUS: %s" % http_status)
            return

        meta = handle.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        total = 0
        try:
            with open(fname, "wb") as podcast_file:
                while True:
                    chunk = handle.read(1024)
                    if not chunk:
                        break
                    total = total + len(chunk)
                    podcast_file.write(chunk)
                    self.out_queue.put((self.task_id, name, total, file_size))
        except IOError as err:
            self.send_error(fname, err)

########################################################################
class DisplayStatus():
    """console progress indicator for multiple threads"""

    #----------------------------------------------------------------------
    def __init__(self, number_threads, number_files):
        self.num = number_threads
        self.total_files = number_files
        self.displays = list()
        self.displays = [["", 0, 0] for _i in range(self.num)]

    def finish(self, failed_files, num_good):
        """ Close out status """
        print # get us off status line
        if not failed_files:
            print("Successfully downloaded %s files" % num_good)
        else:
            print("Downloaded %s files of which %s failed" % (self.total_files,
                                                             len(failed_files)))
            print("Failed files:")
            for filename in failed_files:
                print("\t%s" % filename)

    def update(self, successful_files, args):
        """ Update display status.  JHA More info here """
        (task_id, file_name, amt_read, total_size) = args
        # update the info from this task
        self.displays[task_id][0] = file_name
        self.displays[task_id][1] = amt_read
        self.displays[task_id][2] = total_size

        # now display all of them
        display_str = ""
        for counter in range(0, self.num):
            if self.displays[counter][2]:
                pct = float(self.displays[counter][1]* \
                            100/self.displays[counter][2])
            else:
                pct = 0.0
            tmp_str = r"%3s:%3s  %10s:%7d/%7d  [%03.1f%%]  " % \
                (successful_files, self.total_files,
                 self.displays[counter][0][0:8], self.displays[counter][1],
                 self.displays[counter][2], pct)
            display_str = display_str + tmp_str

        display_str = display_str + chr(8)*(len(display_str)+1)
        print display_str,

# ----------------------------------------------------------------------
def download_url_list(urls):
    """
    Run the program
    """
    num_threads = min(3, len(urls))
    queue = Queue.Queue()
    out_queue = Queue.Queue()
    status = DisplayStatus(num_threads, len(urls))
    successful_files = 0
    failed_files = list()

    # create a thread pool and give them a queue
    for thread_number in range(num_threads):
        the_thread = Downloader(thread_number, queue, out_queue)
        the_thread.setDaemon(True)
        the_thread.start()

    # give the queue some data
    for url in urls:
        queue.put(url)

    while queue.unfinished_tasks or out_queue.unfinished_tasks:
        if out_queue.empty():
            time.sleep(1)
        else:
            update = out_queue.get(True, 1)

            # if total length is 0, there was an error
            if update[3] == 0:
                failed_files.append(update[1])
            elif update[2] == update[3]:
                # if length read is total length - increment successful reads
                successful_files += 1

            # update our UI
            status.update(successful_files, update)
            out_queue.task_done()

    # wait for the queue to finish
    queue.join()
    status.finish(failed_files, successful_files)

# disable line too long warning
# pylint: disable-msg=C0301
URLS = [
    ("http://www.irs.gov/pub/irs-pdf/f1040.pdf", "1040.pdf", "Files\\one.pdf"),
    ("http://www.irs.gov/pub/irs-pdf/f1040a.pdf", "1040a.pdf", "Files\\two.pdf"),
    #("http://www.irs.gov/pub/irs-pdf/f1040ez.pdf", "1040ez.pdf"),
    #("http://www.irs.gov/pub/irs-pdf/f1040es.pdf", "1040es.pdf"),
    #("http://www.irs.gov/pub/irs-pdf/f1040sb.pdf", "1040sb.pdf"),
]

EPISODES = [
    ('http://www.thetvcritic.org/historypodcasts/media/2012-10-30_the_state_part1.mp3', 'Episode 11 \x96 The Eastern Provinces'),
    ('http://www.thetvcritic.org/historypodcasts/media/2012-10-02_2012-10-02_10_constantinople.mp3', 'Episode 10 \x96 Constantinople'),
    ('http://www.thetvcritic.org/historypodcasts/media/2012-09-14_9_the_balkan_provinces.mp3', 'Episode 9 \x96 The Balkan Provinces'),
    ('http://www.thetvcritic.org/historypodcasts/media/2013-04-12_24_the_western_emperor.mp3', 'Episode 24 \x96 The Western Emperor'),
]
MIXED = [
    ('http://www.pheedo.com/e/d393bb0dd4a4a37fc497cbeda8fe411c/sa_p_podcast_121125.mp3', 'When Old Habits Die Easy.mp3'),
    ('http://www.pheedo.com/e/77ad9636b0df9b954ad0db23c702e0ff/sa_p_podcast_121114.mp3', "Rats' Whiskers Inspire New Way to See.mp3"),
    ('http://www.thetvcritic.org/historypodcasts/media/2013-04-12_24_the_western_emperor.mp3', 'Episode 24 \x96 The Western Emperor'),
]

SHORT_EPISODES = [
    ('http://www.scientificamerican.com/podcast/podcast.mp3?fileId=F539C695-DAC8-423B-B8AF91A1595132EF', "good1.mp3", 'FILES\\JIMA1.mp3'),
    ('http://www.ntificamerican.com/podcast/podcast.mp3?fileId=F539C695-DAC8-423B-B8AF91A1595132EF', "bad.mp3", 'FILES\\JIMA.mp3'),
    ('http://www.scientificamerican.com/podcast/podcast.mp3?fileId=F539C695-DAC8-423B-B8AF91A1595132EF', "good2.mp3", 'FILES\\JIMA2.mp3'),
    ('http://www.scientificamerican.com/podcast/podcast.mp3?fileId=F539C695-DAC8-423B-B8AF91A1595132EF', "good3.mp3", 'FILES\\JIMA4.mp3'),
    #('http://www.pheedo.com/e/d393bb0dd4a4a37fc497cbeda8fe411c/sa_p_podcast_121125.mp3', 'When Old Habits Die Easy.mp3', 'FILES\\one.mp3'),
    #('http://www.pheedo.com/e/77ad9636b0df9b954ad0db23c702e0ff/sa_p_podcast_121114.mp3', "Rats' Whiskers Inspire New Way to See.mp3", 'FILES\\two.mp3'),
    #('http://www.pheedo.com/e/c137f56d4dc78cc759c685455e0feb24/sa_p_podcast_121106.mp3', 'Stable or Sexy It Depends on Ovulation.mp3', 'FILES\\three.mp3'),
    #('http://www.pheedo.com/e/ee3e0a37e46dcf03e39303581f8cb8b2/sa_p_podcast_130211.mp3', 'You May Think Your Name Is Rare.mp3', 'FILES\\four.mp3'),
    #('http://www.pheedo.com/e/bdd7d5f86d83eb56529f73de9285e0f8/sa_p_podcast_130203.mp3', 'We Are What We Smell.mp3', 'FILES\\five.mp3'),
    #('http://www.pheedo.com/e/4c13efb43913c44179af7711c8f95171/sa_p_podcast_130130.mp3', 'Coffee Boosts Recognition of Positive Words.mp3', 'FILES\\six.mp3'),
    #('http://www.pheedo.com/e/8aef19eb4f8eb5b80aa34c1986997690/sa_p_podcast_130123.mp3', 'Diapers Hinder Walking for Babies.mp3', 'FILES\\seven.mp3'),
]
# pylint: enable-msg=C0301

if __name__ == "__main__":
    #download_url_list(URLS)
    download_url_list(SHORT_EPISODES)
    #download_url_list(MIXED)

