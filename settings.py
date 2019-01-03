import logging

# Environment
ENVIRONMENT = 'DEVELOPEMENT'
DEBUG = True

# Files
if ENVIRONMENT == 'DEVELOPEMENT':
    CREDENTIALS_FILE = './DEV/files/credentials.json'
    INPUTS_FILE = './DEV/files/inputs.JSON'
    RULES_FILE = './DEV/files/rules.JSON'
    OUTPUTS_FILE = './DEV/files/outputs.JSON'
    LOG_FILE = './DEV/logs/instagram.log'
    METRICS_FILE = './DEV/logs/metrics.JSON'
elif ENVIRONMENT == 'PRODUCTION':
    CREDENTIALS_FILE = './files/credentials.json'
    INPUTS_FILE = './files/inputs.JSON'
    RULES_FILE = './files/rules.JSON'
    OUTPUTS_FILE = './files/outputs.JSON'
    LOG_FILE = './logs/instagram.log'
    METRICS_FILE = './logs/metrics.JSON'

# Browser path
CHROMEDRIVER_PATH = r"C:\git\projects\SM-bot\chromedriver_win32\chromedriver.exe"

# Logs
FORMATTER =  logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

