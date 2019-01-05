from selenium import webdriver
import functions as fn
import insta_functions as ifn
from settings import *

def daily_routine(credentials: dict, inputs : dict, rules : dict, history, logs ):

    # open browser
    option = webdriver.ChromeOptions()
    option.add_argument(argument="--incognito")
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

    # create Instagram session
    session = ifn.Session(**credentials, browser=browser, rules=rules, history=history, logs=logs)

    # open browser
    session.connect()

    # open notifications
    session.open_activity_feed()

    # like pictures
    session.like_from_hashtags(inputs['hashtags'])

    return session