
# Environment
ENVIRONMENT = 'DEVELOPMENT'

# import environment-specific settings
if ENVIRONMENT == 'DEVELOPMENT':
    from settings.development import *
elif ENVIRONMENT == 'PRODUCTION':
    from settings.production import *




