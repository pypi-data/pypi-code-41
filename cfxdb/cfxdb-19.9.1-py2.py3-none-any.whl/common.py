##############################################################################
#
#                        Crossbar.io Fabric
#     Copyright (C) Crossbar.io Technologies GmbH. All rights reserved.
#
##############################################################################

import web3
import struct


def unpack_uint256(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 32, 'data must be bytes[32], but was bytes[{}]'.format(len(data))

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint256(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**256), 'value must be uint256, but was {}'.format(value)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (32 - len(data)) + data
    else:
        return b'\x00' * 32


class uint256(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 32

    @property
    def value(self):
        return unpack_uint256(self._data)

    @value.setter
    def value(self, value):
        self._data = pack_uint256(value)

    def serialize(self):
        return self._data


def unpack_uint128(data):
    assert data is None or (type(data) == bytes and len(data) == 16)

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint128(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**128)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (16 - len(data)) + data
    else:
        return b'\x00' * 16


class uint128(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 16

    @property
    def value(self):
        return unpack_uint128(self._data)

    @value.setter
    def value(self, value):
        self._data = pack_uint128(value)

    def serialize(self):
        return self._data


class address(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 20

    @property
    def value(self):
        w2, w1, w0 = struct.unpack('>LQQ', self._data)
        return w2 << 16 + w1 << 8 + w0

    @value.setter
    def value(self, value):
        assert(type(value) == int and value >= 0 and value < 2**160)
        w0 = value % 2**64
        value = value >> 8
        w1 = value % 2**64
        value = value >> 8
        w2 = value % 2**32
        self._data = struct.pack('>LQQ', w2, w1, w0)

    def serialize(self):
        return self._data
