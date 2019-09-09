# Get generic PSU settings
from psu_base.psu_settings import *

# The current version of the DEMO application
APP_VERSION = '0.0.1'

# App identifiers
APP_CODE = 'DEMO'
APP_NAME = 'Infotext Demo Site'

# On-premises apps will have additional "context" appended to the URL
# i.e. https://app.banner.pdx.edu/<URL_CONTEXT>/index
URL_CONTEXT = 'demo'

# CAS will return users to the root of the application
CAS_REDIRECT_URL = f'/{URL_CONTEXT}'

# Globally require authentication?
REQUIRE_LOGIN = True
# List of URLs in your app that should be excluded from global authentication requirement
APP_PUBLIC_URLS = ['^/$', f'^/{URL_CONTEXT}/?$']

