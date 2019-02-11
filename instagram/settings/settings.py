import os
# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT')

# import environment-specific settings
if ENVIRONMENT == 'DEVELOPMENT':
    from instagram.settings.development import *
elif ENVIRONMENT == 'PRODUCTION':
    from instagram.settings.production import *

# version
SCOTT_VERSION = '1.4.0'
SCHEDULER_VERSION = '1.3.0'

# password secret key
PASSWORD_KEY = os.getenv('PASSWORD_KEY', None)



