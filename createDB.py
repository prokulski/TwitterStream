import sqlite3

conn = sqlite3.connect('twitter.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS tweets')
conn.commit()

c.execute('''CREATE TABLE tweets
    (tweetText text, user text, date text)''')
conn.commit()

conn.close()
