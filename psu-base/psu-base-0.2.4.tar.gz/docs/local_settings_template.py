# ############################################################
#
#   Copy this file to local_settings.dat and update the values
#   as needed for the local runtime environment.
#
# ############################################################

# Environment choices: {DEV, TEST, PROD}
ENVIRONMENT = 'DEV'

# Name of machine running the application
ALLOWED_HOSTS = ['localhost']

# Debug mode (probably only true in DEV)
DEBUG = True

# SSO URL
CAS_URL = 'https://sso-stage.oit.pdx.edu/idp/profile/cas/login'

# Finti URL (dev, test, or prod)
FINTI_URL = 'http://localhost:8888'
# Finti URLs (for reference)
# http://localhost:8888
# https://ws-test.oit.pdx.edu
# https://ws.oit.pdx.edu

# FINTI_TOKEN = << put your Finti token here >>

# You may disable elevated developer access in non-production
# ELEVATE_DEVELOPER_ACCESS = False

# You may extend session expiration during development
# SESSION_COOKIE_AGE = 4 * 60 * 60  # 4 hours
