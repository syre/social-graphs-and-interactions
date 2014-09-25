#!/usr/bin/env python3
import twitter
import pprint
import pymongo
import sys
import datetime
import dateutil.parser
import math

with open("bot_config.txt","r") as f:
    config = f.readlines()
config_dict = dict(line.strip().split("=") for line in config if not line.startswith("#"))

CONSUMER_KEY = config_dict["CONSUMER_KEY"]  # API key
# API secret key
CONSUMER_SECRET = config_dict["CONSUMER_SECRET"]
# Access token
OAUTH_TOKEN = config_dict["OAUTH_TOKEN"]
# access token secret
OAUTH_TOKEN_SECRET = config_dict["OAUTH_TOKEN_SECRET"]

# connect to twitter
twitter_api = twitter.Twitter(auth=twitter.OAuth(
    OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

DB_HOSTNAME = config_dict["DB_HOSTNAME"]
DB_PORT = int(config_dict["DB_PORT"])

HOME_LAT = 41.9479831
HOME_LNG = -87.8365125

# set up database connection
try:
    client = pymongo.MongoClient(DB_HOSTNAME, DB_PORT)
except pymongo.errors.ConnectionFailure:
    print("failed to connect to database")
    sys.exit()
db = client["twitter_bot"]
tweet_collection = db["tweets"]
followback_users_collection = db["followback_users"]
home_timeline_collection = db["home_timeline_tweets"]

def get_user_timeline_tweets(api):
    """ retrieve 200 newest tweets from user timeline"""
    tweets = api.statuses.user_timeline(count=200)
    if not tweets:
        print("failed to fetch statuses")
        sys.exit()
    return tweets

def get_home_timeline_tweets(api, home_timeline_db):
    """retrieve newest tweets from home timeline"""
    if home_timeline_db.count():
        newest_tweet = home_timeline_db.find().skip(home_timeline_db.count() - 1)[0]
        if newest_tweet:
            tweets = api.statuses.home_timeline(count=200, since_id = int(newest_tweet["id"]))
        else:
            tweets = api.statuses.home_timeline(count=200)
    else:
        tweets = api.statuses.home_timeline(count=200)
    return tweets

def is_new_tweet(tweet_db, tweet):
    """checks if a tweet is new (not in the "tweets" collection """
    result = tweet_db.find_one({"id": tweet["id"]})
    if result:
        pprint.pprint("tweet with id: {} exists in db".format(tweet["id"]))
        return False
    return True


def is_current_followback_user(followback_db, user):
    """checks if a user is in the "followback_users" collection"""
    result = followback_db.find_one({"id": user["id"]})
    if result:
        return True
    return False

def post_tweet(text, api, coordinates=(HOME_LAT, HOME_LNG), display_coord=True):
    """posts a tweet, if no coordinates are specified, the "home coordinates" are used
        TODO: allow an image to be uploaded (statuses.update_with_media)
    """
    if len(text) <= 140:
        api.statuses.update(status=text, lat=coordinates[0], long=coordinates[1], display_coordinates=display_coord)
    else:
        print("tweet text too long")

def post_retweet(tweet_id, api):
    api.statuses.retweet(id=tweet_id)

def save_followback_user(followback_db, user):
    """saves user to "followback_users" mongodb collection """
    user = {"id": user["id"],
            "screen_name": user["screen_name"],
            "save_date": datetime.datetime.now().isoformat()}
    followback_db.insert(user)
    pprint.pprint("put user with id: {} in db".format(user["id"]))



def save_tweet(tweet_db, tweet):
    """saves tweet to "tweets" mongodb collection"""
    tweet = {"text": tweet["text"],
             "coordinates": tweet["coordinates"],
             "retweet_count": tweet["retweet_count"],
             "id": tweet["id"],
             "created_at": tweet["created_at"],
             "user_id": tweet["user"]["id"]}
    tweet_db.insert(tweet)
    pprint.pprint("put tweet with id: {} in db".format(tweet["id"]))


def follow_followback_users(followback_db, api, number):
    """ function for following a number of users
     with "followback" in name/description """
    users = []
    page_num = 0
    user_count = 0
    while(user_count < number):
        user_page = api.users.search(q="followback", count=20, page=page_num)
        filtered = [u for u in user_page if not is_current_followback_user(followback_db, u)]
        users.extend(filtered)
        user_count += len(filtered)
        page_num += 1

    for user in users[:number]:
            api.friendships.create(screen_name=user["screen_name"])
            save_followback_user(followback_db, user)

def unfollow_nonreciprocal_followers(followback_db, api):
    """function for unfollowing users that havent followed us back
    after 24 hours, maybe refactor"""
    one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    followback_users = list(followback_db.find())
    result = []
    for i in range(1, math.floor(len(followback_users) / 100) + 1):
        result.extend(api.friendships.lookup(screen_name=",".join(
            [user["screen_name"] for user in followback_users[(i * 100) - 100:100 * i]])))
    last = followback_users[(math.floor(len(followback_users) % 100) * 100):len(followback_users)]
    result.extend(api.friendships.lookup(
        screen_name=",".join([user["screen_name"] for user in last])))

    for result_user in result:
            if "none" in result_user["connections"]:
                pprint.pprint("no relationship whatsoever with user with id: {}".format(result_user["id"]))
                continue
            db_user = followback_db.find_one({"id": result_user["id"]})
            followed_date = dateutil.parser.parse(db_user["save_date"])
            if "followed_by" in result_user["connections"]:
                pprint.pprint("user with id {} is following us".format(result_user["id"]))
            elif followed_date > one_day_ago:
                pprint.pprint("user with id: {} is less than 24 hours old".format(result_user["id"]))
            else:
                pprint.pprint("destroying friendship with user with id {}".format(result_user["id"]))

                destroy_result = api.friendships.destroy(screen_name=result_user["screen_name"])
                if "id" in destroy_result:
                    pprint.pprint("friendship with user with {} was destroyed".format(destroy_result["id"]))


if __name__ == "__main__":
    timeline_tweets = get_user_timeline_tweets(twitter_api)
    for tweet in timeline_tweets:
        if is_new_tweet(tweet_collection, tweet):
            save_tweet(tweet_collection, tweet)
    
    home_timeline_tweets = get_home_timeline_tweets(twitter_api, home_timeline_collection)
    for tweet in home_timeline_tweets:
        if is_new_tweet(home_timeline_collection, tweet):
            save_tweet(home_timeline_collection, tweet)

    popular_tweet = max(home_timeline_tweets, key=lambda t: t["retweet_count"])
    post_retweet(popular_tweet["id"], twitter_api)

    #follow_followback_users(followback_users_collection, twitter_api, 49)
    #unfollow_nonreciprocal_followers(followback_users_collection, twitter_api)
