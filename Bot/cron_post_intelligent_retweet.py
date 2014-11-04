#!/usr/bin/env python3
from twitter_bot import *
import random
import time
"""post_popular_retweet should start at 1:00 san fransisco time + random delay (2h)
   in the cron tab"""
random.seed()
time.sleep(random.randint(0,60*60*2))

post_retweet(find_best_retweet()["id"])
