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

#!/usr/bin/env python

# $Id: buckets.py 9726 2005-04-08 20:35:34Z widdows $

# It works like a hashtable, but stores multiple values for each key.

class Buckets:

    def __init__(self):
        self.table = {}

    def store(self, key, value):
        vs = self.table.get(key, [])
        if value in vs:
            return
        vs.append(value)
        self.table[key] = vs
        return
        
    def remove(self, key, value):
        vs = self.table.get(key, [])
        try:
            vs.remove(value)
            self.table[key] = vs
        except:
            return
        return

    def get(self, key):
        return self.table.get(key, [])

    def keys(self):
        return self.table.keys()

    def values(self):
        return self.table.values()

    def __len__(self):
        return len(self.table)

    def has_key(self, key):
        return self.table.has_key(key)

    def __setitem__(self, key, value):
        self.store(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        del self.table[key]

    def __contains__(self, key):
        return self.table.has_key(key)

            
def test():
    b = Buckets()
    for i in range(0, 100):
        mi = i % 10
        b[mi] = i
    keys = b.keys()
    keys.sort()
    for key in keys:
        if key in b:
            print key, b[key]
    return

if __name__ == '__main__':
    test()
    
