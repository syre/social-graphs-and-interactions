__author__ = 'Anders'
from twitter_bot import *
from datetime import date
import os
import random
import time
from PIL import Image

day = date(2014, 11, 17)#date.today()


def add_image(tweetText):
    strings = tweetText[:tweetText.find("/picture")]
    image = tweetText[tweetText.find("/picture")+8:tweetText.find("picture/")]
    image = "../Interventions/"+image.replace(" ", "")
    return strings, image

def load_interventions():
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
    return dateDict


def post(tweet0, tweet1, image0, image1):
    random.seed()
    time.sleep(random.randint(0, 60*60*5)) #Max kl. 23

    if image0 != "":
        post_local_picture_tweet(tweet0, twitter_api, image0)
    else:
        post_tweet(tweet1, twitter_api)

    time.sleep(random.randint(0, 60*60*5)) #Max kl. 4
    time.sleep(random.randint(0, 60*60*5)) #Max kl. 9
    if image1 != "":
        post_local_picture_tweet(tweet1, twitter_api, image1)
    else:
        post_tweet(tweet2, twitter_api)


dateDict = load_interventions()
image0, image1 = "", ""
if "/picture" in dateDict[day][0]:
    dateDict[day][0], image0 = add_image(dateDict[day][0])
if "/picture" in dateDict[day][1]:
    dateDict[day][1], image1 = add_image(dateDict[day][1])

post(dateDict[day][0], dateDict[day][1], image0, image1)