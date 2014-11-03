#!/usr/bin/env python3
import random
from twitter_bot import *
import time
"""cron_follow should start at  8:30 CDT (Chicago time) + random delay (15m)
   in the cron tab"""
   
random.seed()
choice = random.randint(0,2)
func_list = [personal, recommendation, steal]
func = random.choice(func_list)
func()
#if choice == 0:
#    print "Personal!"
#    personal()
#elif choice == 1:
#    print "recommendation :)"
#    recommendation()
#else:
#    print "steal! (Muhahaha!)"
	
def personal():
    random.seed()
    choice = random.randint(0,1)
    if choice == 0:
        f = open("personal.txt", 'r')
        strings = f.readlines()
        f.close()
        choice = random.randint(0,len(strings)-1)
		
        personalTweet = strings[choice]
		if (personal_tweets_collection.find({"text":personalTweet})
			personalTweet_db = personal_tweets_collection.find({"text":personalTweet})
			five_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=5)
			if personalTweet_db["tweeted_at"] > five_days_ago:
				post_tweet(personalTweet, twitter_api)
				personal_tweets_collection.update({'text':personalTweet},{$set:{'tweeted_at':datetime.datetime.now().isoformat()}})
			print personalTweet
		else:
			save_own_current_tweets(recommendation_tweets_collection, tweet_text)
    else: 
        event = find_new_event()
    
def recommendation():
    f = open("recommendation.txt", 'r')
    strings = f.readlines()
    f.close()
	if (recommendation_tweets_collection.find({"tweeted_at"})):
		two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
		tweets = recommendation_tweets_collection.find({"tweeted_at"})
		for tweet in tweets: #cleaning. There should only be 1! but you never know	
			time = tweet["tweeted_at"]
			text = tweet["text"]
			if time > two_days_ago:
				recommendation_tweets_collection.remove({"text":text, "tweeted_at":time})
		else:
			if text in strings:
				index = strings.index(text)
				resp = strings[index].split(";")
				if resp[1] != "!NOT!":
					response = "I'm going to" + resp[1]+resp[0]					
				recommendation_tweets_collection.remove({"text":text, "tweeted_at":time})
	else:
		random.seed()
		choice = random.randint(0,len(strings)-1)
		string = strings[choice].split(";")
		tweet_text = "Can anyone recommend "+string[0]+"?"
		post_tweet(tweet_text, twitter_api)
		save_own_current_tweets(recommendation_tweets_collection, tweet_text)
def steal():
