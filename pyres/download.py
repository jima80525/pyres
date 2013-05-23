import urllib2
import shutil
import urlparse
import os
import Queue
import time
import threading
import timeit

########################################################################
class Downloader(threading.Thread):
    """Threaded File Downloader"""

    #----------------------------------------------------------------------
    def __init__(self, taskId, queue, outQueue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.outQueue = outQueue
        self.taskId = taskId
        name = "task %d" % taskId
        self.name = name
        #print "Initialized %s"%name

    #----------------------------------------------------------------------
    def run(self):
        while True:
            url = self.queue.get()
            self.download_file(url)
            self.queue.task_done()

    #----------------------------------------------------------------------
    def download_file(self, url):
        """"""
        handle = urllib2.urlopen(url)
        basename = os.path.basename(url)
        fname = "Files\\"+basename
        meta = handle.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        #print "%s: downloading to %s at size %d"%(self.name, fname, file_size)
        total = 0
        with open(fname, "wb") as f:
            while True:
                chunk = handle.read(1024)
                total = total + 1024
                if not chunk: break
                f.write(chunk)
                #print("%s: posting %d %d" % (basename,total,file_size))
                self.outQueue.put((self.taskId, basename,total,file_size))

########################################################################
class DisplayStatus():
    """console progress indicator for multiple threads"""

    #----------------------------------------------------------------------
    def __init__(self, number_threads):
        self.num = number_threads
        self.displays = list()
        for ii in range(0, self.num):
            self.displays.append(["", 0, 0])

    def update(self, taskId, file_name, amt_read, total_size):
        # update the info from this task
        self.displays[taskId][0] = file_name
        self.displays[taskId][1] = amt_read
        self.displays[taskId][2] = total_size

        # now display all of them
        display_str = ""
        for ii in range(0, self.num):
            if self.displays[ii][2]:
                pct = float(self.displays[ii][1]*100/self.displays[ii][2])
            else:
                pct = 0.0
            tmp_str = r"%8s:%7d/%7d  [%3.1f%%]  " % (self.displays[ii][0][0:8],
                                                     self.displays[ii][1],
                                                     self.displays[ii][2],
                                                     pct)
            display_str = display_str + tmp_str

        display_str = display_str + chr(8)*(len(display_str)+1)
        print display_str,

# ----------------------------------------------------------------------
def main(urls):
    """
    Run the program
    """
    num_threads = 3
    queue = Queue.Queue()
    outQueue = Queue.Queue()
    status = DisplayStatus(num_threads)

    # create a thread pool and give them a queue
    for i in range(num_threads):
        t = Downloader(i, queue, outQueue)
        t.setDaemon(True)
        t.start()

    # give the queue some data
    for url in urls:
        queue.put(url)

    #while not queue.unfinished_tasks:
    #while not queue.empty() or not outQueue.empty():
    while queue.unfinished_tasks or outQueue.unfinished_tasks:
        if outQueue.empty():
            time.sleep(1)
        else:
            (taskId, file_name, amt_read, total_size) = outQueue.get(True, 1)
            status.update(taskId, file_name, amt_read, total_size)
            outQueue.task_done()

    # wait for the queue to finish
    queue.join()

urls = ["http://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040es.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"]
episodes = [
    ('http://www.thetvcritic.org/historypodcasts/media/2012-10-30_the_state_part1.mp3', 'Episode 11 \x96 The Eastern Provinces'),
    ('http://www.thetvcritic.org/historypodcasts/media/2012-10-02_2012-10-02_10_constantinople.mp3', 'Episode 10 \x96 Constantinople'),
    ('http://www.thetvcritic.org/historypodcasts/media/2012-09-14_9_the_balkan_provinces.mp3', 'Episode 9 \x96 The Balkan Provinces'),
    ('http://www.thetvcritic.org/historypodcasts/media/2013-04-12_24_the_western_emperor.mp3', 'Episode 24 \x96 The Western Emperor'),
]
mixed = [
    'http://www.pheedo.com/e/d393bb0dd4a4a37fc497cbeda8fe411c/sa_p_podcast_121125.mp3',
    'http://www.pheedo.com/e/77ad9636b0df9b954ad0db23c702e0ff/sa_p_podcast_121114.mp3',
    'http://www.thetvcritic.org/historypodcasts/media/2013-04-12_24_the_western_emperor.mp3',
]
shortepisodes = [
    'http://www.pheedo.com/e/d393bb0dd4a4a37fc497cbeda8fe411c/sa_p_podcast_121125.mp3',
    'http://www.pheedo.com/e/77ad9636b0df9b954ad0db23c702e0ff/sa_p_podcast_121114.mp3',
    'http://www.pheedo.com/e/c137f56d4dc78cc759c685455e0feb24/sa_p_podcast_121106.mp3',
    'http://www.pheedo.com/e/ee3e0a37e46dcf03e39303581f8cb8b2/sa_p_podcast_130211.mp3',
    'http://www.pheedo.com/e/bdd7d5f86d83eb56529f73de9285e0f8/sa_p_podcast_130203.mp3',
    'http://www.pheedo.com/e/4c13efb43913c44179af7711c8f95171/sa_p_podcast_130130.mp3',
    'http://www.pheedo.com/e/8aef19eb4f8eb5b80aa34c1986997690/sa_p_podcast_130123.mp3',
    #'http://www.pheedo.com/e/6385c74ddefbc7d2050edcfd35d69871/sa_p_podcast_130115.mp3',
    #'http://www.pheedo.com/e/73f26c17fa37f8e298421507233d56da/sa_p_podcast_130108.mp3',
    #'http://www.pheedo.com/e/1a83014204393291d4d3818a32aa5b19/sa_p_podcast_121229.mp3',
    #'http://www.pheedo.com/e/51066cbba46addcd7c0735227d8bf09b/sa_p_podcast_121222.mp3',
    #'http://www.pheedo.com/e/f67562745d75ef01feb7bb824280327c/sa_p_podcast_121208.mp3',
    #'http://www.pheedo.com/e/d3bd455410b4da425f54555748cdf8ef/sa_p_podcast_121202.mp3',
]

if __name__ == "__main__":
    #main(urls)
    #main(shortepisodes)
    main(mixed)
exit()
def downloadProgress(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192 * 2
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

def download(url, fileName):
    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()

def worker(episodes, lock, threadIdx):
    url = None
    fname = None
    while len(episodes):
        with lock:
            # sanity check
            if not len(episodes): return
            url, fname = episodes.pop()
        print threadIdx, url
        downloadProgress(url, fname)

def withNew(episodes, size):
    episode_lock = threading.Lock()
    threads = []
    while size:
        t = threading.Thread(target=worker, args=(episodes, episode_lock, size))
        t.start()
        threads.append(t)
        size -= 1
    for tt in threads:
        tt.join()

# OLD threadiong stuff below here
def startThread(url, fileName):
    t = threading.Thread(target=download, args=(url,fileName))
    #threads.append(t)
    t.start()
    return t

def FULLwithT(episodes):
    threads = []
    for e in episodes:
        url, fname = e
        threads.append(startThread(url, fname))
    for tt in threads:
        tt.join()

def withT(episodes, size=2):
    while episodes:
        subset = episodes[0:size]
        episodes = episodes[size:]
        FULLwithT(subset)

def withoutT(episodes):
    for i, e in enumerate(episodes):
        print("before %d" % i)
        url, fname = e
        download(url, fname)


episodes = [
    ('http://www.thetvcritic.org/historypodcasts/media/2012-10-30_the_state_part1.mp3', 'Episode 11 \x96 The Eastern Provinces'),
    ('http://www.thetvcritic.org/historypodcasts/media/2012-10-02_2012-10-02_10_constantinople.mp3', 'Episode 10 \x96 Constantinople'),
    ('http://www.thetvcritic.org/historypodcasts/media/2012-09-14_9_the_balkan_provinces.mp3', 'Episode 9 \x96 The Balkan Provinces'),
    ('http://www.thetvcritic.org/historypodcasts/media/2013-04-12_24_the_western_emperor.mp3', 'Episode 24 \x96 The Western Emperor'),
]
mixed = [
    ('http://www.pheedo.com/e/d393bb0dd4a4a37fc497cbeda8fe411c/sa_p_podcast_121125.mp3', 'Files\When Old Habits Die Easy.mp3'),
    ('http://www.pheedo.com/e/77ad9636b0df9b954ad0db23c702e0ff/sa_p_podcast_121114.mp3', "Files\Rats' Whiskers Inspire New Way to See.mp3"),
    ('http://www.thetvcritic.org/historypodcasts/media/2013-04-12_24_the_western_emperor.mp3', 'Episode 24 \x96 The Western Emperor'),
]
shortepisodes = [
    ('http://www.pheedo.com/e/d393bb0dd4a4a37fc497cbeda8fe411c/sa_p_podcast_121125.mp3', 'Files\When Old Habits Die Easy.mp3'),
    ('http://www.pheedo.com/e/77ad9636b0df9b954ad0db23c702e0ff/sa_p_podcast_121114.mp3', "Files\Rats' Whiskers Inspire New Way to See.mp3"),
    ('http://www.pheedo.com/e/c137f56d4dc78cc759c685455e0feb24/sa_p_podcast_121106.mp3', 'Files\Stable or Sexy It Depends on Ovulation.mp3'),
    ('http://www.pheedo.com/e/ee3e0a37e46dcf03e39303581f8cb8b2/sa_p_podcast_130211.mp3', 'Files\You May Think Your Name Is Rare.mp3'),
    ('http://www.pheedo.com/e/bdd7d5f86d83eb56529f73de9285e0f8/sa_p_podcast_130203.mp3', 'Files\We Are What We Smell.mp3'),
    ('http://www.pheedo.com/e/4c13efb43913c44179af7711c8f95171/sa_p_podcast_130130.mp3', 'Files\Coffee Boosts Recognition of Positive Words.mp3'),
    ('http://www.pheedo.com/e/8aef19eb4f8eb5b80aa34c1986997690/sa_p_podcast_130123.mp3', 'Files\Diapers Hinder Walking for Babies.mp3'),
    #('http://www.pheedo.com/e/6385c74ddefbc7d2050edcfd35d69871/sa_p_podcast_130115.mp3', 'Files\Images of Thin Bodies Impact Body Preferences.mp3'),
    #('http://www.pheedo.com/e/73f26c17fa37f8e298421507233d56da/sa_p_podcast_130108.mp3', 'Files\Dexter Talks Psychopath Stress Management.mp3'),
    #('http://www.pheedo.com/e/1a83014204393291d4d3818a32aa5b19/sa_p_podcast_121229.mp3', 'Files\Dan Ariely Talks Creativity and Dishonesty.mp3'),
    #('http://www.pheedo.com/e/51066cbba46addcd7c0735227d8bf09b/sa_p_podcast_121222.mp3', 'Files\Natural Setting and Tech Break Boost Creativity.mp3'),
    #('http://www.pheedo.com/e/f67562745d75ef01feb7bb824280327c/sa_p_podcast_121208.mp3', 'Files\Civilian Trauma May Contribute to Combat PTSD.mp3'),
    #('http://www.pheedo.com/e/d3bd455410b4da425f54555748cdf8ef/sa_p_podcast_121202.mp3', 'Files\Bad Boys and Gals Present as More Attractive.mp3'),
]
start_time = timeit.default_timer()
download('http://www.thetvcritic.org/historypodcasts/media/2012-10-30_the_state_part1.mp3', 'Episode 11 \x96 The Eastern Provinces')
#download('http://www.pheedo.com/e/8aef19eb4f8eb5b80aa34c1986997690/sa_p_podcast_130123.mp3', 'Files\Diapers Hinder Walking for Babies.mp3')
end_time = timeit.default_timer() - start_time
print("normal time %d"%end_time)
start_time = timeit.default_timer()
downloadProgress('http://www.thetvcritic.org/historypodcasts/media/2012-10-30_the_state_part1.mp3', 'Episode 11 \x96 The Eastern Provinces')
#downloadProgress('http://www.pheedo.com/e/8aef19eb4f8eb5b80aa34c1986997690/sa_p_podcast_130123.mp3', 'Files\Diapers Hinder Walking for Babies.mp3')
end_time = timeit.default_timer() - start_time
print
print("progressBar time %d"%end_time)
exit()

def threadit(number):
    start_time = timeit.default_timer()
    print("Starting with %d"%number)
    withT(episodes, number)
    print("finished with %d"%number)
    wi = timeit.default_timer() - start_time
    return wi

start_time = timeit.default_timer()
print "Starting without"
withoutT(episodes)
wo = timeit.default_timer() - start_time


times = dict()
for x in range(2,9):
    times[x] = threadit(x)
    print("Ran size %d in %s"%(x,times[x]))
print
print "TOTALS"
for s in times:
    print("Ran size %d in %s"%(s,times[s]))
    #print s, times[s]
print("wout", wo)
exit()

start_time = timeit.default_timer()
print "Starting without"
withoutT(episodes)
wo = timeit.default_timer() - start_time

print("With", wi)
print("wout", wo)
exit()
threadit = False
print("starting download")

#for i in range(5):
    #t = threading.Thread(target=worker, args=(i,))
    #threads.append(t)
    #t.start()
#exit()
#('09/14/12:19:14:04', 'Episode 9 \x96 The Balkan Provinces', '', 'http://www.thetvcritic.org/historypodcasts/media/2012-09-14_9_the_balkan_provinces.mp3', 0)
#download('http://www.thetvcritic.org/historypodcasts/media/2012-09-14_9_the_balkan_provinces.mp3',
    #'Episode 9 \x96 The Balkan Provinces')
print("finished")
