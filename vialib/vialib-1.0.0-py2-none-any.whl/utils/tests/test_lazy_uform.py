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
Unit Tests for the Lazy UForm interface

The uform to be tested against looks like so

top-collection:
    name - top collection
    members - [ sub-collection x n ]

sub-collection
    name - sub collection %d
    members - [ number-collection, alphabet-collection ]

number-collection
    name - number collection
    members - [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

alphabet-collection
    name - alphabet collection
    members - [ a, b, c, d, e, f, g, h, i, j, k, l,
                m, n, o, p, q, r, s, t, u, v, w, x, y, z]
                
Seung Chan Lim (slim@maya.com)
"""

###############################################################################
#
###############################################################################
import socket
import time
from MAYA.unittest import reposunittest
from MAYA.VIA import uform, uuid




###############################################################################
#
###############################################################################
class TestLazyUform(reposunittest.ReposEnabledTestCase):
    def __init__(self, repos=None):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    globals(),
                                                     module_path="../lazyuform.py",
                                                     repos=repos)

        print "Preparing uforms",

        # we need a few uforms to test this
        nc = uform.UForm(eform={"name" : "number collection",
                                "members" : [0, 1, 2, 3, 4, 5,
                                             6, 7, 8, 9]})
        ac = uform.UForm(eform={"name" : "alphabet collection",
                                "members" : ['a', 'b', 'c', 'd',
                                             'e', 'f', 'g', 'h',
                                             'i', 'j', 'k', 'l',
                                             'm', 'n', 'o', 'p',
                                             'q', 'r', 's', 't',
                                             'u', 'v', 'w', 'x',
                                             'y', 'z']})
        sc1 = uform.UForm(eform={"name" : "sub collection 1",
                                 "members" : [nc.uuid, ac.uuid]})
        sc2 = uform.UForm(eform={"name" : "sub collection 2",
                                 "members" : [nc.uuid, ac.uuid]})
        tc = uform.UForm(eform={"name" : "top collection",
                                "members" : [sc1.uuid, sc2.uuid]})
        
        if repos.setAttr(nc) == 0:
            print ".",
            if repos.setAttr(ac) == 0:
                print ".",
                if repos.setAttr(sc1) == 0:
                    print ".",
                    if repos.setAttr(sc2) == 0:
                        print ".",
                        if repos.setAttr(tc) == 0:
                            print "[ success ]"
                            self.uuid = tc.uuid
                            self.uform = LazyUform(tc.uuid, repos)
                        else:
                            print "[ fail ]"
                    else:
                        print "[ fail ]"
                else:
                    print "[ fail ]"
            else:
                print "[ fail ]"
        else:
            print "[ fail ]"
        
    def testSimple(self):
        if hasattr(self, "uform"):
            # check the length first
            self.assertEquals(len(self.uform["name"]), len("top collection"))
            self.assertEquals(self.uform["name"], "top collection")
            self.assertEquals(len(self.uform["members"]), 2)

    def testLevelOne(self):
        if hasattr(self, "uform"):
            #print self.repos.getAttr(self.uform.uuid, "members")
            #print self.uform["members"]
            self.uform["members"][0]
            self.uform["members"][0]["members"]
            self.assertEquals(len(self.uform["members"][0]["members"]), 2)
            self.assertEquals(len(self.uform["members"][1]["members"]), 2)
            self.assertEquals(self.uform["members"][0]["name"], "sub collection 1")
            self.assertEquals(self.uform["members"][1]["name"], "sub collection 2")
            
    def testLevelTwo(self):
        if hasattr(self, "uform"):
            self.assertEquals(self.uform["members"][0]["members"][0]["name"], "number collection")
            self.assertEquals(self.uform["members"][0]["members"][1]["name"], "alphabet collection")            
            self.assertEquals(self.uform["members"][1]["members"][0]["name"], "number collection")
            self.assertEquals(self.uform["members"][1]["members"][1]["name"], "alphabet collection")


    def testLevelThree(self):
        if hasattr(self, "uform"):
            self.assertEquals(len(self.uform["members"][1]["members"][0]["members"]), 10)
            self.assertEquals(len(self.uform["members"][1]["members"][1]["members"]), 26)
            self.assertEquals(self.uform["members"][0]["members"][0]["members"][5:9], [5,6,7, 8])
            self.assertEquals(self.uform["members"][0]["members"][1]["members"][-3:], ['x','y','z'])

    def testPrefetchUForm(self):
        r = Repository("joshua3.maya.com:8889")
        u = uform.UForm(eform={"name" : "prefetched uform",
                               "number" : 1,
                               "float" : 2.2,
                               "eform" : {"a" : "b"},
                               "list" : [1, 2, "a", "B"],
                               "relation" : self.uform.uuid})
        u["cycle"] = u.uuid
        self.assertEquals(r.setAttr(u), 0)

        s = time.time()
        uf1 = LazyUform(u.uuid, r)
        uf1.preFetch(["name", "number", "float", "eform", "list", "relation", "cycle"])
        uf1["cycle"].preFetch(["name"])
        print time.time() - s
        
        # we close the socket just to make sure we're depending on
        # the pre fetch
        s = time.time()
        uf2 = LazyUform(u.uuid, r)
        uf2["name"]
        uf2["number"]
        uf2["float"]
        uf2["eform"]
        uf2["list"]
        uf2["relation"]
        uf2["cycle"]
        uf2["cycle"]["name"]
        print time.time() - s
        r.s.close()
        
        #self.assertEquals(len(uf1.keys()), 7 + 3) # 3 for shepherd attributes
        self.assertEquals(uf1["name"], "prefetched uform")
        self.assertEquals(uf1["number"], 1)
        self.assertEquals(uf1["float"], 2.2)
        self.assertEquals(uf1["eform"], {"a" : "b"})
        self.assertEquals(uf1["list"], [1,2, "a", "B"])
        self.assertEquals(uf1["cycle"]["name"], "prefetched uform")
        # now since the socket is closed, the following test should
        # raise an exception
        try:
            uf1["relation"]["name"]
        except socket.error:
            pass
        else:
            self.assert_("This should have raised an error!" == 0)

        try:
            uf1["cycle"]["number"]
        except socket.error:
            pass
        else:
            self.assert_("This should have raised an error!" == 0)
            
    def testPrefatchCollection(self):
        muf = uform.UForm()
        members = []
        
        for i in range(50):
            uf = uform.UForm(eform={"name" : "uform %d"%(i)})
            self.assertEquals(self.repos.setAttr(uf), 0)
            members.append(uf.uuid)
            
        muf["members"] = members
        self.assertEquals(self.repos.setAttr(muf), 0)
        
        luf = LazyUform(muf.uuid, self.repos)
        m = luf["members"]
        self.assert_(isinstance(m, LazyUform.ValueProxy))
        self.assertEquals(len(m), 50)
        
        s = time.time()
        
        for i in range(len(m)):
            self.assertEquals(m[i]["name"], "uform %s"%(i))
        print time.time() - s
        

        luf = LazyUform(muf.uuid, self.repos)
        m = luf["members"]
        self.assert_(isinstance(m, LazyUform.ValueProxy))
        
        s = time.time()
        m.preFetch(["name"])
        
        for i in range(len(m)):
            self.assertEquals(m[i]["name"], "uform %s"%(i))

        print time.time() - s


        members.append({}) # bogus value
        self.assertEquals(self.repos.setAttr(muf), 0)

        luf = LazyUform(muf.uuid, self.repos)
        m = luf["members"]
        self.assert_(isinstance(m, LazyUform.ValueProxy))
        self.assertEquals(len(m), 51)
        # because of the bogus value this will fail
        try:
            m.preFetch(["name"])
        except:
            pass
        else:
            self.assert_("This should raise an exception" == 0)
            
        
    def testNonzero(self):
        self.assertEquals(self.uform or "I'm zero", self.uform)


    def testGet(self):
        uf = uform.UForm(eform={"name" : "HA HA"})
        self.assertEquals(self.repos.setAttr(uf), 0)
        luf = LazyUform(uf.uuid, self.repos)
        self.assertEquals(luf.get("name"), "HA HA")
        

    def testKeys(self):
        uf = uform.UForm(eform={"a" : 1, "b" : 2})
        self.assertEquals(self.repos.setAttr(uf), 0)
        luf = LazyUform(uf.uuid, self.repos)
        for key in uf.keys():
            self.assert_(key in luf.keys())

    def testPrefetchUuid(self):
        uf1 = uform.UForm(eform={"relation" : uuid.UUID()})
        uf2 = uform.UForm(eform={"members" : [uf1.uuid]})
        self.assertEquals(self.repos.setAttr(uf1), 0)
        self.assertEquals(self.repos.setAttr(uf2), 0)
        luf = LazyUform(uf2.uuid, self.repos)
        coll = luf["members"]
        coll.preFetch(["relation"])

        for item in coll:
            self.assertEquals(type(item["relation"]), type(LazyUform(None, None)))

        

    def testLock(self):
        pass
        
        
###############################################################################
#
###############################################################################
if __name__ == "__main__":
    from MAYA.VIA.repos import Repository

    reposunittest.main(Repository("joshua3.maya.com:8889"))
