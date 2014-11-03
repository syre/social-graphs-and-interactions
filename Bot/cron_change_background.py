#!/usr/bin/env python3
from twitter_bot import *
import random
import time
"""cron_change_background should start every 3 days in the cron tab at 6:00 san fransisco time + 15 min. delay"""

random.seed()
time.sleep(random.randint(0,60*15))

img_urls = find_profile_background_images()

set_profile_background_image(random.choice(img_urls))
