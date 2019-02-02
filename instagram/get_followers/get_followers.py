from instagram import functions as fn, insta, mongo, loggers, proxy
import mongoengine
import logging
import logging.config
from selenium import webdriver
from instagram.settings.settings import *
from selenium.webdriver.chrome import options

logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))


def get_followers_users(bot_username,debug=False ):

    # configure logging
    logger = logging.getLogger(__name__)
    logger.addFilter(loggers.ContextFilter())
    if debug:
        logging._handlers['console'].setLevel('DEBUG')
    logger.info('Start script')
    try:
        logger.debug('Environment is set to: ' + os.environ['ENVIRONMENT'])
    except KeyError:
        logger.debug('No ENVIRONMENT variable set. Default environment is PRODUCTION')

    logger.info('Version: ' + VERSION)

    # connect to MongoDB
    logger.debug('Connect to MongoDB')
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

    # get user credentials and rules
    user = mongo.Users.objects(username=bot_username).first()
    account = mongo.Accounts.objects(username=user.username).first()
    credentials = dict(username=account.insta_username, password=account.insta_password)
    rules = mongo.Rules.objects(username=user.username).first()

    # get proxy information
    if user.use_proxy:
        proxies = mongo.Proxies.objects(username=user.username).first()
        logger.debug('Got proxies information')

    else:
        proxies = None
        logger.debug('No proxies set for this user')

    # open browser
    logger.debug('Open browser')
    chrome_options = options.Options()
    if proxies:
        logger.info('Connect through proxy ' + proxies.proxies['address'])

        # build chrome extension for proxy authentication
        chrome_extension = proxy.build_chrome_ext(proxies)
        chrome_options.add_extension(chrome_extension)
    else:
        logger.info('Connect without proxy')

    # set language to English
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

    try:
        browser = webdriver.Chrome(options=chrome_options)
    except:
        try:
            browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=chrome_options)
        except Exception as e:
            logger.error(e)
            raise (e)

    # open Instagram session
    logger.debug('Open session')
    session = insta.Session(credentials, browser, rules)
    logger.info('Connect to Instagram')
    session.connect()

    # get accounts list
    accounts = mongo.Accounts.objects()
    accounts_list = [x['insta_username'] for x in accounts]

    # get followers
    for account in accounts_list :
        logger.info(f'Get followers for {account}')

        # get the last existing followers list for this account
        last_list = mongo.Followers.objects(account = account).order_by('-id').first()

        try :
            last_followers_count = last_list.followers_count
            old_followers = last_list.followers
        except:
            last_followers_count = 0
            old_followers = []

        finally:

            # get the new list length to limit the query to new results
            new_followers_count = session.get_user_followers_count(account)
            max = new_followers_count-last_followers_count

            logger.info(f'Get {max} new followers')
            try:
                new_followers = session.get_user_followers(account, max_followers=max)
            except Exception as e:
                logger.error(e)
                break

            else:
                followers = list(set(old_followers + new_followers['followers']))

        try :
            mongo.Followers(account = account,
            date = session.start_time.date(),
            followers = followers,
            followers_count = new_followers_count,
            new_followers = new_followers['followers'],
            new_followers_count = max
            ).save()
        except mongoengine.errors.NotUniqueError as e:
            logger.error(e)
            pass

get_followers_users(debug=True, bot_username ='Scott')