import os
import sys
try :
    cwd = sys._MEIPASS # get working directory if app bundled in .exe
except AttributeError :
    cwd = os.getcwd()

# Config
CONFIG_FILE = os.path.join(cwd, 'instagram','files','config.json')

# Browser driver path
if os.name == 'nt':
    CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver_win32','chromedriver.exe')

if os.name == 'posix':
    CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver_linux', 'chromedriver')

# Logging
LOG_CONFIG = os.path.join(cwd, 'instagram','settings','log_config.json')