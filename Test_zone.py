import functions as fn
import insta_functions as ifn
from settings.settings import *
import routines as rt

insta_username = 'all_you_need_is_code'
username = 'Scott'

# launch daily routine
session = rt.daily_routine(username = username, insta_username = insta_username, connect=True)

# get followers list by an account
followers = session.get_followers_list_from()




""" Test zone """

import importlib
importlib.reload(ifn)
importlib.reload(fn)

# import dns
from pymongo import MongoClient
import mongoengine
import mongo
import functions as fn
import datetime
# importlib.reload(mongo)

# get  config
config = fn.read_json_file(CONFIG_FILE)

mongoengine.connect(host = config['databases'] )


metrics = mongo.Metrics(
    username='user',
    insta_username = 'insta_user',
    datetime = datetime.datetime.now()
)

metrics.save()






history_1 = mongo.History(
    username = 'user1',
    insta_username = 'insta_user1',
    clicked_links = ['link1','link2']
)

# inputs = fn.get_data_from_files(USER_INPUTS_FILE, RULES_FILE, HISTORY_FILE, METRICS_FILE)
# user_inputs = inputs['user_inputs_file']
# rules = inputs['rules_file']
# history = inputs['history_file']
# metrics = inputs['metrics_file']
#
# userInputs_db = mongo.UserInputs(**user_inputs)
# history2_db = mongo.History(**history2)
# metrics_db = mongo.Metrics(**metrics)

time = dict(
    timeout = 20,
    delay_min = 2,
    delay_max = 8
)
limits =dict(
    posts_per_hashtage_min = 6,
    posts_per_hashtage_max = 30,
    total_likes_max = 100,
    likes_per_account = 2,
    probability = 0.8
)

rules_db = mongo.Rules(
    username = 'Scott',
    insta_username = 'all_you_need_is_code',
    likes_per_account= 2,
    probability = 8/10,
    general = time,
    connection= time,
    get_followers = time,
    like = limits

)
# result = history2_db.save()
#
#
#
# print(result.id)

test = mongo.Users(username = 'jean',
                   insta_username = 'jean_petit',
                   email_address = 'jean@mail.com')

test.save()


history = mongo.History.objects(insta_username='all_you_need_is_code')

metrics = mongo.Metrics(
    username='user',
insta_username = 'insta_user',
datetime = datetime.datetime.now()
)