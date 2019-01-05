from selenium import webdriver
import functions as fn
import insta_functions as ifn
from datetime import datetime
from settings import *
# debug imports
import importlib
# importlib.reload(ifn)
# importlib.reload(fn)

# get account credentials
credentials = fn.read_json_file(CREDENTIALS_FILE)

# get data from files
inputs = fn.read_json_file(INPUTS_FILE)
rules = fn.read_json_file(RULES_FILE)
outputs = fn.read_json_file(OUTPUTS_FILE)
metrics = fn.read_json_file(METRICS_FILE)

# track repeated actions
try :
    accounts_counter = fn.Counters(**outputs['accounts_counter'], global_count=True)
except KeyError :
    accounts_counter = fn.Counters(global_count=True)

try :
    no_repeat = dict(clicked_links = outputs['clicked_links'],accounts_counter = accounts_counter )
except KeyError :
    no_repeat = dict(clicked_links=[], accounts_counter=accounts_counter)

# open browser
option = webdriver.ChromeOptions()
option.add_argument(argument="--incognito")
browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

# activate logs
logger = fn.get_logger(__name__ + '|' + credentials['username'])
counter = fn.Counters()
logs = dict(logger = logger, counter = counter)

# create Instagram session
session = ifn.Session(**credentials, browser = browser, rules = rules, no_repeat = no_repeat, logs = logs)


# open browser
session.connect()

# open notifications
session.open_activity_feed()

# like pictures
session.like_from_hashtags(inputs['hashtags'])

# get followers list by an account
followers = session.get_followers_list_from('christian_ipina')

# write metrics in files
# TODO : save this in a database
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S%z")
session_metrics = {str(now) : session.logs['counter'].counters}
try :
    metrics[session.username].append(session_metrics)
except KeyError :
    metrics[session.username] = [session_metrics]
outputs = dict(clicked_links = no_repeat['clicked_links'],accounts_counter =  no_repeat['accounts_counter'].counters)
fn.write_json_file(outputs, OUTPUTS_FILE)
fn.write_json_file(metrics, METRICS_FILE)





""" Test zone """

import time
import copy
importlib.reload(ifn)
importlib.reload(fn)

session = ifn.Session(**credentials, browser = browser, rules = rules, no_repeat = no_repeat, logs = logs)

