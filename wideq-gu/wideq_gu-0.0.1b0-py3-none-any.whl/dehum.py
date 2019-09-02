import enum
from typing import Optional
from .client import Device
from .util import lookup_lang, lookup_enum, lookup_enum_lang, lookup_enum_value, lookup_reference_name, lookup_reference_title, lookup_reference_comment

KEY_ON = 'on'
KEY_OFF = 'off'

class DehumOperation(enum.Enum):
    ON = '@operation_on'
    OFF = '@operation_off'
    스마트제습 = '@AP_MAIN_MID_OPMODE_SMART_DEHUM_W'
    쾌속제습 = '@AP_MAIN_MID_OPMODE_FAST_DEHUM_W'
    저소음제습 = '@AP_MAIN_MID_OPMODE_CILENT_DEHUM_W'
    집중건조 = '@AP_MAIN_MID_OPMODE_CONCENTRATION_DRY_W'
    의류건조 = '@AP_MAIN_MID_OPMODE_CLOTHING_DRY_W'
    공기제균 = '@AP_MAIN_MID_OPMODE_IONIZER_W'

class DehumWindStrength(enum.Enum):
    약 = '@AP_MAIN_MID_WINDSTRENGTH_DHUM_LOW_W'
    강 = '@AP_MAIN_MID_WINDSTRENGTH_DHUM_HIGH_W'

class DehumAIRREMOVAL(enum.Enum):
    OFF = '@AP_OFF_W'
    ON = '@AP_ON_W'

class DehumDevice(Device):
    """A higher-level interface for a dehum."""

    def set_on(self, is_on):
        key = 'Operation'
        mode = DehumOperation.ON if is_on else DehumOperation.OFF
        mode_value = self.model.enum_value(key, mode.value)
        self._set_control(key, mode_value)

    def set_mode(self, mode):
        key = 'OpMode'
        value = DehumOperation[mode].value
        mode_value = self.model.enum_value(key, value)
        self._set_control(key, mode_value)

    def set_humidity(self, hum):
        """Set the device's target humidity.
        """
        self._set_control('HumidityCfg', hum)
    
    def set_windstrength(self, mode):
        key = 'WindStrength'
        value = DehumWindStrength[mode].value
        mode_value = self.model.enum_value(key, value)
        self._set_control(key, mode_value)
    
    def set_airremoval(self, is_on):
        key = 'AirRemoval'
        mode = DehumAIRREMOVAL.ON if is_on else DehumAIRREMOVAL.OFF
        mode_value = self.model.enum_value(key, mode.value)
        self._set_control(key, mode_value)

    def poll(self) -> Optional['dehumStatus']:
        """Poll the device's current state.

        Monitoring must be started first with `monitor_start`.

        :returns: Either a `dehumStatus` instance or `None` if the status is
            not yet available.
        """
        # Abort if monitoring has not started yet.
        if not hasattr(self, 'mon'):
            return None

        data = self.mon.poll()
        if data:
            res = self.model.decode_monitor(data)
            return DehumStatus(self, res)
        
        else:
            return None


class DehumStatus(object):
    """Higher-level information about a dehum's current status.

    :param dehum: The DehumDevice instance.
    :param data: JSON data from the API.
    """

    def __init__(self, dehum: DehumDevice, data: dict):
        self.dehum = dehum
        self.data = data

    @staticmethod
    def _str_to_num(s):
        """Convert a string to either an `int` or a `float`.
        Troublingly, the API likes values like "18", without a trailing
        ".0", for whole numbers. So we use `int`s for integers and
        `float`s for non-whole numbers.
        """

        f = float(s)
        if f == int(f):
            return int(f)
        else:
            return f

    def get_bit(self, key: str, index: int) -> str:
        bit_value = int(self.data[key])
        bit_index = 2 ** index
        mode = bin(bit_value & bit_index)
        if mode == bin(0):
            return KEY_OFF
        else:
            return KEY_ON

    @property
    def device_name(self):
        """Get the type of the dehum."""
        return self.dehum.device.name

    @property
    def device_type(self):
        """Get the type of the dehum."""
        return self.dehum.model.model_type

    @property
    def is_on(self):
        op = DehumOperation(lookup_enum('Operation', self.data, self.dehum))
        return op == DehumOperation.ON

    @property
    def state(self):
        """Get the state of the dryer."""
        key = 'Operation'
        value = lookup_enum_lang(key, self.data, self.dehum)
        if value is None:
            return KEY_OFF
        return value

    @property
    def mode(self):
        key = 'OpMode'
        value = lookup_enum_lang(key, self.data, self.dehum)
        return value

    @property
    def windstrength_state(self):
        key = 'WindStrength'
        value = lookup_enum_lang(key, self.data, self.dehum)
        return value

    @property
    def airremoval_state(self):
        key = 'AirRemoval'
        value = lookup_enum_lang(key, self.data, self.dehum)
        return value

    @property
    def current_humidity(self):
        return self._str_to_num(self.data['SensorHumidity'])

    @property
    def target_humidity(self):
        return self._str_to_num(self.data['HumidityCfg'])