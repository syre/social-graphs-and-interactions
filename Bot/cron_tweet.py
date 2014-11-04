#!/usr/bin/env python3
import random
from twitter_bot import *
import time
"""cron_follow should start at 15:00 san fransisco time + random delay (30m)
   in the cron tab"""


#if choice == 0:
#    print "Personal!"
#    personal()
#elif choice == 1:
#    print "recommendation :)"
#    recommendation()
#else:
#    print "steal! (Muhahaha!)"

def findIndexOfSubString(tweet, strings):
    subString = tweet['text'][22:-1] #extract the uniqueness of the tweet-string
    index = -1
    index = [strings.index(s) for s in strings if subString in s] #look for it in string (IT SHOULD BE THERE!!)
    return index

def chooseRecomText(strings):
    random.seed()
    choice = random.randint(0,len(strings)-1)
    string = strings[choice].split(";")
    return string

def personal():
    print ("personal!")
    random.seed()
    choice = random.randint(0,1)
    if choice == 0:
        f = open("personal.txt", 'r')
        strings = f.readlines()
        f.close()
        choice = random.randint(0,len(strings)-1)
        personalTweet = strings[choice]
        flag=0
        for result in personal_tweets_collection.find({"text": {'$exists':'true', '$in':[personalTweet]}}):
            if flag==1:
                break
            five_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=5)
            if dateutil.parser.parse(result["tweeted_at"]) < five_days_ago:
                print ("More than 5 days: %r" % personalTweet)
                #post_tweet(personalTweet, twitter_api)
                personal_tweets_collection.update({'text':personalTweet},{'$set':{'tweeted_at':datetime.datetime.now().isoformat()}})
                flag +=1

                print ("""Chosed to tweet a personal tweet. Chosed a tweet from personal.txt and that was in the db.\n
                The tweet has been tweetet more than 5 days ago, so we tweet it again\n
                We update it in the db""")
            else:
                print ("""Chosed to tweet a personal tweet. Chosed a tweet from personal.txt and that was in the db.\n
                The tweet has been tweetet within 5 days, so we won't tweet anything""")
        if flag ==0: #no result from db
            print (personalTweet)
            post_tweet(personalTweet, twitter_api)
            save_own_current_tweets(personal_tweets_collection, personalTweet)
            """Chosed to tweet a personal tweet. Chosed a tweet from personal.txt and that was NOT in the db.\n
                The tweet has been postet and saved in the db"""
    else:
        events = find_new_events()
        eventDicts = events[0] #Choose the events that happening today
        print (eventDicts)
        choice = random.randint(0,len(eventDicts['events'])-1)
        event = eventDicts["events"][choice] #Choose a random event
        f = open("eventText.txt", 'r')
        eventText = f.readlines()
        f.close()
        #choiceEventText = random.randint(0,len(eventText)-1)
        strings = random.choice(eventText).split(";")
        print ("strings: %r" % strings)
        adjectives = ["NONE"]
        f = open("adjective.txt", 'r')
        adjectives.extend(f.readlines())
        f.close()
        print ("adjectives: %r" % adjectives)
        adjective = random.choice(adjectives).rstrip()
        print ("adjective: %r" % adjective)
        if "multiple" not in event["place"].lower(): #Tries to avoid a miss-spelling
            tweetEvent = strings[0] + " " +event["name"] + " " + strings[1].rstrip() + " " + event["place"]
            if adjective != "NONE":
                tweetEvent += ", "+adjective.rstrip()
            print (tweetEvent)
            post_tweet(tweetEvent, twitter_api)
        else:
            tweetEvent = strings[0] + " " +event["name"]
            if adjective != "NONE":
                tweetEvent += ". "+adjective
            print (tweetEvent)
            post_tweet(tweetEvent, twitter_api)

def recommendation():
    print ("recommendation!")
    f = open("recommendation.txt", 'r')
    strings = f.readlines()
    f.close()
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    for tweet in recommendation_tweets_collection.find():  #cleaning.
            if dateutil.parser.parse(tweet["tweeted_at"]) < seven_days_ago:  #the tweet is more than 7 days old
                recommendation_tweets_collection.remove({"text":tweet["text"], "tweeted_at":tweet["tweeted_at"]})
    flag = 0
    listOfDb = []
    for tweet in recommendation_tweets_collection.find(): #search the db
        if flag == 1: #give only 1 response!
            break
        two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        if dateutil.parser.parse(tweet["tweeted_at"]) > two_days_ago and tweet["response"]!=1: #tweet has been posted within 2 days and there hasn't been a response
            index = findIndexOfSubString(tweet, strings)
            flag +=1
            if index > -1: #it has been found
                resp = strings[index[0]].split(";")
                if resp[1] != "!NOT!":
                    response = "I'm going to " + resp[1].rstrip()+" " +resp[0]
                    print ("response: " + response)
                #post_tweet(response, twitter_api)
                recommendation_tweets_collection.update({"text":tweet['text'], "tweeted_at":tweet["tweeted_at"]}, {'$set':{'response':1}}) #has been answered! removing it
                """Chosed to tweet a recommendation tweet. Saw that there was a recommendation in the db.
                Generate a "respond" and has been postet and saved in the db"""
            else:
                print ("error! the tweet from db could be found in txt-file. check the txt for the tweet: %s" % tweet['text'])
        else: #no response or has been posted within 2 days
            listOfDb.append(tweet)

    if flag ==0: #no result from db
        if len(listOfDb)>0:
            print ("Recommendation: result from db but nothing to answer or all is 'old'")
            indexes = []
            for tweet in listOfDb:
                indexes.extend(findIndexOfSubString(tweet, strings))
            print (indexes)
            print ("hej")
            strings = [x for i,x in enumerate(strings) if i not in indexes]
            string = chooseRecomText(strings)
            tweet_text = "Can anyone recommend "+string[0]+"?"
            print (tweet_text)
            #post_tweet(tweet_text, twitter_api)
            save_own_current_tweets(recommendation_tweets_collection, tweet_text)
        else:
            print ("Recommendation: no result from db")
            string = chooseRecomText(strings)
            tweet_text = "Can anyone recommend "+string[0]+"?"
            print (tweet_text)
            #post_tweet(tweet_text, twitter_api)
            save_own_current_tweets(recommendation_tweets_collection, tweet_text)
            """Chosed to tweet a recommendation tweet. There was NO recommendation tweets in the db.\n
                Chosed a tweet from recommendation.txt and it has been postet and saved in the db"""


random.seed()
time.sleep(random.randint(0,60*30))

func_list = [personal,recommendation] #personal
func = random.choice(func_list)
func()