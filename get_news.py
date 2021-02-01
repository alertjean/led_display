#!/usr/bin/env python

import feedparser
from rss import links

#for country in links.keys():
for country in ['IN']:
    for category in links[country].keys():
    #for category in ('politics'):
        for link in links[country][category].keys():
            feed = feedparser.parse(link)
            items = feed["items"]
            try:
                for item in items:
                    if item.has_key("title"):
                        print("[{0}]".format(item["title"]))
                    else:
                        print "No title {}".format(link)
            except ValueError:
                print "Failure {}".format(link)


