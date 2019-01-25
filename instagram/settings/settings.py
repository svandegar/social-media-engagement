import os
# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'PRODUCTION')

# import environment-specific settings
if ENVIRONMENT == 'DEVELOPMENT':
    from instagram.settings.development import *
elif ENVIRONMENT == 'PRODUCTION':
    from instagram.settings.production import *

# version
VERSION = '1.1.0'




