import functions as fn
import random
import timeit
from datetime import datetime
import logging


class Session:
    def __init__(self, credentials: dict, browser, rules, history):
        self.username = credentials['username']
        self.password = credentials['password']
        self.browser = browser
        self.rules = rules
        self.timeout = rules.general['timeout']
        self.clicked_links = history.clicked_links
        self.accounts_counter = fn.Counters(*history.accounts_counter)
        self.start_time = datetime.utcnow()
        self.logger = logging.getLogger(__name__)
        self.counter = fn.Counters(**dict(
            sleeptime=0,
            connection=0,
            links_opened=0,
            new_post_opened=0,
            post_liked=0,
            post_not_liked=0,
        ))

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
        login_button = fn.find_element(self.browser, "//button[text()='Log in']", timeout=self.timeout)
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

        # Get account name and stop if already liked two posts from this account
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
                    return None
            except KeyError:
                pass
                like_button = fn.find_element(browser, "//span[@aria-label='Like']")

                # Check if the post have already been liked
                if like_button:  # TODO : this condition is not working,
                    counter.increment('new_post_opened')

                    # Like only certain pictures, depending on the probability set in rules
                    rand = random.random()
                    if rand <= rules['probability']:
                        logger.debug(str(rand) + ' <= ' + str(rules['probability']))
                        logger.info("Like post")
                        like_button.click()
                        counter.increment('post_liked')
                        self.accounts_counter.increment(account_name)
                    else:
                        logger.debug(str(rand) + ' > ' + str(rules['probability']))
                        logger.info("Don't like post")
                        counter.increment('post_not_liked')
                else:
                    counter.increment('Already_liked_post_opened')
                    logger.info('Already_liked post opened')
        else:
            logger.info('No account name found')

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

            # get all the links linked to one hashtag
            browser.get("https://www.instagram.com/explore/tags/" + hashtag)
            number_of_posts_to_like = random.randint(*rules['postsPerHashtag'].values())
            logger.info(str(number_of_posts_to_like) + ' posts to like')
            posts = browser.find_element_by_tag_name('main')
            links = posts.find_elements_by_tag_name('a')
            links_filtered = [x for x in links if x not in self.clicked_links]

            # get a subset of the links to like
            try:
                links_to_like = random.sample(links_filtered, number_of_posts_to_like)
            except ValueError:
                logger.warning('Not enough links to fill the sample of :' + str(number_of_posts_to_like))
                break
            links_urls = [x.get_attribute("href") for x in links_to_like]
            for link in links_urls:
                self.like(link)
                self.clicked_links.append(link)
                fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
                try:
                    if counter.counters['post_liked'] >= rules['totalLikesMax']:
                        logger.info('Max posts to like reached : ' + str(counter.counters['post_liked']))
                        break
                except:
                    counter.counters['post_liked'] = 0
            if counter.counters['post_liked'] >= rules['totalLikesMax']:
                logger.info('Max posts to like reached : ' + str(counter.counters['post_liked']))
                break
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

    def get_followers_list(self, account=None):
        browser = self.browser
        logger = self.logger
        counter = self.counter
        rules = self.rules.get_followers
        if account:
            account = account
        else:
            account = self.username
        browser.get('https://www.instagram.com/' + account)
        followers_link = fn.find_element(browser, "//a[text()=' followers']")
        followers_link.click()
        fn.random_sleep(rules['delay'], logger=logger, counter=counter)
        modal = browser.find_element_by_xpath("//div[@role='dialog']")
        list_a = modal.find_elements_by_tag_name('a')
        browser.execute_script("return arguments[0].scrollIntoView();", list_a[10])
        print('scrolled from 10')
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
        list_a = modal.find_elements_by_tag_name('a')
        browser.execute_script("return arguments[0].scrollIntoView();", list_a[-1])
        fn.wait_element(browser, list_a[-1])
        old_last_element = list_a[-1].text
        logger.debug('Last element of the list :' + old_last_element)
        new_last_element = None
        fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
        while old_last_element != new_last_element:
            old_last_element = list_a[-1].text
            fn.random_sleep(**rules['delay'], logger=logger, counter=counter)
            list_a = modal.find_elements_by_tag_name('a')
            browser.execute_script("return arguments[0].scrollIntoView();", list_a[-2])
            new_last_element = list_a[-1].text
            logger.debug('Last element of the list :' + new_last_element)
        logger.debug('End of loop')

        # get followers from elements list
        names = []
        for link in list_a:
            name = link.text
            if name != '':
                names.append(name)
                logger.debug('Follower added : ' + name)
        followers = list(filter(None, names))
        return followers
