import functions as fn
import random


class Session:
    def __init__(self, username, password, browser, rules):
        self.username = username
        self.password = password
        self.browser = browser
        self.rules = rules
        self.timeout = rules['global']['timeout']

    def connect(self):
        self.browser.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
        # Find username, password and login input fields
        input_username = fn.find_element(self.browser, "//input[@name='username']", timeout=self.timeout)
        input_password = fn.find_element(self.browser, "//input[@name='password']", timeout=self.timeout)
        login_button = fn.find_element(self.browser, "//button[text()='Log in']", timeout=self.timeout)
        fn.random_sleep(2, 5)

        # Fill username and password and login
        input_username.send_keys(self.username)
        input_password.send_keys(self.password)
        login_button.click()
        fn.random_sleep(2, 5)

        # Deny app download if asked
        deny_app_download_button = fn.find_element(self.browser, "//a[text()='Not Now']", self.timeout)
        deny_app_download_button.click()

        # Deny notifications in browser for current session
        deny_notifications_button = fn.find_element(self.browser, "//button[text()='Not Now']", self.timeout)
        deny_notifications_button.click()
        fn.random_sleep(2, 5)

    def like(self, hashtags: list, clicked_links : list):
        rules_like = self.rules['like']
        random.shuffle(hashtags)
        for hashtag in hashtags:
            browser = self.browser
            browser.get("https://www.instagram.com/explore/tags/" + hashtag)
            for _ in range(*rules_like['count'].values()):
                picture = fn.find_element(browser,"//a/div/div[1]/img")
                a = picture.find_elements_by_xpath("//ancestor::a")
                # if fn.wait_element(browser,a,self.timeout):
                link = a[random.randint(0, len(a))].get_attribute("href")
                print('got link ' + link)
                if link not in clicked_links:
                    browser.get(link)
                    fn.random_sleep(**rules_like['delay'])
                    heart = fn.find_element(browser, "//span[@aria-label='Like']")
                    if heart:  # click only if not already liked
                        if random.random() > rules_like['probability']:
                            heart.click()
                    fn.random_sleep(**rules_like['delay'])
                    clicked_links.append(link)
                browser.back()
        return clicked_links
