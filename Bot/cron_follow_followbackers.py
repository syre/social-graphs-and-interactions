#!/usr/bin/env python3
from twitter_bot import *
import random
import time
"""cron_follow should start at  8:30 CDT (Chicago time) + random delay (15m)
   in the cron tab"""
random.seed()
time.sleep(random.randint(0,60*15))

timeline_tweets = get_user_timeline_tweets()
for tweet in timeline_tweets:
    if is_new_tweet(tweet_collection, tweet):
        save_tweet(tweet_collection, tweet)

follow_followback_users(25, 30)
