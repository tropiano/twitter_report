from turtle import update
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys
import json
import tweepy
from twitter_report import settings
from report.scheduler import update_db
# This is the function you want to schedule - add as many as you want and then register them in the start() function below


def update_user_stats():

    db = f"{settings.BASE_DIR}/db.sqlite3"

    with open(f'{settings.BASE_DIR}/credentials.json', 'r') as fp:
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
    conn = update_db.create_connection(db)

    # get user name and id
    user_data_all = []
    with conn:
        users = update_db.get_user_id(conn)
    user_names = list(users.keys())
    print("Updating user stats for the following users")
    for n in user_names:
        print(n)

    # get the user stats
    for user in user_names:
        user_data_all.append(update_db.get_user_data(
            client=client, user_name=user))

    # merge user and its id
    for data in user_data_all:
        data["user_id_id"] = users[data["name"]]
        data.pop("name", None)

    with conn:
        for data in user_data_all:
            update_db.update_stats(conn, data)


def start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.coalesce': 'true'})
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(update_user_stats, 'cron',
                      hour=1, minute=19, name='update_stats', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)
