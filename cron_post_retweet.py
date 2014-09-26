#!/usr/bin/env python3
from twitter_bot import *

"""post_popular_retweet should start at 20:00 CDT (Chicago time) + random delay (2h)
   in the cron tab"""

home_timeline_tweets = get_home_timeline_tweets(twitter_api, home_timeline_collection)
for tweet in home_timeline_tweets:
    if is_new_tweet(home_timeline_collection, tweet):
        save_tweet(home_timeline_collection, tweet)

popular_tweet = max(home_timeline_tweets, key=lambda t: t["retweet_count"])
post_retweet(popular_tweet["id"], twitter_api)