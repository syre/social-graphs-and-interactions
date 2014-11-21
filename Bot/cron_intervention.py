#!/usr/bin/env python3
from twitter_bot import *
import datetime
interventions = {"14/11/14": "#getyourflushot",
                 "17/11/14": "#highfiveastranger",
                 "19/11/14": "#somethinggood",
                 "21/11/14": "#HowManyPushups",
                 "24/11/14": "#GoldenGateAliens",
                 "26/11/14": "#turkeyface",
                 "27/11/14": "#SFThanks",
                 "28/11/14": "#blackfridaystories",
                 "01/12/14": "MISSING!"}

for date, hashtag in interventions.items():
    date = datetime.datetime.strptime(date, "%d/%m/%y").date()
    today = date.today()
    if date == today:
        print("Today is: {} , retweeting {}".format(date, hashtag))
        intervention_retweet(hashtag)
        intervention_favorite(hashtag)
