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
import unittest
from MAYA.unittest import reposunittest
from MAYA.utils.authentication import cookie_authenticator as c_auth
from MAYA.VIA import uuid




###############################################################################
#
###############################################################################
class AuthTest(reposunittest.ReposEnabledTestCase):
    def __init__(self, repos):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    module_path="../cookie_authenticator.py",
                                                    repos=repos)


    def testAuth(self):
        user_id = "limsc"
        password = "djslim"
        app_id = "testing"
        client_ip = "127.0.0.1"
        
        resp = c_auth.authenticateUser(self.repos, user_id, password,
                                       app_id, client_ip)

        self.assertNotEquals(resp, 0) # it authenticated
        
        ret = c_auth.verifyAuthentication(resp[c_auth.cookie_fmt["user"]%(app_id)],
                                          resp[c_auth.cookie_fmt["token"]%(app_id)],
                                          self.repos,
                                          app_id,
                                          client_ip)

        self.assertEquals(len(ret), 3) # good return value
        self.assertEquals(ret[0], user_id) # verified user
        self.assert_(uuid.isa(ret[1])) # portal
        self.assertEquals(ret[2], 0) # verification success code


        self.assertRaises(IOError,
                          c_auth.verifyAuthentication,
                          resp[c_auth.cookie_fmt["user"]%(app_id)],
                           resp[c_auth.cookie_fmt["token"]%(app_id)],
                           self.repos,
                           app_id,
                           "bogus_ip")
        user_uu = self.repos.getAttr(ret[1],
                                      "portal_users")[0][0]
        self.assertEquals(self.repos.getAttr(user_uu, "label"), user_id)
        





###############################################################################
#
###############################################################################
if __name__ == "__main__":
    from MAYA.VIA.repos import Repository

    reposunittest.main(Repository("condor.maya.com:6201"))
