import tweepy
import json
import sqlite3

# Twitter API
twitter_api_key = "Ta6rwvmSXwKvxXEZnrGTbapTY"
twitter_api_secret = "Cthj9OthgrfuRZepQAR3gJ2XqTogz0VTapuRrACna8Pzn7dpTS"
twitter_acces_token = "1081179628318982144-2XLZDE3yh3JckoFdNIWH6sHTyNMI7I"
twitter_acces_secret = "l4cdDlm6sqqI24JO7VGc3DWqTTn4wlHWdo23tDjg5y4fT"

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
    # lista użytkowników z listy https://twitter.com/dziennikarz/lists/dziennikarze/members
    users = []
    cur = -1
    i = 1

    while True:
        lista = api.list_members(slug="Dziennikarze", owner_screen_name="dziennikarz", cursor = cur)
        for e in lista[0]:
            # user ID dodany do listy
            users.append(e.id_str)
            # który to i o to za user?
            print(str(i) + ': ' + e.screen_name)
            i = i + 1

        # następna strona wyników
        cur = lista[1][1]

        # czy to była ostatnia?
        if cur == 0:
            break


    # dodaje siebie dla testow
    users.append('66435928')

    print('Zebrano ' + str(len(users)) + ' userów')

    # Run the stream!
    l = TweetStreamListener()
    stream = tweepy.Stream(auth, l)

    # Filter the stream for these keywords. Add whatever you want here!
    stream.filter(follow=users)
