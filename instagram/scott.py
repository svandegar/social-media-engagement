import logging.config, mongoengine
from instagram import insta as ifn, functions as fn, mongo
from selenium import webdriver
from instagram.settings.settings import *
import click
from selenium.webdriver.chrome import options
import instagram.loggers


@click.command()
@click.option('--username', '-u', prompt=True, help='Scott username')
@click.option('--debug', is_flag=True, help='Set logger level to debug')
@click.version_option(version=VERSION)
def main(username: str, like_from_hashtags = True, debug=False):
    """
    Follow the Instagram routine defined by rules set for the account
    """
    username = username.title()

    # set logging config
    logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))
    logger = logging.getLogger(__name__)
    if debug:
        logging._handlers['console'].setLevel('DEBUG')
    logger.info('Start script')
    try:
        logger.debug('Environment is set to: ' + os.environ['ENVIRONMENT'])
    except KeyError:
        logger.debug('No ENVIRONMENT variable set. Default environment is PRODUCTION')

    logger.info('Version: '+ VERSION)

    # connect to MongoDB
    logger.debug('connect to MongoDB')
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

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

            # get proxy information
            if user.use_proxy:
                proxies = mongo.Proxies.objects(username=user.username).first()
                logger.debug('Got proxies information')
            else :
                proxies = None
                logger.debug('No proxies available')

            # open browser
            logger.debug('Open browser')
            chrome_options = options.Options()
            if proxies :
                logger.info('Connect through proxy ' + proxies.proxies['address'])
                chrome_options.add_argument('--proxy-server=%s:%s' %(proxies.proxies['address'],proxies.proxies['port']))
            else :
                logger.info('Connect without proxy')
            chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
            try :
                browser = webdriver.Chrome(options=chrome_options)
            except :
                try :
                    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=chrome_options)
                except Exception as e :
                    logger.error(e)
                    raise(e)

            # open Instagram session
            logger.debug('Open session')
            session = ifn.Session(credentials, browser, rules, history)
            logger.info('Connect to Instagram')
            session.connect()

            # scripts
            session.open_activity_feed()

            if like_from_hashtags:
                try:
                    logger.info('Start like_from_hashtags. Max posts to like: ' + str(session.rules.like['totalLikesMax']))
                    counters = session.like_from_hashtags(user_inputs.hashtags)
                    logger.info('End like_from_hashtags. Number of posts liked: ' + str(session.counter['post_liked']))

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

    logger.info('End of script')


main(sys.argv[1:])