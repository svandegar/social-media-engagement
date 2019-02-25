from instagram import functions as fn, insta, mongo, loggers, proxy as proxi_fn
import mongoengine
import logging
import logging.config
from selenium import webdriver
from instagram.settings.settings import *
from selenium.webdriver.chrome import options
import click
from cryptography.fernet import Fernet

logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))

@click.command()
@click.option('--bot_username', '-u', prompt=True, help='Scott username')
@click.option('--debug', is_flag=True, help='Set logger level to debug')
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
        logger.debug('No ENVIRONMENT variable set. Default environment , adapis PRODUCTION')

    logger.info('Version: ' + GET_FOLLOWERS_VERSION)

    # check Password key
    try:
        if PASSWORD_KEY:
            cipher_suite = Fernet(PASSWORD_KEY)
        else:
            raise ValueError('Environement variable PASSWORD_KEY is missing')
    except ValueError as e:
        logger.error(e)
        raise e

    # connect to MongoDB
    logger.debug('Connect to MongoDB')
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

    # get user credentials and rules
    user = mongo.Users.objects(username=bot_username).first()
    account = mongo.Accounts.objects(username=user.username).first()
    credentials = dict(username=account.insta_username, password=account.insta_password)
    try:
        rules = mongo.Rules.objects.get(username=bot_username)
        logger.debug('Got specific user rules')
    except:
        rules = mongo.Rules.objects.get(username='default')
        logger.debug('Apply generic user rules')

    # get proxy information
    try:
        proxy = mongo.Proxies.objects.get(id=account.proxy)
        logger.debug(f'Got proxy id {account.proxy}')
        proxy.proxy['clear_password'] = cipher_suite.decrypt(
            bytes(proxy.proxy['password'], encoding='utf-8')).decode('utf-8')

    except:
        proxy = None
        logger.debug('No proxy set for this account')

    # open browser
    logger.debug('Open browser')
    chrome_options = options.Options()
    if proxy:
        logger.info(f'Connect through proxy at {proxy.location}')

        # build chrome extension for proxy authentication
        chrome_extension = proxi_fn.build_chrome_ext(proxy)
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
    session = insta.Session(credentials, browser, rules,cipher_suite)
    logger.info('Connect to Instagram')
    session.connect()

    # get accounts list
    accounts = mongo.Accounts.objects()
    accounts_list = [x['insta_username'] for x in accounts]

    # get followers
    for account in accounts_list :
        if account != credentials['username']:
            try :
                logger.info(f'Get followers for {account}')

                # get the last existing followers list for this account
                last_list = mongo.Followers.objects(account = account).order_by('-id').first()
                old_followers = []
                last_followers_count = 0
                try :
                    last_followers_count = last_list.followers_count
                    old_followers = last_list.followers

                except:
                    logger.info('No followers history')

                finally:
                    # get the new list length to limit the query to new results
                    new_followers_count = session.get_user_followers_count(account)
                    max = new_followers_count-last_followers_count

                    logger.info(f'Get {max} new followers')
                    try:
                        actual_followers = session.get_user_followers(account, max_followers=max)
                        new_followers = list(set(actual_followers['followers'])-set(old_followers))
                    except Exception as e:
                        logger.error(e)
                        break

                    else:
                        followers = list(set(old_followers + new_followers))

                try :
                    logger.debug('Save followers in Mongo')
                    mongo.Followers(account = account,
                    date = session.start_time.date(),
                    followers = followers,
                    followers_count = new_followers_count,
                    new_followers = new_followers,
                    new_followers_count = max
                    ).save()
                except mongoengine.errors.NotUniqueError as e:
                    logger.error(e)
            except Exception as e:
                logger.error(f'loop ended unexpectedly on this account {account}',e)


get_followers_users(sys.argv[1:])