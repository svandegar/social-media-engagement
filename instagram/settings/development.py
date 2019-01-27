import os
import sys
try :
    cwd = sys._MEIPASS # get working directory is app bundled in .exe
except AttributeError :
    cwd = os.getcwd()

# Config
CONFIG_FILE = os.path.join(cwd, 'instagram','DEV','files','config.json')

# Browser path
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver_win32','chromedriver.exe')

# Logging
LOG_CONFIG = os.path.join(cwd, 'instagram','settings','log_config.json')