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

Seung Chan Lim ( slim@maya.com )
"""

###############################################################################
#
###############################################################################
import sys
sys.path.insert(0, "../")
try:
    import xmlrpc
except ImportError:
    from MAYA.utils.xmlrpc import toXmlRpcDataType as x, toVsmfDataType as v
from MAYA.VIA import uuid, uform, vsmf
from MAYA.utils import date



###############################################################################
#
###############################################################################
BIG_NUMBER = 100
BIG_RANGE = range(BIG_NUMBER)




###############################################################################
#
###############################################################################
def convertUuid():
    uu = uuid.UUID()
    for i in BIG_RANGE:
        a = x(uu)
        v(a)
        
def convertUform():
    uf = uform.UForm(uuid.UUID(),
                     {"s" : "",
                      "i" : 1,
                      "f" : 1.2,
                      "e" : {"A" : 3},
                      "l" : [4,5,1,"a"]})
    for i in BIG_RANGE:
        a = x(uf)
        v(a)


def convertEform():
    ef =  {"s" : "",
           "i" : 1,
           "f" : 1.2,
           "e" : {"A" : 3},
           "l" : [4,5,1,"a"]}
    for i in BIG_RANGE:
        a = x(ef)
        v(a)


def convertBinary():
    b = vsmf.Binary("")
    for i in BIG_RANGE:
        a = x(b)
        #v(a)


def convertBoolean():
    b = True
    for i in BIG_RANGE:
        a = x(b)
        v(a)


def convertDate():
    d = date.fromUnix()
    for i in BIG_RANGE:
        a = x(d)
        v(a)
        

def convertList():
    l = [1] * BIG_NUMBER
    for i in BIG_RANGE:
        a = x(l)
        v(a)
        
    
def convertString():
    s = "a" * BIG_NUMBER
    for i in BIG_RANGE:
        a = x(s)
        v(a)


def convertInt():
    n = BIG_NUMBER
    for i in BIG_RANGE:
        a = x(n)
        v(a)


def convertFloat():
    f = float(BIG_NUMBER) + 0.23
    for i in BIG_RANGE:
        a = x(f)
        v(a)


def convertMime():
    m = vsmf.MimeVal("plain/text", "Hello World")
    for i in BIG_RANGE:
        a = x(i)
        #v(a)
    


###############################################################################
#
###############################################################################
if __name__ == "__main__":    
    from hotshot import Profile, stats
    from copy import copy

    prof_files = []
    keys = locals().keys()
    l = copy(locals())
    for k in keys:
        o = l[k]
        if k.startswith("convert") and callable(o):
            prof = Profile(k)
            prof_files.append(k)                    
            prof.runcall(o)            
            prof.close()

    for name in prof_files:
        stat = stats.load(name)
        stat.strip_dirs()
        stat.sort_stats("time", "calls")
        print "=" * 79
        print name
        print "=" * 79
        stat.print_stats()
