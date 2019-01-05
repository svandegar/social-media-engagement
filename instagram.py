import functions as fn
import insta_functions as ifn

from settings import *
import routines as rt

# get account credentials
credentials = fn.read_json_file(CREDENTIALS_FILE)

# get data from files
inputs = fn.read_json_file(INPUTS_FILE)
rules = fn.read_json_file(RULES_FILE)
history_file = fn.read_json_file(HISTORY_FILE)
metrics_file = fn.read_json_file(METRICS_FILE)

# repeated actions tracking
history = fn.Repeated_Actions_Tracker(history_file)

# activate logs
logger = fn.get_logger(__name__ + '|' + credentials['username'])
counter = fn.Counters()
logs = dict(logger=logger, counter=counter)

# launch daily routine
session = rt.daily_routine(credentials,inputs,rules,history, logs)

# get followers list by an account
# followers = session.get_followers_list_from()

# update metrics file
updated_metrics_file = fn.update_metrics_file(metrics_file,session)
fn.write_json_file(updated_metrics_file, METRICS_FILE)

# update history file
updated_history_file = history.get_history()
fn.write_json_file(updated_history_file, HISTORY_FILE)






""" Test zone """

import time
import copy
import importlib
importlib.reload(ifn)
importlib.reload(fn)

session = ifn.Session(**credentials, browser = browser, rules = rules, no_repeat = history, logs = logs)

