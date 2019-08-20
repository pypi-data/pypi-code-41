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

tests bidirectional data type coercion


Seung Chan Lim ( slim@maya.com )
"""

###############################################################################
#
###############################################################################
import xmlrpclib
import time
from MAYA.unittest import reposunittest
from MAYA.VIA import uuid, uform, vsmf
from MAYA.utils import date
from MAYA import datatypes





###############################################################################
#
###############################################################################
class TestSupport(reposunittest.ReposEnabledTestCase):
    def __init__(self, repos=None):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    module_path="../__init__.py",
                                                    repos=repos)


    def testString(self):
        xml_rpc_data = self.module.toXmlRpcDataType("hello")
        self.assertEquals(xml_rpc_data, "hello")
        self.assertEquals(self.module.toVsmfDataType(xml_rpc_data), "hello")


    def testInt(self):
        xml_rpc_data = self.module.toXmlRpcDataType(1)
        self.assertEquals(xml_rpc_data, 1)
        self.assertEquals(self.module.toVsmfDataType(xml_rpc_data), 1)


    def testBoolean(self):
        xml_rpc_data = self.module.toXmlRpcDataType(True)
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, xmlrpclib.Boolean(1))
        self.assert_(isinstance(native_data, datatypes.Boolean))
        self.assertEquals(native_data.val, 1)


    def testDateTime(self):
        t = time.time()
        d = date.fromUnix(t)
        date_string = d.toString()
        date_string = date_string.replace("-", "")
        date_string = date_string.replace("Z", "")
        xml_rpc_data = self.module.toXmlRpcDataType(d)
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, xmlrpclib.DateTime(date_string))
        self.assert_(isinstance(native_data, datatypes.Date))
        self.assertEquals(int(native_data.toUnix()), int(t))

        
    def testBinary(self):
        buf = """\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xec\x00\x00\x015\x08\x06\x00\x00\x00\xe4\x95\x0cG\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x07&IDATx\x9c\xed\xdc\xdbr\xdbF\x10E\xd1\xa6+\xff\xff\xcb\xca\x8b'Vd](\x8a\x00\xfa\xf4\xac\xf5\xe8\x92\t\xd8\xe0\xaen\x0f\x99\xdc^^^^"""

        xml_rpc_data = self.module.toXmlRpcDataType(datatypes.Binary(buf))
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, xmlrpclib.Binary(buf))
        self.assert_(isinstance(native_data, datatypes.Binary))
        self.assertEquals(native_data.getBuf(), buf)
                     

    def testUform(self):
        uu = uuid.UUID()
        xml_rpc_data = self.module.toXmlRpcDataType(uform.UForm(uu, {"name" : "foo"}))
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(type(xml_rpc_data), type({}))
        self.assertEquals(len(xml_rpc_data), 3)
        self.assertEquals(xml_rpc_data["type"], "uform")
        self.assertEquals(type(xml_rpc_data["uuid"]) , type({}))
        self.assertEquals(xml_rpc_data["uuid"]["type"], "uuid")
        self.assertEquals(xml_rpc_data["uuid"]["buffer"], uu.getBuf())
        self.assertEquals(xml_rpc_data["eform"], {"type" : "eform",
                                                  "avpairs" : [("name", "foo")]})
        
        self.assert_(isinstance(native_data, uform.UForm))
        self.assertEquals(native_data.items(), [("name", "foo")])


    def testUuid(self):
        uu = uuid.UUID()
        buf = uu.getBuf()
        xml_rpc_data = self.module.toXmlRpcDataType(uu)
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, {"type" : "uuid",
                                         "buffer" : xmlrpclib.Binary(buf)})
        self.assert_(isinstance(native_data, uuid.UUID))
        self.assertEquals(native_data.getBuf(),  buf)
        

    def testEform(self):
        uu = uuid.UUID()
        buf = uu.getBuf()
        xml_rpc_data = self.module.toXmlRpcDataType({"members" : [uu]})
        self.assertEquals(xml_rpc_data, {"type" : "eform",
                                         "avpairs" : [("members", [{"type" : "uuid",
                                                                    "buffer" : xmlrpclib.Binary(buf)}])]})
        if (hasattr(uform, "EForm")): # test only if newer version of the module is used
            native_data = self.module.toVsmfDataType(xml_rpc_data)
            
            self.assert_(isinstance(native_data, uform.EForm))
            
            self.assert_(native_data.has_key("members"))
            self.assertEquals(type(native_data["members"]), type([]))
            self.assert_(isinstance(native_data["members"][0], uuid.UUID))
            self.assertEquals(native_data["members"][0].getBuf(), buf)
            

    def testMime(self):
        buf = """\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xec\x00\x00\x015\x08\x06\x00\x00\x00\xe4\x95\x0cG\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x07&IDATx\x9c\xed\xdc\xdbr\xdbF\x10E\xd1\xa6+\xff\xff\xcb\xca\x8b'Vd](\x8a\x00\xfa\xf4\xac\xf5\xe8\x92\t\xd8\xe0\xaen\x0f\x99\xdc^^^^"""
        xml_rpc_data = self.module.toXmlRpcDataType(datatypes.MimeVal("image/png",
                                                                      buf))
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, {"type" : "mime",
                                         "content_type" : "image/png",
                                         "content_buffer" : xmlrpclib.Binary(buf)})
        self.assert_(isinstance(native_data, datatypes.MimeVal))
        self.assertEquals(native_data.getType(), "image/png")
        self.assertEquals(native_data.getBuf(), buf)
                     

    def testArray(self):
        uu = uuid.UUID()
        buf = uu.getBuf()
        xml_rpc_data = self.module.toXmlRpcDataType([1, uu, "hello"])
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, [1, {"type" : "uuid",
                                             "buffer" : xmlrpclib.Binary(buf)}, "hello"])
        self.assertEquals(type(native_data), type([]))
        self.assertEquals(len(native_data), 3)
        self.assertEquals(native_data[0], 1)
        self.assert_(isinstance(native_data[1], uuid.UUID))
        self.assertEquals(native_data[1].getBuf(), buf)
        self.assertEquals(native_data[2], "hello")
        

    def testDouble(self):
        xml_rpc_data = self.module.toXmlRpcDataType(1.1)
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, 1.1)
        self.assertEquals(native_data, 1.1)


    def testNull(self):
        xml_rpc_data = self.module.toXmlRpcDataType(datatypes.Null())
        native_data = self.module.toVsmfDataType(xml_rpc_data)
        self.assertEquals(xml_rpc_data, {"type" : "null"})
        self.assert_(isinstance(native_data, datatypes.Null))





###############################################################################
#
###############################################################################
if __name__ == "__main__":
    reposunittest.main()
