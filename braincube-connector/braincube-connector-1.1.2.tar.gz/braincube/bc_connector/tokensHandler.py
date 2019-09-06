import json
import json as __json
import os
import re as __research
import traceback
import webbrowser
import logging

import requests
from flask import Flask as __Flask, render_template
from flask import redirect
from flask import request
from flask_cors import CORS as __CORS
from flask_cors import cross_origin
from gevent import pywsgi

from braincube.bc_connector.config_handler import get_client_id, get_client_secret, get_domain

logger = logging.getLogger(__name__)

file_path = os.path.expanduser('~/.braincube') + '/OAuth2AccessToken'

__app = __Flask(__name__)
__app.config['CORS_HEADERS'] = 'Content-Type'

cert_file = os.path.expanduser('~/.braincube/cert.pem')
key_file = os.path.expanduser('~/.braincube/key.pem')

http_server = pywsgi.WSGIServer(('localhost', 5000), __app, certfile=cert_file, keyfile=key_file)

redirect_uri = "https://localhost:5000/token"

scopes = "BASE%20API"


@__app.before_first_request
def set_domain():
    __cors = __CORS(__app, resources={r"/*": {"origins": ("https://%s/*" % get_domain())}})


@__app.route('/')
@cross_origin()
# Code executed when launching the local server
# Opens the Braincube authorization page or the React page according to the parameter passed in query
def launch_connector():
    authorize_uri = "https://%s/sso-server/vendors/braincube/authorize.jsp" % get_domain()
    url = authorize_uri \
          + '?client_id=' + get_client_id() \
          + '&response_type=code' \
          + '&scope=' + scopes \
          + '&redirect_uri=' + redirect_uri
    logger.debug("starting connector from: %s and redirect to %s" + authorize_uri, url)
    return redirect(url)  # -> /token


@__app.route('/token')
@cross_origin()
# Code executed when returning from the Braincube authorization page
# Allows to recover a token thanks to the received code
def get_token_from_code():
    code = __research.search('code=(.*)', request.url).group(1)
    content = {"grant_type": "authorization_code",
               "code": code,
               "redirect_uri": redirect_uri,
               "client_id": get_client_id(),
               "client_secret": get_client_secret()
               }
    logger.info("Pending recovery attempt, please wait")
    token_uri = "https://%s/sso-server/ws/oauth2/token" % get_domain()
    logger.debug("Asking for token to: %s with: %s", token_uri, content)
    retrieve_token = requests.post(token_uri, data=content)
    global TOKEN  # The only way to return a result from a flask app
    TOKEN = __json.loads(retrieve_token.text)['access_token']
    return render_template("closing.html")


@__app.route('/closing')
@cross_origin()
def closing():
    shutdown_server()
    return "server closed"


def shutdown_server():
    """ Close the local server"""
    logger.info("Shutting down the local serveur.")
    http_server.close()


def retrieve_tokens(oauth2_acces_token=None):
    """ Try to get an sso token from an OAuth2 access token"""
    sso_token = None
    if oauth2_acces_token is not None:  # if we have a specified token
        logger.info("Trying with specified oauth2 access token")
        sso_token = get_sso_token(oauth2_acces_token)
    if sso_token is None:
        logger.info("Trying with locally saved oauth2 access token")
        oauth2_acces_token = read_local_oauth_access_token()  # Try to read local written token
        sso_token = get_sso_token(oauth2_acces_token)
    if sso_token is None:
        logger.info("Trying by calling SSO to acquire an oauth2 access token ")
        oauth2_acces_token = get_token_from_web()  # Retrieve a token from web
        sso_token = get_sso_token(oauth2_acces_token)
    return oauth2_acces_token, sso_token


def get_token_from_web():
    """ Redirect to the sso server to get an oauth2 token """
    webbrowser.open('https://localhost:5000/')
    try:
        http_server.serve_forever()

    except OSError:
        logger.error('The port 5000 of the machine is already open, please close your activity before restarting it')
    token = TOKEN
    write_local_oauth_access_token(token)
    return token


def read_local_oauth_access_token():
    """ Try to read the OAuth access token on disk """
    if os.path.isfile(file_path):
        with open(file_path) as token:
            return token.read()


def write_local_oauth_access_token(sso_token):
    """ write the OAuth access token on disk """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as outfile:
        outfile.write(sso_token)


def get_sso_token(oauth2_acces_token):
    # Return a sso_token thanks to the token, which allows the access to the REST API
    if str(oauth2_acces_token):
        headers = {'Authorization': 'Bearer ' + str(oauth2_acces_token)}
        __sso_token_uri = "https://{domain}/sso-server/rest/session/openWithToken".format(domain=get_domain())
        logger.debug("Asking for an sso token at: %s", __sso_token_uri)
        try:
            result = requests.get(__sso_token_uri, headers=headers)
            if result.status_code != 200:
                logger.warn("Authentication failure: try again with other credentials")
            else:
                logger.info("Successful authentication, you can now access your data")
                return json.loads(result.text)
        except Exception as e:
            logging.debug(traceback.format_exc())
