"""
Deletes all tweets in your account in batches.

Twitter API v2 endpoints:

- User lookup (OAuth 1.0): GET /2/users/me
- Delete tweet (OAuth 1.0; limited to 50 reqs/day): DELETE /2/tweets/:id

Requirements:

- Request and download a backup of your twitter account
- Create an App in the Twitter developer portal
- Complete the user authentication setup for your App (for OAuth 1.0 support)
- Generate consumer keys for your app
- Generate authentication tokens to access your own account with Read and Write permissions
- Run the script daily (due to the delete endpoint rate limit)
"""

import argparse
import json
import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
from sre_constants import MAXGROUPS

import filetype
import requests
from requests_oauthlib import OAuth1
from notifypy import Notify


logger = logging.getLogger("twitter-delete-all")


NEXT_START_POSITION_FILE = Path.home() / '.twitter-delete-all-start-position'
MAX_DELETES_PER_RUN = 50


def get_oauth_keys() -> tuple[str]:
    # These are your app consumer keys (API Key and Secret)
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")

    # These are your personal Access Token and Secret
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    return consumer_key, consumer_secret, access_token, access_token_secret


def read_start_pos(filename: Path) -> int:
    try:
        return int(filename.read_text())
    except:
        return 0


def write_start_pos(filename: Path, new_pos: int):
    filename.write_text(str(new_pos))


def get_user_id(auth) -> str:
    response = requests.get("https://api.twitter.com/2/users/me", auth=auth)
    response_json = response.json()
    return response_json["data"]["id"]


def get_tweets_from_backup(twitter_backup: Path) -> list[dict]:
    with zipfile.ZipFile(twitter_backup) as zf:
        try:
            data = zf.read("data/tweets.js")
        except KeyError:
            print('ERROR: Did not find data/tweets.js in zip file')
            exit(2)

    # Remove the js assignment and keep the object list
    data = data.decode('utf-8').partition("=")[2]

    # Return sorted from newest to oldest (tweet ids are incremental)
    return sorted(json.loads(data), key=lambda t: int(t["tweet"]["id"]), reverse=True)


def delete_tweets_with_api(oauth_keys, tweets: list[dict], start_pos: int, num_deletes: int):
    # Create the OAuth 1.0 credentials
    oauth = OAuth1(
        oauth_keys[0],
        client_secret=oauth_keys[1],
        resource_owner_key=oauth_keys[2],
        resource_owner_secret=oauth_keys[3],
    )

    total_tweets = len(tweets)
    count = 0
    for i in range(start_pos, start_pos + num_deletes):
        if i > total_tweets - 1:
            break

        try:
            tweet_id = tweets[i]['tweet']['id']
            logger.debug(f"Deleting tweet '{tweet_id}")
            response = requests.delete(f"https://api.twitter.com/2/tweets/{tweet_id}", auth=oauth)
            response_json = response.json()
            deleted = response_json["data"]["deleted"]
        except Exception as e:
            logger.error(f"Error deleting tweet '{tweet_id}': {response.status_code}: {response.text}")
            break

        if not deleted:
            break

        count += 1

    return count


def notify_user(count):
    notification = Notify()
    notification.title = "Twitter Delete Script"
    notification.message = "No tweets deleted!" if not count else f"Deleted {count} tweets!"
    notification.send()


def main():
    parser = argparse.ArgumentParser(description="Deletes all your tweets using a Twitter backup")
    parser.add_argument("twitter_backup", type=Path, help="Path of the backup file (.zip)")
    args = parser.parse_args()

    if not args.twitter_backup.is_file():
        print(f"Error: invalid backup file '{args.twitter_backup}'")
        exit(1)

    kind = filetype.guess(args.twitter_backup)
    if not kind or kind.mime != "application/zip":
        print(f"Error: backup file must be of type zip '{args.twitter_backup}'")
        exit(1)

    oauth_keys = get_oauth_keys()
    if not all(oauth_keys):
        print("All four env variables must be defined: CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN and ACCESS_TOKEN_SECRET")
        exit(1)

    # 1) Get tweets from backup
    tweets = get_tweets_from_backup(args.twitter_backup)

    # 2) Read start position from file
    start_position = read_start_pos(NEXT_START_POSITION_FILE)
    
    # 3) Delete tweets forever using the API (limited to 50)
    count = delete_tweets_with_api(oauth_keys, tweets, start_position, MAX_DELETES_PER_RUN)

    # 4) Write next start position
    write_start_pos(NEXT_START_POSITION_FILE, start_position + count)
 
    # 5) Notify the user of the state
    notify_user(count)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG,
    #     format='%(asctime)s %(levelname)-8s %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S',
    #     filename="logging.txt", filemode='a')

    main()
