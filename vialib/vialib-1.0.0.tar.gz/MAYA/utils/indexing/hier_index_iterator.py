#######################################################################
#
#       COPYRIGHT 2006 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
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
from MAYA.VIA import repos, uuid
from MAYA.utils.indexing import hier_index

# Class to encapsulate our generic iterator.
class HierIndexIterator:
    
    # Initialize object with index and function to apply to each
    # record
    def __init__(self, hi, func):
        self.hi = hi
        self.func = func
        self.count=0

    # Recursive function to traverse a node in a hierarchical index.
    # The node is either an inner node, in which case we can expect it
    # to have child nodes, or a leaf node, in which case it has
    # members.  No assumption is made as to the structure of the
    # index.
    def iterate(self, path=[]):
        
        children = self.hi.getChildren(path)
        if children:

            # If there are any children, iterate over them, append
            # each one in turn to the imput path, and make recursive
            # call to go one level deeper.
            for c in children:
                new_path = path + [ c ]
                self.iterate(new_path)

        else:

            # Assume this is a leaf node, and get the members.
            records = self.hi.getMembers(path) or []

            # Apply function to each record.
#            for x in records:
            apply(self.func, (records, path,))
            self.count+=1
#            print self.count

def flight_example():
    # The root for flight manifest index UUIDs.
    index_root_uuid = uuid.fromString('~fd000efdda.da.14')

    # Create a repository connection to one of the Joshua cluster
    # server side proxies.
    r = repos.Repository('replication.civium.net:80')

    # Construct instance of a hierarchical index reader.
    hi = hier_index.HIndexReader(r, index_root_uuid)

    # Simple function to print an attribute from a passenger record.
    def my_func(uu):
        print uu
         
    # Create iterator object
    iterator = HierIndexIterator(hi, my_func)
    
    # To start iteration, simply make the first call with an empty
    # path.
    
    iterator.iterate(path=['us','dc'])
    return

def pop_place_example():
    r = repos.Repository('replication.civium.net:80')
    pop_place_root = uuid._('~fd000efddada14')
    pop_place_idx = hier_index.HIndexReader(r, pop_place_root)
    def my_func(uu):
        print uu
    iterator = HierIndexIterator(pop_place_idx, my_func)
    iterator.iterate()
    return

def school_example():
    r = repos.Repository('replication.civium.net:80')
    school_root = uuid._('~012e60ad80890611dabf14046922801ea6')
    school_idx = hier_index.HIndexReader(r, school_root)
    def my_func(uu):
        print uu
    iterator = HierIndexIterator(school_idx, my_func)
    iterator.iterate()
    return

if __name__ == '__main__':
    flight_example()

    
