"""Client library for using OAuth2, with applications without web access."""

import importlib.util

__author__ = 'Luis Maia <luis.maia@xfel.eu>'
__version__ = '5.1.0'

# https://pypi.python.org/pypi/oauthlib
oauthlib_spec = importlib.util.find_spec("oauthlib")
# https://github.com/requests/requests
requests_spec = importlib.util.find_spec("requests")
# https://github.com/requests/requests-oauthlib
requests_oauthlib_spec = importlib.util.find_spec("requests_oauthlib")

if oauthlib_spec is not None and \
        requests_spec is not None and \
        requests_oauthlib_spec is not None:
    import oauthlib
    import requests
    import requests_oauthlib

    if oauthlib.__version__ < '3.0.2':
        msg = ('You are using oauthlib version %s. '
               'Please upgrade it to version 3.0.2.')
        raise Warning(msg % oauthlib.__version__)

    if requests.__version__ < '2.22.0':
        msg = ('You are using requests version %s. '
               'Please upgrade it to version 2.22.0.')
        raise Warning(msg % requests.__version__)

    if requests_oauthlib.__version__ < '1.2.0':
        msg = ('You are using requests_oauthlib version %s. '
               'Please upgrade it to version 1.2.0.')
        raise Warning(msg % requests_oauthlib.__version__)
