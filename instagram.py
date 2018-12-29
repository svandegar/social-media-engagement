from selenium import webdriver
import functions as fn
import insta_connector as ic
import importlib
importlib.reload(ic)
importlib.reload(fn)


# get Instagram account credentials
credentials = fn.read_json_file('credentials.json')

# get inputs
inputs = fn.read_json_file('./files/inputs.JSON')
rules = fn.read_json_file('./files/rules.JSON')
outputs = fn.read_json_file('./files/outputs.JSON')

# Open browser
option = webdriver.ChromeOptions()
option.add_argument(argument="--incognito")
browser = webdriver.Chrome(executable_path=r"C:\git\projects\SM-bot\chromedriver_win32\chromedriver.exe",
                           options=option)

# open Instagram session
session = ic.Session(**credentials,browser = browser, rules = rules)
session.connect()

# like pictures
session.like(inputs['hashtags'],outputs['clicked_links'])
fn.write_json_file(outputs,'./files/outputs.JSON')
