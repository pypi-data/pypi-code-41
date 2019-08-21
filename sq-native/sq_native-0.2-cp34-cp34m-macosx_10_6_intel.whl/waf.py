# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Web Application Firewall Binding
"""
from ctypes import POINTER, Structure, byref, c_bool, c_char_p, c_int, c_size_t

from . import lib
from ._compat import UNICODE_CLASS
from .input import C_PWInput, PWInput

PW_ERR_INTERNAL = -6
PW_ERR_TIMEOUT = -5
PW_ERR_INVALID_CALL = -4
PW_ERR_INVALID_RULE = -3
PW_ERR_INVALID_FLOW = -2
PW_ERR_NORULE = -1
PW_GOOD = 0
PW_MONITOR = 1
PW_BLOCK = 2


class C_PWRet(Structure):

    _fields_ = [
        ("action", c_int),
        ("data", c_char_p),
    ]


if lib is not None:
    lib.powerwaf_initializePowerWAF.argstype = [c_char_p, c_char_p]
    lib.powerwaf_initializePowerWAF.restype = c_bool
    lib.powerwaf_runPowerWAF.argstype = [
        c_char_p, POINTER(C_PWInput), c_size_t]
    lib.powerwaf_runPowerWAF.restype = POINTER(C_PWRet)
    lib.powerwaf_freeReturn.argstype = [POINTER(C_PWRet)]
    lib.powerwaf_freeReturn.restype = None
    lib.powerwaf_clearRule.argstype = [c_char_p]
    lib.powerwaf_clearRule.restype = None


def initialize(rule_name, rule_data):
    """ Initialize a WAF rule.
    """

    if lib is None:
        return None

    if isinstance(rule_name, UNICODE_CLASS):
        rule_name = rule_name.encode("utf-8")

    if isinstance(rule_data, UNICODE_CLASS):
        rule_data = rule_data.encode("utf-8")

    if not isinstance(rule_name, bytes):
        raise ValueError("rule_name must be a string or bytes")

    if not isinstance(rule_data, bytes):
        raise ValueError("rule_data must be a string or bytes")

    return lib.powerwaf_initializePowerWAF(rule_name, rule_data)


def clear(rule_name):
    """ Clear a WAF rule.
    """
    if lib is None:
        return None

    if isinstance(rule_name, UNICODE_CLASS):
        rule_name = rule_name.encode("utf-8")

    if not isinstance(rule_name, bytes):
        raise ValueError("rule_name must be a string or bytes")

    lib.powerwaf_clearRule(rule_name)


def get_version():
    """ Get the WAF runtime version.
    """
    if lib is None:
        return None

    return lib.powerwaf_getVersion()


def run(rule_name, parameters, budget):
    """ Run a WAF rule.
    """
    if lib is None:
        return None

    if isinstance(rule_name, UNICODE_CLASS):
        rule_name = rule_name.encode("utf-8")

    if not isinstance(rule_name, bytes):
        raise ValueError("rule_name must be a string or bytes")

    if not isinstance(parameters, PWInput):
        parameters = PWInput.from_python(parameters)

    return PWRet(lib.powerwaf_runPowerWAF(
        rule_name, byref(parameters._obj), c_size_t(budget)))


def free(result):
    """ Free the result of the run function.
    """
    if lib is None:
        return
    lib.powerwaf_freeReturn(result)


class PWRet:
    """
    Higer-level WAF return value.
    """

    def __init__(self, obj):
        self._obj = obj

    def __del__(self):
        if self._obj is None:
            return
        free(self._obj)
        self._obj = None

    @property
    def action(self):
        if self._obj is not None and self._obj[0]:
            return self._obj[0].action

    @property
    def data(self):
        if self._obj is not None and self._obj[0]:
            return self._obj[0].data

    def __repr__(self):
        return "<PWRet action={0.action!r} data={0.data!r}>".format(self)
