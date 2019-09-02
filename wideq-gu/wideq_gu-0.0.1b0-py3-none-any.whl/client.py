"""A high-level, convenient abstraction for interacting with the LG
SmartThinQ API for most use cases.
"""
import json
import enum
import logging
import requests
import base64
from collections import namedtuple
from typing import Any, Optional

from . import core

DEFAULT_COUNTRY = 'KR'
DEFAULT_LANGUAGE = 'ko-KR'
#: Represents an unknown enum value.
_UNKNOWN = 'Unknown'
DEBUG_MODE = False

class Monitor(object):
    """A monitoring task for a device.

    This task is robust to some API-level failures. If the monitoring
    task expires, it attempts to start a new one automatically. This
    makes one `Monitor` object suitable for long-term monitoring.
    """

    def __init__(self, session, device_id):
        self.session = session
        self.device_id = device_id

    def start(self):
        self.work_id = self.session.monitor_start(self.device_id)

    def stop(self):
        self.session.monitor_stop(self.device_id, self.work_id)

    def poll(self):
        """Get the current status data (a bytestring) or None if the
        device is not yet ready.
        """

        try:
            return self.session.monitor_poll(self.device_id, self.work_id)
        except core.MonitorError:
            # Try to restart the task.
            self.stop()
            self.start()
            return None

    @staticmethod
    def decode_json(data):
        """Decode a bytestring that encodes JSON status data."""

        return json.loads(data.decode('utf8'))

    def poll_json(self):
        """For devices where status is reported via JSON data, get the
        decoded status result (or None if status is not available).
        """

        data = self.poll()
        return self.decode_json(data) if data else None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, tb):
        self.stop()


class Client(object):
    """A higher-level API wrapper that provides a session more easily
    and allows serialization of state.
    """

    def __init__(self, gateway=None, auth=None, session=None,
                 country=DEFAULT_COUNTRY, language=DEFAULT_LANGUAGE):
        # The three steps required to get access to call the API.
        self._gateway = gateway
        self._auth = auth
        self._session = session

        # The last list of devices we got from the server. This is the
        # raw JSON list data describing the devices.
        self._devices = None

        # Cached model info data. This is a mapping from URLs to JSON
        # responses.
        self._model_info = {}
        self._lang_pack_product = {}
        self._lang_pack_model = {}

        # Locale information used to discover a gateway, if necessary.
        self._country = country
        self._language = language

    @property
    def gateway(self):
        if not self._gateway:
            self._gateway = core.Gateway.discover(
                self._country, self._language
            )
        return self._gateway

    @property
    def auth(self):
        if not self._auth:
            assert False, "unauthenticated"
        return self._auth

    @property
    def session(self):
        if not self._session:
            self._session, self._devices = self.auth.start_session()
        return self._session

    @property
    def devices(self):
        """DeviceInfo objects describing the user's devices.
        """

        if not self._devices:
            self._devices = self.session.get_devices()
        return (DeviceInfo(d) for d in self._devices)

    def get_device(self, device_id):
        """Look up a DeviceInfo object by device ID.

        Return None if the device does not exist.
        """

        for device in self.devices:
            if device.id == device_id:
                return device
        return None

    @classmethod
    def load(cls, state):
        """Load a client from serialized state.
        """

        client = cls()

        if 'gateway' in state:
            data = state['gateway']
            client._gateway = core.Gateway(
                data['auth_base'], data['api_root'], data['oauth_root'],
                data.get('country', DEFAULT_COUNTRY),
                data.get('language', DEFAULT_LANGUAGE),
            )

        if 'auth' in state:
            data = state['auth']
            client._auth = core.Auth(
                client.gateway, data['access_token'], data['refresh_token']
            )

        if 'session' in state:
            client._session = core.Session(client.auth, state['session'])

        if 'model_info' in state:
            client._model_info = state['model_info']

        if 'lang_pack_product' in state:
            client._lang_pack_product = state['lang_pack_product']

        if 'lang_pack_model' in state:
            client._lang_pack_model = state['lang_pack_model']

        if 'country' in state:
            client._country = state['country']

        if 'language' in state:
            client._language = state['language']

        return client

    def dump(self):
        """Serialize the client state."""

        out = {
            'model_info': self._model_info,
            'lang_pack_product': self._lang_pack_product,
            'lang_pack_model': self._lang_pack_model,
        }

        if self._gateway:
            out['gateway'] = {
                'auth_base': self._gateway.auth_base,
                'api_root': self._gateway.api_root,
                'oauth_root': self._gateway.oauth_root,
                'country': self._gateway.country,
                'language': self._gateway.language,
            }

        if self._auth:
            out['auth'] = {
                'access_token': self._auth.access_token,
                'refresh_token': self._auth.refresh_token,
            }

        if self._session:
            out['session'] = self._session.session_id

        out['country'] = self._country
        out['language'] = self._language

        return out

    def refresh(self):
        self._auth = self.auth.refresh()
        self._session, self._devices = self.auth.start_session()

    @classmethod
    def from_token(cls, refresh_token, country=None, language=None):
        """Construct a client using just a refresh token.

        This allows simpler state storage (e.g., for human-written
        configuration) but it is a little less efficient because we need
        to reload the gateway servers and restart the session.
        """

        client = cls(
            country=country or DEFAULT_COUNTRY,
            language=language or DEFAULT_LANGUAGE,
        )
        client._auth = core.Auth(client.gateway, None, refresh_token)
        client.refresh()
        return client

    def model_info(self, device):
        """For a DeviceInfo object, get a ModelInfo object describing
        the model's capabilities.
        """
        url = device.model_info_url
        if url not in self._model_info:
            self._model_info[url] = device.load_model_info
        return ModelInfo(self._model_info[url])

    def lang_pack_product(self, device):
        """For a LanguagePack object, get a LangPackProduct object describing
        the model's capabilities.
        """
        url = device.lang_pack_product_url
        if url not in self._lang_pack_product:
            self._lang_pack_product[url] = device.load_lang_pack_product
        return LangPackProduct(self._lang_pack_product[url])

    def lang_pack_model(self, device):
        """For a LanguagePack object, get a LangPackModel object describing
        the model's capabilities.
        """
        url = device.lang_pack_model_url
        if url not in self._lang_pack_model:
            self._lang_pack_model[url] = device.load_lang_pack_model
        return LangPackModel(self._lang_pack_model[url])


class DeviceType(enum.Enum):
    """The category of device."""

    REFRIGERATOR = 101
    KIMCHI_REFRIGERATOR = 102
    WATER_PURIFIER = 103
    WASHER = 201
    DRYER = 202
    STYLER = 203
    DISHWASHER = 204
    OVEN = 301
    MICROWAVE = 302
    COOKTOP = 303
    HOOD = 304
    AC = 401  # Includes heat pumps, etc., possibly all HVAC devices.
    AIR_PURIFIER = 402
    DEHUMIDIFIER = 403
    ROBOT_KING = 501  # Robotic vacuum cleaner?
    ARCH = 1001
    MISSG = 3001
    SENSOR = 3002
    SOLAR_SENSOR = 3102
    IOT_LIGHTING = 3003
    IOT_MOTION_SENSOR = 3004
    IOT_SMART_PLUG = 3005
    IOT_DUST_SENSOR = 3006
    EMS_AIR_STATION = 4001
    AIR_SENSOR = 4003

class DeviceTypeKor(enum.Enum):
    """The category of device."""

    냉장고 = 101
    김치냉장고 = 102
    정수기 = 103
    세탁기 = 201
    건조기 = 202
    스타일러 = 203
    식기세척기 = 204
    오븐 = 301
    전자레인지 = 302
    인덕션 = 303
    후드 = 304
    에어컨 = 401  # Includes heat pumps, etc., possibly all HVAC devices.
    공기청정기 = 402
    제습기 = 403
    로보킹 = 501  # Robotic vacuum cleaner?
    TV = 701
    보일러 = 801
    스피커 = 901
    ARCH = 1001
    MISSG = 3001
    SENSOR = 3002
    SOLAR_SENSOR = 3102
    IOT_LIGHTING = 3003
    IOT_MOTION_SENSOR = 3004
    IOT_SMART_PLUG = 3005
    IOT_DUST_SENSOR = 3006
    EMS_AIR_STATION = 4001
    AIR_SENSOR = 4003


class DeviceInfo(object):
    """Details about a user's device.

    This is populated from a JSON dictionary provided by the API.
    """

    def __init__(self, data):
        self.data = data

    @property
    def model_id(self):
        return self.data['modelNm']

    @property
    def id(self):
        return self.data['deviceId']

    @property
    def model_info_url(self):
        return self.data['modelJsonUrl']

    @property
    def lang_pack_product_url(self):
        return self.data['langPackProductTypeUri']

    @property
    def lang_pack_model_url(self):
        return self.data['langPackModelUri']

    @property
    def macaddress(self):
        return self.data['macAddress']

    @property
    def name(self):
        return self.data['alias']

    @property
    def type(self):
        """The kind of device, as a `DeviceType` value."""
        if DEBUG_MODE:
            with open('model_{}_{}({}).json'.format(DeviceTypeKor(self.data['deviceType']).name, self.model_id, self.name), 'w', -1, 'utf-8') as outfile:
                json.dump(self.data, outfile, ensure_ascii=False, indent="\t")
        return DeviceType(self.data['deviceType'])

    @property
    def load_model_info(self):
        """Load JSON data describing the model's capabilities.
        """
        if DEBUG_MODE:
            with open('json_{}_{}({}).json'.format(DeviceTypeKor(self.data['deviceType']).name, self.model_id, self.name), 'w', -1, 'utf-8') as outfile:
                json.dump(requests.get(self.model_info_url).json(), outfile, ensure_ascii=False, indent="\t")
        return requests.get(self.model_info_url).json()

    @property
    def load_lang_pack_product(self):
        """Load JSON data describing the model's capabilities.
        """
        if DEBUG_MODE:
            with open('lang_prodcut_{}_{}({}).json'.format(DeviceTypeKor(self.data['deviceType']).name, self.model_id, self.name), 'w', -1, 'utf-8') as outfile:
                json.dump(requests.get(self.lang_pack_product_url).json(), outfile, ensure_ascii=False, indent="\t")
        return requests.get(self.lang_pack_product_url).json()

    @property
    def load_lang_pack_model(self):
        """Load JSON data describing the model's capabilities.
        """
        if self.lang_pack_model_url is None:
            return 'None'
        if self.lang_pack_model_url == '':
            return 'None'
        if DEBUG_MODE:
            with open('lang_model_{}_{}({}).json'.format(DeviceTypeKor(self.data['deviceType']).name, self.model_id, self.name), 'w', -1, 'utf-8') as outfile:
                json.dump(requests.get(self.lang_pack_model_url).json(), outfile, ensure_ascii=False, indent="\t")
        return requests.get(self.lang_pack_model_url).json()


BitValue = namedtuple('BitValue', ['options'])
EnumValue = namedtuple('EnumValue', ['options'])
LangValue = namedtuple('LangValue', ['packs'])
RangeValue = namedtuple('RangeValue', ['min', 'max', 'step'])
#: This is a value that is a reference to another key in the data that is at
#: the same level as the `Value` key.
ReferenceValue = namedtuple('ReferenceValue', ['reference'])


class ModelInfo(object):
    """A description of a device model's capabilities.
    """

    def __init__(self, data):
        self.data = data

    @property
    def model_type(self):
        return self.data['Info']['modelType']

    def value(self, name: str):
        """Look up information about a value.

        :param name: The name to look up.
        :returns: One of (`BitValue`, `EnumValue`, `RangeValue`,
            `ReferenceValue`).
        :raises ValueError: If an unsupported type is encountered.
        """
        d = self.data['Value'][name]
        if d['type'] in ('Enum', 'enum'):
            return EnumValue(d['option'])
        elif d['type'] == 'Range':
            return RangeValue(
                d['option']['min'], d['option']['max'],
                d['option'].get('step', 1)
            )
        elif d['type'].lower() == 'bit':
            bit_values = {opt['startbit']: opt['value'] for opt in d['option']}
            return BitValue(bit_values)
        elif d['type'].lower() == 'reference':
            ref = d['option'][0]
            return ReferenceValue(self.data[ref])
        elif d['type'] == 'Boolean':
            return EnumValue({'0': 'False', '1' : 'True'})
        elif d['type'] == 'String':
            pass 
        else:
            raise ValueError("unsupported value type {}".format(d['type']))

    def default(self, name):
        """Get the default value, if it exists, for a given value.
        """
        return self.data['Value'][name]['default']

    def enum_value(self, key, name):
        """Look up the encoded value for a friendly enum name.
        """
        options = self.value(key).options
        options_inv = {v: k for k, v in options.items()}  # Invert the map.
        return options_inv[name]

    def enum_name(self, key, value):
        """Look up the friendly enum name for an encoded value.
        """
        options = self.value(key).options
        if value not in options:
            #logging.warning(
            #    'Value `%s` for key `%s` not in options: %s. Values from API: '
            #    '%s', value, key, options, self.data['Value'][key]['option'])
            return _UNKNOWN
        return options[value]

    def reference_name(self, key: str, value: Any) -> Optional[str]:
        """Look up the friendly name for an encoded reference value.

        :param key: The referenced key.
        :param value: The value whose name we want to look up.
        :returns: The friendly name for the referenced value.  If no name
            can be found None will be returned.
        """
        value = str(value)
        reference = self.value(key).reference
        if value in reference:
            return reference[value]['name']
        return None

    def reference_title(self, key: str, value: Any) -> Optional[str]:
        """Look up the friendly name for an encoded reference value.

        :param key: The referenced key.
        :param value: The value whose name we want to look up.
        :returns: The friendly name for the referenced value.  If no name
            can be found None will be returned.
        """
        value = str(value)
        reference = self.value(key).reference
        if value in reference:
            return reference[value]['title']
        return None

    def reference_comment(self, key: str, value: Any) -> Optional[str]:
        """Look up the friendly name for an encoded reference value.

        :param key: The referenced key.
        :param value: The value whose name we want to look up.
        :returns: The friendly name for the referenced value.  If no name
            can be found None will be returned.
        """
        value = str(value)
        reference = self.value(key).reference
        if value in reference:
            return reference[value]['_comment']
        return None

    @property
    def binary_monitor_data(self):
        """Check that type of monitoring is BINARY(BYTE).
        """
        return self.data['Monitoring']['type'] == 'BINARY(BYTE)'

    def decode_monitor_binary(self, data):
        """Decode binary encoded status data.
        """
        decoded = {}
        for item in self.data['Monitoring']['protocol']:
            key = item['value']
            value = 0
            for v in data[item['startByte']:item['startByte'] +
                          item['length']]:
                value = (value << 8) + v
            decoded[key] = str(value)
        return decoded

    def decode_monitor_json(self, data):
        """Decode a bytestring that encodes JSON status data."""
        return json.loads(data.decode('utf8'))

    def decode_monitor(self, data):
        """Decode  status data."""
        if self.binary_monitor_data:
            return self.decode_monitor_binary(data)
        else:
            return self.decode_monitor_json(data)

class LangPackProduct(object):
    """A description of a device model's capabilities.
    """

    def __init__(self, data):
        self.data = data

    def value(self, name: str):
        """Look up information about a value.
        """
        d = self.data['pack']
        return LangValue(d)

    def enum_value(self, key, name):
        """Look up the encoded value for a friendly enum name.
        """
        packs = self.value(key).packs
        packs_inv = {v: k for k, v in packs.items()}  # Invert the map.
        return packs_inv[name]

    def enum_name(self, key, value):
        """Look up the friendly enum name for an encoded value.
        """
        packs = self.value(key).packs
        if value not in packs:
            #logging.warning(
            #    'Value `%s` for key `%s` not in packs: %s. Values from API: '
            #    '%s', value, key, packs, self.data['pack'])
            return _UNKNOWN
        return packs[value]

    def decode_monitor(self, data):
        return json.loads(self)

class LangPackModel(object):
    """A description of a device model's capabilities.
    """

    def __init__(self, data):
        self.data = data

    def value(self, name: str):
        """Look up information about a value.
        """
        d = self.data['pack']
        return LangValue(d)

    def enum_value(self, key, name):
        """Look up the encoded value for a friendly enum name.
        """
        packs = self.value(key).packs
        packs_inv = {v: k for k, v in packs.items()}  # Invert the map.
        return packs_inv[name]

    def enum_name(self, key, value):
        """Look up the friendly enum name for an encoded value.
        """
        packs = self.value(key).packs
        if value not in packs:
            #logging.warning(
            #    'Value `%s` for key `%s` not in packs: %s. Values from API: '
            #    '%s', value, key, packs, self.data['pack'])
            return _UNKNOWN
        return packs[value]

    def decode_monitor(self, data):
        return json.loads(self)


class Device(object):
    """A higher-level interface to a specific device.

    Unlike `DeviceInfo`, which just stores data *about* a device,
    `Device` objects refer to their client and can perform operations
    regarding the device.
    """

    def __init__(self, client: Client, device: DeviceInfo):
        """Create a wrapper for a `DeviceInfo` object associated with a
        `Client`.
        """
        self.client = client
        self.device = device
        self.model: ModelInfo = client.model_info(device)
        self.lang_product: LangPackProduct = client.lang_pack_product(device)
        self.lang_model: LangPackModel = client.lang_pack_model(device)

    def _set_control(self, key, value):
        """Set a device's control for `key` to `value`."""
        self.client.session.set_device_controls(
            self.device.id,
            {key: value},
        )

    def _get_config(self, key):
        """Look up a device's configuration for a given value.

        The response is parsed as base64-encoded JSON.
        """
        data = self.client.session.get_device_config(
            self.device.id,
            key,
        )
        return json.loads(base64.b64decode(data).decode('utf8'))

    def _get_control(self, key):
        """Look up a device's control value."""
        data = self.client.session.get_device_config(
            self.device.id,
            key,
            'Control',
        )

        # The response comes in a funky key/value format: "(key:value)".
        _, value = data[1:-1].split(':')
        return value

    def monitor_start(self):
        """Start monitoring the device's status."""
        mon = Monitor(self.client.session, self.device.id)
        mon.start()
        self.mon = mon

    def monitor_stop(self):
        """Stop monitoring the device's status."""
        try:
            self.mon.stop()
        except AttributeError:
            logging.warning('접속실패')
