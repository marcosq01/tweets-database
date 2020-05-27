#!/usr/bin/python

import tweepy
import json
import time
import sys
import glob
import pyodbc

#####
import os

from tweepy import API


from dotenv import load_dotenv
load_dotenv(dotenv_path='app.env', verbose=True)
consumer_key = os.getenv("CONSUMER_KEY")
#print(consumer_key)
consumer_secret = os.getenv("CONSUMER_SECRET")
#print(consumer_secret)
access_token = os.getenv("ACCESS_TOKEN")
#print(access_token)
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
#print(access_token_secret)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
####

server = 'database-1.cfrrewunyxyr.us-east-2.rds.amazonaws.com,1433'
database = 'TwitterProject'
driver = '{SQL Server}'
username = 'admin'
password = 'Esquimal21'

conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

cursor = conn.cursor()
# TEST db connection
cursor.execute('SELECT * FROM RESEARCHERS')

for row in cursor:
    print(row)

# read all json files
file_str = r'bdatweets_*.json'
# list of pathnames according to above regex
file_lst = glob.glob(file_str)

def process_tweet(tweet, researcherID, search_id):
    # user info    
    user_id = tweet['user']['id']
    handle = tweet['user']['screen_name']
    name = tweet['user']['name']
    bio = tweet['user']['description']
    location = tweet['user']['location']
    verified = tweet['user']['verified']
    statuses_count = tweet['user']['statuses_count']
    followers_count = tweet['user']['followers_count']
    friends_count = tweet['user']['friends_count']
    favourites_count = tweet['user']['favourites_count']
    created_at = tweet['user']['created_at']
    

    ################################      TWEET info
    tweet_id = tweet['id']
    tweet_text = tweet['text']
    # userid
    favorite_count = tweet['favorite_count']
    # search_id
    lang = tweet['lang']

    # if tweet is a retweet, if it's in the dictionary
    if 'retweeted_status' in tweet:
        retweet_id = tweet['retweeted_status']['id']
        process_tweet(tweet['retweeted_status'], researcherID, search_id)
    else:
        retweet_id = None

    #if tweet is a quote
    if 'quoted_status' in tweet:
        quote_id = tweet['quoted_status_id']
        #print('hola')
        process_tweet(tweet['quoted_status'], researcherID, search_id)
    else:
        quote_id = None


    # if place is not null
    if tweet['place'] != None:
        place_id = tweet['place']['id']
    else:
        place_id = None

    # if tweet is a reply
    if tweet['in_reply_to_status_id'] != None:
        reply_id = tweet['in_reply_to_status_id']
        # tw would be the new tweet
        tw = api.get_status(reply_id)._json
        process_tweet(tw, researcherID, search_id)
    else:
        reply_id = None

    if 'possibly_sensitive' in tweet:
        possibly_sensitive = tweet['possibly_sensitive']
    else:
        possibly_sensitive = None

    tweet_created_at = tweet['created_at']

    if tweet['coordinates'] != None:
        tweet_coordinates = ', '.join(str(x) for y in tweet['coordinates']['coordinates'])
        tweet_coordinates_type = tweet['coordinates']['type']
    else:
        tweet_coordinates = None
        tweet_coordinates_type = None

    if tweet['place'] != None:
        tweet_place_id = tweet['place']['id']
    else:
        tweet_place_id = None

    ########################################


    # read hashtag information [indices, text]
    hashtag_objects = tweet['entities']['hashtags']

    #read mention information
    user_mention_object = tweet['entities']['user_mentions']

    # insert USER only if the user doesn't exists already in the database
    rows = cursor.execute('SELECT * FROM USERS WHERE userid = ?', user_id).fetchall()
    if len(rows) == 0:
        cursor.execute('''
            INSERT INTO USERS (userid, handle, name, bio, location, verified, statuses_count, followers_count, friends_count, favourites_count, created_at)
                VALUES
                    (?,?,?,?,?,?,?,?,?,?,?)
        ''', (user_id, handle, name, bio, location, verified, statuses_count, followers_count, friends_count, favourites_count, created_at))
        conn.commit()

    # insert PLACE, if it is available
    if tweet['place'] != None:
        # insert place only if the place doesn't exists already in the database
        rows = cursor.execute('SELECT * FROM PLACES WHERE place_id = ?', tweet_place_id).fetchall()
        if len(rows) == 0:
            place_id = tweet['place']['id']
            place_name = tweet['place']['name']
            place_full_name = tweet['place']['full_name']
            place_type = tweet['place']['place_type']
            country = tweet['place']['country']
            country_code = tweet['place']['country_code']
            # check if i'm getting correctly the coordinates as a string
            coordinates = ', '.join(str(x) for x in tweet['place']['bounding_box']['coordinates'])
            coordinates_type = tweet['place']['bounding_box']['type']
            cursor.execute('''INSERT INTO PLACES (place_id, short_name, full_name, coordinates, coordinates_type, place_type, country, country_code) 
                VALUES (?,?,?,?,?,?,?,?)''', (place_id, place_name, place_full_name, coordinates, coordinates_type, place_type, country, country_code))
            conn.commit()


    # insert TWEET object only if the tweet doesn't exists already in the database
    rows = cursor.execute('SELECT * FROM TWEETS WHERE tweet_id = ?', tweet_id).fetchall()
    if len(rows) == 0:
        cursor.execute('''
            INSERT INTO TWEETS (tweet_id, tweet_text, userid, favorite_count, search_id, retweet_id, quote_id, reply_id, lang, possibly_sensitive, created_at, coordinates, coordinates_type, place_id)
                VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (tweet_id, tweet_text, user_id, favorite_count, search_id, retweet_id, quote_id, reply_id, lang, possibly_sensitive, tweet_created_at, tweet_coordinates, tweet_coordinates_type, tweet_place_id))
        conn.commit()


    # insert HASHTAGS
    for hashtag in hashtag_objects:
        # insert only unique hashtags
        rows = cursor.execute('''SELECT * FROM HASHTAGS WHERE tweet_id = ? AND
                hashtag = ?''', (tweet_id, hashtag['text'])).fetchall()
        if len(rows) == 0:
            cursor.execute('''
                INSERT INTO HASHTAGS (tweet_id, hashtag)
                    VALUES(?,?)
            ''', (tweet_id, hashtag['text']))
            conn.commit()

    # insert MENTIONS
    for mention in user_mention_object:
        #insert only unique mentions
        rows = cursor.execute('''SELECT * FROM MENTIONS WHERE tweet_id = ? AND handle = ?''',
            (tweet_id, mention['screen_name'])).fetchall()
        if len(rows) == 0:
            cursor.execute('''INSERT INTO MENTIONS (tweet_id, handle, name) 
            VALUES(?,?,?)''', (tweet_id, mention['screen_name'], mention['name']))
            conn.commit()

    



# process every file
for file_idx, file_name in enumerate(file_lst):
    counter = 0
    with open(file_name, 'r') as f:
        for line in f:
            if counter == 0:
				# read researcher ID from the first line
                researcherID = int(line)
                counter = counter + 1
                continue
            if counter == 1:
				# read search ID from the second line
                searchID = int(line)
                counter = counter + 1
                continue
            if line != '\n':
				# each line is a tweet json object, load it and display user id
                tweet = json.loads(line)
                process_tweet(tweet, researcherID, searchID)
				


cursor.close()
conn.close()