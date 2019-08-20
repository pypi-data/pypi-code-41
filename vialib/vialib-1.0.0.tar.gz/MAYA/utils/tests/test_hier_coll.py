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
"""

###############################################################################
#
###############################################################################
from MAYA.unittest import reposunittest
from MAYA.VIA import uform, uuid





###############################################################################
#
###############################################################################
_INBOX_UUID_ = uuid.fromString("~0140EFC9FB54A84d0eA9D56F37A42788EC")
_AF_INBOX_UUID_ = uuid.fromString("~0140b5f8b0583811d8b55354e626af27bb")
_AF_ECONOMY_INBOX_UUID_ = uuid.fromString("~019a7f6fa0583a11d88d1e4ecd368661bf")
_AF_ECONOMY_2004_INBOX_UUID_ = uuid.fromString("~01ac4f35e05b3b11d8a3a3513c61302332")
_AF_ECONOMY_FEB_2004_INBOX_UUID_ = uuid.fromString("~01ac6492a05b3b11d8a3a360b90abb36a2")
_AF_ECONOMY_FEB_5_2004_INBOX_UUID_ = uuid.fromString("~01ac7868c05b3b11d8a3a34d2b0ca25d7e")
_COLLECTION_ROLE_ = uuid.fromString("~fd000a02510bfd17204424")





###############################################################################
#
###############################################################################
class Test(reposunittest.ReposEnabledTestCase):
    def __init__(self, repos=None):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    globals(),
                                                    module_path="../hier_coll.py",
                                                    repos=repos)

    def testReader(self):
        r = HcollectionReader(self.repos, _INBOX_UUID_)
        g = self.repos.getAttr
        self.assertEquals(g(_INBOX_UUID_, "members"), r.getMembers())
        self.assertEquals(g(_AF_INBOX_UUID_, "members"), r.getMembers(["afghanistan"]))
        self.assertEquals(g(_AF_ECONOMY_INBOX_UUID_, "members"), r.getMembers(["afghanistan", "economy"]))
        self.assertEquals(g(_AF_ECONOMY_2004_INBOX_UUID_, "members"), r.getMembers(["afghanistan", "economy", "2004"]))
        self.assertEquals(g(_AF_ECONOMY_FEB_2004_INBOX_UUID_, "members"), r.getMembers(["afghanistan", "economy", "2004", "february 2004"]))
        self.assertEquals(g(_AF_ECONOMY_FEB_5_2004_INBOX_UUID_, "members"), r.getMembers(["afghanistan", "economy", "2004", "february 2004", "february 05, 2004"]))
        self.assertEquals([], r.getMembers(["afghanistan", "economy", "2004", "february 2004", "february 05, 2004", "so what?"]))
        

    def testWriter(self):
        coll_uu = uuid.UUID()
        love_uu = uuid.UUID()
        hate_uu = uuid.UUID()

        print coll_uu
        
        self.repos.setAttr(love_uu, "name", "LOVE")
        self.repos.setAttr(hate_uu, "name", "hAtE")
        
        w = HcollectionWriter(self.repos, coll_uu)
        r = HcollectionReader(self.repos, coll_uu)
        
        self.assert_(_COLLECTION_ROLE_ in self.repos.getAttr(coll_uu, "roles"))

        self.assertEquals(w.addMember(["I"], love_uu), w.getMembers()[0])
        self.assertEquals(w.addMember(["I"], hate_uu), w.getMembers()[0])
        w.addMember(["I", "love", "you"], uuid.fromString("python-renex"))   
        w.addMember(["I", "Hate", "You"], uuid.fromString("python-renex"))


        self.assertEquals(len(r.getMembers()), 1)
        self.assertEquals(r.getMembers(["I"]), [love_uu, hate_uu])
        self.assertEquals(r.getMembers(["I", "LOVE", "YOU"]), [uuid.fromString("python-renex")])
        self.assertEquals(r.getMembers(["I", "HATE", "YOU"]), [uuid.fromString("python-renex")])

        self.assertRaises(ValueError, w.removeMember, ["I"], uuid.UUID())
        self.assertRaises(ValueError, w.removeMember, ["I", "LOVE", "HIM"], uuid.UUID())

        self.assertEquals(w.removeMember(["I"], hate_uu), w.getMembers()[0])


        w.addMember(["I", "LOVE", "YOU"], uuid.fromString("python-renex"))        
        w.addMember(["I", "LOVE", "YOU"], uuid.fromString("python-renex"))
        
        self.assertEquals(len(r.getMembers(["I", "LOVE", "YOU"])), 3)
        w.removeMember(["I", "LOVE", "YOU"], uuid.fromString("python-renex"), remove_dups=True)
        self.assertEquals(len(r.getMembers(["I", "LOVE", "YOU"])), 0)



if __name__ == "__main__":
    from MAYA.VIA.repos import Repository

    reposunittest.main(Repository("joshua3.maya.com:8888"))
