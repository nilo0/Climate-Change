import json, sys, random, requests
from climate_change_nc import twitter
from datetime import datetime, timedelta
import git, shutil, glob


TMP_DIR = "/path/to/tmp/dir"
LOCAL_GIT_REPO = "/path/to/local/git/repo"


def info(title, message):
    url = "https://hooks.slack.com/services/XXXXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
    title = (title)
    message = (message)

    slack_data = {
        "username": "ClimateChangeBot",
        "icon_emoji": ":satellite:",
        "channel" : "#alert",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }

    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)


def log_last_lines(date):
    fname = f"${TMP_DIR}/log/{date.strftime('%y%m%d')}.log"
    with open(fname) as f:
        lines = f.readlines()
        return "".join(lines[-20:])


def count_substring(path, substring):
    substring_counts = -1
    with open(path, 'r') as file:
        content = file.read()
        substring_count = content.count(substring)
    return substring_count


def count_file(path):
    with open(path, 'r') as file:
        line_count = 0
        for line in file:
            line_count += 1
    return line_count


def count_tweets(date):
    log_file = f"${TMP_DIR}/log/{date.strftime('%y%m%d')}.log"
    tweets_file = f"${TMP_DIR}/data/{date.strftime('%Y%m%d')}_tweets.csv"
    replies_file = f"${TMP_DIR}/data/{date.strftime('%Y%m%d')}_replies.csv"
    quotes_file = f"${TMP_DIR}/data/{date.strftime('%Y%m%d')}_quotes.csv"
    users_file = f"${TMP_DIR}/data/{date.strftime('%Y%m%d')}_users.csv"

    return {
        "tweets": count_file(tweets_file),
        "replies": count_file(replies_file),
        "quotes": count_file(quotes_file),
        "users": count_file(users_file),
        "errors": count_substring(log_file, "ERROR"),
    }


bearer = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

date = datetime.now() - timedelta(5)

try:
    api = twitter.MyTwitter(bearer)
    info("New day, new run", f"Downloading tweets of {date.strftime('%y-%m-%d')}...")

    api.get_daily_tweets(date)

    info("Successfully finished", f"Copying new files...")


    data_dir = f"{LOCAL_GIT_REPO}/data"
    source_data_files = f"${TMP_DIR}/data/{date.strftime('%Y%m%d')}_*"
    for f in glob.glob(f"${TMP_DIR}/data/{date.strftime('%Y%m%d')}_*"):
        shutil.copy(f, f"{data_dir}/data")
    shutil.copy(f"${TMP_DIR}/log/{date.strftime('%y%m%d')}.log", f"{data_dir}/log")

    info("Successfully copied", "Commiting new files")
    repo = git.Repo(git_repo)
    repo.git.add('.')
    files = repo.git.status('--porcelain')
    repo.git.commit('-m', f"{date.strftime('%y%m%d')} data", author='Niloofar Rahmati <nil.rahmati@gmail.com>')

    info("Successfully commited", f"Pushing new files.\nCommited files:\n{files}")
    repo.git.push('origin', 'main')

    counts = count_tweets(date)
    info("Summary", f"""
 # tweets: {counts['tweets']}
 # replies: {counts['replies']}
 # quotes: {counts['quotes']}
 # users: {counts['users']}
 # ERRORS: {counts['errors']}
     """)

    info("All nicely done", ":heart:")

except Exception as e:
    info("[error] Something went wrong.", f"{log_last_lines(date)}\n{e}")

