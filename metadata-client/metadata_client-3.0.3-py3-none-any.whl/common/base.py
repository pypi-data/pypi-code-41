"""Base Class with helper methods common to all modules"""

import json
import logging

from .config import *


class Base:
    @staticmethod
    def load_json_from_str(hash_str):
        if hash_str == '':
            return {}
        else:
            return json.loads(hash_str)

    @staticmethod
    def load_json_from_content(response):
        return Base.load_json_from_str(response.content.decode('utf8'))

    @staticmethod
    def format_response(response, action, success_code, module_name):
        r_content = Base.load_json_from_content(response)

        if response.status_code == success_code and r_content != {}:
            res = Base.response_success(module_name, action, r_content)
        elif response.status_code == NO_CONTENT and r_content == {}:
            res = Base.response_success(module_name, action, r_content)
        else:
            app_info = r_content['info']
            res = Base.response_error(module_name, action, app_info)

        return res

    @staticmethod
    # TODO, Make it validate and return key, value criteria
    def unique_key_format_result(res, module_name, unique_id=None):
        if len(res['data']) > 0:
            data = res['data'][0]
            info = res['info']
        else:
            data = {}

            if unique_id:
                info = '{0} "{1}" could not be found!'.format(module_name,
                                                              unique_id)
            else:
                info_msg = 'No {0} could be found respecting the specified ' \
                           'search criteria'
                info = info_msg.format(module_name)

        res = {'success': res['success'],
               'info': info,
               'app_info': res['app_info'],
               'data': data}
        return res

    @staticmethod
    def response_success(module_name, action, r_content):
        if action == CREATE:
            msg = '{0} created successfully'.format(module_name)
        elif action == UPDATE:
            msg = '{0} updated successfully'.format(module_name)
        elif action == GET:
            msg = 'Got {0} successfully'.format(module_name)
        elif action == DELETE:
            msg = '{0} deleted successfully'.format(module_name)
        elif action == SET:
            msg = '{0} set successfully'.format(module_name)
        else:
            return Base.response_error(module_name, action, r_content)

        res = {'success': True, 'info': msg, 'app_info': {}, 'data': r_content}
        logging.debug('response_success => {0}'.format(res))
        return res

    @staticmethod
    def response_error(module_name, action, app_info):
        if action == CREATE:
            msg = 'Error creating {0}'.format(module_name)
        elif action == UPDATE:
            msg = 'Error updating {0}'.format(module_name)
        elif action == GET:
            msg = '{0} not found!'.format(module_name)
        elif action == DELETE:
            msg = 'Error deleting {0}'.format(module_name)
        elif action == SET:
            msg = 'Error setting {0}'.format(module_name)
        else:
            msg = 'ACTION is not correct!'

        res = {'success': False, 'info': msg, 'app_info': app_info, 'data': {}}
        logging.debug('response_error => {0}'.format(res))
        return res

    @staticmethod
    def cal_debug(c_name, m_name, r_content):
        msg = '*** {0}.{1} (content) => {2}'.format(c_name, m_name, r_content)
        logging.debug(msg)

    # Method that generates the RESTful API URL
    def get_api_url(self, model_name, api_specifics=''):
        complete_api_specifics = '{0}{1}'.format(model_name, api_specifics)
        return '{0}{1}'.format(self.base_api_url, complete_api_specifics)

    # Method that will create a new session token
    # if the current token is no longer active
    def check_session_token(self):
        self.oauth_client.check_session_token()

    #
    def api_get(self, api_url, **kwargs):
        """Sends a GET request. Returns :class:`Response` object.
        :param api_url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        """
        kwargs.setdefault('allow_redirects', True)

        self.check_session_token()
        return self.oauth_client.session.get(api_url,
                                             headers=self.headers,
                                             **kwargs)

    #
    def api_post(self, api_url, **kwargs):
        """Sends a GET request. Returns :class:`Response` object.
        :param api_url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        """
        kwargs.setdefault('allow_redirects', True)

        self.check_session_token()
        return self.oauth_client.session.post(api_url,
                                              headers=self.headers,
                                              **kwargs)

    #
    def api_put(self, api_url, **kwargs):
        """Sends a GET request. Returns :class:`Response` object.
        :param api_url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        """
        kwargs.setdefault('allow_redirects', True)

        self.check_session_token()
        return self.oauth_client.session.put(api_url,
                                             headers=self.headers,
                                             **kwargs)

    #
    def api_delete(self, api_url, **kwargs):
        """Sends a GET request. Returns :class:`Response` object.
        :param api_url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        """
        kwargs.setdefault('allow_redirects', True)

        self.check_session_token()
        return self.oauth_client.session.delete(api_url,
                                                headers=self.headers,
                                                **kwargs)
