from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import random
import time
from settings.settings import *
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import mongo

""" Scrapping """


def wait_element(browser, element, timeout=20):
    """ Wait till the element is loaded, then select the element.
        if not loaded after 20 sec, throw Timeout error
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of(element))
        return True
    except TimeoutException:
        print("Timed out waiting for page to load")
        return False


def find_element(browser, XPATH: str, timeout=20):
    """ Wait till the element is loaded, then returns the element.
        if not loaded after 20 sec, throw Timeout error
    """
    try:
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, XPATH)))
        return browser.find_element_by_xpath(XPATH)
    except TimeoutException:
        print("Timed out waiting for page to load")
        return False


def find_elements(browser, XPATH: str, timeout=20):
    """ Wait till the elements are loaded, then returns the elements.
        if not loaded after 20 sec, throw Timeout error
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
    """read a JSON file to store its content on a variable"""
    with open(file, encoding='utf-8') as file:
        result = json.load(file)
        return result


def write_json_file(data: dict, filename: str):
    """convert the input data dict to JSON
    and write it to a json with the input filename"""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)


""" Logging """


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', utc=True)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, level='Debug'):
    logger = logging.getLogger(logger_name)
    level = level.title()
    if level == 'Warn':
        logger.setLevel(logging.WARN)
    elif level == 'Debug':
        logger.setLevel(logging.DEBUG)
    elif level == 'Info':
        logger.setLevel(logging.INFO)
    elif level == 'Error':
        logger.setLevel(logging.ERROR)
    elif level == 'Critical':
        logger.setLevel(logging.CRITICAL)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger


class Counters:
    def __init__(self, global_count=False, **elements):
        """
        Counter object to count and increment different values.
        :param global_count: if True, add a global counter which is the sum of the sub-counters
        :param elements: optional **kwargs {counter_name : value} to initialize the counter with existing values
        """
        self.global_count = global_count
        self.counters = {}
        if global_count:
            self.counters['global_count_value'] = 0
        for element in elements:
            self.counters[element] = elements[element]

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

def counter_to_mongo(counter : Counters):
    mongo = []
    for key in counter.counters:
        mongo.append(dict(name = key, value = counter.counters[key]))
    return mongo

def counter_from_mongo(mongo : list):
    elements = {}
    for counter in mongo:
        elements = {counter['name'] : counter['value']}
    return Counters(**elements, global_count=True)




class Repeated_Actions_Tracker:
    def __init__(self, history_document = None):

        if history_document:
            self.clicked_links = history_document.clicked_links
            try:
                self.accounts_counter = counter_from_mongo(history_document.accounts_counter)
            except KeyError:
                self.accounts_counter = Counters(global_count=True)
        else:
            self.clicked_links = []
            self.accounts_counter = Counters(global_count=True)

    def get_history(self):
        history = mongo.History(clicked_links=self.clicked_links, accounts_counter=counter_to_mongo(self.accounts_counter))
        return history


def update_metrics_file(metrics_file, session):
    session_metrics = {str(session.start_time): session.logs['counter'].counters}
    try:
        metrics_file[session.username].append(session_metrics)
    except KeyError:
        metrics_file[session.username] = session_metrics
    return metrics_file

def save_to_mongo(object):
    object.save()

def update_mongo(object, **parameters):
    object.modify(**parameters)

""" Randomization """


def random_sleep(min=2, max=5, logger=None, counter=None):
    sleeptime = random.randint(min, max)
    time.sleep(sleeptime)
    if counter:
        counter.increment('Sleeptime', sleeptime)
    if logger:
        logger.debug('Sleep :' + str(sleeptime))
    return sleeptime


""" Data connections """


def get_data_from_files(user_inputs, rules, history, metrics):
    user_inputs_file = read_json_file(user_inputs)
    rules_file = read_json_file(rules)
    history_file = read_json_file(history)
    metrics_file = read_json_file(metrics)
    return dict(user_inputs_file = user_inputs_file,
                rules_file = rules_file,
                history_file=history_file,
                metrics_file = metrics_file)
