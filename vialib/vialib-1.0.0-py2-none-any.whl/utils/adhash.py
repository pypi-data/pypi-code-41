#######################################################################
#
#       COPYRIGHT 2005 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

# $Id: adhash.py 9726 2005-04-08 20:35:34Z widdows $
# This file implements the ADHASH incremental hashing algorithm, based on MD5.
# It is not intended to be particularly secure (hence the use of MD5 and the
# fixed modulus); it is aimed at representing the contents of a set of hashed
# entities compactly.

import md5, struct

SIXTY_FOUR_BITS = pow(2, 64)
MODULUS = pow(2, 128) - 1

def md5_hash(x):
    m = md5.new()
    m.update(x)
    return m.digest()

# converts a 128-bit binary string to a long integer, assuming big-endian encoding

def md5_to_long(x):
    parts = struct.unpack('!QQ', x)
    return (parts[0] * SIXTY_FOUR_BITS) + parts[1]
    
# converts a long integer to a 128-bit binary string in big-endian encoding
    
def long_to_md5(x):
    return struct.pack('!QQ', x / SIXTY_FOUR_BITS, x % SIXTY_FOUR_BITS)

# add hashBytesB to hashBytesA

def add(hashBytesA, hashBytesB):
    result = (md5_to_long(hashBytesA) + md5_to_long(hashBytesB)) % MODULUS
    return long_to_md5(result)

# add an unhashed value to the hash represented by hashBytes

def addValue(hashBytes, value):
    return add(hashBytes, md5_hash(value))
    
# remove hashBytesB from hashBytesA
    
def remove(hashBytesA, hashBytesB):
    result = (md5_to_long(hashBytesA) - md5_to_long(hashBytesB)) % MODULUS
    return long_to_md5(result)

# remove an unhashed value from the hash represented by hashBytes

def removeValue(hashBytes, value):
    return remove(hashBytes, md5_hash(value))

def new(initvalue = None):
    return AdHash(initvalue)
    
class AdHash:
    def __init__(self, initvalue = None):
        if initvalue:
            self.value = md5_to_long(initvalue)
        else:
            self.value = 0L
        
    def __repr__(self):
        return self.getHash()
    
    def digest(self):
        return self.getHash()
    
    def getHash(self):
        return long_to_md5(self.value)
    
    def add(self, newhash):
        if (type(newhash) == type([])) or (type(newhash) == type(())):
            for h in newhash:
                self.add(h)
        else:
            self.value = (self.value + md5_to_long(newhash)) % MODULUS
        
    def remove(self, newhash):
        if (type(newhash) == type([])) or (type(newhash) == type(())):
            for h in newhash:
                self.remove(h)
        else:
            self.value = (self.value - md5_to_long(newhash)) % MODULUS
