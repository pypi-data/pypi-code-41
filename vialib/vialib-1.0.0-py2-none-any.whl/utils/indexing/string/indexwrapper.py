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
# imports
from MAYA.utils.indexing.string.st_index import stringIndex
from MAYA.utils.shepherding import waitForPresence as wfp
from MAYA.VIA import uuid, uform, repos
import types

# a dictionary interface to string indexes
def _(r, u = None):
    return StringIndexWrapper(r, u)


# test btree index: ~01eaeef83e1bbb11daa62b445d72e26bab

#
#
#
class StringIndexWrapper:
    def __init__(self, r, rootuu = None):
	# the string index impl
	wfp(r, rootuu)
	wfp(r, r.getAttr(rootuu, 'btree_root'))
	self.sIndex = stringIndex(r, st_index = rootuu, use_cache = False)
	return

    # ----- Repository Interface 

    # ----- Non dictionary Interface -------------------------------------------
    def __getattr__(self, atr):
	if atr == 'uuid':
	    return self.sIndex.get_index()
	raise AttributeError

    # ----- Dictionary Interface -----------------------------------------------
    def __getitem__(self, key):
	self.sIndex.spath = [] # clear the current search path
	leafkids = self.sIndex.traverse(self.sIndex.root, key)
	if leafkids == None:
	    raise ValueError
	if type(leafkids) != types.ListType:
	    raise ValueError
	# 
	value = None
	for kid in leafkids:
	    if kid[0] == key:
		value = kid[1]
		break
	else:
	    raise KeyError
	
	# inline
	if type(value) == types.ListType:
	    return value

	# offline
	if uuid.isa(value):
	    value = self.sIndex.getAttr(value, 'members')
	    if value == None:
		return []
	    elif type(value) == types.ListType:
		return value

	#
	raise ValueError

    def __setitem__(self, key, value):
	self.sIndex.insert((key, value))
	pass

    def __contains__(self, key):
	self.sIndex.spath = [] # clear the current search path
	leafkids = self.sIndex.traverse(self.sIndex.root, key)
	if leafkids == None:
	    return False
	if type(leafkids) != types.ListType:
	    return False
	for kid in leafkids:
	    if kid[0] == key:
		return True
	return False

    def __len__(self):
	pass
    
    def __delitem__(self, key):
	self.sIndex.delete(key)
	
    # ----- Helper that waits for presence 

    # reproduces the functionality in traverse -- maybe this should be
    # pushed into that
    def ensurePathExists(self, k):
	# start at root
	next = self.sIndex.root
	while next:
	    wfp(self.sIndex.r, next)
	    kids = self.sIndex.getAttr(next, 'children')

	    childpos = 1
	    while childpos < len(kids):
		if k < kids[childpos][0]:
		    self.ensurePathExists(kids[childpos-1][1], k)

    # ----- Iterator interface -----------------------------------------------
    def iterkeys(self):
	return StringIndexWrapper.TreeWalker(self)

    def __iter__(self):
	return self.iterkeys()

    # ----- Iterator impl -----------------------------------------------
    class TreeWalker:
	# . tree walker does a depth first search of the btree 
	# . maintains two fields: the current leaf and the an edge of the
	#   tree
	def __init__(self, iw):
	    self.sIndex = iw.sIndex;
	    self.searchpath = [self.sIndex.root]
	    self.explorenextnode()

	# 
	def explorenextnode(self):
	    if not self.searchpath:
		return

	    # remove left most
	    node, self.searchpath = self.searchpath[0], self.searchpath[1:]
	    while 'leaf' != self.sIndex.getAttr(node, 'type'):
		children = map(lambda x: x[1], self.sIndex.getAttr(node, 'children'))
		self.searchpath = children + self.searchpath # prepend the children
		node, self.searchpath = self.searchpath[0], self.searchpath[1:]
	    # 
	    self.currentleaf = map(lambda x: x[0], self.sIndex.getAttr(node, 'children'))

	# 
	def getsearchpath(self):
	    return self.searchpath

	# 
	def getcurrentleaf(self):
	    return self.currentleaf

	# 
	def hasNext(self):
	    return self.searchpath or self.currentleaf

	#
	def getNext(self):
	    if not self.currentleaf:
		self.explorenextnode()
	    ret, self.currentleaf = self.currentleaf[0], self.currentleaf[1:]
	    return ret


	# ----- Iterator Interface -----------------------------------------------
	def __iter__(self):
	    return self

	def next(self):
	    if not self.hasNext():
		raise StopIteration
	    return self.getNext()
	

if __name__ == "__main__":
    # test the treewalker: ~01eaeef83e1bbb11daa62b445d72e26bab
    # test the treewalker: ~01f764278001eb100bbf9e527e4ef95422
    ii = _(repos.Repository('localhost:6200'), uuid._('~01f764278001eb100bbf9e527e4ef95422'))
    tw = StringIndexWrapper.TreeWalker(ii)
    print 'cl', tw.getcurrentleaf()
    print 'sp', tw.getsearchpath()
    while tw.hasNext():
	print tw.getNext()
    
    print 'iterator style'
    for k in ii:
	print k

    print 'more iterator style'
    for k in ii:
	print k
