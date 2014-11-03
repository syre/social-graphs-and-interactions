#!/usr/bin/env python3
from twitter_bot import *
import random
import time
"""post_popular_retweet should start for each 8 hour + random delay (2h)
   in the cron tab"""
random.seed()
time.sleep(random.randint(0,60*60*2))

home_timeline_tweets = get_home_timeline_tweets()
for tweet in home_timeline_tweets:
    if is_new_tweet(home_timeline_collection, tweet):
        save_tweet(home_timeline_collection, tweet)
