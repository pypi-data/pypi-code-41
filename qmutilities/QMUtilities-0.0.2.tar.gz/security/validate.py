from flask import request, abort, url_for
from security import secret_manager
import json
from pymemcache.client import base
import base64
from flask import jsonify


class ValidateHeader(object):
    def __init__(self, app, ip_list, secret_name, logging_enabled=False):
        """
        Initialize IPBlock and set up a before_request handler in the
        app.

        You can pass in IP list to verify if incoming request coming from
        a trusted server or not.

        Set Logging_enabled to true to see the IP of the incoming request in the log file
        :param app:
        :param ip_list:
        :param logging_enabled:
        """
        self.logger = None
        self.IP_LIST = ip_list
        self.secret_name = secret_name
        if logging_enabled:
            self.logger = app.logger

        app.before_request(self.check_whitelisting)

        if request.method == "POST":
            app.before_request(self.check_okta_token)

    def check_whitelisting(self):
        """
        checks the IP if it belongs to the input range, otherwise it throws HTTPErr:403 error
        :return:
        """

        # To avoid unnecessary database queries, ignore the IP check for
        # requests for static files
        if request.path.startswith(url_for('static', filename='')):
            return

        # Some static files might be served from the root path (e.g.
        # favicon.ico, robots.txt, etc.). Ignore the IP check for most
        # common extensions of those files.
        ignored_extensions = ('ico', 'png', 'txt', 'xml')
        if request.path.rsplit('.', 1)[-1] in ignored_extensions:
            return

        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

        if ip:
            if self.logger:
                print("Incoming request from IP: {}".format(ip))
            if ip not in self.IP_LIST:
                abort(403, {'message': 'Forbidden Access: {} Not an authorized IP'.format(ip)})
        else:
            return "No IP found, Please check Nginx config", 412

    def check_okta_token(self):

        if request.method == "POST":
            if request.headers.__contains__('Authentication'):
                okta_auth_header = request.headers['Authentication']
                if self.base64_encode(okta_auth_header):
                    assert_id = base64.b64decode(okta_auth_header).split(':')[0]
                else:
                    assert_id = okta_auth_header.split(' ')[4]

                memcache_key = "assert:" + assert_id

                cache_json = json.loads(secret_manager.get_secret(self.secret_name))
                aws_elastic_cache_hostname = cache_json['elastic_cache_hostname']
                port = cache_json['port']

                client = base.Client((aws_elastic_cache_hostname, int(port)))

                if not client.get(memcache_key):
                    abort(403, {'Forbidden': 'Request not from an authorized user'})
            else:
                return jsonify({'Exception': "AuthFailure", 'message': 'No Authorization header provided.','status_code': '424'})

    def base64_encode(self, token):

        if len(token) % 4 != 0:  # check if multiple of 4
            while len(token) % 4 != 0:
                token = token + "="
            decoded_token = base64.b64decode(token)
        else:
            decoded_token = base64.b64decode(token)
        if token == base64.b64encode(decoded_token):
            return True
        else:
            return False
