import requests
import json

from survey_monkey.helpers.Util import read_file, get_param_names, get_full_endpoint_path, get_headers, get_url
from survey_monkey.helpers.Constants import DEFAULT_ENDPOINTS_FILE_PATH, DEFAULT_VERSION
from survey_monkey.helpers.Exceptions import SurveyMonkeyAPIException


class Client:

    def __init__(self, access_token, version=DEFAULT_VERSION, endpoints_file_path=DEFAULT_ENDPOINTS_FILE_PATH):
        """
        Creates the API interface

        :param access_token: Survey Monkey access token (string)
        :param version: Survey Monkey API version (string)
        :param endpoints_file_path: Absolute path for endpoints.json file (string)
        """

        self._version = version

        endpoints_json = json.loads(read_file(endpoints_file_path))
        for endpoint in endpoints_json:
            endpoint_function = self._get_endpoint_function(endpoint, access_token)
            setattr(self, endpoint["identifier"], endpoint_function)

    @property
    def version(self):
        return self._version

    def _get_endpoint_function(self, endpoint, access_token):
        """
        Produces function that interacts with the Survey Monkey API based on endpoint schema

        :param endpoint: the endpoint schema for the Survey Monkey API endpoint (dict)
        :param access_token: Survey Monkey access token (string)
        :return: (function)
        """

        identifier = endpoint["identifier"]
        path = endpoint["endpoint path"]
        param_names = get_param_names(path)

        def endpoint_function(*args, **request_kwargs):
            """
            Endpoint function

            :param args: function arguments (list)
            :param request_kwargs: requests.request kwargs
            :return: (dict)
            """

            if len(args) != len(param_names):
                raise SurveyMonkeyAPIException({
                    "message": "{0} expects {1} arguments but got {2} arguments".format(
                        identifier,
                        len(param_names),
                        len(args)
                    )
                })

            return self._request(
                endpoint["method"],
                get_full_endpoint_path(path, param_names, args),
                access_token,
                **request_kwargs
            )

        endpoint_function.__name__ = identifier
        return endpoint_function

    def _request(self, method, path, access_token, **request_kwargs):
        """
        Wrapper for requests.request

        :param method: HTTP method such that method in {"GET", "POST", ...} (string)
        :param path: endpoint path (contains params) (string)
        :param access_token: Survey Monkey API access token (string)
        :param request_kwargs: requests.request kwargs
        :return: (dict)
        """

        request_kwargs["headers"] = get_headers(
            request_kwargs.get("headers", {}),
            access_token
        )

        url = get_url(self.version, path)
        response = requests.request(method, url, **request_kwargs)

        return self._handle_response(response)

    def _handle_response(self, response):
        """
        Handles responses. If response is invalid, raises a SurveyMonkeyAPIException

        :param response: response from API (response object)
        :return: (dict)
        """

        if not response.content:
            raise SurveyMonkeyAPIException({
                "message": "no content in response",
                "response": response.json()
            })

        if not response.ok:
            raise SurveyMonkeyAPIException({
                "message": "Method: {0}, URL: {1}, Status Code: {2}".format(
                    response.request.method,
                    response.request.url,
                    response.status_code
                ),
                "response": response.json()
            })

        return response.json()
