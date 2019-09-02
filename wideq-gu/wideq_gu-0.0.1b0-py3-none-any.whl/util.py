from typing import TypeVar
from .client import Device

T = TypeVar('T', bound=Device)
_UNKNOWN = 'Unknown'
KEY_OFF = '꺼짐'
KEY_ON = '켜짐'

def lookup_lang(attr: str, value: str, device: T):
    """Looks up an enum value for the provided attr.

    :param attr: The attribute to lookup in the enum.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The enum value.
    """
    if value is None:
        return KEY_OFF
    if value == '@operation_on':
        return KEY_ON
    elif value == '@operation_off':
        return KEY_OFF
    lang = device.lang_product.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = device.lang_model.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = value
    return str(lang)

def lookup_enum_lang(attr: str, data: dict, device: T):
    """Looks up an enum value for the provided attr.

    :param attr: The attribute to lookup in the enum.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The enum value.
    """
    value = device.model.enum_name(attr, data[attr])
    if value is None:
        return KEY_OFF
    if value == '@operation_on':
        return KEY_ON
    elif value == '@operation_off':
        return KEY_OFF
    lang = device.lang_product.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = device.lang_model.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = value
    return str(lang)

def lookup_enum(attr: str, data: dict, device: T):
    """Looks up an enum value for the provided attr.

    :param attr: The attribute to lookup in the enum.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The enum value.
    """
    return str(device.model.enum_name(attr, data[attr]))

def lookup_enum_value(attr: str, data: dict, device: T):
    """Looks up an enum value for the provided attr.

    :param attr: The attribute to lookup in the enum.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The enum value.
    """
    return str(device.model.enum_value(attr, data[attr]))

def lookup_reference_name(attr: str, data: dict, device: T) -> str:
    """Look up a reference value for the provided attribute.

    :param attr: The attribute to find the value for.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The looked up value.
    """
    value = device.model.reference_name(attr, data[attr])
    if value is None:
        return KEY_OFF
    lang = device.lang_product.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = device.lang_model.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = value
    return str(lang)

def lookup_reference_title(attr: str, data: dict, device: T) -> str:
    """Look up a reference value for the provided attribute.

    :param attr: The attribute to find the value for.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The looked up value.
    """
    value = device.model.reference_title(attr, data[attr])
    if value is None:
        return KEY_OFF
    if value == "ERROR_NOERROR_TITLE":
        return "없음"
    if value == "No_Error":
        return "없음"
    lang = device.lang_product.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = device.lang_model.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = value
    return str(lang)

def lookup_reference_comment(attr: str, data: dict, device: T) -> str:
    """Look up a reference value for the provided attribute.

    :param attr: The attribute to find the value for.
    :param data: The JSON data from the API.
    :param device: A sub-class instance of a Device.
    :returns: The looked up value.
    """
    value = device.model.reference_comment(attr, data[attr])
    if value is None:
        return KEY_OFF
    lang = device.lang_product.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = device.lang_model.enum_name(attr, value)
    if lang == _UNKNOWN:
        lang = value
    return str(lang)
