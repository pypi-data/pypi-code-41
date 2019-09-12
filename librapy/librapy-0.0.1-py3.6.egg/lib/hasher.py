#!/usr/bin/env python3

"""
Common hash wrapper for sha3 256. Libra prefixes / salts all hash objects,
first with the role of the hashing function, e.g. AccountAddress,
RawTransaction,  and second by Libra specific prefix, @@$$LIBRA$$@@..
"""

from hashlib import sha3_256

COMMON_HASH_PREFIX = b"@@$$LIBRA$$@@"


def get_hash_function(hashable_type):
    sha3 = sha3_256()
    sha3.update(hashable_type.get_hash_prefix() + COMMON_HASH_PREFIX)
    base = sha3.digest()

    sha3 = sha3_256()
    sha3.update(base)
    return sha3
