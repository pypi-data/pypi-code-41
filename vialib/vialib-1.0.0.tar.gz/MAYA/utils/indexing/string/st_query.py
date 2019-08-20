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

from MAYA.VIA import uuid,uform,repos
from MAYA.utils.shepherding import waitForPresence
TIMEOUTSECS=0

class stringQuery:

  def getAttrs(self,uu,attr):
    waitForPresence(self.r,uu,TIMEOUTSECS)
    m=uform.UForm(uu)
    for i in attr:
	m[i]=None
    return self.r.getAttr(m)
  
  def getAttr(self,uu,attr):
    waitForPresence(self.r,uu,TIMEOUTSECS)
    return self.r.getAttr(uu,attr)

  def __init__(self,r,st_index,type_marker='leaf',debug=0) :
    self.r=r
    self.count=0
    self.spath=[]
    self.st_prefix=st_index
    self.typemarker=type_marker
    self.debug=debug
    if self.st_prefix==None or not uuid.isa(self.st_prefix): 
	print('***ERROR***--No String Index to query on...Please provide the st_index uuid')
	return
    else:
    
        self.stform=self.getAttrs(self.st_prefix,['btree_root','fanout_max','node_kinds','resultslist_max_length'])
	if self.typemarker not in self.stform['node_kinds']:
	    print('***ERROR***--Incorrect Type Marker for the given Index. Please use the correct one')
	    return
        self.root=self.stform['btree_root']
	self.listlimit=self.stform['resultslist_max_length']
        #print self.root
       

  def getRoot(self):
    
    thisroot=self.getAttr(self.st_prefix,'btree_root')
    if thisroot!=self.root:
        self.root=thisroot
        
    return self.root



  def ptQuery(self,query):
    self.spath=[]
    results=[]
    if not (type(query)==type('') or type(query)==type(u'')):
	print('***Warning***..query key must be a string..returning Empty List')
	
    else:
	results=self.exact_match(self.traverse(self.getRoot(),query),query)
    return results

  def prefixQuery(self,query):
    self.spath=[]
    results=[]
    if not (type(query)==type('') or type(query)==type(u'')):
	print('***Warning***..query key must be a string..returning Empty List')
	
    else:
	results=self.prefix_match(self.traverse(self.getRoot(),query),query)
    return results

  def rangeQueryMax(self,query,maxresults=None,with_keys=None):
    (key1,key2)=query
    return self.range_match_max(key1,key2,maxresults,with_keys=with_keys)

  def rangeQuery(self,query):
    return self.rangeQueryMax(query)[0]

  def get_ulist(self,row,with_keys=None):
    #self.debug(row) # jus for display now
    
    if row[-1] > self.listlimit:
	ret = self.getAttr(row[1],'members')
    else:
        ret = row[1]
    if with_keys:
      def wk(a,k=row[0]): return k,a
      ret = map(wk,ret)
    return ret

  def get_results(self,u,key):
    qresults=[]
    uf=self.getAttrs(u,['type','children'])
    if uf['type'] ==self.typemarker:
	for inst in uf['children']:
		#if key==inst[0]:
		if inst[0].startswith(key):
		    if inst[-1] > self.listlimit:
			qresults.extend(self.getAttr(inst[1],'members'))
		    else:
			qresults.extend(inst[1])
	return qresults
    else:
	    childpos=1
	    while childpos < len(uf['children']):
		if key < uf['children'][childpos][0]:
		    qresults=self.get_results(uf['children'][childpos-1][1],key)
	    	    return qresults
		childpos+=1
	    qresults=self.get_results(uf['children'][-1][1],key)
	    return qresults

  def traverse(self,node,key):
    self.spath.append(node)
    if self.debug:print self.spath
    uf=self.getAttrs(node,['type','children'])
    if uf['type'] !=self.typemarker:
	childpos=1
	while childpos < len(uf['children']):
	    if key < uf['children'][childpos][0]:
                return self.traverse(uf['children'][childpos-1][1],key)
	    childpos+=1
	return self.traverse(uf['children'][-1][1],key)  # else return the last leaf
    else:
        return uf['children']
	#return node # the prev return saves a getAttr to lookup for the children attribute, as the last entry in self.spath will have the leaf node's uuid anyways..


  def exact_match(self,children,key):
    qresults=[]
    #children=getchildren(node,key)
    for inst in children:
	if key==inst[0]: #exact match
	    qresults.extend(self.get_ulist(inst))
    return qresults

  def prefix_match(self,children,key):
    qresults=[]
    #children=getchildren(node,key)
    for inst in children:
	if inst[0].startswith(key): #prefix match
	    qresults.extend(self.get_ulist(inst))
    if len(children)==0: # check for empty root/ node! 
	return qresults
    if children[-1][0].startswith(key) :
	if self.getLastChild(self.root)[-1][0]!=children[-1][0]: # see if the prefix extends into the next leaf.. if the last entry is a match..
	    qresults.extend(self.prefix_match(self.getNext(),key))
	#self.debug('more to come soon.....')
    return qresults
    

  def getNext(self):
    if len(self.spath)==1: return None 
    prev=self.spath.pop() #removes the last level entry
    thislevel=self.spath[-1]
    children=self.getAttr(thislevel,'children')
    for i in range(len(children)):
	if prev==children[i][1]:
	    if i!=(len(children)-1): # check for last entry
		#self.spath.append(children[i+1][1])
		return self.getFirstChild(children[i+1][1])
	    else:
		return self.getNext()
    if self.debug:print 'I should NOT be printed at all !!!!somethings wrong!!!'
    return None

  def getFirstChild(self,node):
    self.spath.append(node)
    uf=self.getAttrs(node,['type','children'])
    if uf['type'] !=self.typemarker:
	return self.getFirstChild(uf['children'][0][1])
	
    else:
	return uf['children']

  def getLastChild(self,node):
    #self.spath.append(node) ##Not needed as this is only used for checking for termination and moreover it corrupts the path for prefix search
    uf=self.getAttrs(node,['type','children'])
    if uf['type'] !=self.typemarker:
	return self.getLastChild(uf['children'][-1][1])
	
    else:
	return uf['children']

  def iterate(self,func=None):
    self.spath=[]
    children=self.getFirstChild(self.getRoot())
    allChildren=[]
    for i in children:
        if not func:
          allChildren.extend(self.get_ulist(i))
        else:
          for x in self.get_ulist(i):
            func(x)
    while 1:
      
	children=self.getNext()
	if children==None: break
        for i in children:
          if not func:
            allChildren.extend(self.get_ulist(i))
          else:
            for x in self.get_ulist(i):
              func(x)
    if not func:
      return allChildren

  def iterateKeys(self,func=None):
    self.spath=[]
    children=self.getFirstChild(self.getRoot())
    allChildren=[]
    for i in children:
        if not func:
          allChildren.extend(i[0])
        else:
          func(i[0])
    while 1:
	children=self.getNext()
	if children==None: break
        for i in children:
          if not func:
            allChildren.extend(i[0])
          else:
            func(i[0])
    if not func:
      return allChildren

  def range_match(self,key1,key2):
        return self.range_match_max(key1,key2)[0]

  # returns (results, resumekey)
  # note that in the case of duplicate keys, more results than maxresults may be returned
  # so that the "resumekey" can be correctly identified
  def range_match_max(self,key1,key2,maxresults=None,with_keys=None):
	qresults=[]
	self.spath=[]
    	self.traverse(self.getRoot(),key2)
	check_path=self.spath
	self.spath=[]
	children=self.traverse(self.getRoot(),key1)
        if len(children) == 0: # empty index case
          return (qresults,None)
	if children[-1][0] < key1: #the case where key1 is greater than the last entry of this leaf
          if children[-1][0] == self.getLastChild(self.root)[-1][0]: #if this is the same as the last node of the tree..no matching keys..return empty result
            return qresults,None
          else:
	    children=self.getNext() # AND lesser than the first entry of the next leaf

	wrongkey=True
	for i in range(len(children)):
            # leftmost bug... children[i][0] can be None
	    if children[i][0] is not None and (children[i][0].startswith(key1) or children[i][0] > key1):
		children=children[i:]
		wrongkey=False
		break
	if wrongkey: 
	    print('Incorrect range (key1) value, pls try a different one')
	    return qresults,None
	if self.spath==check_path: # the range is within the same leaf...needs trimming
	    for i in range(len(children)):
	        if children[i][0] > key2:
		    children=children[0:i]
		    wrongkey=False
		    break
	    if wrongkey:
		print('Incorrect range (key2) value, pls try a different one')
	        return qresults,None
	    for i in children:
	        if maxresults is not None and len(qresults) >= maxresults:
	            return qresults,i[0]
	    	qresults.extend(self.get_ulist(i,with_keys))
	    return qresults,None

	for i in children:
	    if maxresults is not None and len(qresults) >= maxresults:
	        return qresults,i[0]
	    qresults.extend(self.get_ulist(i,with_keys)) #add these results
	
	while self.spath!=check_path:
	    children=self.getNext()
	    if self.spath==[self.getRoot()]: # this happens when key2 < key1.. not a good query..but anyways
		print('dont catch me now')
		break
	    if maxresults is not None and len(qresults) >= maxresults:
	        return qresults,children[0][0]
	    if children[-1][0] <= key2: # the whole leaf is less than key2, so add them all
		for ch in children:
		    if maxresults is not None and len(qresults) >= maxresults:
		        return qresults,ch[0]
		    qresults.extend(self.get_ulist(ch,with_keys)) # change this if you want results immediately!
	    else:
		for i in range(len(children)):
	    	    if children[i][0] > key2: # less than or equal to
			for ch in children[0:i]:
		            if maxresults is not None and len(qresults) >= maxresults:
		                return qresults,ch[0]
		    	    qresults.extend(self.get_ulist(ch,with_keys))
			break
	return qresults,None
    
if __name__=='__main__':
    r=repos.Repository('joshua.maya.com:8888')
    #st_index=uuid._('~01efb1c7c4197a11da8f630ded66470c16') # Index of populated places in Pennsylvania. USE lowercase keys
    st_index=uuid._('~01972da88c306811da95fc5cba63f75ff4')
    myQ=stringQuery(r,st_index) #query object
    
    #Point Query example
    
    query='school'
    result=myQ.ptQuery(query)
    print 'query results for point query ',query
    for i in result:
      print r.getAttr(i,'name'),' --- ',i
    print '----------------------------------------'
    
    #prefix query example
    '''query="crossroads"
    result=myQ.prefixQuery(query)
    print 'query results for prefix query ',query
    for i in result:
	if r.getAttr(i, 'name') == '':
            print r.getAttr(i,'name'),' --- ',i
    print '_______________________________________'
    print len(result)
    print result
'''
    #range query example
    '''query=('mcca','mccf')
    #result=myQ.rangeQuery(query)
    print 'query results for range query ',query
    for i in result:
	print r.getAttr(i,'name'),' --- ',i
    print '---------------------------------------'
    '''
    
    
