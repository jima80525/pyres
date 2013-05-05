import feedparser
import urllib2
import shutil
import urlparse
import os
import time
import db
#from future import Future

def download(url, fileName=None):
    def getFileName(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename
            # from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()

def process_feed(url):
    feed = feedparser.parse( url )
    podcast_name = feed['channel']['title']

    podcasts = list()
    for t in feed["items"]:
        v = t['published']
        #for d, v in t.items():
            #if d == 'published':
        # remove last word from published date - it's a timezone
        # and we don't really care about the timezone as most feeds are
        # likely to be with the same timezone and we're only using dates
        # for ordering.
        v = v.rsplit(' ', 1)[0]
        date = time.strptime(v, "%a, %d %b %Y %X")
        try:
            title = t['title'].encode('cp1252', 'replace')
            published = t['published']
        except:
            print "failed title"
        for k in t["links"]:
            if 'audio' in k['type']:
                link = k['href'] or link
        podcasts.append((date, title, link))
    return (podcast_name, podcasts)


urls = (
    "http://rss.sciam.com/sciam/60-second-psych",
    "http://thehistoryofbyzantium.wordpress.com/feed/",
)

def dateToStr(d):
    return time.strftime("%x:%X", d)

def strToDate(s):
    return time.strptime(s, "%x:%X")

conn, cur = db.open_podcasts('rss.db')
for u in urls:
    name, ps = process_feed(u)
    print "\n", name
    try:
        db.add_podcast(cur, name, u, "")
    except:
        pass # ok if it already exists

    for p in ps:
        db.add_new_episode_data(cur, name, dateToStr(p[0]), p[1], "", p[2])

db.show_podcasts(cur)

db.close_podcasts(conn)
exit()

feed = feedparser.parse( python_wiki_rss_url )

for t in feed["items"]:
    print "\nNEW ITEM\n"
#   print t["title"]
    print t["published_parsed"]
#print t["link"]
#print
#   print t["pheedo_origenclosurelink"]
#print
#print t["links"]
#print
    for k in t["links"]:
        if 'audio' in k['type']:
            print "this is the link:" + k['href']
#exit()
#download(t["pheedo_origenclosurelink"], t["title"] + ".mp3")
#print t
#print t["title"]

