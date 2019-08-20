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


Seung Chan Lim (slim@maya.com)
"""

###############################################################################
#
###############################################################################
import string
import random
import os
import math
import time
from MAYA.unittest import reposunittest
from MAYA.VIA import uuid
from MAYA.datatypes import Binary
from MAYA.VIA import vsmf





###############################################################################
#
###############################################################################
class TestPartialSet(reposunittest.ReposEnabledTestCase):

    def __init__(self, repos=None):
        reposunittest.ReposEnabledTestCase.__init__(self,
                                                    module_path="../__init__.py",
                                                    repos=repos)
        random.seed()
        # create a 6 MB file
        a = string.ascii_letters
        max_a = len(a) - 1

        if not os.path.exists("./big.txt"):
            self.createBigFile("./big.txt")
        else:
            buf = (open("./big.txt", "r")).read()

            if not len(buf) == 6 * 1024 * 1024:

                self.createBigFile()
            
        
    def createBigFile(self, path):
                
        print "Creating 6MB file ...",

        fo = open("./big.txt", "w")
        
        for i in range( 6 * 1024 * 1024 ):
            fo.write(a[random.randrange(0, max_a)])
            
        fo.close()
        
        print "[ DONE ]"

        
    def test1(self):
        # read the big file
        print "Reading 6MB File ...",
        buf = vsmf.serialize((open("./big.txt", "r")).read())
        print "[ DONE ]"
        buf_len = len(buf)
        uu = uuid.UUID()
        chunk_size = 1024 * 1024
        print "Set on %s in %d byte chunks (%d bytes total)"%(uu.toString(),
                                                              chunk_size,
                                                              buf_len)
        # redundant, but just to be safe
        self.repos.setAttr(uu, "text_content", None)
        
        if self.repos.setAttr(uu, "description", "test started on %.2f"%(time.time())) == 0:
            # set in MB chunks
            start_offset = 0
            
            while start_offset < buf_len:

                buf_chunk = Binary(buf[start_offset : start_offset + chunk_size])
                print "setting %d bytes at %d ..."%(len(buf_chunk.getBuf()),
                                                    start_offset),
                self.assertEquals(self.repos.setAttrPart(uu,
                                                         "text_content",
                                                         start_offset,
                                                         0,
                                                         buf_chunk),
                                  0)


                print "[ DONE ]"
                start_offset += chunk_size
                
                
            # retrieve the buf and compare 
            self.repos.setParseForms(0)
            bin = self.repos.getAttr(uu, "text_content").getBuf()

            self.assertEquals(buf, bin)
        else:
            print "Permission denied"



        
###############################################################################
#
###############################################################################
if __name__ == "__main__":
    from MAYA.VIA.repos import Repository

    # repository parameter is optional
    reposunittest.main(Repository("condor.maya.com:6202"))

    

