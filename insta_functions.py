import functions as fn
import random
import timeit

class Session:
    def __init__(self, username, password, browser, rules, no_repeat: dict, logs=None):
        self.username = username
        self.password = password
        self.browser = browser
        self.rules = rules
        self.timeout = rules['global']['timeout']
        self.logs = logs
        self.clicked_links = no_repeat['clicked_links']
        self.accounts_counter = no_repeat['accounts_counter']

    def connect(self):
        logger = self.logs['logger']
        counter = self.logs['counter']
        rules_connect = self.rules['connect']
        self.browser.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
        # Find username, password and login input fields
        input_username = fn.find_element(self.browser, "//input[@name='username']", timeout=self.timeout)
        input_password = fn.find_element(self.browser, "//input[@name='password']", timeout=self.timeout)
        login_button = fn.find_element(self.browser, "//button[text()='Log in']", timeout=self.timeout)
        fn.random_sleep(**rules_connect['delay'], **self.logs)

        # Fill username and password and login
        input_username.send_keys(self.username)
        input_password.send_keys(self.password)
        logger.info('Connection to the account :' + self.username)
        counter.increment('Connection')
        login_button.click()
        fn.random_sleep(**rules_connect['delay'], **self.logs)

        # Deny app download if asked
        deny_app_download_button = fn.find_element(self.browser, "//a[text()='Not Now']", self.timeout)
        logger.debug('App download denied')
        deny_app_download_button.click()

        # Deny notifications in browser for current session
        deny_notifications_button = fn.find_element(self.browser, "//button[text()='Not Now']", self.timeout)
        deny_notifications_button.click()
        logger.debug('Notifications denied')
        fn.random_sleep(**rules_connect['delay'], **self.logs)

    def like(self, link):
        """ Opens the post, see if it's not already liked
        and like it depending on the probability set in rules"""
        rules = self.rules['like']
        browser = self.browser
        logger = self.logs['logger']
        counter = self.logs['counter']
        logger.debug('Open link: ' + link)
        browser.get(link)
        counter.increment('Links_opened')
        fn.random_sleep(**rules['delay'], **self.logs)
        # get account and stop if already liked two posts from this
        account_link = fn.find_element(browser, "//h2//a")
        account_name = account_link.get_attribute("title")
        try:
            if self.accounts_counter.counters[account_name] >= rules['likes_per_account']:
                logger.info('Like per account limit reached. Post not liked')
        except KeyError:
            like_button = fn.find_element(browser, "//span[@aria-label='Like']")
            # check if the post have already been liken
            if like_button:  # this condition is not working
                counter.increment('New_post_opened')
                # like only certain pictures, depending on the probability set in rules
                rand = random.random()
                if rand <= rules['probability']:
                    logger.debug(str(rand) + ' <= ' + str(rules['probability']))
                    logger.info("Like post")
                    like_button.click()
                    counter.increment('Post_liked')
                    self.accounts_counter.increment(account_name)
                else:
                    logger.debug(str(rand) + ' > ' + str(rules['probability']))
                    logger.info("Don't like post")
                    counter.increment('Post_not_liked')
            else:
                counter.increment('Already_liked_post_opened')
                # go back to the previous page before opening a new link
        fn.random_sleep(**rules['delay'], **self.logs)
        logger.debug('Back to previous page')
        browser.back()

    def like_from_hashtags(self, hashtags: list):
        """ Loops through the list of hashtags to like posts """
        start = timeit.default_timer()
        logger = self.logs['logger']
        rules = self.rules['like']
        browser = self.browser
        random.shuffle(hashtags)
        logger.debug('Hashtags order: ' + str(hashtags))
        for hashtag in hashtags:
            # get all the links linked to one hashtag
            browser.get("https://www.instagram.com/explore/tags/" + hashtag)
            number_of_posts_to_like = random.randint(*self.rules['like']['postsPerHashtag'].values())
            logger.info(str(number_of_posts_to_like) + ' posts to like')
            posts = browser.find_element_by_tag_name('main')
            links = posts.find_elements_by_tag_name('a')
            links_filtered = [x for x in links if x not in self.clicked_links]
            links_to_like = random.sample(links_filtered, number_of_posts_to_like)
            links_urls = [x.get_attribute("href") for x in links_to_like]
            for link in links_urls:
                self.like(link)
                self.clicked_links.append(link)
                fn.random_sleep(**rules['delay'], **self.logs)
        stop = timeit.default_timer()
        self.logs['counter'].increment('execution_time', stop-start)
        return self.logs['counter']

    def open_activity_feed(self):
        rules = self.rules['global']
        url = r'https://www.instagram.com/accounts/activity/'
        logger = self.logs['logger']
        self.browser.get(url)
        fn.random_sleep(**rules['delay'], **self.logs)
        logger.debug('Back to previous page')
        self.browser.back()

