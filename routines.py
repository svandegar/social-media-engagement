from selenium import webdriver
import insta_functions as ifn
from settings.settings import *
import functions as fn
import mongo
import mongoengine

def daily_routine(insta_user: str, connect = True):
    """

    :param credentials: user config
    :param connect: if connects = True, open a new session. If not, uses the already opened
    :return:
    """

    # get config
    config = fn.read_json_file(CONFIG_FILE)

    #get inputs
    mongoengine.connect(host=config['databases']['Mongo'])
    user_inputs = mongo.UserInputs.objects(insta_user = insta_user)
    rules = mongo.Rules.objects(insta_user = insta_user)
    history = mongo.History.objects(insta_user = insta_user)
    # metrics = mongo.Metrics.objects(insta_user = insta_user)


    # inputs = fn.get_data_from_files(USER_INPUTS_FILE, RULES_FILE, HISTORY_FILE, METRICS_FILE)


    # set actions tracking
    history = fn.Repeated_Actions_Tracker(history)

    # activate logs
    logger = fn.get_logger(__name__ + '|' + config['credentials']['username'])
    counter = fn.Counters()
    logs = dict(logger=logger, counter=counter)

    # open browser
    option = webdriver.ChromeOptions()
    option.add_argument(argument="--incognito")
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

    # create session
    session = ifn.Session(config['credentials'],browser,rules,history,logs)

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