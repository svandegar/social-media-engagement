from selenium import webdriver
import functions as fn
import insta_connector as ic
import importlib
importlib.reload(ic)
importlib.reload(fn)
from datetime import datetime
from settings import *

# get account credentials
credentials = fn.read_json_file(CREDENTIALS_FILE)

# get data from files
inputs = fn.read_json_file(INPUTS_FILE)
rules = fn.read_json_file(RULES_FILE)
outputs = fn.read_json_file(OUTPUTS_FILE)
metrics = fn.read_json_file(METRICS_FILE)

# open browser
option = webdriver.ChromeOptions()
option.add_argument(argument="--incognito")
browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

# activate logs
logger = fn.get_logger(__name__ + '|' + credentials['username'])
counter = fn.Counters()
logs = dict(logger = logger, counter = counter)

# open Instagram session
session = ic.Session(**credentials,browser = browser, rules = rules, logs = logs)
session.connect()

# like pictures
now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
metrics[str(now)] = session.like(inputs['hashtags'],outputs['clicked_links']).counters
fn.write_json_file(outputs, OUTPUTS_FILE)
fn.write_json_file(metrics,METRICS_FILE)