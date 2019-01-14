import logging.config, sys, mongoengine
from instagram import insta as ifn, functions as fn, mongo
from selenium import webdriver
from instagram.settings.settings import *
import click

# set logging config
logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))

@click.command()
@click.argument('username')
@click.option('--connect','-c')
@click.option('--like_from_hashtags')
def main(username:str,connect=False,like_from_hashtags=False):

    logger = logging.getLogger(__name__)
    logger.info('start script')
    try :
        logger.debug('Environment = ' + os.environ['ENVIRONMENT'])
    except KeyError:
        logger.debug('No ENVIRONMENT variable set')

    # connect to MongoDB
    logger.debug('connect to MongoDB')
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

    # open browser
    logger.debug('open browser')
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(CHROMEDRIVER_PATH
                               # , options=chrome_options
                               )

    # get account information
    logger.debug('get account information')
    account = mongo.Accounts.objects(username=username).first()
    try :
        if account:
            credentials = dict(username=account.insta_username, password=account.insta_password)
        else :
            raise ValueError('No account found for the username: ' + str(username))
    except ValueError as e:
        logger.error(e)
    else :
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
    logger.info('End of script')


main(sys.argv[1:])
