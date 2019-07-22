import tweepy
import json
import sqlite3

# Twitter API
# twitter_api_key = "xxxx"
# twitter_api_secret = "xxxx"
# twitter_acces_token = "xxxx"
# twitter_acces_secret = "xxxx"

# import tokens from api_tokens.py file
from api_tokens import *


auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_acces_token, twitter_acces_secret)

api = tweepy.API(auth, wait_on_rate_limit = True)

# DB stuff
conn = sqlite3.connect('twitter.db')
c = conn.cursor()


# Class for defining a Tweet
class Tweet():

    # Data on the tweet
    def __init__(self, text, user, date):
        self.text = text
        self.user = user
        self.date = date

    # Inserting that data into the DB
    def insertTweet(self):

        c.execute("INSERT INTO tweets (tweetText, user, date) VALUES (?, ?, ?)",
            (self.text, self.user, self.date))
        conn.commit()

        print(self.user + ' @ ' + self.date + ': \n' + self.text + '\n')


# Stream Listener class
class TweetStreamListener(tweepy.StreamListener):

    # When data is received
    def on_data(self, data):

        # Error handling because teachers say to do this
        try:

            # Make it JSON
            tweet = json.loads(data)

            # filter out retweets
            if not tweet['retweeted'] and 'RT @' not in tweet['text']:

                # assign all data to Tweet object
                tweet_data = Tweet(
                    str(tweet['text']),
                    tweet['user']['screen_name'],
                    str(tweet['created_at']))

                # Insert that data into the DB
                tweet_data.insertTweet()
                print("success")

        # Let me know if something bad happens
        except Exception as e:
            print(e)
            pass

        return True



# Driver
if __name__ == '__main__':
    # members of https://twitter.com/dziennikarz/lists/dziennikarze/members
    users = []
    cur = -1
    i = 1

    while True:
        lista = api.list_members(slug="Dziennikarze", owner_screen_name="dziennikarz", cursor = cur)
        for e in lista[0]:
            users.append(e.id_str)

        # next page of member list
        cur = lista[1][1]

        # last page?
        if cur == 0:
            break


    # add @lemur78
    users.append('66435928')

    print('Got ' + str(len(users)) + ' users')

    # Run the stream!
    l = TweetStreamListener()
    stream = tweepy.Stream(auth, l)

    # Filter the stream for these users
    stream.filter(follow=users)
