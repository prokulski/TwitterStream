import tweepy
import json
import sqlite3

# import tokens from api_tokens.py file
from api_tokens import *


auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_acces_token, twitter_acces_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)


# DB stuff
# connect to DB
conn = sqlite3.connect('twitter2.sqlite')
c = conn.cursor()

# delete old table
c.execute('DROP TABLE IF EXISTS tweets')
conn.commit()

# create new table
c.execute('''
    CREATE TABLE tweets (
    user_screen_name text,
    user_id text,
    message_id text,
    timestamp text,
    message text,
    in_reply_to_status_id text,
    in_reply_to_user_id text,
    quoted_status_permalink text
    )
    ''')

conn.commit()


# place for list members
users_names = []


# Stream Listener class
class TweetStreamListener(tweepy.StreamListener):

    # When data is received
    def on_data(self, data):

        # Error handling because teachers say to do this
        try:

            # Make it JSON
            tweet = json.loads(data)

            # only tweets from list members
            # and without RTs
            if (tweet['user']['screen_name'] in users_names and
                    'RT @' not in tweet['text']):

                # print elements:
                print('user_screen_name  : ' + tweet['user']['screen_name'])
                print('user_id           : ' + str(tweet['user']['id']))
                print('tweet_id          : ' + str(tweet['id']))
                print('created_at        : ' + str(tweet['created_at']))
                print('timestamp_ms      : ' + str(tweet['timestamp_ms']))

                if tweet['truncated'] == True:
                    tw_text = tweet['extended_tweet']['full_text']
                    print('full_text         : ' +
                          tweet['extended_tweet']['full_text'])
                else:
                    tw_text = tweet['text']
                    print('text              : ' + tweet['text'])

                print('is_quote_status   : ' +
                      str(tweet['is_quote_status']))

                print('in_reply_to_status_id : ' +
                      str(tweet['in_reply_to_status_id']))
                print('in_reply_to_user_id   : ' +
                      str(tweet['in_reply_to_user_id']))

                if tweet['is_quote_status'] == True:
                    print('quoted_status_permalink_expanded')
                    print(tweet['quoted_status_permalink']['expanded'])
                    tw_permalink = tweet['quoted_status_permalink']['expanded']
                else:
                    tw_permalink = None

                # save tweet to database
                c.execute('''
                    INSERT INTO tweets (
                        user_screen_name,
                        user_id,
                        message_id,
                        timestamp,
                        message,
                        in_reply_to_status_id,
                        in_reply_to_user_id,
                        quoted_status_permalink
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                          (tweet['user']['screen_name'],
                           str(tweet['user']['id']),
                           str(tweet['id']),
                           str(tweet['timestamp_ms']),
                           tw_text,
                           str(tweet['in_reply_to_status_id']),
                           str(tweet['in_reply_to_user_id']),
                           str(tw_permalink)
                           ))
                conn.commit()

                '''
                if tweet['extended_entities']['media_url']:
                    print('media_url')
                    print(tweet['extended_entities']['media'][0]['media_url'])
                '''

                # print(json.dumps(tweet, indent=2, sort_keys=True))
                print("\n")

        # Let me know if something bad happens
        except Exception as e:
            print('Exception: ' + str(e))
            print(json.dumps(tweet, indent=2, sort_keys=True))
            pass

        return True


# Driver
if __name__ == '__main__':
    # members of https://twitter.com/dziennikarz/lists/dziennikarze/members
    print("Reading list members...")

    users = []
    cur = -1
    i = 1

    while True:
        lista = api.list_members(slug="Dziennikarze",
                                 owner_screen_name="dziennikarz",
                                 cursor=cur)
        for e in lista[0]:
            users.append(e.id_str)
            users_names.append(e.screen_name)

        # next page of member list
        cur = lista[1][1]

        # last page?
        if cur == 0:
            break

    # add @lemur78 - for tests
    users.append('66435928')
    users_names.append('lemur78')

    print('Done. Got ' + str(len(users)) + ' users')

    # Run the stream!
    l = TweetStreamListener()
    stream = tweepy.Stream(auth, l)

    # Filter the stream for these users
    stream.filter(follow=users)
