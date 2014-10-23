from twitter_bot import *
import random
import time
"""cron_follow should start at  8:30 CDT (Chicago time) + random delay (15m)
   in the cron tab"""
random.seed()
time.sleep(random.randint(0,60*15))

follow_human_users(25, 30)
