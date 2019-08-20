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
Example Unit Test

Seung Chan Lim (slim@maya.com)
"""

###############################################################################
#
###############################################################################
from MAYA.unittest import reposunittest
blah = "1"



###############################################################################
#
###############################################################################
class TestSupport(reposunittest.ReposEnabledTestCase):

    def __init__(self, repos=None):
        """
        You can pass in the path to the module like this example shows
        or you can pass in the name of the module via the "module_name" keyword
        param if the PYTHONPATH is set accordingly.

        You can also send in your global namespace dictionary through the
        global_ns keyword param to allow the constructor to insert all the
        names found in the module's namespace into your global namespace. You
        will still be passed the namespace for each test method.

        You can also send in a repository connection that is to be shared
        across all the
        """
        
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    module_path="reposunittest.py",
                                                    repos=repos)
        print "Test Initializing"
    
        # optioanl
        self.setTestOrder(["test2", "test1"])
        
    ###########################################################################
    # tests - methods that start with the word "test"
    def test1(self):
        """
        All testXXX methods should be aware of two member variables of the self
        instance:
         1. module
         2. repos

        module refers to the module object being tested.
        repos refers to the repository object passed in from the very beginning

        Of course you have all the usual unit test methods from the unittest
        module, such as "assertEquals", "assertRaises", etc.. at your disposal
        """
        

        # you could save yourself some keystrokes an do the following
        # to make the values inside the module's namespace available in the
        # test method's local namespace, but please take caution when doing so
        # for it may shadow your global variables
        locals().update(self.module.__dict__)


    def test2(self):
        pass

        
###############################################################################
#
###############################################################################
if __name__ == "__main__":
    from MAYA.VIA.repos import Repository

    # repository parameter is optional
    reposunittest.main(Repository("joshua.maya.com:6200"))

    
