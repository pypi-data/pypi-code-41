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
Excuse the verbose name for the module... Couldn't think of a good one

ReposEnabledTestCase is a wrapper for doing tests that involve the
repository and also provides convenient means of loading the target
module to be tested

The difference in the way the main works is that by default it has a
runTest method that goes through the methods collection that starts
with the preifx "test" and runs them all.

Seung Chan Lim (slim@maya.com)

"""

###############################################################################
# imports
###############################################################################
import unittest
import imp
import os.path
import sys
import traceback




###############################################################################
# globals
###############################################################################






###############################################################################
# classes
###############################################################################
class ReposEnabledTestCase(unittest.TestCase):
    _TEST_PREFIX_ = "test"
    _TEST_PREFIX_LEN_ = len(_TEST_PREFIX_)
    
    def __init__(self, global_ns=None, module_name=None, module_path=None, repos=None):
        """
        namespace
        """
        
        unittest.TestCase.__init__(self, methodName="runTest")

        self._tests_ = []
        
        # allows multiple methods to be passed in to be run within one
        # instance of the Test Case object

        # try and load the module from either the name or the path
        if not module_name and not module_path:
            
            raise TypeError, "__init__ takes at least 1 of either the module_name or the module_path argument (neither given)"
            # -----------------------------------------------------------------
        else:
            try:
                # try to load the module from specified relative path    
                
                try:
                    if module_path:
                        path = os.path.abspath(module_path)
                        mod = imp.load_source("testModule", path)
                    else:

                        raise IOError
                        # -----------------------------------------------------
                except IOError:

                    raise IOError
                    # ---------------------------------------------------------
                except:
                    sys.stderr.write("*** Module %s has errors ***\n\n"%(path))
                    traceback.print_exc()
                    
                    raise SystemExit
                    # ---------------------------------------------------------
                    
            except IOError:
                if module_path:
                    sys.stderr.write("*** Target module to be tested not found in %s***\n"%(path))
                    
                try:
                    # can't find it in path, try from sys.path space
                    try:
                        if module_name:
                            mod = __import__(module_name, globals(), locals(), ['*'])
                        else:
                            
                            raise ImportError
                            # -----------------------------------------------------
                    except ImportError:
                        
                        raise ImportError
                        # ---------------------------------------------------------
                    except:
                        sys.stderr.write("*** Module %s has errors ***\n\n"%(module_name))
                        traceback.print_exc()
                                
                        raise SystemExit
   	                # ---------------------------------------------------------
                except ImportError:
                    if module_name:
                        sys.stderr.write("*** Target module to be tested not found as %s***\n"%(module_name))
                    
                    raise SystemExit
	            # ---------------------------------------------------------
                else:
                    module_path = mod.__path__[0]

            sys.stderr.write("Target module: %s\n"%(module_path))

            # put everything in the module's namespace into the namespace of
            # target test module except for the special variables that start
            # and end with "__"
            module_ns = dict(filter(lambda i: i[0][:1] != "__" and i[0] != "self", mod.__dict__.items()))
            
            self.module = mod
            
            if global_ns:
                global_ns.update(module_ns)
                
            self.repos = repos
            
                
    def setTestOrder(self, test_names_in_order):
        num_tests = range(len(test_names_in_order))
        
        for i in num_tests:
            method = test_names_in_order[i]
            
            if hasattr(self, method):
                self._tests_.append(method)

                
    def runTest(self, result):
        if len(self._tests_) > 0:
            attrs = self._tests_
        else:
            attrs = dir(self)
        
        for attr in attrs:
            if attr[:self._TEST_PREFIX_LEN_] == self._TEST_PREFIX_:
                # whoa, this is a big hack... 
                self._TestCase__testMethodName = attr
                self._testMethodName = attr
                self.run(result)
                


                
class ReposEnabledTestLoader(unittest.TestLoader):
    def __init__(self, repos):
        if hasattr(unittest.TestLoader, "__init__"):
            print "WARNING: potential interface change on unittest module"
            unittest.TestLoader.__init__(self)
            
        self.repos = repos
        
    def loadTestsFromTestCase(self, testCaseClass):
        """
        overridding the previous definition by just
        instantiating the class with no arguments
        which will make it run the "runTest" method
        """
        
        return ReposEnabledTestSuite([testCaseClass(repos=self.repos)])


class ReposEnabledTestSuite(unittest.TestSuite):
    def __call__(self, result):
        for test in self._tests:
            if result.shouldStop:
                break

            test.runTest(result)
            
        return result


class ReposEnabledTestProgram(unittest.TestProgram):
    """
    a subclass that forces the use of ReposEnabledTestLoader
    as the TestLoader
    """
    
    def __init__(self, repos=None):
        unittest.TestProgram.__init__(self, testLoader=ReposEnabledTestLoader(repos))
        
        
        
main = ReposEnabledTestProgram
