#!/usr/bin/env python3
from twitter_bot import *
import random
import time

"""cron_unfollow should start at 6:00 san fransisco time + random delay (2h)
   in the cron tab"""
random.seed()
time.sleep(random.randint(0,60*60*2))

unfollow_nonreciprocal_followers(followback_users_collection, twitter_api, 20)
unfollow_nonreciprocal_followers(human_users_collection, twitter_api, 20)
