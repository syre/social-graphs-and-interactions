#!/usr/bin/env python3
import twitter
import pprint
import pymongo
import sys
import datetime
import dateutil.parser
import math
import time
import random
import os
import urllib
import bs4
import requests

with open(os.path.join(os.path.dirname(__file__),"bot_config.txt"),"r") as f:
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

HOME_LAT = 37.772105
HOME_LNG = -122.388089

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
human_users_collection = db["real_users"]
recommendation_tweets_collection = db["recommendation_tweets"]
personal_tweets_collection = db["personal_tweets"]
random.seed()

def save_own_current_tweets(tweet_db, tweet):
    """saves a history over "used" tweets to a mongodb collection"""
    tweet = {"text": tweet["text"], "tweeted_at": datetime.datetime.now().isoformat()}
    tweet_db.insert(tweet)
    pprint.pprint("put tweet with text: {} in db: {}".format(tweet["id"], tweet_db))


def get_user_timeline_tweets():
    """ retrieve 200 newest tweets from user timeline"""
    tweets = twitter_api.statuses.user_timeline(count=200)
    if not tweets:
        print("failed to fetch statuses")
        sys.exit()
    return tweets

def get_home_timeline_tweets():
    """retrieve newest tweets from home timeline"""
    if home_timeline_collection.count():
        sorted_tweets = home_timeline_collection.find().sort("id",pymongo.DESCENDING)
        newest_tweet = sorted_tweets[0]
        if newest_tweet:
            tweets = twitter_api.statuses.home_timeline(count=200, since_id = newest_tweet["id"])
            return tweets
    tweets = twitter_api.statuses.home_timeline(count=200)
    return tweets

def is_new_tweet(tweet_db, tweet):
    """checks if a tweet is new (not in the "tweets" collection """
    result = tweet_db.find_one({"id": tweet["id"]})
    if result:
        pprint.pprint("tweet with id: {} exists in db".format(tweet["id"]))
        return False
    return True


def is_current_followback_user(user):
    """checks if a user is in the "followback_users" collection"""
    result = followback_users_collection.find_one({"id": user["id"]})
    if result:
        return True
    return False

def is_current_human_user(user):
  """checks if a user is in the "human_users" collection"""
  result = human_users_collection.find_one({"id": user["id"]})
  if result:
    return True
  return False

def post_tweet(text, api, coordinates=(HOME_LAT, HOME_LNG), display_coord=True):
    """posts a tweet, if no coordinates are specified, the "home coordinates" are used
        TODO: allow an image to be uploaded (statuses.update_with_media)
    """
    if len(text) <= 140:
        # if we reduce latitude any further we're gonna end up in the bay
        # therefore 0-0.02
        latitude=coordinates[0]+random.uniform(0,0.02)
        longitude = coordinates[1]+random.uniform(-0.02,0.02)
        api.statuses.update(status=text, lat=latitude, long=longitude, display_coordinates=display_coord)
    else:
        print("tweet text too long")

def post_picture_tweet(text, api, url, coordinates=(HOME_LAT, HOME_LNG), display_coord=True):
    extension = url.split(".")[-1]
    urllib.request.urlretrieve(url,"tmp."+extension)
    with open("tmp."+extension, "rb") as imagefile:
        # if we reduce latitude any further we're gonna end up in the bay
        # therefore 0-0.02
        latitude=coordinates[0]+random.uniform(0,0.02)
        longitude = coordinates[1]+random.uniform(-0.02,0.02)
        params = {"media[]": imagefile.read(), "status": text,  "lat": str(latitude), "long": str(longitude), "display_coordinates": str(display_coord)}
    api.statuses.update_with_media(**params)

def post_retweet(tweet_id):
    twitter_api.statuses.retweet(id=tweet_id)

def save_followback_user(user):
    """saves user to "followback_users" mongodb collection """
    user = {"id": user["id"],
            "screen_name": user["screen_name"],
            "save_date": datetime.datetime.now().isoformat()}
    followback_users_collection.insert(user)
    pprint.pprint("put user with id: {} in db".format(user["id"]))

def save_human_user(user):
  user_profile = twitter_api.users.show(user_id=user["id"])
  if ("id" in user_profile):
    save_dict = {"save_date": datetime.datetime.now().isoformat()}
    user_profile.update(save_dict)
    human_users_collection.insert(user_profile)
    pprint.pprint("put user with id: {} in human db".format(user_profile["id"]))
  else:
    pprint.pprint("could not fetch user with id: {0} for human db".format(user["id"]))


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


def follow_followback_users(number, delay_in_seconds=0):
    """ function for following a number of users
     with "followback" in name/description
     keeps going til NUMBER users have been added
     if delay_in_seconds is specified a random delay
     is introduced between creating friendships so that
     specified_delay/2 <= delay <= specified_delay"""
    users = []
    page_num = 0
    user_count = 0
    while(user_count < number):
        user_page = twitter_api.users.search(q="followback", count=20, page=page_num)
        filtered = [u for u in user_page if not is_current_followback_user(u)]
        users.extend(filtered)
        user_count += len(filtered)
        page_num += 1

    for user in users[:number]:
            twitter_api.friendships.create(screen_name=user["screen_name"])
            save_followback_user(user)
            if delay_in_seconds:
                time.sleep(random.randint(int(delay_in_seconds)/2,delay_in_seconds))

def follow_human_users(number, delay_in_seconds=0):
  """
  Function for following human users (right now based in San Francisco)
  keeps going til NUMBER users have been added
  if delay_in_seconds is specified a random delay
  is introduced between creating friendships so that
  specified_delay/2 <= delay <= specified_delay
  """
  users = []
  page_num = 0
  user_count = 0
  while (user_count < number):
    user_page = twitter_api.users.search(q="San Francisco", count=20, page=page_num)
    # makes sure user is not already in databases
    filtered = [u for u in user_page if (not is_current_human_user(u)) or (not is_current_followback_user(u))]
    # makes sure user is in san fran
    filtered = [u for u in filtered if u["location"] == "San Francisco, CA"]
    users.extend(filtered)
    user_count += len(filtered)
    page_num += 1
  for user in users[:number]:
          twitter_api.friendships.create(screen_name=user["screen_name"])
          save_human_user(user)
          if delay_in_seconds:
              time.sleep(random.randint(int(delay_in_seconds)/2,delay_in_seconds))

def unfollow_nonreciprocal_followers(followback_db, api, delay_in_seconds=0):
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
            if delay_in_seconds:
                time.sleep(random.randint(int(delay_in_seconds)/2,delay_in_seconds))

def set_profile_background_image(url):
    extension = url.split(".")[-1]
    urllib.request.urlretrieve(url,"tmp_background_image."+extension)
    with open("tmp_background_image."+extension, "rb") as imagefile:
        img = imagefile.read()
        params = {"banner": img}
    resp = twitter_api.account.update_profile_banner(**params)

def find_profile_background_images():
    topics = ["horses", "maldives", "animals", "san francisco monuments", "chicago bulls games"]
    random_topic = random.choice(topics)
    image_urls = []
    for i in range(0,4):
        image_search_url = "https://ajax.googleapis.com/ajax/services/search/images"
        params = {"v": "1.0", "q": random_topic, "imgsz": "xlarge", "start": i}
        r = requests.get(image_search_url, params=params)
        for result in r.json()["responseData"]["results"]:
            image_urls.append(result["url"])

    return image_urls

def find_new_events():
    url = "http://www.sfweekly.com/sanfrancisco/EventSearch"
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text)
    event_list = []
    for group in soup.find_all("div", {"class": "results_cont"}):
        group_dict = {"date": group.find("div", {"class": "groupHeader"}).text.strip()}
        group_dict["events"] = []
        for event in group.find_all("div", {"class": "event item"}):
            group_dict["events"].append({"name": event.find("span", {"class": "event-title"}).text, "place": event.find("div", {"class": "location"}).a.string})
        event_list.append(group_dict)
    return event_list


if __name__ == '__main__':
    #events = find_new_events()
    #print(events[1]["events"])
    print(type(tweet_collection.find()))
    tweets = recommendation_tweets_collection.find({'$exist':{"tweeted_at"}})
    print(tweets)
    for tweet in tweets:
        print(tweet)
