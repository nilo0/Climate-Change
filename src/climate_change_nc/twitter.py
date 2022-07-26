import requests
import time
from datetime import datetime, timedelta

from .my_process import MyProcess
from .my_csv import MyCsv
from .my_logger import MyLogger
from .tweet import Tweet, COLUMNS as TWEET_COLUMNS
from .reply import Reply, COLUMNS as REPLY_COLUMNS
from .quote import Quote, COLUMNS as QUOTE_COLUMNS
from .user import User, COLUMNS as USER_COLUMNS


MIN_TIMEOUT = 30  # seconds
MAX_TIMEOUT = 600  # seconds
MAX_RESULTS = 100  # 10 to 100

TWEET_URL = "https://api.twitter.com/2/tweets/search/recent"
REPLY_URL = "https://api.twitter.com/2/tweets/search/recent"
QUOTE_FMT_URL = "https://api.twitter.com/2/tweets/{}/quote_tweets"
USER_FMT_URL = "https://api.twitter.com/2/users/{}"

HASHTAG_LIST = [
    "#ClimateChange",
    "#climatechange",
    "#climate_change",
    "#GlobalWarming",
    "#globalwarming",
    "#global_warming",
]

NEXT_TOKEN_KEY = "next_token"


class MyTwitter:
    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_daily_tweets(self, date):
        start = datetime(year=date.year, month=date.month, day=date.day, hour=0, minute=0, second=0)
        end = start + timedelta(1)

        logger = MyLogger(date)

        logger.log("Setting up csv files")
        date_str = date.strftime('%Y%m%d')

        tweet_csv = MyCsv(f'{date_str}_tweets', logger)
        tweet_csv.setup(TWEET_COLUMNS)

        reply_csv = MyCsv(f'{date_str}_replies', logger)
        reply_csv.setup(REPLY_COLUMNS)

        quote_csv = MyCsv(f'{date_str}_quotes', logger)
        quote_csv.setup(QUOTE_COLUMNS)

        user_csv = MyCsv(f'{date_str}_users', logger)
        user_csv.setup(USER_COLUMNS)

        logger.log(f"Retrieving tweets from {start.strftime('%y%m%d-%H%M%S')} to {end.strftime('%y%m%d-%H%M%S')}")

        next_token = None
        fetched_users = set({})

        while True:
            logger.log("Retrieving a new set of tweets")

            try:
                tweets, meta = self._get_tweets(start, end, logger, next_token)
            except:
                logger.error(f"Unable to retrieve the patch of {MAX_RESULTS} tweets.")
                time.sleep(15 * 60 / 450 + 1)  # Rate limit
                continue

            logger.log(f"{len(tweets)} new tweets have been retrieved")
            logger.log(f"Meta data of retrieved tweets")
            logger.log(f"- Keys: {meta.keys()}")
            logger.log(f"- Vals: {meta.values()}")

            tweet_csv.write_rows([Tweet(t) for t in tweets])

            for tweet in tweets:
                logger.log(f"Processing a new tweet with id: {tweet['id'] if 'id' in tweet else ''}")

                if 'author_id' in tweet and tweet['author_id'] not in fetched_users:
                    logger.log(f"Retrieving a new user with id {tweet['author_id']}")
                    p = MyProcess(self._get_and_write_user, (tweet['author_id'], user_csv, logger), logger)
                    p.timeout(MIN_TIMEOUT)
                    fetched_users.add(tweet['author_id'])

                if 'conversation_id' in tweet and 'public_metrics' in tweet and 'reply_count' in tweet['public_metrics'] and int(tweet['public_metrics']['reply_count']) > 0:
                    logger.log(f"Retrieving {tweet['public_metrics']['reply_count']} replies from conversation {tweet['conversation_id']} of tweet {tweet['id']}")
                    timeout = min(tweet['public_metrics']['reply_count'] % (MAX_RESULTS / 4) * MIN_TIMEOUT, MAX_TIMEOUT)
                    p = MyProcess(self._get_and_write_replies, (tweet['conversation_id'], reply_csv, logger), logger)
                    p.timeout(timeout)

                if 'public_metrics' in tweet and 'quote_count' in tweet['public_metrics'] and int(tweet['public_metrics']['quote_count']) > 0:
                    logger.log(f"Retrieving {tweet['public_metrics']['quote_count']} quotes of tweet {tweet['id']}")
                    timeout = min(tweet['public_metrics']['quote_count'] % (MAX_RESULTS / 4) * MIN_TIMEOUT, MAX_TIMEOUT)
                    p = MyProcess(self._get_and_write_quotes, (tweet['id'], quote_csv, logger), logger)
                    p.timeout(timeout)

            logger.log("Preparing to retrieve new batch of tweets...")

            if NEXT_TOKEN_KEY in meta and meta[NEXT_TOKEN_KEY]:
                logger.log("Next token have been found...")
                next_token = meta[NEXT_TOKEN_KEY]
            else:
                logger.log("The End.")
                break

    def _get_and_write_user(self, user_id, csv, logger):
        user = self._get_user(user_id, logger)
        csv.write_row(User(user))

    def _get_and_write_replies(self, conversation_id, csv, logger):
        replies = self._get_replies(conversation_id, logger)
        csv.write_rows([Reply(r) for r in replies])

    def _get_and_write_quotes(self, tweet_id, csv, logger):
        quotes = self._get_quotes(tweet_id, logger)
        csv.write_rows([Quote(q) for q in quotes])

    def _get_tweets(self, start, end, logger, next_token=None):
        params = {
            "query": "(" + " OR ".join(
                [f"\"{h}\"" for h in HASHTAG_LIST]) + ") lang:en -is:retweet -is:quote -is:reply",
            "start_time": f"{start.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            "end_time": f"{end.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
            "max_results": MAX_RESULTS,
            "tweet.fields": "id,text,lang,geo,author_id,conversation_id,created_at,public_metrics,possibly_sensitive,referenced_tweets,reply_settings",
            "user.fields": "id,username,created_at,location,public_metrics,url,verified",
            "place.fields": "id,country,name,place_type",
            "sort_order": "recency"
        }

        if next_token:
            params[NEXT_TOKEN_KEY] = next_token
        else:
            if NEXT_TOKEN_KEY in params:
                del (params[NEXT_TOKEN_KEY])

        res = requests.get(TWEET_URL, params=params, headers=self.headers)
        time.sleep(15 * 60 / 450 + 1)  # Rate limit

        if res.status_code == 200 and 'data' in res.json() and 'meta' in res.json():
            return res.json()['data'], res.json()['meta']
        else:
            logger.error(f"Request has been failed ({res.status_code})")
            logger.error(f" - url: {TWEET_URL}")
            logger.error(f" - content: {res.content}")
            return [], {NEXT_TOKEN_KEY: next_token}

    def _get_replies(self, conversation_id, logger):
        params = {
            "query": f"conversation_id:{conversation_id} is:reply",
            "max_results": MAX_RESULTS,
            "tweet.fields": "id,text,lang,geo,author_id,conversation_id,created_at,public_metrics,possibly_sensitive,referenced_tweets,reply_settings",
            "user.fields": "id,username,created_at,location,public_metrics,url,verified",
            "place.fields": "id,country,name,place_type"
        }

        replies = []

        while True:
            try:
                res = requests.get(REPLY_URL, params=params, headers=self.headers, timeout=20)
                time.sleep(15 * 60 / 450 + 1)  # Rate limit

                if res.status_code == 200 and 'data' in res.json():
                    replies += res.json()['data']

                    if 'meta' in res.json() and NEXT_TOKEN_KEY in res.json()['meta'] and res.json()['meta'][NEXT_TOKEN_KEY]:
                        params[NEXT_TOKEN_KEY] = res.json()['meta'][NEXT_TOKEN_KEY]
                    else:
                        logger.log("All replies have been retrieved")
                        return replies
                else:
                    logger.error(f"Request has been failed ({res.status_code})")
                    logger.error(f" - url: {REPLY_URL}")
                    logger.error(f" - content: {res.content}")
                    return replies
            except:
                logger.error(f"In getting replies of a conversation with id: {conversation_id}")
                return replies

    def _get_user(self, user_id, logger):
        try:
            params = {
                "user.fields": "id,username,created_at,name,location,public_metrics,url,protected,verified,description",
            }

            res = requests.get(USER_FMT_URL.format(user_id), params=params, headers=self.headers)
            time.sleep(15 * 60 / 900 + 1)  # Rate limit

            if res.status_code == 200 and 'data' in res.json():
                return res.json()['data']
            else:
                logger.error(f"Request has been failed ({res.status_code})")
                logger.error(f" - url: {USER_FMT_URL.format(user_id)}")
                logger.error(f" - content: {res.content}")
                return {}
        except:
            logger.error(f"In getting a user with id: {user_id}")
            return {}

    def _get_quotes(self, tweet_id, logger):
        params = {
            "max_results": MAX_RESULTS,
            "tweet.fields": "id,text,lang,geo,author_id,conversation_id,created_at,public_metrics,possibly_sensitive,referenced_tweets,reply_settings",
        }

        quotes = []

        while True:
            try:
                res = requests.get(QUOTE_FMT_URL.format(tweet_id), params=params, headers=self.headers, timeout=20)
                time.sleep(15 * 60 / 75 + 1)

                if res.status_code == 200 and 'data' in res.json():
                    quotes += res.json()['data']

                    if 'meta' in res.json() and NEXT_TOKEN_KEY in res.json()['meta'] and res.json()['meta'][NEXT_TOKEN_KEY]:
                        logger.log("Getting the next batch of quotes")
                        params['pagination_token'] = res.json()['meta'][NEXT_TOKEN_KEY]
                    else:
                        logger.log("All quotes have been retrieved")
                        return quotes
                else:
                    logger.error(f"Request has been failed ({res.status_code})")
                    logger.error(f" - url: {QUOTE_FMT_URL.format(tweet_id)}")
                    logger.error(f" - content: {res.content}")
                    return quotes
            except:
                logger.error(f"In getting quotes of a tweet with id: {tweet_id}")
                return quotes
