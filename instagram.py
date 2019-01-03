from selenium import webdriver
import functions as fn
import insta_connector as ic
import importlib
# importlib.reload(ic)
# importlib.reload(fn)
from datetime import datetime
from settings import *

# get account credentials
credentials = fn.read_json_file(CREDENTIALS_FILE)

# get data from files
inputs = fn.read_json_file(INPUTS_FILE)
rules = fn.read_json_file(RULES_FILE)
outputs = fn.read_json_file(OUTPUTS_FILE)
metrics = fn.read_json_file(METRICS_FILE)

# track repeated actions
accounts_counter = fn.Counters(**outputs['accounts_counter'])
no_repeat = dict(clicked_links = outputs['clicked_links'],accounts_counter = accounts_counter )

# open browser
option = webdriver.ChromeOptions()
option.add_argument(argument="--incognito")
browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

# activate logs
logger = fn.get_logger(__name__ + '|' + credentials['username'])
counter = fn.Counters()
logs = dict(logger = logger, counter = counter)

# open Instagram session
session = ic.Session(**credentials,browser = browser, rules = rules,  no_repeat = no_repeat,logs = logs)
session.connect()

# like pictures
session.like_from_hashtags(inputs['hashtags'])

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