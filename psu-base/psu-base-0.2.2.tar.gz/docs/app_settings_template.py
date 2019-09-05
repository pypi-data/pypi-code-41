# Get generic PSU settings
from psu_base.psu_settings import *

# The current version of your application
APP_VERSION = '0.0.1'

# App identifiers:
#   - APP_CODE: used in shared AWS database tables, and/or in JWT creation
#   - APP_NAME: used for display purposes only
APP_CODE = 'DEMO'
APP_NAME = 'Demo Site'

# On-premises apps will have additional "context" appended to the URL
# i.e. https://app.banner.pdx.edu/<URL_CONTEXT>/index
URL_CONTEXT = 'demo'

# CAS will return users to the root of the application
CAS_REDIRECT_URL = f'/{URL_CONTEXT}'

