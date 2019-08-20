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
Unit Test for the MAYA.role module

Seung Chan Lim (slim@maya.com)
"""

###############################################################################
# imports
###############################################################################
import imp
import os.path
import sys
import MAYA.VIA.uuid
import MAYA.VIA.uform
import MAYA.VIA.roles.role
from MAYA.unittest import reposunittest




###############################################################################
# globals
###############################################################################
role1_uu = MAYA.VIA.uuid.fromString("~01320C8980-B14F-49c7-8902-EA0B48D8F5E0")
role2_uu = MAYA.VIA.uuid.fromString("~015B4409B2-BC5F-4d06-B708-C24565490975")
role3_uu = MAYA.VIA.uuid.fromString("~019391BDBC-B4E8-4a95-B51E-063478C8F7CF")
role4_uu = MAYA.VIA.uuid.fromString("~0125055BA0-3AC3-44df-917B-11F3B003C61C")
rolea_uu = MAYA.VIA.uuid.fromString("~01A54BCDBF-44E1-44ee-89C1-36386672F3B1")


role1 = MAYA.VIA.uform.UForm(role1_uu,
                         eform={"name" : "delete me #1",
                                "attributes" : ["attr1", "attr2"],
                                MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_ : []})        
role2 = MAYA.VIA.uform.UForm(role2_uu,
                         eform={"name" : "delete me #2",
                                "attributes" : ["attr3", "attr4"],
                                MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_ : [role1.uuid]})        
role3 = MAYA.VIA.uform.UForm(role3_uu,
                         eform={"name" : "delete me #3",
                                "attributes" : ["attr5", "attr6"],
                                MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_ : [role2.uuid,
                                                                               role1.uuid]})
rolea = MAYA.VIA.uform.UForm(rolea_uu,
                         eform={"name" : "delete me #a",
                                "attributes" : ["attra"],
                                MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_ : [role1.uuid]})
role4 = MAYA.VIA.uform.UForm(role4_uu,
                         eform={"name" : "delete me #4",
                                "attributes" : ["attr7", "attr8"],
                                MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_ : [rolea.uuid,
                                                                               role1.uuid,
                                                                               role2.uuid,
                                                                               role3.uuid]})

# these are role uforms with its implied roles closure filled with
# UForms rather than UUIDs for testing the functions that can
# take advantage of this repository-less route
frole1 = MAYA.VIA.uform.UForm(role1_uu,
		      eform=role1.eform.copy())        
frole2 = MAYA.VIA.uform.UForm(role2_uu,
		      eform=role2.eform.copy())
frole2[MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_] = [frole1]
frole3 = MAYA.VIA.uform.UForm(role3_uu,
		      eform=role3.eform.copy())
frole3[MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_] = [frole1,
                                                       frole2]
frole4 = MAYA.VIA.uform.UForm(role4_uu,
		      eform=role4.eform.copy())
frolea = MAYA.VIA.uform.UForm(rolea_uu,
		      eform=rolea.eform.copy())
frolea[MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_] = [frole1]
frole4[MAYA.VIA.roles.role._IMPLIED_ROLES_CLOSURE_ATTR_] = [frolea,
                                                       frole1,
                                                       frole2,
                                                       frole3]




###############################################################################
# classes
###############################################################################

class Test(reposunittest.ReposEnabledTestCase):
    __TARGET_MODULE__ = "MAYA.VIA.roles"
    __TARGET_MODULE_PATH__ = "../../__init__.py"

    def __init__(self, repos=None):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    globals(),
                                                    module_name=Test.__TARGET_MODULE__,
                                                    module_path=Test.__TARGET_MODULE_PATH__,
                                                    repos=repos)

        if self.repos:
            # commit all the uforms to the repository
            result = self.repos.setAttr(role1)
            result = result or self.repos.setAttr(role2)
            result = result or self.repos.setAttr(role3)
            result = result or self.repos.setAttr(rolea)
            result = result or self.repos.setAttr(role4)
            
            if result != 0:
                # error committing, supress repository-based testing
                self.repos = None

        if not self.repos:
            # this is not an "else" situation to the above if statement
            sys.stderr.write("** WARNING: Repository-based tests suppressed **\n")
        

    def setUp(self):
        pass
                
    def tearDown(self):
        pass

    
    ###################################################################
    # createUFormOfRole tests
    ###################################################################
    def testCreateUFormOfRoleSimple(self):
        
        uf = createUFormOfRole()
        
        self._assertUFormBasics(uf)
        self.assertEquals(len(uf[_ROLES_ATTR_]), 1,
                          "Multiple roles present")
        self.assertEquals(uf[_ROLES_ATTR_][0], entity.uuid,
                          "Entity role not present")
        
        # same, but given a particular UUID
        uf = createUFormOfRole("~01458017F0-4510-4958-A58D-0356429BA852",repos=self.repos)
        
        self.assert_(MAYA.VIA.uuid.isa(uf.uuid),
                     "UForm has an invalid UUID")
        self.assertEquals(uf.uuid,
                          MAYA.VIA.uuid.fromString("~01458017F0-4510-4958-A58D-0356429BA852"),
                          "Incorrect UUID")


    def testCreateUFormOfRoleModerate(self, r=None):
        # test moderate case involving fetching one simple role
        uf = createUFormOfRole(roles=(role1,role1), create_attributes=0, repos=r)
        self._assertUFormBasics(uf)
        self._assertRoles(uf, 1, (role1.uuid,))
        
        # since we set create_attributes to 0
        self.assertRaises(AssertionError, self._assertAttributes, uf, (role1["attributes"],))
        
        uf = createUFormOfRole(roles=(role1,), repos=r)
        self._assertUFormBasics(uf)
        self._assertRoles(uf, 1, (role1.uuid,))

        self._assertAttributes(uf, (role1["attributes"],))


    def testCreateUFormOfRoleModerateWithRepos(self):
        
        if self.repos:
            self.testCreateUFormOfRoleModerate(self.repos)
        

    def testCreateUFormOfRoleComplex(self, r=None):

        # test moderate case involving fetching one simple role
        if r:
            uf = createUFormOfRole(roles=(role4.uuid,), create_attributes=0, repos=r)
        else:
            uf = createUFormOfRole(roles=(frole4,), create_attributes=0)
            
        self._assertUFormBasics(uf)
        self._assertRoles(uf, 1, (role4.uuid,))
        
        # since we set create_attributes to 0
        self.assertRaises(AssertionError, self._assertAttributes,
                          uf, (role1["attributes"],
                               role2["attributes"],
                               role3["attributes"],
                               role4["attributes"],
                               rolea["attributes"]))
        
        if r:
            uf = createUFormOfRole(roles=(role4.uuid,), repos=r)
        else:
            uf = createUFormOfRole(roles=(frole4,))
            
        self._assertUFormBasics(uf)
        self._assertRoles(uf, 1, (role4.uuid,))
        self._assertAttributes(uf, (role1["attributes"],
                                    role2["attributes"],
                                    role3["attributes"],
                                    role4["attributes"],
                                    rolea["attributes"]))

        
    def testCreateUFormOfRoleComplexWithRepos(self):

        if self.repos:
            self.testCreateUFormOfRoleComplex(self.repos)

            
    def testCreateUFormOfRoleCrazy(self, r=None):
        
        # order matters when passing in multiple implied roles tuple
        if r:
            uf = createUFormOfRole(roles=(role1.uuid,
                                          role2.uuid,
                                          role3.uuid,
                                          role4.uuid), create_attributes=0, repos=r)
        else:
            uf = createUFormOfRole(roles=(frole1,
                                          frole2,
                                          frole3,
                                          frole4), create_attributes=0)
            
        self._assertUFormBasics(uf)
        self._assertRoles(uf, 4, (role4.uuid, role3.uuid, role2.uuid, role1.uuid))
        
        # since we set create_attributes to 0
        self.assertRaises(AssertionError, self._assertAttributes,
                          uf, (role1["attributes"],
                               role2["attributes"],
                               role3["attributes"],
                               role4["attributes"],
                               rolea["attributes"]))

        if r:
            uf = createUFormOfRole(roles=(role1.uuid,
                                          role2.uuid,
                                          role3.uuid,
                                          role4.uuid), repos=r)
        else:
            uf = createUFormOfRole(roles=(frole1,
                                          frole2,
                                          frole3,
                                          frole4))

        self._assertUFormBasics(uf)
        self._assertRoles(uf, 4, (role4.uuid, role3.uuid, role2.uuid, role1.uuid))
        self._assertAttributes(uf, (role1["attributes"],
                                    role2["attributes"],
                                    role3["attributes"],
                                    role4["attributes"],
                                    rolea["attributes"]))


    def testCreateUFormOfRoleCrazyWithRepos(self):

        if self.repos:
            self.testCreateUFormOfRoleCrazy(self.repos)

            
    ###################################################################
    # createRoleUForm tests
    ###################################################################
    def testCreateRoleUFormSimple(self):
        ruf = createRoleUForm(label="Hello World")
        
        self._assertRoleBasics(ruf)
        self.assertEquals(len(ruf[_IMPLIED_ROLES_ATTR_]), 1,
                          "Multiple implied roles present")
        self.assertEquals(ruf[_IMPLIED_ROLES_ATTR_][0], entity.uuid,
                          "Entity role not implied")
        self.assertEquals(len(ruf[_IMPLIED_ROLES_CLOSURE_ATTR_]), 1,
                          "Multiple implied roles closure present")
        self.assertEquals(ruf[_IMPLIED_ROLES_CLOSURE_ATTR_][0], entity.uuid,
                          "Entity role not implied")
        self.assertEquals(ruf[entity._LABEL_ATTR_], "Hello_World",
                          "Incorrect Label [%s]"%(str(ruf[entity._LABEL_ATTR_])))

            

    def testCreateRoleUFormModerate(self, r=None):
        # just a new uform made out of inheritance
        if not r:
            ruf = createRoleUForm(implied_roles=(role1,))
        else:
            ruf = createRoleUForm(implied_roles=(role1.uuid,), repos=r)

        self._assertRoleBasics(ruf)
        self._assertImpliedRoles(ruf, 1, (role1.uuid,))

        # try to add some additional attributes
        if not r:
            ruf = createRoleUForm(implied_roles=(role1,),
                                  attrs=("additional_attr1",
                                         "additional_attr2"))
        else:                                        
            ruf = createRoleUForm(implied_roles=(role1.uuid,),
                                  attrs=("additional_attr1",
                                         "additional_attr2"),
                                  repos=r)
        
        self._assertRoleBasics(ruf)
        self._assertImpliedRoles(ruf, 1, (role1.uuid,))
        self.assert_("additional_attr1" in ruf["attributes"])
        self.assert_("additional_attr2" in ruf["attributes"])

        
    def testCreateRoleUFormModerateWithRepos(self):
        if self.repos:
            self.testCreateRoleUFormModerate(self.repos)


    def testCreateRoleUFormComplex(self, r=None):
        

        # try to add some additional attributes
        if not r:
            ruf = createRoleUForm(implied_roles=(role1,
                                                 role2,
                                                 role3,
                                                 role4,
                                                 rolea),
                                  attrs=("additional_attr1",
                                         "additional_attr2"))
        else:                                        
            ruf = createRoleUForm(implied_roles=(role1.uuid,
                                                 role2.uuid,
                                                 role3.uuid,
                                                 role4.uuid,
                                                 rolea.uuid),
                                  attrs=("additional_attr1",
                                         "additional_attr2"),
                                  repos=r)
        
        self._assertRoleBasics(ruf)
        self._assertImpliedRoles(ruf, 5, (role1.uuid, role2.uuid, role3.uuid, role4.uuid, rolea.uuid))
        self.assert_("additional_attr1" in ruf["attributes"])
        self.assert_("additional_attr2" in ruf["attributes"])


    def testCreateRoleUFormComplexWithRepos(self):
        if self.repos:
            self.testCreateRoleUFormComplex(self.repos)

            
    ###################################################################
    # uFormImpliesRole tests
    ###################################################################
    def testUFormImpliesRoles(self, r=None):
        if not r:
            # for failure
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role1.uuid]})                
            self.assertRaises(TypeError, uFormImpliesRole, uf, role1.uuid, r)
            self.assertRaises(TypeError, uFormImpliesRole, uf.uuid, role1, r)
        
        ###
        if r:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role1.uuid]})
        else:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role1]})

        self._assertRoleImplicationByUForm(uf, (role1,), r)

        ####
        
        if r:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role2.uuid]})
        else:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role2]})

        self._assertRoleImplicationByUForm(uf, (role1, role2), r)

        ####
        
        if r:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role3.uuid]})
        else:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role3]})

        self._assertRoleImplicationByUForm(uf, (role1, role2, role3), r)

        ####
        
        if r:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role4.uuid]})
        else:
            uf = MAYA.VIA.uform.UForm(eform={_ROLES_ATTR_ : [role4]})


        self._assertRoleImplicationByUForm(uf, (role1, role2, role3, role4), r)


    def testUFormImpliesRoleWithRepos(self):
        if self.repos:
            self.testUFormImpliesRoles(self.repos)



    ###################################################################
    # roleImpliesRole tests
    ###################################################################
    def testRoleImpliesRole(self, r=None):

        # for failure
        if not r:
            self.assertRaises(TypeError, roleImpliesRole, role4.uuid, role3.uuid, r)
            self.assertRaises(TypeError, roleImpliesRole, role4.uuid, role3, r)

        self._assertRoleImplicationByRole(role4, role4, r)
        self._assertRoleImplicationByRole(role4, role3, r)
        self._assertRoleImplicationByRole(role4, role2, r)
        self._assertRoleImplicationByRole(role4, role1, r)

        self._assertRoleImplicationByRole(role3, role3, r)
        self._assertRoleImplicationByRole(role3, role2, r)
        self._assertRoleImplicationByRole(role3, role1, r)
            
        self._assertRoleImplicationByRole(role2, role2, r)
        self._assertRoleImplicationByRole(role2, role1, r)

        self._assertRoleImplicationByRole(role1, role1, r)
        
        self.assertRaises(AssertionError, self._assertRoleImplicationByRole, role1, role2, r)
        self.assertRaises(AssertionError, self._assertRoleImplicationByRole, role1, role3, r)
        self.assertRaises(AssertionError, self._assertRoleImplicationByRole, role1, role4, r)
        self.assertRaises(AssertionError, self._assertRoleImplicationByRole, role2, role3, r)
        self.assertRaises(AssertionError, self._assertRoleImplicationByRole, role2, role4, r)
        self.assertRaises(AssertionError, self._assertRoleImplicationByRole, role3, role4, r)


    def testRoleImpliesRoleWithRepos(self):
        if self.repos:
            self.testRoleImpliesRole(self.repos)
            

    ###################################################################
    # assertion helper methods
    ###################################################################            
    def _assertRoleBasics(self, uf):
        self.assert_(MAYA.VIA.uform.isa(uf),
                     "Failed to return a uform")
        self.assert_(MAYA.VIA.uuid.isa(uf.uuid),
                     "UForm has an invalid UUID")
        self.assert_(uf.has_key("label"),
                     "UForm missing the label attribute")
        self.assert_(uf.has_key("attributes"),
                     "UForm missing the attributes attribute")
        self.assert_(uf.has_key(_IMPLIED_ROLES_ATTR_),
                     "UForm missing the implied roles attribute")
        self.assert_(uf.has_key(_IMPLIED_ROLES_CLOSURE_ATTR_),
                     "UForm missing the implied roles closure attribute")
        self.assert_(uf.has_key(_ROLES_ATTR_),
                     "UForm missing the roles attribute")
        self.assertEquals(type(uf[_ROLES_ATTR_]), type([]),
                          "Roles is not a collection")
        self.assertEquals(type(uf[_IMPLIED_ROLES_ATTR_]), type([]),
                          "Roles is not a collection")
        self.assertEquals(type(uf[_IMPLIED_ROLES_CLOSURE_ATTR_]), type([]),
                          "Roles is not a collection")
        self.assert_(not (filter(lambda r, m=MAYA.VIA.uuid:
                                 not m.isa(r), uf[_ROLES_ATTR_])),
                     "Role collection contains invalid uuid")
        self.assert_(not (filter(lambda r, m=MAYA.VIA.uuid:
                                 not m.isa(r), uf[_IMPLIED_ROLES_ATTR_])),
                     "Implied roles collection contains invalid uuid")
        self.assert_(not (filter(lambda r, m=MAYA.VIA.uuid:
                                 not m.isa(r), uf[_IMPLIED_ROLES_CLOSURE_ATTR_])),
                     "Implied roles closure collection contains invalid uuid")                
        self.assertEquals(len(uf[_ROLES_ATTR_]), 1,
                          "Multiple roles present")
        self.assertEquals(uf[_ROLES_ATTR_][0], role._UUID_,
                          "Role role not present")
        self._assertNoDuplicates(uf[_ROLES_ATTR_])
        self._assertNoDuplicates(uf[_IMPLIED_ROLES_ATTR_])
        self._assertNoDuplicates(uf[_IMPLIED_ROLES_CLOSURE_ATTR_])
        
        
    def _assertUFormBasics(self, uf):
        self.assert_(MAYA.VIA.uform.isa(uf),
                     "Failed to return a uform")
        self.assert_(MAYA.VIA.uuid.isa(uf.uuid),
                     "UForm has an invalid UUID")
        self.assert_(uf.has_key(_ROLES_ATTR_),
                     "UForm missing the roles attribute")
        self.assertEquals(type(uf[_ROLES_ATTR_]), type([]),
                          "Roles is not a collection")
        self.assert_(not (filter(lambda r, m=MAYA.VIA.uuid:
                                 not m.isa(r), uf[_ROLES_ATTR_])),
                     "Role collection contains invalid uuid")
        self._assertNoDuplicates(uf[_ROLES_ATTR_])


    def _assertRoles(self, uf, role_count, roles):
        self._assertCollection(uf, _ROLES_ATTR_, role_count, roles)


    def _assertImpliedRoles(self, uf, role_count, roles):
        self._assertCollection(uf, _IMPLIED_ROLES_ATTR_, role_count, roles)


    def _assertImpliedRolesClosure(self, uf, role_count, roles):
        self._assertCollection(uf, _IMPLIED_ROLES_CLOSURE_ATTR_, role_count, roles)

    
    def _assertCollection(self, uf, attr_name, count, collection):
        
        assert(len(collection) == count)
        
        self.assertEquals(len(uf[attr_name]), count,
                          "Expecting %d %s(s) to be present"%(count,
                                                              attr_name))
        
        self.assertEquals(len(filter(lambda r, u=uf, a=attr_name: r in uf[a],
                                     collection)), len(collection),
                          "Not all of %s found in %s"%(repr(collection), repr(uf[attr_name])))
        
    def _assertAttributes(self, uf, attrs):

        for attr in attrs:
            for key in attr:
                self.assert_(key in uf.keys(),
                             "%s not in %s"%(key, repr(uf.keys())))


    def _assertRoleImplicationByUForm(self, uf, roles, r=None):
        
        for role in roles:
            assert(MAYA.VIA.uuid.isa(role) or MAYA.VIA.uform.isa(role))
            
            result = uFormImpliesRole(uf, role, r)

            if MAYA.VIA.uform.isa(role):
                role_uu = role.uuid
            else:
                assert(MAYA.VIA.uuid.isa(role))
                role_uu = role

            
            self.assertEquals(result, 1,
                              "Does not imply role %s"%(role_uu.toString()))


    def _assertRoleImplicationByRole(self, roleA, roleB, r):
        if r:
            assert(MAYA.VIA.uform.isa(roleA) and MAYA.VIA.uform.isa(roleB))
            roleA = roleA.uuid
            roleB = roleB.uuid
        
        result = roleImpliesRole(roleA, roleB, r)
        self.assertEquals(result, 1,
                          "Role B is not implied by Role A")


    def _assertNoDuplicates(self, collection):
        assert(type(collection) in (type([]), type(())))
        
        tmp_list = []
        
        for item in collection:
            self.assert_(item not in tmp_list,
                         "%s is a duplicate in %s"%(repr(item),
                                                    repr(collection)))                
            tmp_list.append(item)





#######################################################################
# main
#######################################################################
if __name__ == "__main__":

    try:
        import unittest
        
    except ImportError:
	sys.stderr.write("You do not have the Unit Testing module installed... HALTED.")
	
	raise SystemExit
    else:
        
        try:
            if len(sys.argv) > 1:
                if sys.argv[1] == "--norepos":
                    sys.argv = sys.argv[1:] # pass the rest to unittest
                    
                    raise "Suppress Repository-based tests"
                
            repos = MAYA.VIA.repos.Repository("www.maya.com:6301")

        except:
            repos = None
        
        reposunittest.main(repos)

        raw_input("Press Enter to Exit")
