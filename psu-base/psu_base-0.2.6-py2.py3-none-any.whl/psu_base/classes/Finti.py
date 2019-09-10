from django.conf import settings
from psu_base.classes.Log import Log
import requests
import json

log = Log()


class Finti:
    token = None
    finti_url = None
    auth = None
    content_type = {'Content-Type': 'application/json'}

    ### Calls with JWT
    def jwt_get(self, request, path=None, parameters=None, include_metadata=False):
        """
        If a JWT must be provided, it must be given to Finti in the Authorization header, which means that
        this app cannot send its own token in the Authorization header as it will in all other requests.
        Therefore, this function sends the JWT rather than the service token for authentication.
        """
        log.trace()
        try:
            # Get the JWT from the authorization header (sent from a Vue app)
            auth_header = self.get_jwt_header(request)

            api_url = self.get_url(path)
            parameters = parameters if parameters else {}

            log.info("Calling {0}".format(api_url))
            response = requests.get(api_url, params=parameters, headers=auth_header, verify=False)

            response_data = response.json()
            if include_metadata:
                return response_data
            return response_data['message']
        except Exception as ee:
            log.error("Finti JWT GET error: {}".format(ee))
            return None

    def jwt_delete(self, request):
        """ TO DO: implement DELETE calls """
        log.trace()
        return None

    def jwt_post(self, request, path=None, payload=None, parameters=None, headers=None, include_metadata=False):
        log.trace([path, payload, parameters])
        try:
            auth_header = self.get_jwt_header(request)

            api_url = self.get_url(path)
            parameters = parameters if parameters else {}
            headers = self.check_content_header(headers if headers else {})
            headers.update(auth_header)

            log.info("Calling {0}".format(api_url))
            response = requests.post(
                api_url, data=payload, headers=headers, auth=self.auth, verify=False,
                hooks={'response': self.handle_response}
            )

            response_data = response.json()
            if include_metadata:
                return response_data
            return response_data['message']
        except Exception as ee:
            log.error("Finti JWT POST error: {}".format(ee))
            return "ERROR"

    def jwt_put(self, request, path=None, payload=None, parameters=None, headers=None, include_metadata=False):
        log.trace([path, payload, parameters])
        try:
            auth_header = self.get_jwt_header(request)

            api_url = self.get_url(path)
            log.info("Calling {0}".format(api_url))
            parameters = parameters if parameters else {}
            headers = self.check_content_header(headers if headers else {})
            headers.update(auth_header)

            response = requests.put(
                api_url, data=payload, headers=headers, auth=self.auth, verify=False,
                hooks={'response': self.handle_response}
            )

            response_data = response.json()
            if include_metadata:
                return response_data
            return response_data['message']
        except Exception as ee:
            log.error("Finti JWT PUT error: {}".format(ee))
            return "ERROR"

    # Calls with regular/registered Finti tokens
    def get(self, path, parameters=None, include_metadata=False):
        """
        Get a response from Finti
        :param path:             Finti path relative to root Finti URL
        :param parameters:       Object (map) of parameters to send to Finti
        :param include_metadata: Include status, version, result, jwt?              (default: False)
        """
        log.trace([path, parameters])
        result = None
        try:
            params = parameters if parameters else {}
            api_url = self.get_url(path)
            log.info("Calling {0}".format(api_url))

            response = requests.get(
                api_url, params=params, auth=self.auth, verify=False,
                hooks={'response': self.handle_response}
            )

            response_data = response.json()
            result = response_data if include_metadata else response_data['message']
        except Exception as ee:
            log.error("Finti GET error: {}".format(ee))
        log.end(type(result))
        return result

    # @elapsed
    def delete(self, path, parameters=None, include_metadata=False):
        """
        Make a DELETE call on Finti API
        :param path:             Finti path relative to root Finti URL
        :param parameters:       Object (map) of parameters to send to Finti
        :param include_metadata: Include status, version, result, jwt?              (default: False)
        """
        log.trace([path, parameters])
        try:
            params = parameters if parameters else {}
            api_url = self.get_url(path)
            log.info("Calling {0}".format(api_url))

            response = requests.delete(
                api_url, params=params, auth=self.auth, verify=False,
                hooks={'response': self.handle_response}
            )

            response_data = response.json()
            if include_metadata:
                return response_data
            return response_data['message']

        except Exception as ee:
            log.error("Finti DELETE error: {}".format(ee))
            return None

    # @elapsed
    def post(self, path, payload=None, parameters=None, headers=None, include_metadata=False):
        log.trace([path, payload, parameters])
        try:
            params = parameters if parameters else {}
            api_url = self.get_url(path)
            headers = self.check_content_header(headers if headers else {})

            log.info("Calling {0}".format(api_url))

            response = requests.post(
                api_url, data=payload if payload else {}, headers=headers, auth=self.auth, verify=False,
                hooks={'response': self.handle_response}
            )

            response_data = response.json()
            if include_metadata:
                return response_data
            return response_data['message']
        except Exception as ee:
            log.error("Finti POST error: {}".format(ee))
            return "ERROR"

    # @elapsed
    def put(self, path, payload=None, parameters=None, headers=None, include_metadata=False):
        log.trace([path, payload, parameters])
        try:
            params = parameters if parameters else {}
            api_url = self.get_url(path)
            headers = self.check_content_header(headers if headers else {})

            log.info("Calling {0}".format(api_url))

            response = requests.put(
                api_url, data=payload if payload else {}, headers=headers, auth=self.auth, verify=False,
                hooks={'response': self.handle_response}
            )

            response_data = response.json()
            if include_metadata:
                return response_data
            return response_data['message']
        except Exception as ee:
            log.error("Finti PUT error: {}".format(ee))
            return "ERROR"

    @staticmethod
    def handle_response(response, *args, **kwargs):
        """No need to call this directly. This is called via the get method"""
        wdt_response = {
            'status': '',
            'result': '',
            'version': None,
            'jwt': None,
            'message': ''}
        try:
            log.debug("RESPONSE OBJECT: ({}) {:140.140}...(truncated)".format(response.status_code, response.text))
            wdt_response['status'] = response.status_code

            # Some responses have json-able content, some don't

            if response.status_code == requests.codes.OK:
                try:
                    response_data = response.json()

                    # log.debug("RESPONSE DATA: {}...(truncated)".format(response._content))
                    wdt_response['result'] = 'success'

                    # Check if response structure is the same as wdt_response
                    if type(response_data) in [list, str] or len(set(wdt_response.keys()).difference(set(response_data.keys()))) > 0:
                        wdt_response['message'] = response_data
                    else:
                        return response
                except Exception as ex:
                    response_data = response.text
                    wdt_response['result'] = 'error'
                    wdt_response['message'] = response.text
                    log.error('Status code was OK, but response is not JSON: {}'.format(ex))

            elif response.status_code == requests.codes.NOT_FOUND:
                response_data = response.json()
                wdt_response['result'] = 'not_found'

                # Check if response structure is the same as wdt_response
                if type(response_data) == str or len(set(wdt_response.keys()).difference(set(response_data.keys()))) > 0:
                    wdt_response['message'] =  response_data

                    # log.debug("WDT_RESPONSE: {}".format(wdt_response))
                else:
                    return response

            else:
                log.error("API Unsuccessful:\n{0}".format(response.text))
                if response.status_code == requests.codes.FORBIDDEN:
                    wdt_response['result'] = 'forbidden'
                else:
                    wdt_response['result'] = 'error'
                message = ''
                try:
                    response_data = response.json()
                    if len(set(wdt_response.keys()).difference(set(response_data.keys()))) > 0:
                        wdt_response['message'] =  response_data
                    else:
                        return response
                    message = response_data['error']
                except Exception as ee:
                    message = response.text
                wdt_response['message'] = message

        except Exception as ee:
            log.error("Error handling Finti response: {}".format(ee))
            log.info("Finti response: {}".format(response))

        # Overwrite content with wdt_response format
        response._content = json.dumps(wdt_response).encode('utf-8')
        return response

    def get_url(self, relative_path=''):
        """No need to call this directly. This is called via the get method"""
        return f"{self.finti_url}/{relative_path}".strip('/')

    @staticmethod
    def get_jwt_header(request):
        jwt = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
        return {'Authorization': "Bearer: {}".format(jwt)}

    def check_content_header(self, headers):
        if any((True for ct in ['content-type', 'Content-Type'] if ct in headers.keys())):
            return headers
        return headers.update(self.content_type)

    def __init__(self):
        log.trace()
        self.token = settings.FINTI_TOKEN
        self.finti_url = settings.FINTI_URL.strip('/')
        self.auth = (self.token, '')
