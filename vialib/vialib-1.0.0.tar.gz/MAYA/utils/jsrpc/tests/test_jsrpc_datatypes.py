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
import time,binascii
from MAYA.utils import jsrpc
from MAYA.unittest import reposunittest
from MAYA.VIA import uuid, uform, vsmf
from MAYA import datatypes
from MAYA.utils import date
from MAYA import datatypes
from StringIO import StringIO





###############################################################################
#
###############################################################################
class TestSupport(reposunittest.ReposEnabledTestCase):
    def __init__(self, repos=None):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    module_path="../__init__.py",
                                                    repos=repos)


    def testString(self):
        js_rpc_data = self.module.toJsRpcDataType("hello world")
        self.assertEquals(repr(js_rpc_data), "'hello world'")
        self.assertEquals(self.module.toVsmfDataType(js_rpc_data), "hello world")


    def testInt(self):
        js_rpc_data = self.module.toJsRpcDataType(1)
        self.assertEquals(repr(js_rpc_data), "1")
        self.assertEquals(self.module.toVsmfDataType(js_rpc_data), 1)


    def testBoolean(self):
        js_rpc_data = self.module.toJsRpcDataType(True)
        native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assert_(repr(js_rpc_data) in ("true", "1"))
        self.assert_(isinstance(native_data, datatypes.Boolean) or
                     (type(native_data) == type(False)))
        try:
            self.assertEquals(native_data.val, 1)
        except AttributeError:
            self.assertEquals(native_data, True)


    def testDate(self):

        """
        java script date test:
        d = new Date(1137005269000); alert(d.toString());
        """

        t = time.time()
        d = date.fromUnix(t)
        date_string = d.toString()
        date_string = date_string.replace("-", "")
        date_string = date_string.replace("Z", "")
        js_rpc_data = self.module.toJsRpcDataType(d)
        native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(repr(js_rpc_data), "new Date(%d)"%(long(t * 1000)))
        self.assert_(isinstance(native_data, datatypes.Date))
        self.assertEquals(int(native_data.toUnix()), int(t))

        #a test with timezone
        d = date.fromUnix(t, -5)
        js_rpc_data = self.module.toJsRpcDataType(d)
        native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(repr(js_rpc_data), "new Date(%d)"%(long(t * 1000) + 3600000 * -5))
        self.assert_(isinstance(native_data, datatypes.Date))
        self.assertEquals(int(native_data.toUnix()), int(t))
        self.assertEquals(native_data.timezone(), -5)

    def testDouble(self):
        js_rpc_data = self.module.toJsRpcDataType(1.1)
        native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(repr(js_rpc_data)[:3], "1.1")
        self.assertEquals(native_data, 1.1)


    def testNull(self):
        js_rpc_data = self.module.toJsRpcDataType(datatypes.Null())
        native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(repr(js_rpc_data), "null")
        self.assert_(isinstance(native_data, datatypes.Null))


        
    def testUuid(self):
        uu = uuid.UUID()
        buf = uu.getBuf()
        js_rpc_data = self.module.toJsRpcDataType(uu)
        native_data = self.module.toVsmfDataType(js_rpc_data)
        #self.assert_(isinstance(js_rpc_data, jsrpc.Uuid))
        self.assertEquals(repr(js_rpc_data), "new StringUuid('%s')"%(uu.toString()))
        self.assert_(isinstance(native_data, uuid.UUID))
        self.assertEquals(native_data.getBuf(),  buf)

        
    def testArray(self):
        uu = uuid.UUID()
        buf = uu.getBuf()
        js_rpc_data = self.module.toJsRpcDataType([1, uu, "hello world"])
        native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(repr(js_rpc_data), "[1, new StringUuid('%s'), 'hello world']"%(uu.toString()))
        self.assertEquals(type(native_data), type([]))
        self.assertEquals(len(native_data), 3)
        self.assertEquals(native_data[0], 1)
        self.assert_(isinstance(native_data[1], uuid.UUID))
        self.assertEquals(native_data[1].getBuf(), buf)
        self.assertEquals(native_data[2], "hello world") 

        
    def testUform(self):
        uu = uuid.UUID()
        uf = uform.UForm(uu, {"name" : "foo"})
        js_rpc_data = self.module.toJsRpcDataType(uf)
        native_data = self.module.toVsmfDataType(js_rpc_data)

        #self.assert_(isinstance(js_rpc_data, jsrpc.Uform))
        #self.assertEquals(type(js_rpc_data.uuid) , jsrpc.Uuid)
        self.assertEquals(repr(js_rpc_data.uuid), "new StringUuid('%s')"%(uu.toString()))
        self.assertEquals(type(js_rpc_data.eform), type({}))
        self.assertEquals(js_rpc_data.eform, {"name" : "foo"})
        self.assertEquals(repr(js_rpc_data.eform), "{'name': 'foo'}")
        
        self.assert_(isinstance(native_data, uform.UForm))
        self.assertEquals(native_data.items(), [("name", "foo")])


    def testEform(self):
        uu = uuid.UUID()
        buf = uu.getBuf()
        js_rpc_data = self.module.toJsRpcDataType({"members" : [uu]})
        self.assertEquals(repr(js_rpc_data), "{'members': [new StringUuid('%s')]}"%(uu.toString()))
        
        if (hasattr(uform, "EForm")): # test only if newer version of the module is used
            print "=" * 70
            print js_rpc_data
            print ">" * 70
            native_data = self.module.toVsmfDataType(js_rpc_data)

            self.assert_(isinstance(native_data, uform.EForm) or
                         type(native_data) == type({}))
            
            self.assert_(native_data.has_key("members"))
            self.assertEquals(type(native_data["members"]), type([]))
            print native_data
            self.assert_(isinstance(native_data["members"][0], uuid.UUID))
            self.assertEquals(native_data["members"][0].getBuf(), buf)
           
    def testNonde(self):
        val = None
        self.assertEquals(repr(self.module.toJsRpcDataType(val)), repr(jsrpc.Undefined()))
        d = {"hello" : None}
        d_j = jsrpc.toJsRpcDataType(d)
        self.assertEquals(repr(d_j), "{'hello': undefined}")

            
    def testFault(self):
        f = jsrpc.Fault(1, "hello world")
        self.assertEquals(f.code, 1)
        self.assertEquals(f.msg, "hello world")
        self.assertEquals(repr(f), "{'error': [0x1, 'hello world']}")

    def testSuccess(self):        
        uu = uuid.UUID()
        buf = uu.getBuf()
        js_rpc_data = self.module.toJsRpcDataType(uu)
        s = jsrpc.Success(js_rpc_data)
        self.assertEquals(s.response, js_rpc_data)
        self.assertEquals(repr(s), "{'error': 0, 'response': new StringUuid('%s')}"%(uu.toString()))

    
    def testMime(self):
        buf = """\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xec\x00\x00\x015\x08\x06\x00\x00\x00\xe4\x95\x0cG\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x07&IDATx\x9c\xed\xdc\xdbr\xdbF\x10E\xd1\xa6+\xff\xff\xcb\xca\x8b'Vd](\x8a\x00\xfa\xf4\xac\xf5\xe8\x92\t\xd8\xe0\xaen\x0f\x99\xdc^^^^"""

        js_rpc_data = self.module.toJsRpcDataType(datatypes.MimeVal("image/png",
                                                                      buf))
        #native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(js_rpc_data, jsrpc.Url(StringIO(buf)))
        #self.assert_(isinstance(native_data, datatypes.MimeVal))
        #self.assertEquals(native_data.getType(), "image/png")
        #self.assertEquals(native_data.getBuf(), buf)


    def testBinary(self):
        
        buf = """\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xec\x00\x00\x015\x08\x06\x00\x00\x00\xe4\x95\x0cG\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x07&IDATx\x9c\xed\xdc\xdbr\xdbF\x10E\xd1\xa6+\xff\xff\xcb\xca\x8b'Vd](\x8a\x00\xfa\xf4\xac\xf5\xe8\x92\t\xd8\xe0\xaen\x0f\x99\xdc^^^^"""

        js_rpc_data = self.module.toJsRpcDataType(datatypes.Binary(buf))
        #native_data = self.module.toVsmfDataType(js_rpc_data)
        self.assertEquals(js_rpc_data, binascii.b2a_base64(buf))
        #self.assert_(isinstance(native_data, datatypes.Binary))
        #self.assertEquals(native_data.getBuf(), buf)



    def testComplex(self):
        def _check(a, b):
            if type(a) == type([]):
                map(_check, a, b)
            elif type(a) == type({}):
                map(_check, a.values(), b.values())
            else:
                self.assertEquals(jsrpc.toVsmfDataType(a), b)
                
        l = [1, 10030, [[[uuid._ ( '~01fdaeaf2ce2da11d6b9d5461e22d7315b' ), datatypes.Boolean(1), -34.666698455810547, -58.5, 'Buenos Aires', uuid._ ( 'GM~016a23b290dc7f11d69b61506e6e8925e4' ), None, 1], [uuid._ ( '~01fdbe8226e2da11d6b9d568cc521b510a' ), datatypes.Boolean(1), -7.2333002090454102, 112.75, 'Surabaja', uuid._ ( 'GM~016a23b290dc7f11d69b61506e6e8925e4' ), None, 1], [uuid._ ( '~01fddbd808e2da11d6b9d507eb2135547d' ), datatypes.Boolean(1), 40.75, -74.0, 'New York', uuid._ ( 'GM~016a23b290dc7f11d69b61506e6e8925e4' ), None, 1], [uuid._ ( '~01a380b7b65b6211d6ac2222da32b8333f' ), datatypes.Boolean(1), -74.5, 179.9833333, 'Pennell Bank', uuid._ ( 'fbd7aaad6cd55518:2bbaaccf:dea0963bd7:-7ffa' ), None, 1]], []]]

        js_rpc_data = self.module.toJsRpcDataType(l)
        
        #self.assertEquals(repr(js_rpc_data).strip(),
        #"[1, 10030, [[[new StringUuid('~01fdaeaf2ce2da11d6b9d5461e22d7315b'), true, -34.666698455810547, -58.5, 'Buenos Aires', new StringUuid('GM~016a23b290dc7f11d69b61506e6e8925e4'), null, 1], [new StringUuid('~01fdbe8226e2da11d6b9d568cc521b510a'), true, -7.2333002090454102, 112.75, 'Surabaja', new StringUuid('GM~016a23b290dc7f11d69b61506e6e8925e4'), null, 1], [new StringUuid('~01fddbd808e2da11d6b9d507eb2135547d'), true, 40.75, -74.0, 'New York', new StringUuid('GM~016a23b290dc7f11d69b61506e6e8925e4'), null, 1], [new StringUuid('~01a380b7b65b6211d6ac2222da32b8333f'), true, -74.5, 179.9833333, 'Pennell Bank', new StringUuid('fbd7aaad6cd55518:2bbaaccf:dea0963bd7:-7ffa'), null, 1]], []]]")
        native_data = jsrpc.toVsmfDataType(js_rpc_data)
        self.assertEquals(len(native_data), len(l))
        _check(js_rpc_data, native_data)

    def testUformBug(self):
        uf = uform.UForm(uuid._ ( '~01c30c89f008d711d9a8c920811a154fd9' ),
                         {'publisher': uuid._ ( '~fd000efddafc1731' ),
                          'genders_served': None, 
                          'description': None,
                          'prog_intake_process': None,
                          'facility': uuid._ ('~01a3432a9007ea11d9a8980033325620ec' ),
                          'image': None, 'creator': [uform.UForm(uuid._ ( '~01eb1e57ce068d11d98be82d1e04742b5b' ),
                                                                 {'name': 'Allegheny County Department of Human Services'}),
                                                     uuid._ ( '~fd000efddafc1731' )],
                          'elegibility': None,
                          'modified': None,
                          'cost': None,
                          'hours_of_operation': None,
                          'max_age_served': None, 
                          'min_age_served': None,
                          'name': 'Service Offering 5753'})
        js_rpc_data = self.module.toJsRpcDataType(uf)
 
        self.assertEquals(repr(js_rpc_data), """new Uform(new StringUuid('~01c30c89f008d711d9a8c920811a154fd9'), {'publisher': new StringUuid('~fd000efddafc1731'), 'genders_served': undefined, 'description': undefined, 'prog_intake_process': undefined, 'facility': new StringUuid('~01a3432a9007ea11d9a8980033325620ec'), 'image': undefined, 'creator': [new Uform(new StringUuid('~01eb1e57ce068d11d98be82d1e04742b5b'), {'name': 'Allegheny County Department of Human Services'}), new StringUuid('~fd000efddafc1731')], 'elegibility': undefined, 'modified': undefined, 'cost': undefined, 'hours_of_operation': undefined, 'max_age_served': undefined, 'min_age_served': undefined, 'name': 'Service Offering 5753'})""")

    def testFromString(self):
        pass



    
        
###############################################################################
#
###############################################################################
if __name__ == "__main__":
    reposunittest.main()
