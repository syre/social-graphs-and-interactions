
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


# ## Exercise 3 (Natural Language Processing)
# 

# In[40]:

import nltk
from nltk.book import *
get_ipython().magic(u'matplotlib inline')



# In[23]:

text3.concordance("rain")


# In[16]:

text1.similar("good")


# In[30]:

text4.common_contexts(["good","bad"])


# In[28]:

text3.dispersion_plot(["good", "evil"])


# In[55]:

fdist1 = nltk.FreqDist(text2)
fdist1.most_common(75)


# In[56]:

# used 50 since i was unable to see the words on the x axis with 75
fdist1.plot(50,cumulative=True)


# #NLPP Exercises 1.8

# ### 1.8.1

# In[57]:

6 / (3 + 1)


# ### 1.8.2

# In[58]:

26 ** 100


# ### 1.8.3 What happens when you type ["Monty", "Python"]*20
# A single list is created with 20 "Monty", "Pythons"
# 

# In[60]:

["Monty", "Python"]*20


# ### 1.8.4 How many words and distinct words in text2?

# In[66]:

print("total words: {0}".format(len(text2)))
print("total distinct words: {0}".format(len(set(text2))))


# ### 1.8.5 Which genre is more lexical diverse?
# We are using the definition of lexical diversity from the MTSW book and the new NLTK book ( len(set(text)) / len(text) ) because of a discrepancy from the old and the new book. According to the table it seems Humour is more lexical diverse with a value of 0.231 where Fiction: Romance only has a value of 0.121

# ### 1.8.6 Produce a dispersion plot of the four main protagonists in Sense and Sensibility

# In[67]:

text2.dispersion_plot(["Elinor", "Marianne", "Edward", "Willoughby"])


# We can observe that the females play a much larger role in the novel than the males and are mentioned very often.
# An estimate from the plot is that the couples are: (Elinor, Edward) and (Marianne, Wiloughby)

# ### 1.8.7 Find collocations in text 5

# In[68]:

text5.collocations()


# ### 1.8.8 Explain len(set(text4))

# The set function in python converts the sequence to a set thus removing duplicates.
# The len function counts the number of elements in the sequence.

# ### 1.8.12
# The first is a slice expression which slices from element 6 to 12, the second expression extracts the second element in the list, the second expression will typically be more relevant for NLP

# In[72]:

print("Monty Python"[6:12])
print(["Monty", "Python"][1])


# ### 1.8.15

# In[74]:

sorted([w for w in set(text5) if w.startswith("b")])


# ### 1.8.17

# In[83]:

print(text9.index("sunset"))
print(text9[621:643])


# ### 1.8.19
# The second will give the larger sequence and this will always be the case. Because the set function is used before the list comprehension thus it removes lower word duplicates as done by the w.lower()

# In[106]:

print(len(sorted(set([w.lower() for w in text1]))))
print(len(sorted([w.lower() for w in set(text1)])))


# Another example

# In[107]:

words = ["boss", "Boss", "boss", "boss"]
first = sorted(set([w.lower() for w in words]))
second = sorted([w.lower() for w in set(words)])
print(first)
print(second)


# ### 1.8.22

# In[97]:

four_letter_words = [w for w in text5 if len(w) == 4]
fdist = FreqDist(four_letter_words)
fdist.most_common()


# ### 1.8.23

# In[99]:

for word in text6:
    if word.isupper():
        print(word,)


# ### 1.8.25

# In[101]:

words = ['she', 'sells', 'sea', 'shells', 'by', 'the', 'sea', 'shore']
print([w for w in words if w.startswith("sh") or len(w) > 4])


# ### 1.8.26 What does the following Python code do? sum([len(w) for w in text1]) Can you use it to work out the average word length of a text?
# It counts the sum of word lengths in the text1 text.
# We can work out the average word length like this:

# In[102]:

sum([len(w) for w in text1])/len(text1)


# ### 1.8.27 Define a function called vocab_size(text) that has a single parameter for the text, and which returns the vocabulary size of the text.

# In[103]:

def vocab_size(text):
    return len(set(text))

