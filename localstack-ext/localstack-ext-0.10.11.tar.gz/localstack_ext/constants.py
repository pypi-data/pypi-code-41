# version of localstack-ext
VERSION = '0.10.11'

# TODO: fix this. Also, not sure which timezone AWS uses - should be UTC, but there
# have been examples of AccessToken validation failure because of local time comparison
TOKEN_EXPIRY_SECONDS = 24 * 60 * 60
