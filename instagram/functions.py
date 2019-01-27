from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import random
import time
import datetime

""" Scrapping """


def wait_element(browser, element, timeout=20):
    """ Wait till the element is loaded, then select the element.
        if not loaded after 20 sec, throw Timeout error
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of(element))
        return True
    except TimeoutException as e:
        print(e)
        return False


def find_element(browser, XPATH: str, timeout=20):
    """ Wait till the element is loaded, then returns the element.
        if not loaded after 20 sec, throw Timeout error and return False
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, XPATH)))
        return browser.find_element_by_xpath(XPATH)
    except TimeoutException as e:
        print(e)
        return False


def find_elements(browser, XPATH: str, timeout=20):
    """ Wait till the elements are loaded, then returns the elements.
        if not loaded after 20 sec, throw Timeout error and return False
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, XPATH)))
        return browser.find_elements_by_xpath(XPATH)
    except TimeoutException:
        print("Timed out waiting for page to load")
        return False


""" Files """


def read_json_file(file):
    """read a JSON file and return a dict """
    with open(file, encoding='utf-8') as file:
        result = json.load(file)
        return result


def write_json_file(data: dict, filename: str):
    """convert the input data dict to JSON
    and write it to a json with the input filename"""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)


""" Counter """


class Counters:
    def __init__(self, global_count=False, *counters, **elements):
        """
        Counter object to count and increment different values.
        :param global_count: if True, add a global counter which is the sum of the sub-counters
        :param elements: optional **kwargs {counter_name : value} to initialize the counter based on a dict
        :param counters: optional *args [{name : str, value : int}] to initialize the counter based on a list of dicts
        """
        self.global_count = global_count
        self.counters = {}
        if global_count:
            self.counters['global_count_value'] = 0
        for element in elements:
            self.counters[element] = elements[element]
        for counter in counters:
            self.counters[counter['name']] = counter['value']

    def increment(self, name='global', increment_value=1):
        """
        If name not existing, create a counter with key = name and value = increment value
        Otherwize, increment the named counter.
        :param name: counter to create or increment
        :param increment_value: increment value
        """
        if name in self.counters:
            self.counters[name] += increment_value
        else:
            self.counters[name] = increment_value
        if self.global_count:
            self.counters['global_count_value'] += increment_value

    def reset(self, name):
        """set the value of the named meter to 0"""
        self.counters[name] = 0

    def __getitem__(self, item):
        return self.counters[item]

    def get_list(self):
        """

        :return: list of dicts [{name : str, value : int}]
        """
        list = []
        for counter in self.counters:
            list.append(dict(name=counter, value=self.counters[counter]))
        return list


""" Randomization """


def random_sleep(min=2, max=5, logger=None, counter=None):
    sleeptime = random.randint(min, max)
    time.sleep(sleeptime)
    if counter:
        counter.increment('sleeptime', sleeptime)
    if logger:
        logger.debug('Sleep :' + str(sleeptime))
    return sleeptime

def random_time(time1 : str, time2 : str):
    datetime1 = datetime.datetime.strptime(time1,'%H:%M')
    datetime2 = datetime.datetime.strptime(time2,'%H:%M')
    seconds1 = datetime1.hour*3600 + datetime1.minute*60
    seconds2 = datetime2.hour*3600 + datetime2.minute*60
    sec_random = random.randint(seconds1,seconds2)
    midnight = datetime.datetime.strptime('00:00','%H:%M')
    result = midnight + datetime.timedelta(seconds=sec_random)
    return (datetime.datetime.strftime(result,'%H:%M'))


""" Diverses """

def human_to_int(string : str):
    string = string.lower()
    string = string.replace(',','')
    if 'k' in string:
        total_string = float(string.replace('k',''))*1000
    elif 'm' in string:
        total_string = float(string.replace('m',''))*1000000
    elif 'b' in string:
        total_string = float(string.replace('b',''))*1000000000
    else:
        total_string = float(string)
    return float(total_string)
