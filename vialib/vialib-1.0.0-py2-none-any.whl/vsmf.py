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
# Seung Chan Lim (slim@maya.com)


try:
    import warnings as _warnings
except:
    def _warn(msg):
        print "WARNING: %s\n"%(msg)
else:
    def _warn(msg):
        _warnings.warn(msg, category=DeprecationWarning, stacklevel=3)
import MAYA.datatypes
from VIA import vsmf





_warn("You should be using the new structure MAYA.VIA.vsmf to import this module")

# we do it the following way to also import names starting with "_"
(globals()).update(vsmf.__dict__)






class mimeVal(MAYA.datatypes.MimeVal):
    def __init__(self,type,buf):
        _warn("You should be using the new structure MAYA.datatypes.MimeVal to instantiate this class")

        MAYA.datatypes.MimeVal.__init__(self, type, buf)
       
        
class binary(MAYA.datatypes.Binary):
    def __init__(self,buf):
        _warn("You should be using the new structure MAYA.datatypes.Binary to instantiate this class")

        MAYA.datatypes.Binary.__init__(self, buf)
        
        
class null(MAYA.datatypes.Null):
    def __init__(self):
        _warn("You should be using the new structure MAYA.datatypes.Null to instantiate this class")
    
# hack per Jeff to deal with deprecated use of boolean class
def boolean(a):
    if a: return vsmf.True
    return vsmf.False
