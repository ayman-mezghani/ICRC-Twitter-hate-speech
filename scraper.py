import tweepy
import json
from typing import List
from datetime import datetime

QUERY_CHAR_LIMIT = 1024


def _splitter_helper(ls: List[str], char_limit: int) -> List[List[str]]:
    # init step
    res = []
    sublist = []
    sublist_char_length = 0

    for kw in ls:
        # 3 to account for ' OR' to be prepended to each string when constructing the query
        entry_length = len(kw) + 3

        # if sublist can't contain the new item
        if sublist_char_length + entry_length > char_limit:
            print(sublist_char_length)
            res.append(sublist)

            sublist = []
            sublist_char_length = 0

        # append account_id to the sublist and add its corresponding entry length to sublist_char_length
        sublist.append(kw)
        sublist_char_length += entry_length

    # final step
    print(sublist_char_length)
    res.append(sublist)

    return res


def splitter(kw_list: List[str], char_limit: int) -> List[List[str]]:
    """
    Splits a list of accounts into smaller slices of max size `char_limit`.

    :param kw_list: keywords list
    :param char_limit: limit of number of characters per slice
    :return: a list containing slices of keywords
    """

    res = []

    if len(kw_list) != 0:
        res += _splitter_helper(kw_list, char_limit)

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
    query = ' OR '.join(keyword_list)
    return query


def init() -> str:
    f = open('token.json')
    token = json.load(f)['bearer_token']
    return token


def create_client(token: str) -> tweepy.Client:
    # https://docs.tweepy.org/en/latest/client.html#client
    client = tweepy.Client(bearer_token=token, return_type=dict)
    return client


def get_tweets(client: tweepy.Client, keywords: List[str], start_time: datetime, end_time: datetime):
    # https://docs.tweepy.org/en/latest/client.html#search-tweets
    query = _create_query(keyword_list=keywords)

    tweets = client.search_all_tweets(query=query,
                                      start_time=start_time,
                                      end_time=end_time,
                                      max_results=500,
                                      tweet_fields=','.join(
                                          ['id', 'text', 'attachments', 'author_id', 'context_annotations',
                                           'conversation_id', 'created_at', 'entities', 'geo', 'in_reply_to_user_id',
                                           'lang',
                                           # 'non_public_metrics', 'organic_metrics', 'promoted_metrics',
                                           'public_metrics', 'referenced_tweets', 'reply_settings', 'source',
                                           'withheld']),
                                      user_fields=','.join(
                                          ['id', 'name', 'username', 'created_at', 'description', 'entities',
                                           'location', 'pinned_tweet_id', 'profile_image_url', 'protected',
                                           'public_metrics', 'url', 'verified', 'withheld']),
                                      )

    return tweets
