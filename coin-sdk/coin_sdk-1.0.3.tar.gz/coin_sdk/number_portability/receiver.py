import logging
import time
from abc import abstractmethod, ABC
from json import JSONDecodeError
from typing import Type, Optional, Callable

import sseclient
from requests import ConnectionError
from requests.exceptions import ChunkedEncodingError, ReadTimeout

from coin_sdk.number_portability.domain import MessageType, ConfirmationStatus
from coin_sdk.common.securityservice import SecurityService
from coin_sdk.number_portability.utils import json2obj, handle_http_error, get_stream
from coin_sdk.number_portability.npconfig import NpConfig

logger = logging.getLogger(__name__)


class OffsetPersister(ABC):
    @abstractmethod
    def persist_offset(self, offset):
        pass

    @abstractmethod
    def get_persisted_offset(self):
        pass


class Receiver(ABC):
    class RetriesLeft:
        def __init__(self, config: NpConfig):
            self._config = config
            self.reset()

        def reset(self):
            self._backoff_period = self._config._backoff_period
            self._number_of_retries = self._config._number_of_retries

        def get(self):
            return self._number_of_retries

        def __call__(self):
            return self._number_of_retries > 0

        def backoff(self):
            logger.error(f'Trying to reconnect in {self._backoff_period} seconds. Retries left: {self.get()}')
            time.sleep(self._backoff_period)
            self._number_of_retries -= 1
            self._backoff_period = min(self._backoff_period*2,60)


    def __init__(self, config: NpConfig):
        self._security_service = SecurityService(config)
        self._config = config
        self._offset_persister: Optional[OffsetPersister] = None
        self._recover_offset: Callable[[int], int] = lambda x: x
        self._event_map = {
            MessageType.PORTING_REQUEST_V1.get_event_type(): self.on_porting_request,
            MessageType.PORTING_REQUEST_ANSWER_V1.get_event_type(): self.on_porting_request_answer,
            MessageType.PORTING_REQUEST_ANSWER_DELAYED_V1.get_event_type(): self.on_porting_request_answer_delayed,
            MessageType.PORTING_PERFORMED_V1.get_event_type(): self.on_porting_performed,
            MessageType.DEACTIVATION_V1.get_event_type(): self.on_deactivation,
            MessageType.CANCEL_V1.get_event_type(): self.on_cancel,
            MessageType.ERROR_FOUND_V1.get_event_type(): self.on_error_found,
            MessageType.ACTIVATION_SERVICE_NUMBER_V1.get_event_type(): self.on_activation_service_number,
            MessageType.DEACTIVATION_SERVICE_NUMBER_V1.get_event_type(): self.on_deactivation_service_number,
            MessageType.TARIFF_CHANGE_SERVICE_NUMBER_V1.get_event_type(): self.on_tariff_change_service_number,
            MessageType.RANGE_ACTIVATION_V1.get_event_type(): self.on_range_activation,
            MessageType.RANGE_DEACTIVATION_V1.get_event_type(): self.on_range_deactivation,

            MessageType.ENUM_ACTIVATION_NUMBER_V1.get_event_type(): self.on_enum_activation_number,
            MessageType.ENUM_ACTIVATION_OPERATOR_V1.get_event_type(): self.on_enum_activation_operator,
            MessageType.ENUM_ACTIVATION_RANGE_V1.get_event_type(): self.on_enum_activation_range,
            MessageType.ENUM_DEACTIVATION_NUMBER_V1.get_event_type(): self.on_enum_deactivation_number,
            MessageType.ENUM_DEACTIVATION_OPERATOR_V1.get_event_type(): self.on_enum_deactivation_operator,
            MessageType.ENUM_DEACTIVATION_RANGE_V1.get_event_type(): self.on_enum_deactivation_range,
            MessageType.ENUM_PROFILE_ACTIVATION_V1.get_event_type(): self.on_enum_profile_activation,
            MessageType.ENUM_PROFILE_DEACTIVATION_V1.get_event_type(): self.on_enum_profile_deactivation,
        }

    def start_stream(
            self,
            offset: int = None,
            confirmation_status: ConfirmationStatus = None,
            offset_persister: Type[OffsetPersister] = None,
            recover_offset: Callable[[int], int] = lambda x: x,
            message_types: [MessageType] = None
    ):
        self._running = True
        self._setup(confirmation_status, offset_persister, recover_offset)
        retries_left = self.RetriesLeft(self._config)
        while retries_left():
            try:
                self._connect(offset, confirmation_status, message_types, retries_left)
                return
            except (ConnectionError, ChunkedEncodingError, ReadTimeout) as e:
                # ChunckedEncodingError occurs when backend stops while waiting for new events
                logger.error(type(e).__name__)
                logger.error(e)
                if self._offset_persister:
                    offset = self._offset_persister.get_persisted_offset()
                    offset = self._recover_offset(offset)
                retries_left.backoff();

    def _setup(
            self,
            confirmation_status: ConfirmationStatus,
            offset_persister: Type[OffsetPersister],
            recover_offset: Callable[[int], int]
    ):
        if confirmation_status == ConfirmationStatus.ALL and not offset_persister:
            raise ValueError('offset_persister should be given when confirmation_status equals ALL')
        if offset_persister and not issubclass(offset_persister, OffsetPersister):
            raise ValueError(f'offset_persister should be a subclass of {OffsetPersister.__module__}.OffsetPersister')
        self._offset_persister = offset_persister and offset_persister()
        self._recover_offset = recover_offset

    def _connect(self, offset: int, confirmation_status: ConfirmationStatus, message_types: [MessageType], retries_left: RetriesLeft):
        logger.debug('Opening stream')
        response = get_stream(self._config.sse_url, offset, confirmation_status, message_types, self._security_service)
        logger.debug(f'url: {response.request.url}')
        handle_http_error(response)
        client = sseclient.SSEClient(response)
        retries_left.reset()
        self._consume_stream(client)

    def _consume_stream(self, client: sseclient.SSEClient):
        for event in client.events():
            if self._running == False:
                return
            logger.debug('Received event')
            logger.debug(f'{event}')
            if event.data:
                self._process_event(event)
            else:
                self.on_keep_alive(event.id)

    def stop(self):
        self._running = False

    def _process_event(self, event):
        try:
            event_type = event.event.lower()
            logger.debug(f'Event: {event.event}')
            message = json2obj(event.data).message
            logger.debug(f'Message: {message}')
            message_id = event.id
            logger.debug(f'Message id: {message_id}')
            event_handler = self._event_map.get(event_type, None)
            if event_handler:
                event_handler(message_id, message)
                self._persist_offset(message_id)
            else:
                logger.error(f"Number Portability Message with the following content isn't supported: {event}")
        except (JSONDecodeError, AttributeError):
            logger.error(f"Conversion of Number Portability Message failed for the following event: {event}")

    def _persist_offset(self, message_id):
        if self._offset_persister:
            self._offset_persister.persist_offset(message_id)

    @abstractmethod
    def on_keep_alive(self, message_id):
        pass

    @abstractmethod
    def on_porting_request(self, message_id, message):
        pass

    @abstractmethod
    def on_porting_request_answer(self, message_id, message):
        pass

    @abstractmethod
    def on_porting_request_answer_delayed(self, message_id, message):
        pass

    @abstractmethod
    def on_porting_performed(self, message_id, message):
        pass

    @abstractmethod
    def on_deactivation(self, message_id, message):
        pass

    @abstractmethod
    def on_cancel(self, message_id, message):
        pass

    @abstractmethod
    def on_error_found(self, message_id, message):
        pass

    @abstractmethod
    def on_activation_service_number(self, message_id, message):
        pass

    @abstractmethod
    def on_deactivation_service_number(self, message_id, message):
        pass

    @abstractmethod
    def on_tariff_change_service_number(self, message_id, message):
        pass

    @abstractmethod
    def on_range_activation(self, message_id, message):
        pass

    @abstractmethod
    def on_range_deactivation(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_activation_number(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_activation_range(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_activation_operator(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_deactivation_number(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_deactivation_range(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_deactivation_operator(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_profile_activation(self, message_id, message):
        pass

    @abstractmethod
    def on_enum_profile_deactivation(self, message_id, message):
        pass
