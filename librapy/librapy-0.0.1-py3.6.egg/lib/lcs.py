#!/usr/bin/env python3

"""
This implements LCS as defined in
https://github.com/libra/libra/tree/master/common/canonical_serialization
"""

import array
import struct
import unittest

ARRAY_MAX_LENGTH = 2**31-1
STRING_CODEC = "utf8"


class EncoderException(Exception):
    pass


class Serializer():
    def __init__(self):
        self.data = array.array('B')

    def encode_bool(self, value):
        self.encode_u8(1 if value else 0)
        return self

    def encode_bytes(self, value):
        len_of_value = len(value)
        if len_of_value > ARRAY_MAX_LENGTH:
            raise EncoderException(
                "Array length exceeds maximum length. "
                "Found: {}, expected: {}".format(
                    len_of_value,
                    ARRAY_MAX_LENGTH,
                )
            )

        self.encode_u32(len_of_value)
        self.data.frombytes(value)
        return self

    def encode_i8(self, value):
        self.data.frombytes(struct.pack("<b", value))
        return self

    def encode_i16(self, value):
        self.data.frombytes(struct.pack("<h", value))
        return self

    def encode_i32(self, value):
        self.data.frombytes(struct.pack("<i", value))
        return self

    def encode_i64(self, value):
        self.data.frombytes(struct.pack("<q", value))
        return self

    def encode_map(self, value, key_encoder, value_encoder):
        len_of_value = len(value)
        if len_of_value > ARRAY_MAX_LENGTH:
            raise EncoderException(
                "Map length exceeds maximum length. "
                "Found: {}, expected: {}".format(
                    len_of_value,
                    ARRAY_MAX_LENGTH,
                )
            )

        self.encode_u32(len_of_value)

        serialized_value = {}
        for k, v in value.items():
            serialized_value[key_encoder(k)] = value_encoder(v)

        for k in sorted(serialized_value.keys()):
            self.data.frombytes(k)
            self.data.frombytes(serialized_value[k])
        return self

    def encode_string(self, value):
        self.encode_bytes(value.encode("utf8"))
        return self

    def encode_struct(self, value):
        value.serialize(self)
        return self

    def encode_u8(self, value):
        self.data.frombytes(struct.pack("<B", value))
        return self

    def encode_u16(self, value):
        self.data.frombytes(struct.pack("<H", value))
        return self

    def encode_u32(self, value):
        self.data.frombytes(struct.pack("<I", value))
        return self

    def encode_u64(self, value):
        self.data.frombytes(struct.pack("<Q", value))
        return self

    def encode_vec(self, value, encoder):
        len_of_value = len(value)
        if len_of_value > ARRAY_MAX_LENGTH:
            raise EncoderException(
                "Vector length exceeds maximum length. "
                "Found: {}, expected: {}".format(
                    len_of_value,
                    ARRAY_MAX_LENGTH,
                )
            )

        self.encode_u32(len_of_value)
        for val in value:
            encoder(val)
        return self

    def encode_vec_for_struct(self, value):
        def encoder(value):
            return self.encode_struct(value)
        return self.encode_vec(value, encoder)

    def get_buffer(self):
        return self.data.tobytes()


class Deserializer():
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def decode_bool(self):
        value = self.decode_u8()
        if value != 0 and value != 1:
            raise EncoderException(
                "Invalid boolean. Found: {}, expected 0 or 1.".format(value)
            )

        return value == 1

    def decode_bytes(self):
        len_of_value = self.decode_u32()
        if len_of_value > ARRAY_MAX_LENGTH:
            raise EncoderException(
                "Array length exceeds maximum length. "
                "Found: {}, expected: {}".format(
                    len_of_value,
                    ARRAY_MAX_LENGTH,
                )
            )
        value = self.data[self.offset:self.offset + len_of_value]
        self.offset += len_of_value
        return value

    def decode_i8(self):
        (value, ) = struct.unpack_from("<b", self.data, self.offset)
        self.offset += 1
        return value

    def decode_i16(self):
        (value, ) = struct.unpack_from("<h", self.data, self.offset)
        self.offset += 2
        return value

    def decode_i32(self):
        (value, ) = struct.unpack_from("<i", self.data, self.offset)
        self.offset += 4
        return value

    def decode_i64(self):
        (value, ) = struct.unpack_from("<q", self.data, self.offset)
        self.offset += 8
        return value

    def decode_map(self, key_decoder, value_decoder):
        len_of_value = self.decode_u32()
        if len_of_value > ARRAY_MAX_LENGTH:
            raise EncoderException(
                "Map length exceeds maximum length. "
                "Found: {}, expected: {}".format(
                    len_of_value,
                    ARRAY_MAX_LENGTH,
                )
            )

        value = {}
        for _ in range(len_of_value):
            (k, offset) = key_decoder(self.data[self.offset:])
            self.offset += offset
            (v, offset) = value_decoder(self.data[self.offset:])
            self.offset += offset
            value[k] = v

        return value

    def decode_struct(self, value_type):
        return value_type.deserialize(self)

    def decode_string(self):
        value = self.decode_bytes()
        return value.decode("utf8")

    def decode_u8(self):
        (value, ) = struct.unpack_from("<B", self.data, self.offset)
        self.offset += 1
        return value

    def decode_u16(self):
        (value, ) = struct.unpack_from("<H", self.data, self.offset)
        self.offset += 2
        return value

    def decode_u32(self):
        (value, ) = struct.unpack_from("<I", self.data, self.offset)
        self.offset += 4
        return value

    def decode_u64(self):
        (value, ) = struct.unpack_from("<Q", self.data, self.offset)
        self.offset += 8
        return value

    def decode_vec(self, decoder):
        len_of_value = self.decode_u32()
        if len_of_value > ARRAY_MAX_LENGTH:
            raise EncoderException(
                "Vector length exceeds maximum length. "
                "Found: {}, expected: {}".format(
                    len_of_value,
                    ARRAY_MAX_LENGTH,
                )
            )

        value = []
        for _ in range(len_of_value):
            value.append(decoder())
        return value

    def decode_vec_for_struct(self, struct_type):
        def decoder():
            return struct_type.deserialize(self)
        return self.decode_vec(decoder)


def byte_encoder(value):
    return Serializer().encode_bytes(value).get_buffer()


def byte_decoder(data):
    deserializer = Deserializer(data)
    value = deserializer.decode_bytes()
    return (value, deserializer.offset)


class Addr:
    def __init__(self, addr):
        self.addr = addr

    def __eq__(self, other):
        return self.addr == other.addr

    def deserialize(deserializer):
        return Addr(deserializer.decode_bytes())

    def serialize(self, serializer):
        serializer.encode_bytes(self.addr)


class Bar:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __eq__(self, other):
        return \
            self.a == other.a and \
            self.b == other.b and \
            self.c == other.c and \
            self.d == other.d

    def deserialize(deserializer):
        return Bar(
            deserializer.decode_u64(),
            deserializer.decode_bytes(),
            deserializer.decode_struct(Addr),
            deserializer.decode_u32(),
        )

    def serialize(self, serializer):
        serializer.encode_u64(self.a)
        serializer.encode_bytes(self.b)
        serializer.encode_struct(self.c)
        serializer.encode_u32(self.d)


class Foo:
    def __init__(self, a, b, c, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def __eq__(self, other):
        return \
            self.a == other.a and \
            self.b == other.b and \
            self.c == other.c and \
            self.d == other.d and \
            self.e == other.e

    def deserialize(deserializer):
        return Foo(
            deserializer.decode_u64(),
            deserializer.decode_bytes(),
            deserializer.decode_struct(Bar),
            deserializer.decode_bool(),
            deserializer.decode_map(byte_decoder, byte_decoder),
        )

    def serialize(self, serializer):
        serializer.encode_u64(self.a)
        serializer.encode_bytes(self.b)
        serializer.encode_struct(self.c)
        serializer.encode_bool(self.d)
        serializer.encode_map(self.e, byte_encoder, byte_encoder)


class TestLCS(unittest.TestCase):
    test_vector = bytes.fromhex(
        "ffffffffffffffff060000006463584d423764000000000000000900000000010"
        "20304050607082000000005050505050505050505050505050505050505050505"
        "05050505050505050505630000000103000000010000000103000000161543030"
        "0000000381503000000160a05040000001415596903000000c9175a"
    )

    def test_correctness(self):
        """
        Verify correctness of implementation using common data structure
        """

        bar = Bar(
            100,
            bytes([0, 1, 2, 3, 4, 5, 6, 7, 8]),
            Addr(bytes([5]*32)),
            99
        )

        map_value = {
            bytes([0, 56, 21]): bytes([22, 10, 5]),
            bytes([1]): bytes([22, 21, 67]),
            bytes([20, 21, 89, 105]): bytes([201, 23, 90]),
        }

        foo = Foo(
            2**64-1,
            bytes([100, 99, 88, 77, 66, 55]),
            bar,
            True,
            map_value,
        )

        serializer = Serializer()
        serializer.encode_struct(foo)
        data = serializer.get_buffer()

        self.assertEqual(self.test_vector, data)
        deserializer = Deserializer(self.test_vector)
        fooed = deserializer.decode_struct(Foo)
        self.assertEqual(foo, fooed)
