import feedparser
import urllib2
import shutil
import urlparse
import os
import time
import db

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

def add_episodes_from_feed(cur, url):
    name, ps = process_feed(url)
    try:
        db.add_podcast(cur, name, url, "")
    except:
        pass # ok if it already exists

    for p in ps:
        db.add_new_episode_data(cur, name, dateToStr(p[0]), p[1], "", p[2])

conn, cur = db.open_podcasts('rss.db')
#for u in urls:
    #add_episodes_from_feed(cur, u)

pcs = db.get_podcast_names(cur)

for podcast in pcs:
    episodes = db.find_episodes_to_download(cur, podcast)
    toMark = True
    print "----------------------------------------"
    print podcast
    print "----------------------------------------"
    for e in episodes:
        if toMark:
            db.mark_episode_downloaded(cur, podcast, e[0])
            print e, "MARKED"
            toMark = False
        else:
            print e

    print


#db.show_podcasts(cur)

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
