import logging.config, mongoengine
from instagram import insta, functions as fn, mongo, proxy as proxy_fn, loggers
from selenium import webdriver
from instagram.settings.settings import *
from selenium.webdriver.chrome import options
from cryptography.fernet import Fernet


def likes(username: str, like_from_hashtags=True, debug=False):
    """
    Follow the Instagram routine defined by the rules set for the account
    """
    try:
        # configure logging
        logger = logging.getLogger(f'{__name__} - {username}')
        logger.addFilter(loggers.ContextFilter())
        if debug:
            logging._handlers['console'].setLevel('DEBUG')
        logger.info('Start script')
        try:
            logger.debug('Environment is set to: ' + os.environ['ENVIRONMENT'])
        except KeyError:
            logger.debug('No ENVIRONMENT variable set. Default environment is PRODUCTION')

        logger.info('Version: ' + SCOTT_VERSION)

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
        logger.debug('connect to MongoDB')
        mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])

        # check user credentials
        try:
            user = mongo.Users.objects.get(username=username)
        except :
            logger.warning(f'User {username} not found in the database')
        else:
            # get account information
            logger.debug('get account information')
            try:
                account = mongo.Accounts.objects.get(username=user.username)
                credentials = dict(username=account.insta_username, password=account.insta_password)

            except :
                logger.warning(f'No account found for this user: {username}')
            else:
                # get user rules, history and user inputs
                logger.debug('get user rules, history and user_inputs')
                history = mongo.History.objects.get(username=username)
                user_inputs = mongo.UserInputs.objects.get(username=username)

                try:
                    rules = mongo.Rules.objects.get(username=username)
                    logger.debug('Got specific user rules')
                except:
                    rules = mongo.Rules.objects.get(username='default')
                    logger.debug('Apply generic user rules')

                # get proxy information
                try:
                    proxy = mongo.Proxies.objects.get(id=account.proxy)
                    logger.debug(f'Got proxy id {account.proxy}')
                    proxy.proxy['clear_password'] = cipher_suite.decrypt(bytes(proxy.proxy['password'],encoding='utf-8')).decode('utf-8')

                except:
                    proxy = None
                    logger.debug('No proxy set for this account')

                # open browser
                logger.debug('Open browser')
                chrome_options = options.Options()
                if proxy:
                    logger.info(f'Connect through proxy at {proxy.location}')

                    # build chrome extension for proxy authentication
                    chrome_extension = proxy_fn.build_chrome_ext(proxy)
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
                session = insta.Session(credentials, browser, rules, cipher_suite, history)
                logger.info('Connect to Instagram')
                session.connect()

                # scripts
                logger.debug('Get user followers count')
                followers = session.get_user_followers_count()
                logger.info(f'{followers} followers on this account')

                if like_from_hashtags:
                    try:
                        logger.info(f'Start like_from_hashtags. Max posts to like: {session.totalLikesMax}')
                        counters = session.like_from_hashtags(user_inputs.hashtags)
                        logger.info(f'End like_from_hashtags. Number of posts liked: {session.counter["post_liked"]}')

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
                                                followers=followers
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

                # end
                session.browser.quit()

        finally:
            logger.info('End of script')

    except Exception as e:
        print(e, 'Routine ended unexpectedtly')
        try:
            session.browser.quit()
        except:
            pass
