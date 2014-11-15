__author__ = 'Anders'
from twitter_bot import *
from datetime import date
import os
import random
import time

day = date(2014, 11, 27)#date.today()

with open(os.path.join(os.path.dirname(__file__), "interventions_dates_tweets.txt"), "r") as f:
    interventions = f.readlines()
dateDict = {}
for lines in interventions:
    line = lines.split(";")
    dato = line[0].split(",")
    if len(line[1]) > 140 or len(line[2]) > 140:
        if len(line[1]) > 140:
            print(line[1])
            print(len(line[1]))
        else:
            print(line[2])
            print(len(line[2]))
    dateDict[date(int(dato[0]), int(dato[1]), int(dato[2]))] = [line[1], line[2]]




print(dateDict[day][0])
print(dateDict[day][1])

random.seed()
time.sleep(random.randint(0, 60*60*5)) #Max kl. 23
#post_tweet(dateDict[day][0], twitter_api)
time.sleep(random.randint(0, 60*60*5)) #Max kl. 4
time.sleep(random.randint(0, 60*60*5)) #Max kl. 9
#post_tweet(dateDict[day][1], twitter_api)