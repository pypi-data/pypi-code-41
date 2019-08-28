#!/usr/bin/env python
# -*- coding: utf-8 -*-
import racrypt
from os import path
import binascii
import random
import zeropy.structs as s

import crcPy
import os

#Create sign transaction.
def transaction(pr_key, from_key, to_key, intg, frac):
    salt_sz = 32
    t = s.Transaction()
    t.sender_public = from_key
    t.receiver_public = to_key
    t.amount.integral = intg
    t.amount.fraction = frac
    t.currency = b'RAS'
    t.salt = bytearray(salt_sz)
    for it in range(salt_sz):
        t.salt[it] = random.randint(0, 255)

    lib = racrypt.Crypto()
    lib.load(path.dirname(racrypt.__file__))

    buffer = bytearray()
    buffer += binascii.unhexlify(t.sender_public)
    buffer += binascii.unhexlify(t.receiver_public)
    buffer += t.amount.integral.to_bytes(4, 'little')
    buffer += t.amount.fraction.to_bytes(8, 'little')
    buffer += t.currency
    buffer += bytearray(16 - len(t.currency))
    buffer += t.salt

    result = lib.sign(
        bytes(buffer), len(buffer),
        binascii.unhexlify(from_key),
        binascii.unhexlify(pr_key),
    )

    if result != True:
        return None

    t.hash_hex = lib.signature

    result = lib.verify(bytes(buffer), len(buffer),
                        binascii.unhexlify(from_key),
                        lib.signature)
    print('verify success', result)

    return t


def crcSum(_buffer: bytearray):
	library = crcPy.crcLib()
	library.load(os.path.dirname(crcPy.__file__))
	sum = library.calcCrc(bytes(_buffer), len(_buffer))
	sum = sum.to_bytes(8, 'little')

	return sum


def crc32_buffer(buff: bytearray) -> bytearray:
    buffer = bytearray(0)
    crc32_sum = crcSum(buff)
    buffer += crc32_sum
    # repeat flag
    buffer += b'00'
    buffer += buff
    return buffer

def check_equal_bytearrays(buff1, buff2)->bool:
    if len(buff1) != len(buff2):
        return False
    for it in range(0, len(buff1)):
        if buff1[it] != buff2[it]:
            return False
    return True


def check_crc32_sum(buffer: bytearray) -> bool:
    view = memoryview(buffer)
    buff_sz = len(buffer)
    crc32_sum = view[0:8].tobytes()
    buff = view[8:buff_sz].tobytes()
    arr = bytearray(0)
    arr += buff
    calc_crc32 = crcSum(arr)
    return check_equal_bytearrays(crc32_sum, calc_crc32)
