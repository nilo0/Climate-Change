import requests
import csv
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = f"{Path.home()}/.climate_change_nc/data"
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
USER_URL = "https://api.twitter.com/2/users"
TWEET_URL = "https://api.twitter.com/2/tweets"
MAX_RESULTS = 10  # 10 to 100
HASHTAG_LIST = [
    "#ClimateChange",
    "#climatechange",
    "#cimate_change",
    "#GlobalWarming",
    "#globalwarming",
    "#global_warming",
]


def setup_database(start_date):
    paths = {
        "tweets": {
            "path": f"{DATA_DIR}/{start_date.strftime('%Y%m%d_tweets.csv')}",
            "fieldnames": ["id", "author_id", "conversation_id", "created_at", "lang", "retweet_count", "reply_count", "like_count", "quote_count", "reply_settings", "text"],
        },
        "users": {
            "path": f"{DATA_DIR}/{start_date.strftime('%Y%m%d_users.csv')}",
            "fieldnames": ['id', 'username', 'name', 'protected', 'verified', 'followers_count', 'following_count', 'tweet_count', 'listed_count', 'url', 'description'],
        },
        "replies": {
            "path": f"{DATA_DIR}/{start_date.strftime('%Y%m%d_replies.csv')}",
            "fieldnames": [],
        },
    }

    for filetype, info in paths.items():
        if not Path(info['path']).is_file():
            with open(info['path'], "w", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=info['fieldnames'])
                writer.writeheader()

    return paths


def write_tweets(tweets, path):
    with open(path, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for tweet in tweets:
            writer.writerow([
                tweet['id'],
                tweet['author_id'],
                tweet['conversation_id'],
                tweet['created_at'],
                tweet['lang'],
                tweet['public_metrics']['retweet_count'],
                tweet['public_metrics']['reply_count'],
                tweet['public_metrics']['like_count'],
                tweet['public_metrics']['quote_count'],
                tweet['reply_settings'],
                tweet['text'].replace("\n", "\\n"),
            ])


def write_user(user, path):
    with open(path, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        writer.writerow([
            user['id'],
            user['username'],
            user['name'],
            user['protected'],
            user['verified'],
            user['public_metrics']['followers_count'],
            user['public_metrics']['following_count'],
            user['public_metrics']['tweet_count'],
            user['public_metrics']['listed_count'],
            user['url'],
            user['description'].replace("\n", "\\n"),
        ])


class MyTwitter:
    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}

        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    def get_tweets_of_a_day(self, start_date):
        start = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=12, minute=0, second=0)
        end = start + timedelta(1)

        paths = setup_database(start)

        next_token = None
        users = set({})
        while True:
            tweets, meta = self.get_tweets(start, end, next_token)
            write_tweets(tweets, paths['tweets']['path'])

            for tweet in tweets:
                if'author_id' in tweet and tweet['author_id'] not in users:
                    users.add(tweet['author_id'])
                    user = self.get_user(tweet['author_id'])
                    write_user(user, paths['users']['path'])

            if 'next_token' in meta and meta['next_token']:
                next_token = meta['next_token']
            else:
                break

    def get_tweets(self, start, end, next_token=None):
        params = {
            "query": "(" + " OR ".join([f"\"{h}\"" for h in HASHTAG_LIST]) + ") lang:en -is:retweet",
            "start_time": f"{start.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            "end_time": f"{end.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            "max_results": MAX_RESULTS,
            "tweet.fields": "id,text,lang,geo,author_id,conversation_id,created_at,public_metrics,possibly_sensitive,referenced_tweets,reply_settings",
            "user.fields": "id,username,created_at,location,public_metrics,url,verified",
            "place.fields": "id,country,name,place_type"
        }

        if next_token:
            params['next_token'] = next_token

        res = requests.get(SEARCH_URL, params=params, headers=self.headers)

        if res.status_code == 200:
            return res.json()['data'], res.json()['meta']
        else:
            print(f"Error: Response status {res.status_code}. Check the params:", params)
            return [], {"next_token": None}

    def get_user(self, user_id):
        params = {
            "user.fields": "id,username,created_at,name,location,public_metrics,url,protected,verified,description",
        }

        res = requests.get(f"{USER_URL}/{user_id}", params=params, headers=self.headers)

        if res.status_code == 200:
            return res.json()['data']
        else:
            return {}
