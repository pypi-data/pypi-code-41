# -*- coding: utf-8 -*-
import collections
import datetime
import logging
import json
import sys
import requests
import time

import six
from six.moves.urllib import parse

from .sys_exit_if_needed import sys_exit_if_needed
from .exceptions import NonRetryException
from .eprint import eprint
from .config import get_prefix_section, Config

BASE_URL_PATH = '_ah/api/missinglink/v1/'
GAE_REQUEST_TIMEOUT = datetime.timedelta(seconds=60)
API_REQUEST_MAX_TIMEOUT_TIME = datetime.timedelta(minutes=15)


def _urljoin(*args):
    base = args[0]
    for u in args[1:]:
        base = parse.urljoin(base, u)

    return base


def add_url_params(url, **params):
    from six.moves.urllib.parse import urlencode, unquote, urlparse, parse_qsl, ParseResult

    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    parsed_get_args = collections.OrderedDict(sorted(parsed_get_args.items()))

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: json.dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    # noinspection PyArgumentList
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url


def default_api_retry(stop_max_attempt_number=None):
    from retrying import Retrying

    def retry_if_retry_possible_error(exception):
        if isinstance(exception, (AssertionError, AttributeError)):
            return False

        if isinstance(exception, requests.HTTPError) and exception.response.status_code in (400, 403, 404):
            logging.error('got retry exception (api) %s', exception)
            return False

        logging.debug('got retry exception (api) %s', exception)

        return True

    return Retrying(
        retry_on_exception=retry_if_retry_possible_error,
        wait_exponential_multiplier=50,
        wait_exponential_max=5000,
        stop_max_attempt_number=stop_max_attempt_number)


class ApiCallerException(NonRetryException):
    pass


class _HttpCaller(object):
    def __init__(self, config, http_session, **kwargs):
        self.__config = config
        self.__http_session = http_session
        self.__kwargs = kwargs

    @classmethod
    def __get_method_kwargs(cls, http_method_name, headers, data):
        method_kwargs = {
            'headers': headers
        }

        # data in this case means params
        if http_method_name == 'get' and data is not None:
            method_kwargs['params'] = data
            data = None

        if data is not None:
            method_kwargs['json'] = data

        return method_kwargs

    def __sys_exit_and_eprint(self, error_message):
        with sys_exit_if_needed(**self.__kwargs) as throw_exception:
            if throw_exception:
                exc_info = sys.exc_info()
                e = exc_info[1]

                six.raise_from(ApiCallerException(error_message.strip()), e)

            eprint(error_message)

    def __refresh_token_id_token(self):
        id_token = None

        try:
            id_token = ApiCaller.update_token(self.__config, self.__http_session)
        except requests.HTTPError:
            self.__sys_exit_and_eprint('Authorization failed, try running "ml auth init" again')

        return id_token

    def __api_call(self, http_method_name, url, data):
        id_token = self.__config.id_token if self.__config.id_token else self.__refresh_token_id_token()

        start_time = datetime.datetime.now()
        auth_attempt = 0
        while True:
            attempt_start = datetime.datetime.now()
            headers = {'Authorization': 'Bearer {}'.format(id_token)}
            http_method_name = http_method_name.lower()
            http_method_exec = getattr(self.__http_session, http_method_name)

            r = http_method_exec(url, **self.__get_method_kwargs(http_method_name, headers, data))
            if r.status_code == 401:
                id_token = self.__refresh_token_id_token()
                auth_attempt += 1
                if auth_attempt < 3:
                    continue

                self.__sys_exit_and_eprint('failed to refresh the token, rerun auth init again')

            if r.status_code == 500:
                finish_time = datetime.datetime.now()
                request_runtime = finish_time - attempt_start
                total_runtime = finish_time - start_time
                if request_runtime > GAE_REQUEST_TIMEOUT and total_runtime < API_REQUEST_MAX_TIMEOUT_TIME:
                    continue

            r.raise_for_status()
            return r

    def __handle_sync_api_exc(self, ex):
        try:
            error_message = ex.response.json().get('error', {}).get('message')
        except ValueError:
            error_message = None

        if error_message is None:
            error_message = str(ex)

        self.__sys_exit_and_eprint('\n' + error_message)

    def handle_sync_api(self, http_method_name, method_url, data=None, retry=None):
        if self.__config.refresh_token is None:
            self.__sys_exit_and_eprint('Please run: "ml auth init" to setup authorization')

        url = _urljoin(self.__config.api_host, BASE_URL_PATH, method_url)

        def api_call_with_retry(*args, **kwargs):
            return retry.call(self.__api_call, *args, **kwargs)

        f = self.__api_call if retry is None else api_call_with_retry

        try:
            r = f(http_method_name, url, data)
            return r, r.json()
        except requests.exceptions.HTTPError as ex:
            self.__handle_sync_api_exc(ex)

    @classmethod
    def __infinite_async_api_loop_raise_if_needed(cls, result):
        if result.get('failed'):
            msg = result.get('error_message', 'Internal Server Error %s' % json.dumps(result))
            raise NonRetryException(msg)

    def __infinite_async_api_loop(self, token):
        while True:
            r, result = self.handle_sync_api('get', 'data_volumes/tasks/' + token, retry=default_api_retry())

            self.__infinite_async_api_loop_raise_if_needed(result)

            if result.get('finished'):
                return r, json.loads(result['results']) if 'results' in result else None

            time.sleep(2.0)

    def handle_async_api(self, http_method_name, method_url, data, retry):
        if data is not None:
            data['async'] = True
        else:
            method_url = add_url_params(method_url, **{'async': True})

        retry = retry or default_api_retry()
        r, result = self.handle_sync_api(http_method_name, method_url, data, retry)

        if 'token' not in result:
            return r, result

        token = result['token']

        return self.__infinite_async_api_loop(token)


class ApiCaller(object):
    @classmethod
    def call(cls, ctx_or_config, http_session, http_method_name, method_url, data=None, retry=None, is_async=False, on_response=None, throw_exception=False, **kwargs):
        config = ctx_or_config if isinstance(ctx_or_config, Config) else ctx_or_config.config

        caller = _HttpCaller(config, http_session, throw_exception=throw_exception, **kwargs)

        method = caller.handle_async_api if is_async else caller.handle_sync_api
        r, result = method(http_method_name, method_url, data, retry)

        if on_response:
            on_response(r)

        return result

    @classmethod
    def _should_retry_ml_auth(cls, exception):
        import requests

        logging.debug('got retry exception (ml auth) %s', exception)

        error_codes_to_retries = [
            429,  # Too many requests
        ]

        return isinstance(exception, requests.exceptions.HTTPError) and exception.response.status_code in error_codes_to_retries

    @classmethod
    def update_token(cls, config, http_session):
        from retrying import retry

        @retry(retry_on_exception=cls._should_retry_ml_auth)
        def with_retry():
            url = _urljoin(config.api_host, BASE_URL_PATH, 'users/refresh_token')

            r = http_session.post(
                url,
                json={
                    'refresh_token': config.refresh_token,
                })

            r.raise_for_status()

            data = r.json()

            section = get_prefix_section(config.config_prefix, 'token')
            config.set(section, 'id_token', data['id_token'])
            config.save()

            return data['id_token']

        return with_retry()
