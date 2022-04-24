import json
import time
from datetime import datetime
from typing import List, Tuple

import pandas as pd
import tweepy

QUERY_CHAR_LIMIT = 1024
EXCLUDE_RETWEETS = ' -is:retweet'


def _splitter_helper(ls: List[Tuple[str, datetime]], char_limit: int,
                     earliest_start: datetime) -> List[Tuple[List[str], datetime]]:
    # init step
    res = []
    sublist = []
    sublist_char_length = 0
    sublist_timestamp = datetime.utcnow()

    for kw, t in ls:
        # 6 to account for ' OR' to be prepended to each string when constructing the query, as well as the quotes
        entry_length = len(kw) + 6

        # if sublist can't contain the new item
        if sublist_char_length + entry_length + len(EXCLUDE_RETWEETS) > char_limit:
            # print(sublist_char_length)
            res.append((sublist, sublist_timestamp))

            sublist = []
            sublist_char_length = 0
            sublist_timestamp = datetime.utcnow()

        # timestamp should be the earliest, while not earlier than `earliest_start`
        if sublist_timestamp > earliest_start:
            if t is None or pd.isna(t):
                sublist_timestamp = earliest_start
            else:
                sublist_timestamp = max(min(sublist_timestamp, t), earliest_start)

        # append kw to the sublist and add its corresponding entry length to sublist_char_length
        sublist.append(kw)
        sublist_char_length += entry_length

    # final step
    # print(sublist_char_length)
    res.append((sublist, sublist_timestamp))

    return res


def splitter(kw_list: List[Tuple[str, datetime]], char_limit: int,
             earliest_start: datetime) -> List[Tuple[List[str], str]]:
    """
    Splits a list of accounts into smaller slices of max size `char_limit`.

    :param kw_list: keywords list
    :param char_limit: limit of number of characters per slice
    :param earliest_start: earliest start date for tweet fetching
    :return: a list containing slices of keywords
    """

    none_time_list = [e for e in kw_list if e[1] is None or pd.isna(e[1])]

    print('none', len(none_time_list))
    if len(none_time_list) != 0:
        res = _splitter_helper(none_time_list, char_limit, earliest_start)
    else:
        res = []

    sorted_by_timestamp = sorted([e for e in kw_list if not (e[1] is None or pd.isna(e[1]))],
                                 key=lambda x: x[1],
                                 reverse=True)

    print('sorted', len(sorted_by_timestamp))

    if len(sorted_by_timestamp) != 0:
        res += _splitter_helper(sorted_by_timestamp, char_limit, earliest_start)

    return res


def _create_query(keyword_list: List[str]) -> str:
    """
    Creates a query using keywords.

    For input:
        keyword_list = ["foo", "bar"]

    returns:
        "foo OR bar"

    :param keyword_list: list of keywords
    :return: a valid query for the Twitter API
    """
    query = '("' + '" OR "'.join(keyword_list) + '")' + EXCLUDE_RETWEETS
    return query


def init() -> str:
    f = open('token.json')
    token = json.load(f)['bearer_token']
    return token


def create_client(token: str) -> tweepy.Client:
    # https://docs.tweepy.org/en/latest/client.html#client
    client = tweepy.Client(bearer_token=token, return_type=dict)
    return client


def _get_tweets_count_page(client: tweepy.Client, query: str, start_time: datetime = None, end_time: datetime = None,
                           next_token: str = None):
    count = client.get_all_tweets_count(query=query,
                                        start_time=start_time,
                                        end_time=end_time,
                                        granularity='day',
                                        next_token=next_token,
                                        )
    return count


def _get_tweets_page(client: tweepy.Client, query: str, start_time: datetime = None, end_time: datetime = None,
                     next_token: str = None):
    # https://docs.tweepy.org/en/latest/client.html#search-tweets

    tweets = client.search_all_tweets(query=query,
                                      start_time=start_time,
                                      end_time=end_time,
                                      max_results=100,
                                      expansions=['author_id'],
                                      tweet_fields=['id', 'text', 'attachments', 'author_id', 'context_annotations',
                                                    'conversation_id', 'created_at', 'entities', 'geo',
                                                    'in_reply_to_user_id', 'lang',
                                                    # 'non_public_metrics', 'organic_metrics', 'promoted_metrics',
                                                    'public_metrics', 'referenced_tweets', 'reply_settings', 'source',
                                                    'withheld'],
                                      user_fields=['id', 'name', 'username', 'created_at', 'description', 'entities',
                                                   'location', 'pinned_tweet_id', 'profile_image_url', 'protected',
                                                   'public_metrics', 'url', 'verified', 'withheld'],
                                      next_token=next_token,
                                      )

    return tweets


def get_tweets(client: tweepy.Client, keywords: List[str], start_time: datetime = None,
               end_time: datetime = None) -> Tuple[List[dict], List[dict], datetime]:
    query = _create_query(keyword_list=keywords)

    print('query length', len(query))
    print(query)
    print(start_time)
    print(end_time)

    count_next_token = None
    count = 0
    while True:
        page_counts = _get_tweets_count_page(client=client,
                                             query=query,
                                             start_time=start_time,
                                             end_time=end_time,
                                             next_token=count_next_token)

        count += page_counts['meta']['total_tweet_count']

        if not page_counts['meta'].get('next_token'):
            break
        else:
            count_next_token = page_counts['meta'].get('next_token')

    print(count)

    next_token = None
    i = 0

    tweets = []
    users = []
    while True:
        page = _get_tweets_page(client=client,
                                query=query,
                                start_time=start_time,
                                end_time=end_time,
                                next_token=next_token)

        time.sleep(4)

        tweets += page['data']
        users += page['includes']['users']

        if len(tweets) // 1000 == i:
            i += 1
            print(len(tweets), '/', count)

        if not page['meta'].get('next_token'):
            break
        else:
            next_token = page['meta'].get('next_token')

    return tweets, users, pd.to_datetime(max(e['created_at'] for e in tweets)).tz_localize(None)


def _get_users_batch(client: tweepy.Client, ids: List[str]):
    # https://docs.tweepy.org/en/latest/client.html#tweepy.Client.get_users

    users = client.get_users(ids=ids,
                             user_fields=','.join(
                                 ['created_at', 'description', 'entities', 'id', 'location', 'name', 'pinned_tweet_id',
                                  'profile_image_url', 'protected', 'public_metrics', 'url', 'username', 'verified',
                                  'withheld']),
                             )

    return users


def get_user_data(client: tweepy.Client, ids: List[str]):
    users = []

    n = len(ids)
    for i in range(0, n, 100):
        if i // 1000 == i:
            print(i, '/', n)
        _ids = ids[i:min(i + 100, n)]
        try:
            _users = _get_users_batch(client=client,
                                      ids=_ids)
        except:
            print('something bad happened', i/100 + 1)
        users += _users['data']
        time.sleep(3.1)

    return users


# https://docs.tweepy.org/en/latest/client.html#tweepy.Client.get_users_tweets