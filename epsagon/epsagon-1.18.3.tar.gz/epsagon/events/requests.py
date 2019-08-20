"""
requests events module.
Currently it instruments only botocore.vendored.requests.
For regular requests lib, we use urllib3
"""

from __future__ import absolute_import
import traceback
from uuid import uuid4

from epsagon.utils import add_data_if_needed
from ..trace import trace_factory
from ..event import BaseEvent
from ..http_filters import is_blacklisted_url
from ..utils import update_api_gateway_headers, normalize_http_url
from ..constants import HTTP_ERR_CODE


class RequestsEvent(BaseEvent):
    """
    Represents base requests event.
    """

    ORIGIN = 'requests'
    RESOURCE_TYPE = 'http'

    #pylint: disable=W0613
    def __init__(self, wrapped, instance, args, kwargs, start_time, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param start_time: Start timestamp (epoch)
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(RequestsEvent, self).__init__(start_time)

        self.event_id = 'requests-{}'.format(str(uuid4()))

        prepared_request = args[0]
        self.resource['name'] = normalize_http_url(prepared_request.url)
        self.resource['operation'] = prepared_request.method
        self.resource['metadata']['url'] = prepared_request.url

        add_data_if_needed(
            self.resource['metadata'],
            'request_headers',
            dict(prepared_request.headers)
        )

        add_data_if_needed(
            self.resource['metadata'],
            'request_body',
            prepared_request.body
        )

        if response is not None:
            self.update_response(response)

        if exception is not None:
            self.set_exception(exception, traceback.format_exc())

    def update_response(self, response):
        """
        Adds response data to event.
        :param response: Response from botocore
        :return: None
        """

        self.resource['metadata']['status_code'] = response.status_code
        self.resource = update_api_gateway_headers(
            self.resource,
            response.headers
        )

        add_data_if_needed(
            self.resource['metadata'],
            'response_headers',
            dict(response.headers)
        )

        # Extract only json responses
        self.resource['metadata']['response_body'] = None
        try:
            add_data_if_needed(
                self.resource['metadata'],
                'response_body',
                response.json()
            )
        except ValueError:
            pass

        # Detect errors based on status code
        if response.status_code >= HTTP_ERR_CODE:
            self.set_error()


class RequestsEventFactory(object):
    """
    Factory class, generates requests event.
    """

    @staticmethod
    def create_event(wrapped, instance, args, kwargs, start_time, response,
                     exception):
        """
        Create an event according to the given api_name.
        """
        prepared_request = args[0]
        # Detect if URL is blacklisted, and ignore.
        if is_blacklisted_url(prepared_request.url):
            return

        event = RequestsEvent(
            wrapped,
            instance,
            args,
            kwargs,
            start_time,
            response,
            exception
        )

        trace_factory.add_event(event)
