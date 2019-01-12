import mongo
import functions as fn
import insta as ifn
from settings.settings import *
import logging.config
from selenium import webdriver
import mongoengine

logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))


def main(username: str,connect = True, like_from_hashtags=False):
    logger = logging.getLogger(__name__)

    # connect to MongoDB
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

    # open browser
    logger.debug('open browser')
    browser = webdriver.Chrome(CHROMEDRIVER_PATH)

    # get account information
    logger.debug('get account information')
    account = mongo.Accounts.objects(username=username).first()
    credentials = dict(username=account.insta_username, password=account.insta_password)

    # get user rules, history and user inputs
    logger.debug('get user rules, history and user_inputs')
    rules = mongo.Rules.objects(username=username).first()
    history = mongo.History.objects(username=username).first()
    user_inputs = mongo.UserInputs.objects(username=username).first()

    # open session
    logger.debug('open session')
    session = ifn.Session(credentials, browser, rules, history)
    if connect : session.connect() #while testing, no need to reconnect every time

    # scripts
    if like_from_hashtags:
        logger.info('Start like_from_hashtags')
        counters = session.like_from_hashtags(user_inputs.hashtags)
        logger.info('End like_from_hastags')

        # save like metrics
        metrics = mongo.Metrics(username=username,
                                insta_username=session.username,
                                datetime=session.start_time,
                                sleeptime=counters['sleeptime'],
                                connection=counters['connection'],
                                links_opened=counters['links_opened'],
                                new_post_opened=counters['new_post_opened'],
                                post_liked=counters['post_liked'],
                                post_not_liked=counters['post_not_liked'],
                                execution_time=counters['execution_time'],
                                )
        metrics.save()

        # update history
        mongo.History.objects(insta_username=session.username).first().modify(
            clicked_links=session.clicked_links,
            accounts_counter=session.accounts_counter.get_list())


if __name__ == "__main__":
    main('username')
