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
import MAYA.uuid # important that I don't do from MAYA import uuid

import MAYA.role


UUID = MAYA.uuid.fromString('~FD000A0251.0B.FD57E6F173')
uuid = UUID

# type constants
kBoolType = MAYA.uuid.fromString('~37797b66-c54f-11d4-a02b-dd0955562ed9')
kIntType = MAYA.uuid.fromString('~72517f18-c54f-11d4-a02b-d0aaa875a02c')
kRealType  = MAYA.uuid.fromString('~42141542-c552-11d4-a02b-e725ab89ff76')
kStrType  = MAYA.uuid.fromString('~99000812-ca10-11d4-a70b-88af06dbeff2')
kUUType  = MAYA.uuid.fromString('~6c5362b8-c552-11d4-a02b-91a7c2218469')
kMimeType  = MAYA.uuid.fromString('~afaf94a0-c552-11d4-a02b-ed96cbcf08b4')




import types
import os.path
from MAYA import vsmf




# exceptions
roleError = 'Role Error'

# descriptor constants
kType = 'types'
kRange = 'ranges'
kRequired = 'requireds'




class attrDescriptor:
         # it's a dictionary with a custom __init__
         def __init__(self, attr, role):
                 data = {}
                 idx = 0
                 for r in role['attributes']:
                         if r == attr: break
                         idx = idx + 1
                 else:
                         raise roleError, 'Attribute not described by role'
                 for d in role['attribute descriptors']:
                         self.data[d] = role[d][idx]
                 return data

def typeDescriptor(x):
        # returns the type descriptor of x it there is one, otherwise returns the type of x
        xType = type(x)
        if xType in (types.IntType, types.LongType):
                return kIntType
        elif xType == types.FloatType:
                return kRealType
        elif xType == types.StringType:
                return kStrType
        elif xType == types.InstanceType:
                xClass = x.__class__
                if xClass == MAYA.uuid.UUID:
                        return kUUType
                elif xClass == vsmf.boolean:
                        return kBoolType
                elif xClass == vsmf.binary:
                        return kStrType
                elif xClass == vsmf.mimeVal:
                        return kMimeType
                else:
                        return xType
        else:
                return xType

    
def convertTo(val, type_desc):
    """
    tries very hard to convert the value of 
    /val/ into a type described in /type_desc/
    
    Seung Chan Lim (limsc@maya.com)
    """
    
    from exceptions import TypeError, ValueError

    if not MAYA.uuid.isa(type_desc):
        
        raise TypeError, "second parameter must be a type descriptor UUID"
    
    # feel free to use jmp table here instead of if's
    if type_desc == kBoolType :
        
        try:
            val = int(val)
            
            if val != 0 and val != 1:
            
                raise ValueError
        except:
        
            raise TypeError, "failed to convert %s VSMF bool value"%(repr(val))
            # ----------------------------------------------------------------
        else:
        
            return vsmf.boolean(val)
            # ----------------------------------------------------------------
            
    elif type_desc == kIntType:
        try:
            val = int(val)
            
        except:
        
            raise TypeError, "failed to convert %s VSMF int"%(repr(val))
            # ----------------------------------------------------------------
        else:
        
            return val
            # ----------------------------------------------------------------
            
    elif type_desc == kRealType:
        
        try:
            val = float(val)
            
        except:
        
            raise TypeError, "failed to convert %s VSMF real"%(repr(val))
            # ----------------------------------------------------------------
        else:
        
            return val
            # ----------------------------------------------------------------
            
    elif type_desc == kStrType:
        
        try:
            val = str(val)
            
        except:
        
            raise TypeError, "failed to convert %s VSMF string"%(repr(val))
            # ----------------------------------------------------------------
        else:
        
            return val
            # ----------------------------------------------------------------
            
    elif type_desc == kUUType:        
        
        try:
            val = MAYA.role._UUIDfyOrCreate(val, create=0)
            
        except:
            raise TypeError, "failed to convert %s VSMF UUID"%(repr(val))
            # ----------------------------------------------------------------
        else:
        
            return val
            # ----------------------------------------------------------------
            
    elif type_desc == kMimeType:
        
        try:
            if type(val) == type(""):
                val = vsmf.mimeVal("plain/text", val)
            elif hasattr(val, "filename") and hasattr(val, "value"):                
                # since it's a big module, loading hasd been deferred until
                # now
                import mimetypes
                file_name = os.path.basename(val.filename)
                file_ext = os.path.splitext(val.filename)[-1]
                val = vsmf.mimeVal((mimetypes.guess_type(val.filename)[0] or \
                                    'application/x-unknown'),
                                   val.value)
                val.name = file_name
                val.extension = file_ext

            elif hasattr(val, "_implements_mimeVal"):
                val = val
            else:
                
                raise TypeError                                  
            
        except:
        
            raise TypeError, "failed to convert %s VSMF MIME"%(repr(val))
            # ----------------------------------------------------------------
        else:
        
            return val
            # ----------------------------------------------------------------
            
    else:
    
        raise ValueError, "Uknown type descriptor"  
        # --------------------------------------------------------------------




################################################################################
# test
################################################################################
if __name__ == "__main__":
    import unittest
    import mimetypes
    
    # Seung Chan Lim (limsc@maya.com)
    # unittesting converTo
    class Test(unittest.TestCase):
        class Dummy:
            filename = "test.gif"
            value = "blah"
            
        _bool_val_ = 0
        _real_val_ = 0.234
        _int_val_ = 10
        _str_val_ = "hello"
        _uu_val_ = MAYA.uuid.UUID()
        _uu_str_val_ = "~01741C7D3D-06C5-492d-8981-B2A879EC876E"
        _mime_txt_val_ = "hello world!!!"
        _mime_fied_val_ = Dummy()
        

        def testBool(self):
            try:
                val = convertTo(self._bool_val_, kBoolType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid bool val %s"%(
                                                         str(self._bool_val)))
            else:
                self.assert_(hasattr(val, "_implements_boolean"), 
                             "incorrect vsmf boolean object returnd")
                self.assertEquals(val.val, self._bool_val_, 
                                  "internal boolean values differ")
                
            # all the following should fail
            self.assertRaises(TypeError, convertTo, self._str_val_, 
                              kBoolType)
            self.assertRaises(TypeError, convertTo, self._uu_val_, 
                              kBoolType)
            self.assertRaises(TypeError, convertTo, self._uu_str_val_, 
                              kBoolType)
            self.assertRaises(TypeError, convertTo, self._mime_txt_val_, 
                              kBoolType)
            self.assertRaises(TypeError, convertTo, self._mime_fied_val_, 
                              kBoolType)
            
            
        def testInt(self):
            try:
                val = convertTo(self._int_val_, kIntType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid bool val %s"%(
                                                         str(self._int_val_)))
            else:
                self.assert_(type(val) == type(self._int_val_), 
                             "incorrect vsmf integer returnd")
                self.assertEquals(val, self._int_val_, "integer values differ")
                
            # all the following should fail
            self.assertRaises(TypeError, convertTo, self._uu_val_, 
                              kIntType)
            self.assertRaises(TypeError, convertTo, self._uu_str_val_, 
                              kIntType)
            self.assertRaises(TypeError, convertTo, self._mime_txt_val_, 
                              kIntType)
            self.assertRaises(TypeError, convertTo, self._mime_fied_val_, 
                              kIntType)
        
        def testReal(self):
            try:
                val = convertTo(self._real_val_, kRealType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid real val %s"%(
                                                        str(self._real_val_)))
            else:
                self.assert_(type(val) == type(self._real_val_), 
                             "incorrect vsmf real returnd")
                self.assertEquals(val, self._real_val_, "real values differ")
                
            # all the following should fail
            self.assertRaises(TypeError, convertTo, self._uu_val_, 
                              kRealType)
            self.assertRaises(TypeError, convertTo, self._uu_str_val_, 
                              kRealType)
            self.assertRaises(TypeError, convertTo, self._mime_txt_val_, 
                              kRealType)
            self.assertRaises(TypeError, convertTo, self._mime_fied_val_, 
                              kRealType)
        
        def testString(self):
            try:
                val = convertTo(self._str_val_, kStrType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid string val %s"%(
                                                         str(self._str_val_)))
            else:
                self.assert_(type(val) == type(self._str_val_), 
                             "incorrect vsmf string returnd")
                self.assertEquals(val, self._str_val_, "string values differ")                
        
        def testUuid(self):
  
            try:
                val = convertTo(self._uu_str_val_, kUUType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid UUID val %s"%(
                                                      str(self._uu_str_val_)))
            else:
                self.assert_(MAYA.uuid.isa(val), "incorrect vsmf UUID returnd")
                self.assertEquals(val, MAYA.uuid.fromString(self._uu_str_val_),
                                  "UUID values differ")
                
        
        def testMime(self):
            try:
                val = convertTo(self._mime_txt_val_, kMimeType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid mime val %s"%(
                                                    str(self._mime_txt_val_)))
            else:
                self.assert_(hasattr(val, "_implements_mimeVal"), 
                             "incorrect vsmf mime returnd")
                self.assertEquals(val.buf, self._mime_txt_val_, 
                                  "mime values differ")
                self.assertEquals(val.type, "plain/text", 
                                  "mime types differ")
                
            try:
                val = convertTo(self._mime_fied_val_, kMimeType)
            except (TypeError, ValueError):
                self.fail("failed to convert a valid mime val %s"%(
                                                   str(self._mime_fied_val_)))
            else:
                self.assert_(hasattr(val, "_implements_mimeVal"), 
                             "incorrect vsmf mime returnd")
                self.assertEquals(val.buf, self._mime_fied_val_.value, 
                                  "mime values differ")
                self.assertEquals(val.type, 
                                  mimetypes.guess_type(
                                              self._mime_fied_val_.filename)[0], 
                                  "mime types differ")
                
                
            # all the following should fail
            self.assertRaises(TypeError, convertTo, self._bool_val_, kMimeType)
            self.assertRaises(TypeError, convertTo, self._int_val_, kMimeType)
            self.assertRaises(TypeError, convertTo, self._real_val_, kMimeType)
            self.assertRaises(TypeError, convertTo, self._uu_val_, kMimeType)
        
        
    unittest.main()
