#!/usr/bin/env python3
from twitter_bot import *
import random
import time
"""post_popular_retweet should start at 6:00 san fransisco time + random delay (2h)
   in the cron tab"""
random.seed()
time.sleep(random.randint(0,60*60*2))
one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
home_timeline_tweets = home_timeline_collection.find({"created_at" : {"$gt": one_day_ago}})
popular_tweet = max(home_timeline_tweets, key=lambda t: t["retweet_count"])

post_retweet(popular_tweet["id"])
