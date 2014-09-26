#!/usr/bin/env python3
from twitter_bot import *

"""cron_unfollow should start at 20:00 CDT (Chicago time) + random delay (2h)
   in the cron tab"""

unfollow_nonreciprocal_followers(followback_users_collection, twitter_api, 30)