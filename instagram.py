import functions as fn
import insta_functions as ifn
from settings.settings import *
import routines as rt

# get account credentials
credentials = fn.read_json_file(CREDENTIALS_FILE)


# launch daily routine
session = rt.daily_routine(credentials, connect=True)

# get followers list by an account
followers = session.get_followers_list_from()


""" Test zone """

import importlib
importlib.reload(ifn)
importlib.reload(fn)