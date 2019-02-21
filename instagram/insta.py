from instagram import functions as fn
import random
import timeit
from datetime import datetime
import logging
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions


class Session:
    def __init__(self, credentials: dict, browser, rules, cipher_suite, history=None):
        self.username = credentials['username']
        self.browser = browser
        self.rules = rules
        self.password = cipher_suite.decrypt(bytes(credentials['password'],encoding='utf-8')).decode('utf-8')
        self.timeout = rules.general['timeout']
        self.logger = logging.getLogger(f'{__name__} - {self.username}')
        try:
            self.clicked_links = history.clicked_links
            self.accounts_counter = fn.Counters(*history.accounts_counter)
        except:
            self.logger.debug('No history')
        self.start_time = datetime.utcnow()
        self.counter = fn.Counters(**dict(
            sleeptime=0,
            connection=0,
            links_opened=0,
            new_post_opened=0,
            post_liked=0,
            post_not_liked=0,
        ))
        self.totalLikesMax = random.randint(int(rules.like['totalLikesMax']*0.90),int(rules.like['totalLikesMax']*1.1))

    def connect(self):
        """
        Connects the current session to Instagram
        :return:
        """
        logger = self.logger
        counter = self.counter
        rules = self.rules.connection
        self.browser.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
        # Find username, password and login input fields
        input_username = fn.find_element(self.browser, "//input[@name='username']", timeout=self.timeout)
        input_password = fn.find_element(self.browser, "//input[@name='password']", timeout=self.timeout)
        login_button = fn.find_element(self.browser, "//button[@type='submit']", timeout=self.timeout)
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)

        # Fill username and password then login
        input_username.send_keys(self.username)
        input_password.send_keys(self.password)
        logger.info('New connection to the account :' + self.username)
        counter.increment('connection')
        login_button.click()
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)

        # Deny app download if asked
        deny_app_download_button = fn.find_element(self.browser, "//a[text()='Not Now']", self.timeout)
        if deny_app_download_button:
            deny_app_download_button.click()
            logger.debug('App download denied')

        # Deny notifications in browser for current session
        deny_notifications_button = fn.find_element(self.browser, "//button[text()='Not Now']", self.timeout)
        if deny_notifications_button:
            deny_notifications_button.click()
            logger.debug('Notifications denied')
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)

    def like(self, link):
        """
        Opens the post, see if it's not already liked
        and like it depending on the probability set in rules
        :param link: url of the post to like
        """
        rules = self.rules.like
        browser = self.browser
        logger = self.logger
        counter = self.counter
        logger.debug('Open link: ' + link)
        browser.get(link)
        counter.increment('links_opened')
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)

        try:

            # Get account name and stop if reached account limit
            account_link = fn.find_element(browser, "//h2//a")
            if account_link:
                account_name = account_link.get_attribute("title")
                try:
                    if self.accounts_counter.counters[account_name] >= rules['likesPerAccount']:
                        logger.info('Like per account limit reached. Post not liked')

                        # Go back to the previous page before exiting the function
                        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
                        logger.debug('Back to previous page')
                        browser.back()
                        return
                    else:
                        logger.debug('Post from account under the like per account limit. Evaluate post.')
                except KeyError:
                    logger.debug('Post from account not in list. Evaluate post.')
                    self.accounts_counter.counters[account_name] = 0

                # wait for the page to load
                main = fn.find_element(browser, "//main")

                # Check if the post have already been liked
                try:
                    browser.find_element_by_xpath("//span[@aria-label='Unlike']")
                    counter.increment('Already_liked_post_opened')
                    logger.info('Already_liked post opened')
                except exceptions.NoSuchElementException:
                    # main = fn.find_element(browser, "//main")
                    sections = main.find_elements_by_tag_name("section")
                    buttons = sections[0].find_elements_by_tag_name("button")
                    like_button = buttons[0]
                    counter.increment('new_post_opened')

                    # Like only certain posts, depending on the probability set in rules
                    rand = random.random()
                    if rand <= rules['probability']:
                        logger.debug(str(rand) + ' <= ' + str(rules['probability']))
                        logger.info("Like post {}".format(counter['post_liked']))
                        like_button.click()
                        counter.increment('post_liked')
                        self.accounts_counter.increment(account_name)
                    else:
                        logger.debug(str(rand) + ' > ' + str(rules['probability']))
                        logger.info("Don't like post")
                        counter.increment('post_not_liked')

            else:
                logger.info('No account name found. No action on this link')

        except Exception as e:
            logger.error(e, 'Loop on this post ended unexpectedly: ' + link)

        finally:
            # Go back to the previous page before opening a new link
            fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
            logger.debug('Back to previous page')
            browser.back()

    def like_from_hashtags(self, hashtags: list):
        """
        Loops through the list of hashtags to like posts
        :param hashtags: list of hashtags used to find posts
        """
        start = timeit.default_timer()
        logger = self.logger
        counter = self.counter
        rules = self.rules.like
        browser = self.browser
        random.shuffle(hashtags)
        logger.debug('Hashtags order: ' + str(hashtags))
        for hashtag in hashtags:
            try:

                # get all the links linked to one hashtag
                browser.get("https://www.instagram.com/explore/tags/" + hashtag)
                try:
                    posts = browser.find_element_by_tag_name('main')
                    links = posts.find_elements_by_tag_name('a')
                except:
                    logger.warning('No links found on page https://www.instagram.com/explore/tags/' + hashtag)
                else:
                    links_filtered = [x for x in links if x not in self.clicked_links]

                    # get a subset of the links to like
                    number_of_posts_to_like = random.randint(*rules['postsPerHashtag'].values())
                    subset_size = min(number_of_posts_to_like, len(links_filtered))
                    logger.info(str(subset_size) + ' posts selected for the hashtag ' + hashtag)
                    links_to_like = random.sample(links_filtered, subset_size)

                    # get the links urls and run like function for each one of them
                    links_urls = [x.get_attribute("href") for x in links_to_like]
                    logger.debug('Got %s links for these posts' % len(links_urls))
                    for link in links_urls:
                        self.like(link)
                        self.clicked_links.append(link)
                        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
                        try:
                            if counter.counters['post_liked'] >= self.totalLikesMax:
                                logger.info('Max posts to like reached : ' + str(counter.counters['post_liked']))

                                # timer
                                stop = timeit.default_timer()
                                logger.info('Like session finished after ' + str(stop - start) + ' seconds')
                                self.counter.increment('execution_time', stop - start)
                                return self.counter
                        except:
                            counter.counters['post_liked'] = 0

            except:
                logger.error('Loop on this hashtag ended unexpectedly: ' + str(hashtag))

        # timer
        stop = timeit.default_timer()
        logger.info('Like session finished after ' + str(stop - start) + ' seconds')
        self.counter.increment('execution_time', stop - start)
        return self.counter

    def open_activity_feed(self):
        """
        Open the activity feed page
        """
        logger = self.logger
        counter = self.counter
        rules = self.rules.general
        url = r'https://www.instagram.com/accounts/activity/'
        self.browser.get(url)
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
        logger.debug('Back to previous page')
        self.browser.back()

    def get_user_followers_count(self, user=None):
        browser = self.browser
        logger = self.logger
        counter = self.counter
        if user:
            user = user
        else:
            user = self.username

        # go to the user page and get the followers count string
        browser.get(f'https://www.instagram.com/{user}')
        followers_link = fn.find_element(browser, "//a[text()=' followers']")
        if '\n' in followers_link.text:
            followers_count_string = followers_link.text.split('\n')[0]
        else:
            followers_count_string = followers_link.text.split(' ')[0]

        # convert the followers count string to int
        followers_count = int(fn.human_to_int(followers_count_string))
        return followers_count

    def get_user_followers(self, user=None, max_followers=None):
        browser = self.browser
        logger = self.logger
        counter = self.counter
        start = timeit.default_timer()
        counter.increment('followers', 0)
        if user:
            user = user
        else:
            user = self.username
        got_same_list = 0  # counter to avoid infinite loops in followers list

        # get followers count
        followers_count = self.get_user_followers_count(user)

        # open followers modal
        browser.get(f'https://www.instagram.com/{user}')
        followers_link = fn.find_element(browser, "//a[text()=' followers']")
        followers_link.click()
        fn.random_sleep(2, 6, logger=logger, counter=counter)

        # define number of followers to get
        if not max_followers and max_followers is not 0:
            max_followers = followers_count

        # get the initial followers list length
        modal = fn.find_element(browser, "//div[@role='dialog']")
        list_size = len(modal.find_elements_by_tag_name('li'))

        # scroll in the modal until the list size equals max_followers
        ActionChains(browser).move_to_element(modal).click().key_down(Keys.SPACE).perform()
        logger.debug('first scroll in the modal')
        fn.random_sleep(2, 2, logger, counter)
        while list_size < max_followers:

            # try to click on the 3rd last element to focus on the modal before hitting space to scroll
            modal = fn.find_element(browser, "//div[@role='dialog']")
            if not modal:
                browser.get(f'https://www.instagram.com/{user}')
                followers_link = fn.find_element(browser, "//a[text()=' followers']")
                followers_link.click()
                fn.random_sleep(2, 6, logger=logger, counter=counter)

            try:
                fn.find_elements(modal, "//li//div//div[1]//div[2]//div[2]")[-3].click()

            except exceptions.ElementNotVisibleException as e:
                logger.warning(e)

                # if not working, try the 4th last
                try:
                    fn.find_elements(modal, "//li//div//div[1]//div[2]//div[2]")[-4].click()
                except exceptions.ElementNotVisibleException as e:
                    logger.warning(e)

                    # if not working, try the 5th last
                    try:
                        fn.find_elements(modal, "//li//div//div[1]//div[2]//div[2]")[-5].click()
                    except exceptions.ElementNotVisibleException as e:
                        logger.warning(e)

                        # if still not working, break
                        break
                except AttributeError as e:
                    logger.error(e)
                    break
            except AttributeError as e:
                logger.error(e)
                break

            # scroll by hitting SPACE
            ActionChains(browser).send_keys(Keys.SPACE).perform()

            fn.random_sleep(1, 1, logger, counter)
            list_size = len(modal.find_elements_by_tag_name('li'))

            # compare new list size to the previous to see if it continues to grow.
            logger.info('Followers list size: ' + str(list_size))
            if list_size == counter['followers']:
                got_same_list += 1

            # if list size is five time the same, exit the loop
            if got_same_list == 5:
                logger.warning(f'got same list {got_same_list} times')
                break
            counter.counters['followers'] = list_size

        logger.debug('loop ended')
        logger.info(f'got {list_size} followers')
        if list_size < max_followers:
            logger.warning(f'got only the firsts  {list_size} / {max_followers} followers')

        # get the followers from the browser elements list
        followers = []
        modal = fn.find_element(browser, "//div[@role='dialog']")
        for user in modal.find_elements_by_tag_name('li'):
            username = user.text.split('\n')[0]
            followers.append(username)

        # timer
        stop = timeit.default_timer()
        logger.info('Get user followers session finished after ' + str(stop - start) + ' seconds')
        self.counter.increment('execution_time', stop - start)

        return {'user': user, 'followers': followers, 'followers_count': followers_count}
