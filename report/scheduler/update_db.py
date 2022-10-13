import datetime
import sqlite3
from sqlite3 import Error
import psycopg2
import sys
import os
import json
import tweepy

DEBUG = False

if not DEBUG:
    DB_USER = os.environ.get('DB_USER', default='user')
    DB_PWD = os.environ.get('DB_PWD', default='password')
else:
    DB_USER = 'postgres'
    DB_PWD = 'postgres'


def get_user_data(client=None, user_name='Renate_KE'):
    user_data = {}
    user = client.get_user(username=user_name, user_fields='public_metrics')
    user_id = user.data.id

    today = f"{datetime.datetime.today().strftime('%Y-%m-%d')}T00:00:00Z"
    yesterday = f"{((datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d'))}T00:00:00Z"

    tweets = client.get_users_tweets(id=user_id, exclude="retweets", start_time=yesterday, end_time=today,
                                     tweet_fields=[
                                         'public_metrics', 'author_id', 'conversation_id'],
                                     max_results=100)

    followers = user.data['public_metrics']['followers_count']
    retweets = 0
    likes = 0
    replies = 0
    for t in tweets.data:
        retweets += t.data["public_metrics"]["retweet_count"]
        likes += t.data["public_metrics"]["like_count"]
        replies += t.data["public_metrics"]["reply_count"]
        # print(t.data["public_metrics"])

    user_data["tweets"] = len(tweets.data)
    user_data["retweets"] = retweets
    user_data["likes"] = likes
    user_data["replies"] = replies
    user_data["followers"] = followers
    user_data["timestamp"] = today
    user_data["name"] = user_name

    return user_data


def create_connection(db_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    if db_name.endswith(".sqlite3"):
        try:
            conn = sqlite3.connect(db_name)
        except Error as e:
            print(e)
    else:
        try:
            conn = psycopg2.connect(user=DB_USER,
                                    password=DB_PWD,
                                    host="localhost",
                                    port="5432",
                                    database=db_name)
        except Error as e:
            print(e)

    return conn


def get_user_id(conn, print_query=False):
    """
    Get the user_id given names
    :param conn:
    :param project:
    :return: project id
    """
    sql = f'''SELECT user_name, id FROM
              report_twitter_user'''
    cur = conn.cursor()

    if print_query:
        print(sql)

    cur.execute(sql)
    conn.commit()
    return dict(cur.fetchall())


def update_stats(conn, data, print_query=False):
    """
    Create new stats
    :param conn:
    :param data:
    :return: stats id
    """
    set_keys = ",".join([f"{k}" for k in data.keys()])
    set_lines = ",".join([f":{k}" for k in data.keys()])
    set_vals = ",".join([f"%({k})s" for k in data.keys()])

    postgres_db = type(conn) == psycopg2.extensions.connection

    if not postgres_db:
        sql = f'''INSERT OR IGNORE INTO
                    report_twitter_user_stats({set_keys})
                    VALUES ({set_lines})
                    '''
    else:
        sql = f'''INSERT INTO
                report_twitter_user_stats({set_keys})
                VALUES ({set_vals})
                ON CONFLICT DO NOTHING
                '''

    if print_query:
        print(sql)

    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid


def main():

    db = sys.argv[1]

    with open('credentials.json', 'r') as fp:
        api_cred = json.load(fp)

    CONSUMER_KEY = api_cred["CONSUMER_KEY"]
    CONSUMER_SECRET = api_cred["CONSUMER_SECRET"]
    OAUTH_TOKEN = api_cred["OAUTH_TOKEN"]
    OAUTH_TOKEN_SECRET = api_cred["OAUTH_SECRET"]
    BEARER_TOKEN = api_cred["BEARER_TOKEN"]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    # insert data in SQLite
    conn = create_connection(db)

    # get user name and id
    user_data_all = []
    with conn:
        users = get_user_id(conn)
    user_names = list(users.keys())
    print("Updating user stats for the following users")
    for n in user_names:
        print(n)

    # get the user stats
    for user in user_names:
        user_data_all.append(get_user_data(
            client=client, user_name=user))

    # merge user and its id
    for data in user_data_all:
        data["user_id_id"] = users[data["name"]]
        data.pop("name", None)

    with conn:
        for data in user_data_all:
            update_stats(conn, data)


if __name__ == "__main__":
    main()
