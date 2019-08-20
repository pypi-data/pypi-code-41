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


import time
from MAYA.VIA import vsmf
# The size you pass to the cache is the size that it guarantees.  It may be
# storing anything between that size and 2*size.  When it hits 2*size+1 it
# knocks back down to size.
class Cache:

    def __init__(self, halfsize=1000):
        self.cache_size = 2*halfsize
        self.halfsize = halfsize
        self.access_times = {}
        self.cache = {}
        self.cleanup = None
        self.cleanupdone = None

    # f must be a function that takes a cache obj
    def register_cleanup(self, f):
        self.cleanup = f
        return

    # f must be a function that takes a cache obj
    def register_cleanupdone(self, f):
        self.cleanupdone = f
        return

    def register_remove(self,f):
        self.rem = f
        return

    def get(self, k):        
        x = self.cache.get(k)
        if x:
            self.access_times[k] = time.time()
        return x

    def put(self, k, v):          
        self.access_times[k] = time.time()
        self.cache[k] = v        
        self.clean()
        return
        
    def cacheSize(self):
        x = len(vsmf.serialize(self.access_times.values()))+len(vsmf.serialize(self.cache.values()))
        x += len(vsmf.serialize(self.access_times.keys()))+len(vsmf.serialize(self.cache.keys()))
        return (len(self.cache),x)

    def remove(self, k):        
        try:
            del self.cache[k]
            self.rem(k)
        except:
            pass
        try:
            del self.access_times[k]
        except:
            pass
        return

    def clean(self):
        if len(self.cache) <= self.cache_size:
            return
        
        # run cleanup started hook
        if self.cleanup:
            self.cleanup(self)
        
        sortable = map(lambda k: (self.access_times[k], k), self.access_times.keys())
        sortable.sort()
        delkeys = sortable[:self.halfsize]
        for (t, k) in delkeys:
            self.remove(k)

        # run cleanup done hook
        if self.cleanupdone:
            self.cleanupdone(self)
        return
    
def test():
    c = Cache(3)
    data = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7]
    for x in data:
        c.put(x, 1)
    for x in data:
        print x, c.get(x)
    return

if __name__ == '__main__':
    test()
    
