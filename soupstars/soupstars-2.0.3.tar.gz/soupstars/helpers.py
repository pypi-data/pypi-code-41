import sys


if sys.version_info.major >= 3:
    import urllib
    urlparse = urllib.parse.urlparse
else:
    import urlparse
    urlparse = urlparse.urlparse
