from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json

def await_element_load(browser, XPATH : str):
    """ Wait till the element is loaded, then select the element.
        if not loaded after 20 sec, throw Timeout error
    """
    try:
        WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.XPATH,XPATH)))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
    return browser.find_element_by_xpath(XPATH)


def read_json_file(file):
    """read a JSON file to store its content on a variable"""
    with open(file, encoding='utf-8') as file:
        result = json.load(file)
        return result