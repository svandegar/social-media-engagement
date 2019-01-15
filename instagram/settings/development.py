import os
cwd = os.getcwd()

# Config
# CONFIG_FILE = './instagram/DEV/files/config.json'
CONFIG_FILE = os.path.join(cwd, 'instagram','DEV','files','config.json')
# Browser path
CHROMEDRIVER_PATH = r"C:\git\projects\SM-bot\chromedriver_win32\chromedriver.exe"

# Logging

# LOG_CONFIG = './instagram/settings/log_config.json'
LOG_CONFIG = os.path.join(cwd, 'instagram','settings','log_config.json')