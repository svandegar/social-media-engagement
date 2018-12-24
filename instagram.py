from selenium import webdriver
import functions as fn
from time import sleep

# TODO : replace these two sections by config file or env variables
# Set Instagram account credentials
credentials = fn.read_json_file('credentials.json')
username = credentials['username']
password = credentials['password']

# Enter hashtags list
hashtags = ['coding',
            'programming',
            'programmer',
            'programminglife',
            'coder',
            'programmers',
            'programmingisfun',
            'codinglife']

# end TODO

# Set browser configuration
option = webdriver.ChromeOptions()
option.add_argument(argument="--incognito")
browser = webdriver.Chrome(executable_path=r"C:\git\projects\SM-bot\chromedriver_win32\chromedriver.exe",
                           options=option)

# Open page
browser.get("https://www.instagram.com/accounts/login/?source=auth_switcher")

# Find username, password and login input fields
input_username = fn.await_element_load(browser,"//input[@name='username']")
input_password = fn.await_element_load(browser,"//input[@name='password']")
login_button = fn.await_element_load(browser,"//button[text()='Log in']")
sleep(2)

# Fill username and password and login
input_username.send_keys(username)
input_password.send_keys(password)
login_button.click()
sleep(2)

# Deny notifications in browser for current session
deny_notifications_button = fn.await_element_load(browser,"//button[text()='Not Now']")
deny_notifications_button.click()
sleep(2)

