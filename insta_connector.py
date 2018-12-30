import functions as fn
import random


class Session:
    def __init__(self, username, password, browser, rules, logs = None):
        self.username = username
        self.password = password
        self.browser = browser
        self.rules = rules
        self.timeout = rules['global']['timeout']
        self.logs = logs


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

    def like(self, hashtags: list, used_links: list):
        # TODO : split in sub-functions
        rules_like = self.rules['like']
        browser = self.browser
        logger = self.logs['logger']
        counter = self.logs['counter']
        random.shuffle(hashtags)
        logger.debug('Hashtags order: ' + str(hashtags))
        # loop through the list of hashtags
        for hashtag in hashtags:
            browser.get("https://www.instagram.com/explore/tags/" + hashtag)
            # loop through a random number of pictures. Range defined in the rule 'postsPerHashtag'
            for _ in range(random.randint(*rules_like['postsPerHashtag'].values())):
                # TODO : refactor two next lines to get only pictures instead of every lines
                picture = fn.find_element(browser, "//a/div/div[1]/img")
                a = fn.find_elements(picture, "//ancestor::a")
                counter.increment('Links_founds', len(a))
                link = a[random.randint(0, len(a))].get_attribute("href")
                logger.debug('Got link ' + link)
                # check whether the link has already been clicked
                if link not in used_links:
                    logger.debug('Open link: ' + link)
                    counter.increment('Links_opened')
                    browser.get(link)
                    fn.random_sleep(**rules_like['delay'], **self.logs)
                    # check if already liked
                    like_button = fn.find_element(browser, "//span[@aria-label='Like']")
                    if like_button:
                        counter.increment('Not_already_liked_post_opened')
                        rand = random.random()
                        # like only certain pictures, following the probability set in rules
                        if rand <= rules_like['probability']:
                            logger.debug(str(rand) + ' <= ' + str(rules_like['probability']))
                            logger.info("Like picture")
                            counter.increment('Post_liked')
                            like_button.click()
                        else:
                            logger.debug(str(rand) + ' > ' + str(rules_like['probability']))
                            logger.info("Don't like picture")
                            counter.increment('Post_not_liked')
                    # back to previous page
                    fn.random_sleep(**rules_like['delay'], **self.logs)
                    used_links.append(link)
                    browser.back()
                fn.random_sleep(**rules_like['delay'], **self.logs)
        return counter
