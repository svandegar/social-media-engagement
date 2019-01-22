import logging.config, mongoengine
from instagram import insta as ifn, functions as fn, mongo
from selenium import webdriver
from instagram.settings.settings import *
import click
from selenium.webdriver.chrome import options


@click.command()
@click.option('--username', '-u', prompt=True)
@click.option('--debug', default=False)
@click.option('--connect', '-c', default=True)
@click.option('--like_from_hashtags', '-h', prompt=True)
def main(username: str, like_from_hashtags: str, get_followers = 'No', connect=False,  debug=False):
    username = username.title()
    # set logging config
    logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))
    logger = logging.getLogger(__name__)
    if debug:
        logging._handlers['console'].setLevel('DEBUG')
    logger.info('Start script')
    try:
        logger.debug('Environment = ' + os.environ['ENVIRONMENT'])
        logger.debug('Environment is set to: ' + os.environ['ENVIRONMENT'])
    except KeyError:
        logger.debug('No ENVIRONMENT variable set')

    # connect to MongoDB
    logger.debug('connect to MongoDB')
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

    # open browser
    logger.debug('open browser')
    chrome_options = options.Options()
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=chrome_options)

    # check user credentials
    # TODO : check user credentials
    user = mongo.Users.objects(username=username).first()
    try:
        if not user:
            raise ValueError('This user is not existing: ' + username)
    except ValueError as e:
        logger.warning(e)
    else:
        # get account information
        logger.debug('get account information')
        account = mongo.Accounts.objects(username=user.username).first()
        try:
            if account:
                credentials = dict(username=account.insta_username, password=account.insta_password)
            else:
                raise ValueError('No account found for the user: ' + str(username))
        except ValueError as e:
            logger.warning(e)
        else:
            # get user rules, history and user inputs
            logger.debug('get user rules, history and user_inputs')
            rules = mongo.Rules.objects(username=username).first()
            history = mongo.History.objects(username=username).first()
            user_inputs = mongo.UserInputs.objects(username=username).first()

            # open session
            logger.debug('open session')
            session = ifn.Session(credentials, browser, rules, history)

            if connect:  # while testing, no need to reconnect every time
                logger.info('connect to Instagram')
                session.connect()

            # scripts
            if like_from_hashtags.lower() in ['true', 't', 'y', 'yes', 'oui', 'ok']:
                try:
                    logger.info('Start like_from_hashtags')
                    counters = session.like_from_hashtags(user_inputs.hashtags)
                    logger.info('End like_from_hashtags')

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
                    logger.info('Metrics saved')

                    # update history
                    mongo.History.objects(insta_username=session.username).first().modify(
                        clicked_links=session.clicked_links,
                        accounts_counter=session.accounts_counter.get_list())
                    logger.info('History saved')

                except:
                    logger.error('like_from_hashtags ended unexpectedly')

            if get_followers.lower() in ['true', 't', 'y', 'yes', 'oui', 'ok']:
                # TODO : add the get_followers function usage here
                pass

    logger.info('End of script')


main(sys.argv[1:])

