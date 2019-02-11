from instagram.settings.settings import *
from instagram import mongo, functions as fn
import mongoengine


def get_metrics(username=None,
                insta_username=None,
                date_from=None,
                date_to=None,
                aggregate=None,
                aggregate_on=None,
                **kwargs):
    """
    get all the metrics corresponding to the filters
    :param username: username
    :param insta_username: instagram username
    :param date_from: included in the results
    :param date_to: excluded from the results
    :param aggregate: string : 'sum' or 'count
    :param aggregate_on: field to aggregate the data on. Mandatory if aggregate is set
    :param kwargs: additional filters to the query
    :return: list of mongo.Metrics objects
    """
    query_filter = {}
    if not username and not insta_username:
        raise ValueError('username or insta_username must be specified')
    if username: query_filter['username'] = username
    if insta_username: query_filter['insta_username'] = insta_username
    if date_from: query_filter['datetime__gte'] = date_from
    if date_to: query_filter['datetime__lt'] = date_to
    if kwargs: query_filter.update(kwargs)
    if aggregate == 'sum':
        if aggregate_on:
            result = mongo.Metrics.objects(**query_filter).sum(aggregate_on)
        else:
            raise ValueError('aggregate_on needs to ne defined if aggregate is defined')
    elif aggregate == 'count':
        if aggregate_on:
            result = mongo.Metrics.objects(**query_filter).count(aggregate_on)
        else:
            raise ValueError('aggregate_on needs to ne defined if aggregate is defined')
    else:
        result = mongo.Metrics.objects(**query_filter)

    return result


def summarize(list: list,
              username=None,
              insta_username=None,
              date_from=None,
              date_to=None):
    """
    return the sum of the values in stored in the database
    :param list: mandatory list of strings, corresponding to the field names to sum
    :param username: username
    :param insta_username: instagram username
    :param date_from: included in the results
    :param date_to: excluded from the results
    :return: dict {field_name : sum}
    """
    if not username and not insta_username:
        raise ValueError('username or insta_username must be specified')
    summary = {}
    for value in list:
        summary[value] = get_metrics(username=username,
                                     insta_username=insta_username,
                                     date_from=date_from,
                                     date_to=date_to,
                                     aggregate='sum',
                                     aggregate_on=value)
    return summary


def get_history(username=None, insta_username=None):
    if not username and not insta_username:
        raise ValueError('username or insta_username must be specified')
    query_filter = {}
    if username: query_filter['username'] = username
    if insta_username: query_filter['insta_username'] = insta_username
    result = mongo.History.objects(**query_filter).first()
    return result


def get_accounts_visited(username=None, insta_username=None):
    if not username and not insta_username:
        raise ValueError('username or insta_username must be specified')
    history = get_history(username=username, insta_username=insta_username)
    accounts_counter = history.accounts_counter
    accounts = [x['name'] for x in accounts_counter]
    return accounts


def get_followers_count(username=None,
                        insta_username=None,
                        date_from=None,
                        date_to=None,
                        **kwargs):
    if not username and not insta_username:
        raise ValueError('username or insta_username must be specified')
    metrics = get_metrics(username=username,
                          insta_username=insta_username,
                          date_from=date_from,
                          date_to=date_to,
                          **kwargs)
    followers_count = {}
    for document in metrics:
        followers_count[document.datetime] = document.followers
    return followers_count


def get_followers(insta_username=None,
                  date_from=None,
                  date_to=None,
                  **kwargs):
    if not username and not insta_username:
        raise ValueError('username or insta_username must be specified')
    query_filter = {}
    if insta_username: query_filter['account'] = insta_username
    if date_from: query_filter['datetime__gte'] = date_from
    if date_to: query_filter['datetime__lt'] = date_to
    if kwargs: query_filter.update(kwargs)
    followers = mongo.Followers.objects(**query_filter).order_by('-id').first()
    return followers.followers


""" Test functions """

mongoengine.connect(host="mongodb+srv://SM-E:vPo7QS7J8lDaesvu@social-media-engagement-khrv2.mongodb.net/insta-prod?retryWrites=true")

username = 'Julie'
date_from = None
insta_username = 'julie_une_fois'
metrics_list = ['sleeptime', 'connection', 'links_opened', 'new_post_opened', 'post_liked', 'post_not_liked', 'execution_time']

summary = summarize(metrics_list, username=username, date_from=date_from)
#
#
# history = get_history(username=username)
#
accounts = get_accounts_visited(insta_username=insta_username)[1:]
#
# followers_count = get_followers_count(username=username)

followers = get_followers(insta_username=insta_username)

""" Compare followers to accounts """

common = list(set(followers) & set(accounts))