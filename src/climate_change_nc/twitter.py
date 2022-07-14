import requests
import csv
import time
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = f"{Path.home()}/.climate_change_nc/data"
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
USER_URL = "https://api.twitter.com/2/users"
TWEET_URL = "https://api.twitter.com/2/tweets"
REPLY_URL = "https://api.twitter.com/2/tweets/search/recent"
MAX_RESULTS = 100 # 10 to 100
HASHTAG_LIST = [
    "#ClimateChange",
    "#climatechange",
    "#climate_change",
    "#GlobalWarming",
    "#globalwarming",
    "#global_warming",
]

NEXT_TOKEN_KEY = "next_token"


def log(msg):
    print(f"[{datetime.now().strftime('%y%m%d-%H%M%S')}] {msg}")


def error(msg):
    log(f"[ERROR] {msg}")


def setup_database(date):
    paths = {
        "tweets": {
            "path": f"{DATA_DIR}/{date.strftime('%Y%m%d_tweets.csv')}",
            "fieldnames": ["id", "author_id", "conversation_id", "created_at", "lang", "retweet_count", "reply_count",
                           "like_count", "quote_count", "reply_settings", "text"],
        },
        "users": {
            "path": f"{DATA_DIR}/{date.strftime('%Y%m%d_users.csv')}",
            "fieldnames": ['id', 'username', 'name', 'protected', 'verified', 'followers_count', 'following_count',
                           'tweet_count', 'listed_count', 'url', 'description'],
        },
        "replies": {
            "path": f"{DATA_DIR}/{date.strftime('%Y%m%d_replies.csv')}",
            "fieldnames": ["id", "author_id", "conversation_id", "created_at", "lang", "retweet_count", "reply_count",
                           "like_count", "quote_count", "referenced_tweets", "text"],
        },
        "metadata": {
            "path": f"{DATA_DIR}/{date.strftime('%Y%m%d_metadata.csv')}",
            "fieldnames": ['time', 'newest_id', 'oldest_id', 'result_count', 'next_token']

        }
    }

    for filetype, info in paths.items():
        if Path(info['path']).is_file():
            raise Exception(f"{info['path']} Data file exists")
        else:
            with open(info['path'], "w", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=info['fieldnames'])
                writer.writeheader()

    return paths


def write_tweets(tweets, path):
    log(f"Writing {len(tweets)} tweets to {path}")

    if not tweets:
        return

    try:
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
    except:
        error("Unable to store tweets")


def write_user(user, path):
    log(f"Writing 1 user to {path}")

    if not user:
        return

    try:
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
    except:
        error("Unable to store the user")


def write_replies(replies, path):
    log(f"Writing {len(replies)} replies to {path}")

    if not replies:
        return

    try:
        with open(path, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')

            for reply in replies:
                writer.writerow([
                    reply['id'],
                    reply['author_id'],
                    reply['conversation_id'],
                    reply['created_at'],
                    reply['lang'],
                    reply['public_metrics']['retweet_count'],
                    reply['public_metrics']['reply_count'],
                    reply['public_metrics']['like_count'],
                    reply['public_metrics']['quote_count'],
                    reply['referenced_tweets'],
                    reply['text'].replace("\n", "\\n"),
                ])
    except:
        error("Unable to store replies")


def write_metadata(metadata, type, path):
    log(f"Writing {len(metadata)} of type {type} replies to {path}")

    if not metadata:
        return

    try:
        with open(path, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')

            writer.writerow([
                datetime.now().strftime("%y%m%d-%H%M%S"),
                metadata['newest_id'],
                metadata['oldest_id'],
                metadata['result_count'],
                metadata['next_token']
            ])
    except:
        error("Unable to store replies")


class MyTwitter:
    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}

        log("Setting up databases...")
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    def get_daily_tweets(self, date):
        start = datetime(year=date.year, month=date.month, day=date.day, hour=12, minute=0, second=0)
        end = start + timedelta(1)

        log(f"Retrieving tweets from {start.strftime('%y%m%d-%H%M%S')} to {end.strftime('%y%m%d-%H%M%S')}")

        try:
            paths = setup_database(start)
        except Exception:
            error(
                f"Tweets of {start.strftime('%Y-%m-%d')} has already been downloaded. Please remove its csv file if the you wish to download them again")
            return
        except:
            error(f"Unknown error while trying to download tweets of {start.strftime('%Y-%m-%d')}")
            return

        next_token = None
        fetched_users = set({})
        while True:
            log("Retrieving new set of tweets")
            tweets, meta = self._get_tweets(start, end, next_token)

            log(f"{len(tweets)} new tweets have been retrieved")
            log(f"Meta data of retrieved tweets")
            log(f"- Keys: {meta.keys()}")
            log(f"- Vals: {meta.values()}")

            write_tweets(tweets, paths['tweets']['path'])
            write_metadata(meta, paths['metadata']['path'])

            for tweet in tweets:
                log(f"Processing a new tweet with id: {tweet['id'] if 'id' in tweet else ''}")

                if 'author_id' in tweet and tweet['author_id'] not in fetched_users:
                    log(f"Retrieving a new user...")
                    fetched_users.add(tweet['author_id'])
                    user = self._get_user(tweet['author_id'])
                    write_user(user, paths['users']['path'])

                if 'conversation_id' in tweet and 'public_metrics' in tweet and 'reply_count' in tweet['public_metrics'] and int(tweet['public_metrics']['reply_count']) > 0:
                    log(f"Retrieving {tweet['public_metrics']['reply_count']} replies...")
                    replies = self._get_replies(tweet['conversation_id'])
                    write_replies(replies, paths['replies']['path'])

            log("Preparing to retrieve new batch of tweets...")

            if NEXT_TOKEN_KEY in meta and meta[NEXT_TOKEN_KEY]:
                log("Next token have been found...")
                next_token = meta[NEXT_TOKEN_KEY]
            else:
                log("The End.")
                break

    def _get_tweets(self, start, end, next_token=None):
        params = {
            "query": "(" + " OR ".join(
                [f"\"{h}\"" for h in HASHTAG_LIST]) + ") lang:en -is:retweet -is:quote -is:reply",
            "start_time": f"{start.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            "end_time": f"{end.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            "max_results": MAX_RESULTS,
            "tweet.fields": "id,text,lang,geo,author_id,conversation_id,created_at,public_metrics,possibly_sensitive,referenced_tweets,reply_settings",
            "user.fields": "id,username,created_at,location,public_metrics,url,verified",
            "place.fields": "id,country,name,place_type"
        }

        if next_token:
            params[NEXT_TOKEN_KEY] = next_token
        else:
            if NEXT_TOKEN_KEY in params:
                del (params[NEXT_TOKEN_KEY])

        res = requests.get(SEARCH_URL, params=params, headers=self.headers)
        time.sleep(2)

        if res.status_code == 200 and 'data' in res.json() and 'meta' in res.json():
            return res.json()['data'], res.json()['meta']
        else:
            print(f"Error: Response status {res.status_code}. Check the params:", params)
            print(f"     : {res.content}")
            return [], {NEXT_TOKEN_KEY: None}

    def _get_replies(self, conversation_id):
        params = {
            "query": f"conversation_id:{conversation_id} is:reply",
            "max_results": MAX_RESULTS,
            "tweet.fields": "id,text,lang,geo,author_id,conversation_id,created_at,public_metrics,possibly_sensitive,referenced_tweets,reply_settings",
            "user.fields": "id,username,created_at,location,public_metrics,url,verified",
            "place.fields": "id,country,name,place_type"
        }

        replies = []

        while True:
            res = requests.get(REPLY_URL, params=params, headers=self.headers)
            time.sleep(2)

            if res.status_code == 200 and 'data' in res.json():
                replies += res.json()['data']

                if 'meta' in res.json() and NEXT_TOKEN_KEY in res.json()['meta'] and res.json()['meta'][NEXT_TOKEN_KEY]:
                    params[NEXT_TOKEN_KEY] = res.json()['meta'][NEXT_TOKEN_KEY]
                else:
                    return replies

    def _get_user(self, user_id):
        params = {
            "user.fields": "id,username,created_at,name,location,public_metrics,url,protected,verified,description",
        }

        res = requests.get(f"{USER_URL}/{user_id}", params=params, headers=self.headers)
        time.sleep(2)

        if res.status_code == 200 and 'data' in res.json():
            return res.json()['data']
        else:
            return {}
