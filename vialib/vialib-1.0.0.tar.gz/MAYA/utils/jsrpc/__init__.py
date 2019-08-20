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
"""

JS-RPC

Seung Chan Lim ( slim@maya.com )
"""

###############################################################################
#
###############################################################################
import mimetypes
import types,binascii
from MAYA.VIA import uform, uuid, vsmf
from MAYA import datatypes
from MAYA.utils import date
from StringIO import StringIO
from urllib import quote, unquote





###############################################################################
#
###############################################################################
RUNTIME_ERROR = 21
TYPE_ERROR = 26
VALUE_ERROR = 32




###############################################################################
#
###############################################################################
class Uuid(object):
    def __init__(self, uu):
        assert(uuid.isa(uu))
        self._data = uu

    def __repr__(self):

        return "new StringUuid('%s')"%(self._data.toString())
    
    def toString(self):

        return self._data.toString()
    
class Uform(object):
    def __init__(self, uu, eform):
        self.uuid = Uuid(uu)
        self.eform = dict(eform)
        
    def __repr__(self):

        return "new Uform(%s, %s)"%(repr(self.uuid),
                                                    repr(self.eform))


class Date(object):
    def __init__(self, sec, tz=0):
        self._data = long(sec * 1000)
        if tz:
            #only set if it is not None
            self._tz = tz
        else:
            self._tz = 0

    def __repr__(self):
        return "new Date(%d)"%(self._data + int(3600000*self._tz))

    def getMilliSeconds(self):

        return self._data

    def getTimezone(self):
        return self._tz
    

class Boolean(object):
    def __init__(self, val):
        self._data = val and True or False

    def __repr__(self):

        return (self._data and "true" or "false")

    def __nonzero__(self):

        return self._data

    
class Null(object):
    def __repr__(self):

        return "null"
    

class Undefined(object):
    def __repr__(self):

        return "undefined"

    
class Url(object):
    def __init__(self, f, uri=None):
        assert(hasattr(f, "read"))
        self._f = f
        self.uri = uri or ""

    def read(self, n=-1):
        
        return self._f.read(n)
    
    def __eq__(self, other):
        
        return (self._f.read() == other.read())

    def __repr__(self):

        return "new Url('%s')"%(self.uri)
    
    
class Fault(object):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __repr__(self):

        return "{'error': [0x%x, %s]}"%(self.code,
                                        repr(self.msg))

class Success(object):
    def __init__(self, response):
        self.response = response

    def __repr__(self):

        return "{'error': 0, 'response': %s}"%(repr(self.response))




###############################################################################
#
###############################################################################
def fromString(js_str):
    """
    Given a JavaScript string returns the JS-RPC data type
    """
    raise NotImplemented

    
def toVsmfDataType(data):
    """

    Given a JS-RPC data type return the native VSMF version of the 
    data
    
    """

    if isinstance(data, Uuid):
        #print "is JS UUID: %s"%(repr(data))
        
        return uuid.fromString(data.toString())
    
    elif isinstance(data, Uform):

        return uform.UForm(toVsmfDataType(data.uuid),
                           toVsmfDataType(data.eform))
    
    elif isinstance(data, Null):

        return datatypes.Null()

    elif isinstance(data, Url):
        
        raise NotImplemented
    
    elif isinstance(data, Date):
        # datatypes.Date
        
        return date.fromUnix((data.getMilliSeconds()/1000.0),data.getTimezone())
    
    elif isinstance(data, Boolean):
        # datatypes.Boolean
        if data:
            if hasattr(vsmf, "True"): # new way
                
                return vsmf.True
            else: # old way
                
                return datatypes.Boolean(1)
        else:
            if hasattr(vsmf, "False"): # new way
                
                return vsmf.False
            else: # old way

                return datatypes.Boolean(0)

    elif type(data) == type({}):
        # we treat dictionary objects as Eforms for backward compatibility
        # EForm
        eform = {}

        
        for key in data.keys():
            eform[key] = toVsmfDataType(data[key])
            
        return eform
    elif type(data) in (type(()), type([])):
        new_data = []
        data_len = xrange(len(data))
        
        for i in data_len:
            new_data.append(toVsmfDataType(data[i]))

        return new_data
    elif type(data) in types.StringTypes:
            
        return data
    else:

        return data



    
def toJsRpcDataType(data):
    """

    Given native VSMF datatypes (plus True/False) it returns the JS-RPC version
    of the datatype
    
    WARNING: passing in a dictionary object will return an eform!
    
    """
    
    if uuid.isa(data):
        # UUID
        
        return Uuid(data)

    elif uform.isa(data):
        # UForm
        if not hasattr(uform, "EForm"):
            eform = data.eform # old way
        else:
            eform = uform.EForm(data) # new way
            
        return Uform(data.uuid, toJsRpcDataType(eform))

    elif type(data) == type({}) or (hasattr(uform, "isa_eform") and uform.isa_eform(data)):
        # we treat dictionary objects as Eforms for backward compatibility
        # EForm
        eform = {}

        for key in data.keys():
            eform[key] = toJsRpcDataType(data[key])
            
        return eform
    
    elif isinstance(data, datatypes.Binary):
        # base64 binary
	return binascii.b2a_base64(data.getBuf())
#        return Url(StringIO(data.getBuf()), ".bin")
    
    elif (hasattr(datatypes,'Boolean') and isinstance(data, datatypes.Boolean)) or (type(1) != type(True) and type(data) == type(True)):
        # boolean
        return Boolean(data)
    
    elif isinstance(data, datatypes.MimeVal):
        # struct MIME

        return Url(StringIO(data.getBuf()), "%s"%(mimetypes.guess_extension(data.getType())))
    elif isinstance(data, datatypes.Date):
        # date time ISO8601
        seconds = data.toUnix()
        tz = data.timezone()
        
        return Date(seconds, tz)
    elif isinstance(data, datatypes.Null):
        # struct NULL

        return Null()
    elif type(data) in (type([]), type(())):
        new_data = []
        data_len = xrange(len(data))
        
        for i in data_len:
            new_data.append(toJsRpcDataType(data[i]))

        return new_data
    elif type(data) in types.StringTypes:

        if type(data) == type(u""):
            data = data.encode("utf-8")
            
        return data
    elif  data == None:
        
        return Undefined()
    else:

        return data


    
