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
import numpy as np
#import nltk.tokenize.punkt
import sklearn.naive_bayes
import sklearn.linear_model

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
non_rec_tweets_collection = db["non_reciprocal_user_tweets"]
rec_tweets_collection = db["reciprocal_user_tweets"]
random.seed()


def save_own_current_tweets(tweet_db, tweet, flag=0):
    """saves a history over "used" tweets to a mongodb collection"""
    tweetSave = {"text": tweet, "tweeted_at": datetime.datetime.now().isoformat(), "response":flag}
    tweet_db.insert(tweetSave)
    #pprint.pprint("put tweet with text: {} in db: {}".format(tweet["id"], tweet_db))




def get_user_timeline_tweets():
    """ retrieve 200 newest tweets from user timeline"""
    tweets = twitter_api.statuses.user_timeline(count=200)
    if not tweets:
        print("failed to fetch statuses")
        sys.exit()
    return tweets

def get_home_timeline_tweets():
    """retrieve newest tweets from home timeline"""
    sorted_tweets = home_timeline_collection.find().sort("id",pymongo.DESCENDING)
    max_id = sorted_tweets[0]["id"]

    # gets first 200 tweets
    tweets = twitter_api.statuses.home_timeline(count=200, since_id = max_id)
    min_id = min(tweets, key=lambda x: x["id"])["id"]
    max_id = max(tweets, key=lambda x: x["id"])["id"]
    # gets 600 more
    for i in range(3):
        next_tweets = twitter_api.statuses.home_timeline(count=200, max_id=min_id, since_id = max_id)
        if next_tweets:
            tweets.extend(next_tweets)
            max_id = max(next_tweets, key=lambda x: x["id"])["id"]
            min_id = min(next_tweets, key=lambda x: x["id"])["id"]
    return tweets

def is_new_tweet(tweet_db, tweet):
    """checks if a tweet is new (not in the "tweets" collection """
    result = tweet_db.find_one({"id": tweet["id"]})
    if result:
        pprint.pprint("tweet with id: {} exists in db".format(tweet["id"]))
        return False
    return True


def is_current_followback_user(id):
    """checks if a user is in the "followback_users" collection"""
    result = followback_users_collection.find_one({"id": id})
    if result:
        return True
    return False

def is_current_human_user(id):
  """checks if a user is in the "human_users" collection"""
  result = human_users_collection.find_one({"id": id})
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


def post_local_picture_tweet(text, api, picture, coordinates=(HOME_LAT, HOME_LNG), display_coord=True):

    with open(os.path.join(os.path.dirname(__file__), picture), "rb") as image_file:
        latitude=coordinates[0]+random.uniform(0,0.02)
        longitude = coordinates[1]+random.uniform(-0.02,0.02)
        params = {"media[]": image_file.read(), "status": text,  "lat": str(latitude), "long": str(longitude), "display_coordinates": str(display_coord)}

    api.statuses.update_with_media(**params)


def post_retweet(tweet_id):
    twitter_api.statuses.retweet(id=tweet_id)

def save_followback_user(user):
    """saves user to "followback_users" mongodb collection """
    user = {"id": user["id_str"],
            "screen_name": user["screen_name"],
            "save_date": datetime.datetime.now().isoformat()}
    followback_users_collection.insert(user)
    pprint.pprint("put user with id: {} in db".format(user["id"]))

def save_human_user(id):
  user_profile = twitter_api.users.show(user_id=id)
  if ("id_str" in user_profile):
    save_dict = {"save_date": datetime.datetime.now().isoformat()}
    user_profile.update(save_dict)
    human_users_collection.insert(user_profile)
    pprint.pprint("put user with id: {} in human db".format(user_profile["id"]))
  else:
    pprint.pprint("could not fetch user with id: {0} for human db".format(id))


def save_tweet(tweet_db, tweet):
    """saves tweet to "tweets" mongodb collection"""
    inserting_tweet = {"text": tweet["text"],
             "coordinates": tweet["coordinates"],
             "retweet_count": tweet["retweet_count"],
             "id": tweet["id_str"],
             "user_id": tweet["user"]["id_str"],
             "user": {"followers_count": tweet["user"]["followers_count"], "created_at": tweet["user"]["created_at"]},
             "entities": tweet["entities"]
             }
    dt = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    inserting_tweet["created_at"] = dt
    tweet_db.insert(inserting_tweet)
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
        filtered = [u for u in user_page if not is_current_followback_user(u["id_str"])]
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
    filtered = [u for u in user_page if (not is_current_human_user(u["id_str"])) or (not is_current_followback_user(u["id_str"]))]
    # makes sure user is in san fran
    filtered = [u for u in filtered if u["location"] == "San Francisco, CA"]
    users.extend(filtered)
    user_count += len(filtered)
    page_num += 1
  for user in users[:number]:
          twitter_api.friendships.create(screen_name=user["screen_name"])
          pprint.pprint("creating friendship with user: {}".format(user["id_str"]))
          save_human_user(user["id_str"])
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
        # sleep due to Twitter API restrictions
        time.sleep(90)
    last = followback_users[(math.floor(len(followback_users) % 100) * 100):len(followback_users)]
    result.extend(api.friendships.lookup(
        screen_name=",".join([user["screen_name"] for user in last])))

    for result_user in result:
            if "none" in result_user["connections"]:
                pprint.pprint("no relationship whatsoever with user with id: {}".format(result_user["id"]))
                continue

            db_user = followback_db.find_one({"id": result_user["id_str"]})

            if not db_user:
                pprint.pprint("user with id: {} is not in database".format(result_user["id"]))
                continue
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

def follow_humans_from_list(number, delay_in_seconds=0):
    url = "http://ec2-54-77-226-94.eu-west-1.compute.amazonaws.com/static/targets"
    id_list = requests.get(url).text
    id_list = id_list.split("\n")
    id_list = [int(x.strip()) for x in id_list if x]
    new_ids = [id for id in id_list if not is_current_human_user(id) and not is_current_followback_user(id)]
    if (new_ids):
        for id in new_ids[:number]:
            twitter_api.friendships.create(user_id=id)
            pprint.pprint("creating friendship with user: {}".format(id))
            save_human_user(id)
            if delay_in_seconds:
                time.sleep(random.randint(int(delay_in_seconds)/2,delay_in_seconds))

def follow_reciprocal_humans_from_list(number, delay_in_seconds=0):
    url = "http://ec2-54-77-226-94.eu-west-1.compute.amazonaws.com/static/targets"
    id_list = requests.get(url).text
    id_list = id_list.split("\n")
    id_list = [int(x.strip()) for x in id_list if x]
    random_id = random.choice(id_list)
    # get users that the random human is following
    human_following_user_ids = set(twitter_api.friends.ids(user_id=random_id, count=5000)["ids"])
    # get users that are following the random human
    following_human_user_ids = set(twitter_api.followers.ids(user_id=random_id, count=5000)["ids"])

    reciprocal = human_following_user_ids & following_human_user_ids
    # filter on already in human and followback db
    reciprocal = {id for id in reciprocal if not is_current_human_user(id) and not is_current_followback_user(id)}
    if reciprocal:
        for id in random.sample(reciprocal, number):
            twitter_api.friendships.create(user_id=id)
            save_human_user(id)
            if delay_in_seconds:
                time.sleep(random.randint(int(delay_in_seconds)/2,delay_in_seconds))

def find_best_retweet():
    """Pulls in 100 tweets from 10 categories (1000 tweets)
    rates it according to """
    hashtags = ["Horses", "Bulls", "Coldplay", "Travelling", "Foodie", "Animals", "ChicagoBulls", "Indie", "Maldives", "Dogs"]
    one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    tweets = []

    def extract_attributes_from_tweet(tweet):
        """extract attributes from tweet closure"""
        followers = tweet["user"]["followers_count"]
        num_words = len(nltk.tokenize.punkt.PunktWordTokenizer().tokenize(tweet["text"]))

        dt = datetime.datetime.strptime(tweet["user"]["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        age = (datetime.datetime.now()-dt).total_seconds()

        hashtags_len = len(tweet["entities"]["hashtags"])
        urls_len = len(tweet["entities"]["urls"])
        if (tweet["retweet_count"] >= 10):
            good = 1
        else:
            good = 0
        return np.array([followers, num_words, age, hashtags_len, urls_len, good])

    for hashtag in hashtags:
        r = twitter_api.search.tweets(q="#"+hashtag, count=100, until=str(one_day_ago.date()))["statuses"]
        tweets.extend(r)
    attribute_names = ["number of followers", "age of user", "number of links", "number of words", "number of hashtags"]
    class_names = ["Good", "Bad"]
    X = np.empty((len(tweets), 6))
    for i, tweet in enumerate(tweets):
        X[i] = extract_attributes_from_tweet(tweet)
    y = X[:,5]
    X = X[:,:5]
    bayes = sklearn.naive_bayes.MultinomialNB()
    bayes.fit(X,y)

    one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=18)
    best_tweet = ""
    prob = 0
    home_timeline_tweets = home_timeline_collection.find({"created_at" : {"$gt": one_day_ago}})
    for tweet in home_timeline_tweets:
        # get the tweet without the good attribute
        pred = bayes.predict(extract_attributes_from_tweet(tweet)[:5])
        if pred > prob:
            best_tweet = tweet
            prob = pred
    return tweet

def intervention_retweet(hashtag):
    # goddamn that unparseable url
    bot_screennames = ["2787613616", "matsie_at_dtu", "hybrishybris",
                        "AndrenatorC", "CPH_Startup", "Lakerolls", "FitVeganGirl_",
                        "RichardsIndie", "TheRexyGuy", "AxelCyrilian", "Where_is_JB_now",
                        "Pralesworth", "henrikholm89", "zakflanigan", "RealAndersDuck",
                        "AlyciaGerald", "jsmth_t", "hirihiker", "SirZenji", "meetjamesmet",
                        "madpopo79", "cj_hitower", "THINKDEEPYO", "JackBoHorseMan",
                        "Timmy_abroad", "Shtinoehh", "ioapsy", "SuperRexy", "SimonWJorgensen",
                        "clintcrock", "zoesprings", "marcussor", "neergdave", "AnnasHollywood",
                        "sonia_manning", "canuckWong", "sapiezynski", "ericfullhammer", "ethanwoods88"]

    tweets = twitter_api.search.tweets(q=hashtag, count=100)

    for tweet in tweets["statuses"][:4]:
        try:
            post_retweet(tweet["id"])
        except (twitter.api.TwitterHTTPError, urllib.error.HTTPError):
            print("sharing not allowed for that tweet")
            continue

    tweets = tweets["statuses"][4:]
    retweet_count = 0
    while(retweet_count < 15):
        for tweet in tweets:
            if tweet["user"]["screen_name"] not in bot_screennames:
                try:
                    post_retweet(tweet["id"])
                except (twitter.api.TwitterHTTPError, urllib.error.HTTPError):
                    print("sharing not allowed for that tweet")
                    continue
                retweet_count += 1
                time.sleep(random.randint(30,60))
        max_id = max(tweets, key=lambda x: x["id"])["id"]
        min_id = min(tweets, key=lambda x: x["id"])["id"]
        tweets = twitter_api.search.tweets(q=hashtag, count=100, since_id=max_id, max_id=min_id)["statuses"]

def intervention_favorite(hashtag):
    tweets = twitter_api.search.tweets(q=hashtag, count=100)
    for tweet in tweets["statuses"]:
        try:
            twitter_api.favorites.create(id=tweet["id_str"])
        except (twitter.api.TwitterHTTPError,urllib.error.HTTPError) as e:
            print(e)
            continue


if __name__ == '__main__':
    post_tweet("Bulls vs Kings, let's go Kingslayers! #NBA #ChicagoBulls #Bulls", twitter_api)
