from selenium import webdriver
import insta_functions as ifn
from settings.settings import *
import functions as fn
import mongo
import mongoengine


def daily_routine(insta_username: str, username: str, connect=True):
    """

    :param credentials: user config
    :param connect: if connects = True, open a new session. If not, uses the already opened
    :return:
    """

    # get config
    config = fn.read_json_file(CONFIG_FILE)

    # get inputs
    mongoengine.connect(host=config['databases']['Mongo'])
    user_inputs = mongo.UserInputs.objects(insta_username=insta_username).first()
    rules = mongo.Rules.objects(insta_username=insta_username).first()
    history_document = mongo.History.objects(insta_username=insta_username).first()

    # inputs = fn.get_data_from_files(USER_INPUTS_FILE, RULES_FILE, HISTORY_FILE, METRICS_FILE)

    # set actions tracking
    history = fn.Repeated_Actions_Tracker(history_document)

    # activate logs
    logger = fn.get_logger(__name__ + '|' + insta_username)
    counter = fn.Counters()
    logs = dict(logger=logger, counter=counter)

    # open browser
    option = webdriver.ChromeOptions()
    option.add_argument(argument="--incognito")
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=option)

    # create session
    session = ifn.Session(config['credentials'][insta_username], browser, rules, history, logs)

    # connect
    if connect: session.connect()

    # open notifications
    session.open_activity_feed()

    # like pictures
    session.like_from_hashtags(user_inputs.hashtags)

    # save session metrics
    try :
        Links_opened = session.logs['counter'].counters['Links_opened']
    except KeyError:
        logger.debug('No Links_opened to log')
        Links_opened = 0
    try:
        New_post_opened = session.logs['counter'].counters['New_post_opened']
    except KeyError:
        logger.debug('No New_post_opened to log')
        New_post_opened = 0
    try:
        Post_liked = session.logs['counter'].counters['Post_liked']
    except KeyError:
        logger.debug('No Post_liked to log')
        Post_liked =0
    try:
        Post_not_liked = session.logs['counter'].counters['Post_not_liked']
    except KeyError:
        logger.debug('No Post_not_liked to log')
        Post_not_liked = 0
    metrics = mongo.Metrics(username=username,
                                 insta_username=session.username,
                                 datetime=session.start_time,
                                 Sleeptime=session.logs['counter'].counters['Sleeptime'],
                                 Connection=session.logs['counter'].counters['Connection'],
                                 Links_opened=Links_opened,
                                 New_post_opened=New_post_opened,
                                 Post_liked=Post_liked,
                                 Post_not_liked=Post_not_liked,
                                 execution_time=session.logs['counter'].counters['execution_time'],
                                 )
    metrics.save()

    # update history
    new_history = history.get_history()
    mongo.History.objects(insta_username=insta_username).first().modify(clicked_links = new_history.clicked_links,
                                                                        accounts_counter = new_history.accounts_counter)

    # new_history.modify(username = session.username,
    #                    insta_username = session.username
    #                     clicked_links = new_history.clicked_links,
    #                     accounts_counter = new_history.accounts_counter)

    # updated_metrics_file = fn.update_metrics_file(metrics, session)
    # fn.write_json_file(updated_metrics_file, METRICS_FILE)

    # update history file
    # updated_history_file = history.get_history()
    # fn.write_json_file(updated_history_file, HISTORY_FILE)

    return session
