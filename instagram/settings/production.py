import os
cwd = os.getcwd()

# Config
CONFIG_FILE = os.path.join(cwd, 'instagram','files','config.json')

# Browser path
CHROMEDRIVER_PATH = r"..\chromedriver_win32\chromedriver.exe"

# Logging
LEVEL = 'DEBUG'
LOG_CONFIG = os.path.join(cwd, 'instagram','settings','log_config.json')