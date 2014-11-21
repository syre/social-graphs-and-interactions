#!/usr/bin/env python3
from twitter_bot import *
import random
import time
"""cron_follow should start at  11:00 san fransisco time + random delay (15m)
   in the cron tab"""
random.seed()
for i in range(4):
    time.sleep(random.randint(0,60*15))

    follow_human_users(60, 20) # takes maximally 20min

    time.sleep(random.randint(0,60*15))

    follow_humans_from_list(60, 20) # takes maximally 20min

    time.sleep(random.randint(0,60*15))

    follow_reciprocal_humans_from_list(60, 20) # takes maximally 20min

    time.sleep(60*60*2.5)
