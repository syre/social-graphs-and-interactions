
# coding: utf-8

## NLTK

# In[1]:

#import nltk
#nltk.download()


# In[2]:

from nltk.book import *


# In[3]:

text1.concordance("monstrous")


# In[4]:

text1.similar("monstrous")


## Exercise 1

### Example 1.5 in book:

# In[2]:

import twitter
import json

CONSUMER_KEY = 'dBzN5LgoHAZfC5cQK7ItOwHRi' #API key
CONSUMER_SECRET = '1keiti4AmqArm6Quumpmq2fW19YFwoOUmd023xb5lf6fof3Eh4' #API secret key
OAUTH_TOKEN = '2787905696-YNEKdOUnD3nXPWUHopY2nDNPfYIfJkMkLh5vxsC'  #Access token
OAUTH_TOKEN_SECRET = '85kXzVNoIZ2O9s8nxwPLWbcap6lc1VfXn1HHl6PYkl0Tr' #access token secret

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)

print twitter_api

q= '#MTVEMA'
count = 100
search_results = twitter_api.search.tweets(q=q, count=count)
statuses = search_results['statuses']

for _ in range(5):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e:
        break
    
    kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
    
    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']
    
print json.dumps(statuses[0], indent=1)


# In[10]:

print json.dumps(statuses[3], indent=1)


# In[14]:

import pprint
hej = [s for s in statuses if s['coordinates']]
pprint.pprint(hej[0])


#### Coordinate

                The coordinate field contains the longitude and latitude for the person who has tweeted the tweet on that time. 
                
### Example 1.6:

# In[7]:

status_texts = [status['text'] for status in statuses]
screen_names = [user_mention['screen_name'] for status in statuses for user_mention in status['entities']['user_mentions']]
hashtags = [hashtags['text'] for status in statuses for hashtags in status['entities']['hashtags']]

#Compute a collection of all words from all tweets
words = [w for t in status_texts for w in t.split()]

#Explore the first 5 items for each...
print "Texts:"
print json.dumps(status_texts[0:5], indent=1)
print "\nNames:"
print json.dumps(screen_names[0:5], indent=1)
print "\nHashtags:"
print json.dumps(hashtags[0:5], indent=1)
print "\nWords:"
print json.dumps(words[0:5], indent=1)


### Example 1.7:

# In[9]:

from collections import Counter

for item in [words, screen_names, hashtags]:
    c = Counter(item)
    print c.most_common()[:10] #top 10
    print


#### Explain Counter:

                bla bla
                
### Example 1.8:

# In[13]:

# install prettytable: !pip install prettytable
from prettytable import PrettyTable
for label, data in (('Word', words),
                    ('Screen Name', screen_names),
                    ('Hashtag', hashtags)):
    pt = PrettyTable(field_names=[label, 'Count'])
    c = Counter(data)
    [pt.add_row(kv) for kv in c.most_common()[:10]]
    pt.align[label], pt.align['Count'] = 'l', 'r' #set column alignment
    print pt


### Example 1.9:

# In[15]:

import nltkMethods

print nltkMethods.lexical_diversity(words)
print nltkMethods.lexical_diversity(screen_names)
print nltkMethods.lexical_diversity(hashtags)
print nltkMethods.average_words(status_texts)


### Example 1.10: 

# In[16]:

retweets = [
            #Store out a tuple ofr these three values...
            (status['retweet_count'], 
             status['retweeted_status']['user']['screen_name'], 
             status['text'])
            
            #... for each status...
            for status in statuses
            if status.has_key('retweeted_status')
]

#Slice off the first 5 from the sorted results and display each item in the tuple
pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text'])
[pt.add_row(row) for row in sorted(retweets,reverse=True)[:5]]
pt.max_width['Text']=50
pt.align = 'l'
print pt


### Example 1.11:

# In[36]:

#Get retweet_status id!
import pprint
for status in statuses:
    if status.has_key('retweeted_status'):
        pprint.pprint(status['retweeted_status']['id'], indent=1) #509560138517053440L
        ID = status['retweeted_status']['id']
        break #get the first id


# In[37]:

_retweets = twitter_api.statuses.retweets(id=ID)
print [r['user']['screen_name'] for r in _retweets]


# In[ ]:



