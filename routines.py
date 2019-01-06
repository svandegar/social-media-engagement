from selenium import webdriver
import insta_functions as ifn
from settings.settings import *
import functions as fn

def daily_routine(credentials: dict, connect = True):
    """

    :param credentials: user credentials
    :param connect: if connects = True, open a new session. If not, uses the already opened
    :return:
    """

    # get inputs
    inputs = fn.get_data_from_files(USER_INPUTS_FILE, RULES_FILE, HISTORY_FILE, METRICS_FILE)

    # set actions tracking
    history = fn.Repeated_Actions_Tracker(inputs['history_file'])

    # activate logs
    logger = fn.get_logger(__name__ + '|' + credentials['username'])
    counter = fn.Counters()
    logs = dict(logger=logger, counter=counter)

    # open browser
    option = webdriver.ChromeOptions()
    option.add_argument(argument="--incognito")
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

    # create session
    session = ifn.Session(**credentials,
                          browser=browser,
                          rules=inputs['rules_file'],
                          history=history,
                          logs=logs)

    # connect
    if connect : session.connect()

    # open notifications
    session.open_activity_feed()

    # like pictures
    session.like_from_hashtags(inputs['user_inputs_file']['hashtags'])

    # update metrics file
    updated_metrics_file = fn.update_metrics_file(inputs['metrics_file'], session)
    fn.write_json_file(updated_metrics_file, METRICS_FILE)

    # update history file
    updated_history_file = history.get_history()
    fn.write_json_file(updated_history_file, HISTORY_FILE)

    return session