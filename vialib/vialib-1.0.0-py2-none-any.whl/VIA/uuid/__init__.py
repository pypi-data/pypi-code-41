#######################################################################
#
#       COPYRIGHT 2008 RHIZA LABS, LLC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY RHIZA OR
# MAYA DESIGN
#
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY
# RHIZA OR MAYA AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR
# CONSENT OF THE OWNER.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH
# THE TERMS  OF THE APPLICABLE LICENSE AGREEMENT FROM RHIZA. THIS LEGEND MAY
# NOT BE REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY RHIZA LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

#uuid. Py2.0+ only

###############################################################################
#
###############################################################################
from __future__ import absolute_import

import sys
from time import time
from struct import pack,unpack
try: # attempt to get better randoms from randpool
    from MAYA.utils.crypto import get_random_bytes
    def rand2(): return unpack("H",get_random_bytes(2))[0]
except:
    from random import randint
    def rand2(): return randint(0,0xffff)
        
JSON_PREFIX=''  # this is the one place this is defined

try:
    from _warnings import warn
    def _warn(msg): warn(msg, category=DeprecationWarning, stacklevel=3)
except:
    def _warn(msg): print "WARNING: %s\n"%(msg)

UUID_LENGTH_LIMIT = 200

###############################################################################
#
###############################################################################
seq = None  #delay initialize until used to increase theoretical entropy
lastUTC = 0

#UUID schemes
RANDOM = 0
DCE    = 1
HANDLE = 2
ASN_1  = 3
IP     = 4
IP_6   = 5
ETHER  = 6

default_uuid_scheme = DCE

#take these out of this source file?
VIA         = 0xFD000A0251L
VIA_SC 	    = VIA
com_maya    = 0xFD000B70D4L
com_mayaviz = 0xFD000CDF57L
com_civium  = 0xFD000E4DDAL
VIA_ROLE_SC = 0xFD000A02510BL

#-----------------------------------------------------
# UUID schemes matching between number representation
# and a string human readable phrase
#-----------------------------------------------------
Schemes = {}
Schemes[RANDOM] = 'Random number'
Schemes[DCE]    = 'Open Group incl. DCE and Microsoft variants'
Schemes[HANDLE] = 'CNRI Handle System'
Schemes[ASN_1]  = 'ASN.1 Object Identifier'
Schemes[IP]     = 'IP Address'
Schemes[IP_6]   = 'IPv6 Address'
Schemes[ETHER]  = 'Ethernet MAC Address'

Schemes[VIA]         = 'Visage Information Architecture'
Schemes[com_maya]    = 'MAYA Design'
Schemes[com_mayaviz] = 'MAYA Viz'
Schemes[com_civium]  = 'Civium'


###############################################################################
#
###############################################################################
class UUIDTypeException(Exception): pass

class UUIDFormatException(Exception): pass

class UUID(object):
    __slots__ = ('uuBuf',)
    def __init__(self, uuBuf = None, scheme=default_uuid_scheme):
        if uuBuf == None:
            self.uuBuf = generateUUID(scheme)
        else:
            if type(uuBuf) == type(""):
                if len(uuBuf) > UUID_LENGTH_LIMIT:
                    raise Exception("UUID length error")
                self.uuBuf = uuBuf
            else:
                raise UUIDTypeException

    #returns binary value for UUID
    def getBuf(self):
        return self.uuBuf

    def setBuf(self,uuBuf):
        if type(uuBuf) == type(""):
            if len(uuBuf) > UUID_LENGTH_LIMIT:
                raise Exception("UUID length error")
            self.uuBuf = uuBuf
        else:
            raise UUIDTypeException

    def getLen(self):
        return len(self.uuBuf)

    def __getstate__(self): return self.uuBuf
    def __setstate__(self, s): self.uuBuf = s

    def __repr__(self):
        if self.uuBuf != None:
            return "UUID_('" + self.toString() + "')"
        else:
            return "UUID('')"

    # DO THIS SOMEDAY SOON....
    #def __str__(self):
    #    return self.toString()
    
    #returns "printable" value
    def toString(self):
        if len(self.uuBuf) < 1: return ''
        scheme = ord(self.uuBuf[0])
        if scheme >= 33 and scheme <= 125:
            return self.uuBuf #self printing
        else:
            return "~"+''.join(map(lambda x: "%02x" % ord(x), self.uuBuf))

    def __cmp__(self,other):
        if hasattr(other,"_implements_uuid"):
            return cmp(self.getBuf(), other.getBuf())
        else:
            return cmp(self.getBuf(), other)

    def __hash__(self):
        return hash(self.uuBuf)

    # a hack to let vsmf.py know that this object can be
    # considered a uuid
    def _implements_uuid(self):
        return 1

    def rightExtend(self, bin_or_uu, encode_length=1):
        from MAYA.VIA import vsmf
        
        if type(bin_or_uu) == type(""): # buffer
            buf = bin_or_uu
        elif isa(bin_or_uu): # uuid
            buf = bin_or_uu.getBuf()
        else:
            raise TypeError, "You can only right extend with another uuid or a binary buffer"
        # ---------------------------------------------------------------------

        if encode_length:
            ext = vsmf.writeEint(len(buf))
        else:
            ext = ""
            
        ext += buf
        
        return UUID(self.getBuf() + ext)
        
            

    def leftExtend(self, bin_or_uu):
        if type(bin_or_uu) == type(""): # buffer
            buf = bin_or_uu
            _warn("Hope you're not left extending with a random non-unique buffer")
        elif isa(bin_or_uu): # uuid
            buf = bin_or_uu.getBuf()
        else:
            raise TypeError, "You can only left extend with another uuid or a binary buffer"
        # ---------------------------------------------------------------------

        return UUID(buf + self.getBuf()) # removed eint per request


    def toJSON(self):
        return {JSON_PREFIX:['UUID',self.toString()]}

###############################################################################
#
###############################################################################
def fromString(s):
    if s == '': raise UUIDFormatException
    if type(s) == type(u''): s = s.encode('utf8')
    if len(s) > 0 and s[0] == '~':
        # jas:if anyone can think of a faster way -- feel free to reimpl
        # the following de-hexifies a value with arbitrary non-hexdigit
        # punctuation in it.  Currently I allow punctuation even between
        # nybbles -- this is not necessary.
        buf = []
        first = 0
        byt = 0
        for c in s:
            c = c.lower()
            if c >= '0' and c <= '9':
                v = ord(c) - ord('0')
            elif c >= 'a' and c <= 'f':
                v = ord(c) - ord('a') + 10                    
            else:
                continue
            byt = byt * 16 + v
            if first:
                buf.append(chr(byt))
                first = 0
                byt = 0
            else:
                first = 1
        if first: raise UUIDFormatException
        buf = ''.join(buf)
    elif s == '' or s[0] >= chr(33) and s[0] <= chr(125):
        buf = s
    else:
        raise UUIDFormatException
    return UUID(buf)

def _(s):
    from MAYA.VIA import vsmf
    # if constructor is handed binary, then don't convert
    if len(s) > 0 and (isinstance(s,bytearray) or isinstance(s,vsmf.Binary) or (vsmf.CHECK_SKIND and vsmf.IS_BSTRING(s))): return UUID(str(s))
    return fromString(s) #shortcut
    
def isa(u): return hasattr(u,"_implements_uuid")

def generateUUID(scheme=default_uuid_scheme):
    if scheme == DCE:
        return gen_DCE()
    raise "unknown UUID scheme"

def gen_DCE():
    global seq
    global lastUTC
    # time in 100 nanoseconds since 15-Oct-1582
    t = 0x01B21DD213814000l + long(time() * 10000000L)
    if seq is None:
        seq = rand2() & 0x3fff
    if t <= lastUTC:
        seq = seq + 1L
        seq = int(seq % 16384)
    lastUTC = t
    tstr = hex(t)[2:-1].lower()
    padlen = 15 - len(tstr)
    tstr = '1' + '0'*padlen + tstr
    return pack(">cHHHHHHHH",chr(1),
                int(tstr[-8:-4],16),int(tstr[-4:],16),
                int(tstr[-12:-8],16),int(tstr[-16:-12],16),
                (seq & 0x3fff) | 0x8000,
                rand2() | 0x8000, rand2() , rand2())


#-----------------------------------------------------
# VIA Role UUID generator/space-manager
#-----------------------------------------------------
## Jas: I don't like this being here in the uuid module...
## Jas: (and now I have removed it - see svn if you need it)
