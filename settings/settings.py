import logging

# Environment
ENVIRONMENT = 'PRODUCTION'
DEBUG = True

# import environment-specific settings
if ENVIRONMENT == 'DEVELOPEMENT':
    from settings.developement import *
elif ENVIRONMENT == 'PRODUCTION':
    from settings.production import *

# Logs
FORMATTER =  logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

