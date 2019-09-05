#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# Copyright (C) 2019 Matilda Peak - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
# -----------------------------------------------------------------------------

"""A class handling transmission of data to Chronicler.
"""

import os
from datetime import datetime, timedelta
import logging
import requests
from multiprocessing import Process, Queue
import queue

_LOGGER = logging.getLogger('chroniclerTransmitter')

# Chronicler POST timeout
_CHRONICLER_POST_TIMEOUT_S = 2.0
# Maximum consecutive Chronicler transmission errors
# before we give up transmitting.
_CHRONICLER_MAX_CONSECUTIVE_ERR_COUNT = 50
# The maximum time we stop sending.
# We stop sending if there's been a transmission error
# but we'll try again after this period of time...
_MAX_STOP_SENDING_AGE = timedelta(minutes=8)

# Key values for application material
# in messages sent to Chronicler
_APP_ID_HDR_KEY = 'X-MP-AppId'
_APP_CODE_HDR_KEY = 'X-MP-AppCode'

# Timeout reading from the internal async queue.
# This must be greater than zero.
_ASYNC_QUEUE_TIMEOUT_S = 2.0


class ChroniclerTransmitter:
    """A class handling transmission of data to Chronicler.
    """

    def __init__(self, url: str, resource: str, app_id: str, app_code: str):
        """Creates a new ChroniclerTransmitter that can send to Chronicler
        at the url and resources defined. These would typically be
        something like 'http://chronicler.matildapeak.io:9090' and
        'inbound/matildapeak/test/default/curl/test-event' respectively.

        To prevent rejection from Chronicler you must provide a valid
        application ID and application secret code.

        :param url: The base URL
        :type url" ``str``
        :param resource: The inbound resource
        :type resource: ``str``
        :param app_id: Your application ID
        :type app_id: ``str``
        :param app_code: Your application secret
        :type app_code: ``str``
        """

        assert url
        assert isinstance(url, str)
        assert len(url)
        assert resource
        assert isinstance(resource, str)
        assert len(resource)
        assert app_id
        assert isinstance(app_id, str)
        assert len(app_id)
        assert app_code
        assert isinstance(app_code, str)
        assert len(app_code)
        assert _ASYNC_QUEUE_TIMEOUT_S > 0.0

        self._url = url
        self._resource = resource
        self._chronicler_resource = os.path.join(url, resource)

        # An asynchronous queue,
        # used whn the post_async() method is used.
        self._async_queue = None
        self._async_process = None
        self._async_run = False

        # The application ID and corresponding secret code are passed
        # to Chronicler in the HTTP header.
        self._post_header = {_APP_ID_HDR_KEY: app_id,
                             _APP_CODE_HDR_KEY: app_code}

        # The number of consecutive POST errors.
        # Once this reaches _CHRONICLER_MAX_CONSECUTIVE_ERR_COUNT the
        # transmitter switches itself off by setting _stop_sending.
        # Reset after successful transmission unless already stopped.
        self._consecutive_error_count = 0
        # An array of the various unsuccessful response codes received
        # (i.e. all those excluding code 201).
        # This is used to log each new error response once.
        self._send_rejection_codes = []
        # A flag to stop sending.
        # This set from within this class
        # if we get too many consecutive errors.
        self._stop_sending = False
        # And the time we stopped sending.
        # We'll try again after _MAX_STOP_SENDING_AGE
        self._stop_sending_time = None

        # The latest (longest) POST duration.
        # Logged each time it increases.
        #
        # In early tests (running from home)
        # I've seen a peak of around 900mS.
        # But ignore any posts that take longer than 500mS.
        self._longest_post = timedelta(seconds=0.5)

    def post(self, payload: dict) -> bool:
        """Sends the payload to Chronicler.
        This method does nothing if the Chronicler URL is not set
        or if there have been too many transmission errors.

        If you want to avoid blocking use the ``post_async()``
        method of this class.

        :param payload: A data item
        :type payload: ``dict``
        :returns: True on success
        :rtype: ``bool``
        """
        assert payload

        # Do nothing if Chronicler address isn't known.
        if not self._url:
            return False
        # If we've stopped sending should we try again?
        if self._stop_sending:
            if datetime.now() - self._stop_sending_time >= \
                    _MAX_STOP_SENDING_AGE:
                _LOGGER.info('Stopped sending for long enough,'
                             ' trying again...')
                self._stop_sending = False
                self._stop_sending_time = None
                self._consecutive_error_count = 0
            else:
                # Not stopped sending for long enough.
                # Ignore this payload.
                return False

        # Post...

        # Timestamp the start of the POST...
        post_start_time = datetime.now()

        # Send the data (a dictionary), expecting a 201 response.
        # At the moment Chronicler expects something in the body (data).
        resp = None
        try:
            resp = requests.post(self._chronicler_resource,
                                 headers=self._post_header,
                                 params=payload,
                                 data='-',
                                 timeout=_CHRONICLER_POST_TIMEOUT_S)
        except requests.exceptions.ConnectionError as con_err:
            _LOGGER.debug('ConnectionError (%s)', con_err)
        except requests.exceptions.ReadTimeout as rd_err:
            _LOGGER.debug('ReadTimeout (%s)', rd_err)
        except TimeoutError:
            _LOGGER.debug('TimeoutError')

        # How long did the POST take?
        elapsed_time = datetime.now() - post_start_time
        _LOGGER.debug('POST elapsed_time=%s', elapsed_time)

        # Analyse...

        # Assume success
        ret_val = True

        # Did we encounter a transmission error?
        # And have we had too many?
        if not resp:

            # A warning if the first time, debug for others
            if self._consecutive_error_count == 0:
                _LOGGER.warning('Failed to get a response from "%s"'
                                ' (first offence)', self._chronicler_resource)
            else:
                _LOGGER.debug('Failed to get a response from "%s"',
                              self._chronicler_resource)

            # Have we had too many consecutive errors?
            self._consecutive_error_count += 1

            # A failure
            ret_val = False

        else:

            # We got a response, but was it rejected...

            status = resp.status_code
            if status != 201:

                # Count this in our consecutive error count
                self._consecutive_error_count += 1
                # Warn, once for each type of rejection
                if status not in self._send_rejection_codes:
                    _LOGGER.warning('Chronicler rejected message'
                                    ' with new status code (%s)', status)
                    self._send_rejection_codes.append(status)

                # A failure
                ret_val = False

            else:

                # Success
                _LOGGER.debug('Sent')

                # Do we need to reset the consecutive error count?
                if self._consecutive_error_count:
                    _LOGGER.info('Recovered from %s transmission errors.',
                                 self._consecutive_error_count)
                    self._consecutive_error_count = 0

                # Log if that was the longest...
                if elapsed_time > self._longest_post:
                    self._longest_post = elapsed_time
                    _LOGGER.info('New longest successful POST duration (%s)',
                                 elapsed_time)

        # Failure? And too many?
        if not ret_val and self._consecutive_error_count >= \
                _CHRONICLER_MAX_CONSECUTIVE_ERR_COUNT:

            _LOGGER.error("Too many Chronicler transmission errors (%s)."
                          " Will try again after %s.",
                          self._consecutive_error_count,
                          _MAX_STOP_SENDING_AGE)
            self._stop_sending = True
            self._stop_sending_time = datetime.now()

        # Done
        return ret_val

    def _post_async(self) -> None:
        """A multiprocessing Process to pull things off the internal
        queue and write them to our post() method.
        """
        assert self._async_queue

        # Wait on the internal queue
        # while we're running
        while self._async_run:
            # Wait on the queue
            payload = None
            try:
                payload = self._async_queue.get(False, _ASYNC_QUEUE_TIMEOUT_S)
            except queue.Empty:
                pass
            if payload:
                _LOGGER.debug('Picked-up payload. Sending...')
                self.post(payload)

    def post_async(self, payload: dict) -> None:
        """Post a message to Chronicler asynchronously. This essentially
        calls our ``post()`` method without blocking the user's calling
        thread by using a process and connecting queue.

        If you use this method you must call ``stop_async()`` when you come
        to discarding te class object.
        """
        if self._async_queue is None:
            # No queue so this is the first async call.
            # Create a queue and start the process to read from it...
            self._async_run = True
            self._async_queue = Queue()
            self._async_process = Process(target=self._post_async)
            self._async_process.start()

        # Now, just put the payload on the queue and return to the caller
        self._async_queue.put(payload)

    def stop_async(self) -> None:
        """Stops the asynchronous process
        (so the class instance can be removed).

        This call blocks until the internal asynchronous process has stopped.
        """
        self._async_run = False
        self._async_process.join()

        self._async_queue = None
        self._async_process = None
