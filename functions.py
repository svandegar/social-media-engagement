from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import random
import time

def wait_element(browser, element, timeout = 20):
    """ Wait till the element is loaded, then select the element.
        if not loaded after 20 sec, throw Timeout error
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element(element))
        return True
    except TimeoutException:
        print("Timed out waiting for page to load")
        return False

def find_element(browser, XPATH : str, timeout = 20):
    """ Wait till the element is loaded, then select the element.
        if not loaded after 20 sec, throw Timeout error
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH,XPATH)))
        return browser.find_element_by_xpath(XPATH)
    except TimeoutException:
        print("Timed out waiting for page to load")
        return False



def read_json_file(file):
    """read a JSON file to store its content on a variable"""
    with open(file, encoding='utf-8') as file:
        result = json.load(file)
        return result

def random_sleep(min =2, max =5):
    time.sleep(random.randint(min,max))