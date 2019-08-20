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

XML-RPC datatype <--> Vsmf datatype conversion utility

array <--> list
int <--> int
double <--> double
boolean <--> boolean / vsmf.Boolean
dateTime.iso8601 <--> vsmf.Date
base64 binary <--> vsmf.Binary
struct:UUID <--> UUID
struct:UForm <--> UForm
struct:MIME <--> vsmf.MimeVal
struct:EForm <--> EForm / dictionary
struct:NULL <!--> vsmf.Null


Seung Chan Lim ( slim@maya.com )

"""

###############################################################################
#
###############################################################################
from MAYA.VIA import uuid, vsmf, uform
from MAYA import datatypes
from xmlrpclib import Binary, Boolean, DateTime
from types import StringTypes
from MAYA.utils import date




###############################################################################
#
###############################################################################
def toVsmfDataType(data):
    """

    Given an XML-RPC data type return the native VSMF version of the 
    data
    
    """

    if type(data) == type({}):
        # one of ours
        try:
            type_info = data["type"]
            
            if type_info == "uuid":
                buf = data["buffer"]
                if type(buf) in StringTypes:
                    native_data =uuid.fromString(buf)
                else:
                    native_data = uuid.UUID(buf.data)
            elif type_info == "uform":
                native_data = uform.UForm(toVsmfDataType(data["uuid"]),
                                          toVsmfDataType(data["eform"]))
            elif type_info == "eform":
                eform = dict(data["avpairs"])
                
                if hasattr(uform, "EForm"): # new version
                    native_data = uform.EForm(eform)
                else: # old version
                    native_data = eform
            elif type_info == "mime":
                native_data = datatypes.MimeVal(data["content_type"],
                                                data["content_buffer"].data)
            elif type_info == "null":
                native_data = datatypes.Null()
            else:

                raise TypeError, "Unknown type %s"%(type_info)
            
        except (KeyError, TypeError), err:
            # not one of ours
            
            return data
        else:

            return native_data

        
    elif isinstance(data, Binary):
        # to datatype.Binary

        return datatypes.Binary(data.data)
    elif isinstance(data, DateTime):
        # datatypes.Date
        date_string = str(data)
        
        return date.fromString("%s-%s-%s%sZ"%(date_string[0:4],
                                             date_string[4:6],
                                             date_string[6:8],
                                             date_string[8:]))
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

    elif type(data) in (type(()), type([])):
        new_data = []
        data_len = range(len(data))
        for i in data_len:
            new_data.append(toVsmfDataType(data[i]))

        return new_data
    else:

        return data
    
        
    
def toXmlRpcDataType(data):
    """

    Given native VSMF datatypes (plus True/False) it returns the XML-RPC version
    of the datatype
    
    WARNING: passing in a dictionary object will return an eform!
    
    """
    
    if uuid.isa(data):
        # struct UUID
        
        return {"type" : "uuid",
                "buffer" : Binary(data.getBuf())}

    elif uform.isa(data):
        # struct UForm
        
        if hasattr(data, "eform"):
            eform = data.eform # old way
        else:
            eform = uform.EForm(data) # new way
            
        return {"type" : "uform",
                "uuid" : toXmlRpcDataType(data.uuid),
                "eform" : toXmlRpcDataType(eform)}
    elif type(data) == type({}) or (hasattr(uform, "isa_eform") and uform.isa_eform(data)):
        # we treat dictionary objects as Eforms for backward compatibility
        # struct EForm
        
        avpairs = data.items()
        num_avpairs = range(len(avpairs))
        
        for i in num_avpairs:
            # first item is the name, so keep it as a string
            avpairs[i] = (avpairs[i][0], toXmlRpcDataType(avpairs[i][1]))
            
        return {"type" : "eform",
                "avpairs" : avpairs}
    elif isinstance(data, datatypes.Binary):
        # base64 binary

        return Binary(data.getBuf())
    elif isinstance(data, datatypes.Boolean) or type(data) == type(True):
        # boolean

        return Boolean(data)
    
    elif isinstance(data, datatypes.MimeVal):
        # struct MIME

        return {"type" : "mime",
                "content_type" : data.getType(),
                "content_buffer" : Binary(data.getBuf())}
    elif isinstance(data, datatypes.Date):
        # date time ISO8601
        date_string = data.toString()
        date_string = date_string.replace("-", "")
        date_string = date_string.replace("Z", "")
        
        return DateTime(date_string)
    elif isinstance(data, datatypes.Null):
        # struct NULL

        return {"type" : "null"}
    elif type(data) in (type([]), type(())):
        new_data = []
        data_len = range(len(data))
        
        for i in data_len:
            new_data.append(toXmlRpcDataType(data[i]))

        return new_data        
    else:

        return data

