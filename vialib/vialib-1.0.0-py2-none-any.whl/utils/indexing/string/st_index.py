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

from MAYA.VIA import uuid,uform,vsmf,repos
import time
from MAYA.utils import scalablecoll
LIST_LIMIT=3
DEBUG=0

try:
  x = IS_A_LIST([])
except NameError, e:
  def IS_A_LIST(a):
    return type(a) is list or type(a) is tuple

#The public methods are:

#__init__ - which either loads a existing index passed thro the 'st_index' parameter or creates a new index based on the other parameters. For details of the parameters, check the init method. It also has some init parameters for building the index such as 'use_cache' etc

# get_index(self) - returns the head of the index. This is useful to obtain the index head for newly created index.

#  insert(self,m)-- where m is a tuple ( key, value) where key is a string and value is either a singleton value for the given key or a list/tuple of values pertaining to the given key. 

#  delete(self,m)-- m is either a string(key) in which case the key and all its corresponding values are deleted or m is a tuple of strings(key,value) where value is the value to be deleted for the given key. 

#  flush_cache(self,m): -- If 'use_cache' was enabled, this method needs to be called to commit all changes since last flush into uforms. m is required to force the flush, can be anything but None. If you are using cache, make sure you had flushed them before querying the index else the results may not be what you would expect.

#  ptQuery(self,m):-- m is a query string which is queried to look for matching results in the index. Return value is either a list of zero of more values. -- Note: Added the query feature in this code to facilitate both query and add/deletes on the same code base - feb 3, 2011.

class stringIndex :

  
  def getAttr_repos(self,uf,attr=None):

	if uuid.isa(uf):
	    uu=uf
	    if attr==None:
		attr=self.default_attrs #if no attributes are specified,use the default attr list
		uf=uform.UForm(uu)
		for x in attr:
		    uf[x]=None
		return self.r.getAttr(uf)
	    elif type(attr)==type('') or type(attr)==type(u''):
		return self.r.getAttr(uu,attr)
	    else:
		uf=uform.UForm(uu)
		for x in attr:
		    uf[x]=None
		return self.r.getAttr(uf)
	else:
	    return self.r.getAttr(uf)

  def getAttr_cache(self,uuid,attr):
    if self.myrepos.has_key(uuid) and self.myrepos[uuid].has_key(attr) :
      self.myrepos[uuid]['time']=int(time.time())
      return self.myrepos[uuid][attr]
    else:
      if len(self.myrepos) >= self.cachemaxsize:
        self.clearcache()  
      m=self.getAttr_repos(uuid)
      if not self.myrepos.has_key(uuid):
        self.myrepos[uuid] = {}
      for k in m.keys():
        self.myrepos[uuid][k]=m[k]
      self.myrepos[uuid]['time']=int(time.time())
      return self.myrepos[uuid][attr]        

  def getAttr_cache_old(self,uuid,attr) :
    #if DEBUG: print "in getattr cache",uuid,attr,len(self.myrepos),self.myrepos.get(uuid)
    if len(self.myrepos) < self.cachemaxsize:
	if self.myrepos.has_key(uuid) and self.myrepos[uuid].has_key(attr) :
	    self.myrepos[uuid]['time']=int(time.time())
	    return self.myrepos[uuid][attr]
	    
	else:
	
	    m=self.getAttr_repos(uuid)
	    if self.myrepos.has_key(uuid):
		for atr in m.keys():
                  if self.myrepos[uuid].has_key(atr) and DEBUG: print "already have key with value..overwriting as",atr,self.myrepos[uuid][atr],m[atr]
                  self.myrepos[uuid][atr]=m[atr]
	    else: 
		rdict={}
		for k in m.keys():
		    rdict[k]=m[k] 
		self.myrepos[uuid]=rdict
	    self.myrepos[uuid]['time']=int(time.time())
    	    return self.myrepos[uuid][attr]
    else:
	self.clearcache()
        ret = self.getAttr(uuid,attr)
        if DEBUG: print "response for getAttr is",uuid,attr,ret
	return ret
  
  def clearcache(self,flush=None):
	if DEBUG:print('clearing cache')
	if flush:	# this would flush my entire local cache.. 
	    if DEBUG:print('flusing entire cache')
	    for i in self.myrepos.keys():
		#print i,self.myrepos[i]
	        if self.myrepos[i].has_key('dirty') and self.myrepos[i]['dirty']==1: # if there had been a setAttr for 
		    uf=uform.UForm(i)							 #this uuid, then do a setAttr to repository
		    for a in self.myrepos[i].keys():
		      if a not in ['time','dirty']:   				     
		        uf[a]=self.myrepos[i][a]
		    self.setAttr_repos(uf)
	    	del self.myrepos[i]

	else:
	    thistime=time.time()
	    tulist=[]
	    for u in self.myrepos.keys():
	        tulist.append((thistime-self.myrepos[u]['time'],u))
	    tulist.sort()
	    if DEBUG:print(len(tulist))
            if DEBUG:
              for k in self.myrepos:
                print k,self.myrepos[k]
              print "----"
	    tulist=tulist[self.cacheminsize:] #list of uuids to be removed from cache
	    for t,i in tulist:
	        if self.myrepos[i].has_key('dirty') and self.myrepos[i]['dirty']==1: # if there had been a setAttr for 
		    uf=uform.UForm(i)							 #this uuid, then do a setAttr to repository
		    for a in self.myrepos[i].keys():
		      if a not in ['time','dirty']:   				     
		        uf[a]=self.myrepos[i][a]
		    self.setAttr_repos(uf)
                    if DEBUG: print "writing to repos",uf
	        del self.myrepos[i]		# and then delete it from my local cache, assuming that my setAttr_repos doesnt fail!
	    tulist=[]
	if DEBUG:print(len(self.myrepos))
        if DEBUG:
          for k in self.myrepos:
            print k,self.myrepos[k]
          print "----"
	

  def setAttr_cache(self,uuid,attr):
    if len(self.myrepos) < self.cachemaxsize:
	if self.myrepos.has_key(uuid):
	    for i in range(len(attr)/2):
	        self.myrepos[uuid][attr[i*2]]=attr[(i*2)+1]
	else:
	    rdict={}
	    for i in range(len(attr)/2):
		rdict[attr[i*2]]=attr[(i*2)+1]
	    self.myrepos[uuid]=rdict

	self.myrepos[uuid]['time']=int(time.time())
	self.myrepos[uuid]['dirty']=1
    else:
	self.clearcache()
	self.setAttr(uuid,attr)

  def setAttr_repos(self,uf,attr=None):
	if uuid.isa(uf):
	    uu=uf
            if IS_A_LIST(attr):
              for i in range(len(attr)/2):
		self.r.setAttr(uu,attr[i*2],attr[(i*2)+1])
	else:
	    self.r.setAttr(uf)
    	    

  def create_new_index(self,uid=None,fanout_max=512,fanout_min=None,source_dataset=None,name=None,description=None,resultslist_max_length=LIST_LIMIT):
    if not uuid.isa(uid):
	uid=uuid.UUID() #create a new one, if no uuid was passed in
    if fanout_max==None:
	#self.message('error','fanout_max value is invalid. Enter a value')
	print('fanout_max value is invalid. Enter a value')
	return None
    
    if fanout_min==None: fanout_min=int(0.5*float(fanout_max))
    
   
    if name==None: name='Generic B-Tree Index'
    label='_'.join(name.upper().split(' '))
    if description==None and uuid.isa(source_dataset): description='This is a string index of the dataset pointed by '+ source_dataset.toString()
    else: description='This is a string index'
    
    uf=uform.UForm(uid)
    rootuf=uform.UForm()
    rootuf['type']='leaf'
    rootuf['children']=[]
    rootuf['roles']=[self.bTreerole]
    self.setAttr_repos(rootuf)
    uf['btree_root']=rootuf.uuid
    uf['name']=name
    uf['label']=label
    if source_dataset!=None:
        uf['source_dataset']=source_dataset
    uf['fanout_min']=fanout_min
    uf['fanout_max']=fanout_max
    uf['resultslist_max_length']=resultslist_max_length
    uf['node_kinds']=['internal node','leaf']
    #uf['results_types']={'0': 'instance list',
    #			 '1': 'instance collection'}
    uf['roles']=[self.btreeHeadRole]
    self.setAttr_repos(uf)
    self.root=uf['btree_root']
    self.listlimit=uf['resultslist_max_length']
    self.fanout_max=fanout_max
    self.fanout_min=fanout_min
    self.fanout_minmax=int(self.fanout_min*self.lazyfactor)
    self.fanout_maxxed=int(self.fanout_max+(self.fanout_max*self.lazyfactor))
    if DEBUG:print uf
    return uf.uuid

  def __init__(self,r,st_index=None,fanout_max=512,fanout_min=None,source_dataset=None,name=None,description=None,resultslist_max_length=LIST_LIMIT,type_marker='leaf',lazyfactor=0.2,use_cache=1,cachemaxsize=2000,cachestorefactor=0.6,check_duplicates=0) :
    self.r=r
    self.bTreerole=uuid._('~fd000b70d47403627472')
    self.btreeHeadRole=uuid._('~01f3a6213c8c2811d9a1b0045f7750463a')
    self.collectionrole=uuid._('~fd000a02510bfd17204424')
    self.st_prefix=st_index
    self.typemarker=type_marker
    self.lazyfactor=lazyfactor # this is the ratio of the fanout_max - the extra key,value pairs to be added to any node above the fanout_max limit... dunno if we need this.. jus some experiment
    self.usecache=use_cache #default is to use RAM cache
    if self.usecache:
	    self.myrepos={} #initialize cache dictionary
	    self.getAttr=self.getAttr_cache  # use the cached getAttr & setAttr function
	    self.setAttr=self.setAttr_cache
	    if DEBUG:print('cache initialized ....')
	    self.cachemaxsize=cachemaxsize #number of max uforms to be cached
	    self.cachestorefactor=cachestorefactor #the factor of cache max size that needs to be retained
	    self.cacheminsize=int(self.cachestorefactor*self.cachemaxsize)
    else:	
	    if DEBUG:print('NO CACHE initialized...be prepared for extremely slow performance')
	    self.getAttr=self.getAttr_repos #use the non cached repository function for getAttr & setAttr
	    self.setAttr=self.setAttr_repos
    self.checkdup=check_duplicates #enable this to 1, if you want to prevent redundant data to be added to the index.. might make the indexing slow though
    self.default_attrs=['children','type','members']
    self.count=0
    self.spcount=0
    self.spath=[]
    self.uprefix=None
    if self.st_prefix==None or not uuid.isa(self.st_prefix):
	
	if DEBUG:print('CREATE NEW INDEX')
	self.st_prefix=self.create_new_index(fanout_max=fanout_max,fanout_min=fanout_min,name=name,resultslist_max_length=resultslist_max_length,source_dataset=source_dataset,description=description)
    else:
        self.stform=self.getAttr_repos(self.st_prefix,['btree_root','fanout_max','fanout_min','node_kinds','resultslist_max_length'])
        if self.typemarker not in self.stform['node_kinds']:
	    print('***ERROR***--Incorrect Type Marker for the given Index. Please use the correct one')
	    return
        self.root=self.stform['btree_root']
        self.listlimit=self.stform['resultslist_max_length']
        self.fanout_max=self.stform['fanout_max']
        self.fanout_min=self.stform['fanout_min']
        # set default fanout_min if necessary
        if self.fanout_min==None: self.fanout_min=int(0.5*float(self.fanout_max))
        self.fanout_minmax=int(self.fanout_min+(self.fanout_min*self.lazyfactor))
        self.fanout_maxxed=int(self.fanout_max+(self.fanout_max*self.lazyfactor))
	if DEBUG:print(self.stform)
	##return self.st_prefix


  def get_index(self):
      return self.st_prefix

  def flush_cache(self,m):
    if not self.usecache:
	if DEBUG:print('No Cache enabled to flush')
	return
    if DEBUG:print(m)
    self.clearcache(m)
    

  def insert(self,m):
    self.spath=[]
    (key,value)=m
    if type(value)==type([]) or type(value)==type(()):
	pass
    else:
	value=[value]
    if DEBUG:print (key,value)
    self.insert_keyval(key,value)
    
    

  def delete(self,m): #m is either a string(key) in which case the key and all its corresponding values are deleted or m is a tuple of strings(key,value) where value is the value to be deleted for the given key. 
    self.spath=[]
    if type(m)==type('') or type(m)==u'':
	key=m
	value=None
    elif type(m)==type(()) or type(m)==type(()):
	(key,value)=m
    else:
	print 'Invalid input for deletion',m
	return
    if DEBUG:print(key,value)
    self.delete_keyval(key,value)


  def ptQuery(self,query):
    self.spath=[]
    results=[]
    if not (type(query)==type('') or type(query)==type(u'')):
	print('***Warning***..query key must be a string..returning Empty List')
	
    else:
	results=self.exact_match(self.traverse(self.root,query),query)
    return results

  def traverse(self,node,key):
    self.spath.append(node)
    children=self.getAttr(node,'children')
    typ=self.getAttr(node,'type')
    if DEBUG: print "in traverse",self.spath,node,key,children,type
    if typ !=self.typemarker:
	childpos=1
	while childpos < len(children):
	    if key < children[childpos][0]:
		return self.traverse(children[childpos-1][1],key)
	    childpos+=1
	return self.traverse(children[-1][1],key)  # else return the last leaf
    else:
	return children

  def exact_match(self,children,key):
    qresults=[]
    #children=getchildren(node,key)
    for inst in children:
	if key==inst[0]: #exact match
	    qresults.extend(self.get_ulist(inst))
    return qresults

  def get_ulist(self,row):
    #self.debug(row) # jus for display now
    if row[-1] > self.listlimit:
	return self.getAttr(row[1],'members')
    else:
	return row[1]

  def extenduu(self,pre,l):
        return uuid.UUID(pre.getBuf()+vsmf.writeEint(l))


  def create_resultset(self,value,typ=None):
        if DEBUG: print value,type
	if self.uprefix!=None :
	    newid=self.extenduu(self.uprefix,self.ucount)
	    self.ucount+=1
	    uf=uform.UForm(newid)
	else: uf=uform.UForm()

	if typ=='leaf' or typ=='internal node':
	    uf['children']=value
            uf['type']=typ
	    uf['roles']=[self.bTreerole]
	    
	else:
	    uf['members']=value
	    uf['roles']=[self.collectionrole]
	if DEBUG: print uf
	if not self.usecache:  # dumb interface issues with the cached setAttr and repos setAttr
	    self.setAttr(uf)
	    return uf.uuid
	sav=[]
	for i in uf.keys():
	    sav.append(i)
	    sav.append(uf[i])
	self.setAttr(uf.uuid,sav)
        return uf.uuid


  def check_key_and_add(self,uid,children,key,value):
    result=False
    for i in range(len(children)):
	if key==children[i][0]: #Key already exists, so just add the new value to it
	  if DEBUG:print('key already exists.. hooray!!')
	  if uuid.isa(children[i][1]):
		uval=self.getAttr(children[i][1],'members')
	  else:
		uval=children[i][1]
	  if self.checkdup==1:
		onenew=False
		for v in value:
		    if v not in uval:
			uval.append(v)
			onenew=True
		if not onenew:	#if not even a single new value was added.. return 
		    if DEBUG:print('No new values to be added for the key ',key)
		    return True
	  else:
		uval.extend(value) #assumes value to be a list of entries for the given key
	  
	  if len(uval) <= self.listlimit: # embedded as list directly in children
	    children[i][1]=uval
	    children[i][2]=len(uval)
	  elif children[i][2] <= self.listlimit: # need to the change the list to an external UUID
	    children[i][1]=self.create_resultset(uval)
	    children[i][2]=len(uval)
	  else:  # it already points to external uuid
	    children[i][2]=len(uval)
	    self.setAttr(children[i][1],['members',uval])
	  self.setAttr(uid,['children',children])
	  result=True
	  break
    return result
  

  def insert_keyval(self,key,value):
    self.count+=1
    children=self.traverse(self.root,key)
    if self.check_key_and_add(self.spath[-1],children,key,value): return 1
    #inserting new key value pair
    if len(value) > self.listlimit:
    	newtuple=[key,self.create_resultset(value),len(value)]
    else:
	newtuple=[key,value,len(value)]
    if DEBUG:print newtuple
    self.add_to_node(self.spath,newtuple)
    return 
    
    
	
  def split(self,path,children,typ):
	self.spcount+=1
	thischild=path.pop()
	newchild=self.create_resultset(children[len(children)/2:],typ)
	newleafkey=children[len(children)/2][0]
	self.setAttr(thischild,['children',children[0:len(children)/2]])
	return ([newleafkey,newchild],[children[0][0],thischild])
    
  def add_to_node(self,path,newtuple,oldtuple=None):
    #self.debug(path)
    thischild=path[-1]
    children=self.getAttr(thischild,'children')
    typ=self.getAttr(thischild,'type')
    if oldtuple!=None:
	children=self.modify_oldkey_pair(children,oldtuple)
    children.append(newtuple)
    children.sort()
    if len(children) > self.fanout_maxxed:
	(newtuple,oldtuple)=self.split(path,children,typ)
	if DEBUG: print(newtuple,oldtuple)
	if thischild==self.root:
	    if DEBUG:print('Root needs to split!!')
	    self.root=self.create_resultset([oldtuple,newtuple],'internal node')
	    self.setAttr(self.st_prefix,['btree_root',self.root])
	    if DEBUG:print('New Root created at ',self.root)
	    return
	self.add_to_node(path,newtuple,oldtuple) #changed self.spath to path ********
	return
    else:
	#self.debug(children)
	self.setAttr(thischild,['children',children])
	return

  def modify_oldkey_pair(self,children,oldtuple):
    (key,uid)=oldtuple
    for i in range(len(children)):
	if children[i][1]==uid:
	    children[i][0]=key
	    break
    return children


  def check_key_and_delete(self,children,key,value=None):
    if DEBUG:print(key,value)
    for i in range(len(children)):
	if children[i][0]==key: #key found
	    if value==None: #deleting all values for the found key
		if DEBUG:print('No value given..deleting key and all of its contents')
		children.pop(i)
		return children
	    else:
		child_len=children[i][2]
		del_index=[]
		if child_len <= self.listlimit:
		    for j in range(child_len):
			if children[i][1][j]==value : #if the value matches as well
			    del_index.append(j) #tag the index value for deletion later

		    del_index.reverse() #needed to preserve the proper popping 
		    for k in del_index: children[i][1].pop(k)
		    if len(children[i][1])==child_len: # if nothing has been popped
			return None
		    elif len(children[i][1])==0: #after popping, if the list if empty, delete the key
			children.pop(i)
			return children
		    else:
			children[i][2]=len(children[i][1])
			return children
		else: # if the results point to an external uform
		    members=self.getAttr(children[i][1],'members')
		    #self.debug(members)
		    for j in range(child_len):
			if members[j]==value: #if the value matches too
			    del_index.append(j)  #tag the index value for deletion later
		    del_index.reverse() #needed to preserve the proper popping 
		    for k in del_index: members.pop(k)
		    if len(members)==child_len: # if nothing has been popped
			return None
		    elif len(members)==0: #after popping, if the list if empty, delete the key.. BUT wat happens to the external uform? just let it float in GRIS like space junk?
			children.pop(i)
			return children
		    elif len(members) <= self.listlimit: #if the member count is less than listlimit, modify the stuct
			children[i][1]=members  #ahh.. yet another space junkie!
			children[i][2]=len(members)
			return children   
			
		    else: #if its still an external uuid, update the members
			self.setAttr(children[i][1],['members',members])
			children[i][2]=len(members)
			return children
    return None # if key not found

  def delete_keyval(self,key,value=None):
    children=self.traverse(self.root,key)
    key_bd=children[0][0] #this is key used by the child's parent to refer to this leaf/node. We need this to check for change
    if DEBUG:print(key_bd)
    children=self.check_key_and_delete(children,key,value)
    if DEBUG:print len(children)
    if children==None:
	print('DELETE failed: Either the key or the given value for the key was not found in index')
	return
    else:

	thischild=self.spath.pop()
	if DEBUG:print "THISCHILD",thischild
    	if len(children) >= self.fanout_minmax: #simple case, jus update the children attrib of thischild
	    self.setAttr(thischild,['children',children])
	    if DEBUG:print('simple deletion.. no worries')
	    if DEBUG:print(children[0])
	    if key_bd!=children[0][0]: # there;s a change in the first tuple's key..need to propagate to parent
		self.update_keys(self.spath,(children[0][0],thischild,))
 	    return
    	else:
	    self.fix_underflow(self.spath,thischild,children)



  def fix_underflow(self,path,thischild,children):
        ovpath=[]
	for p in path:
	    ovpath.append(p)
	ovpath.append(thischild)
	if DEBUG:print 'ovpath is ',ovpath
        if DEBUG:print('re-inserts time!! ')
	kv_tuples=children
	if DEBUG:print(kv_tuples)
	#goto the parent and delete the child
	if len(path) == 0:
            self.setAttr(thischild,['children',children])
            return
        parent=path.pop()
	recpath=[]
	for p in path: #for recursive splits
	    recpath.append(p)
	children=self.getAttr(parent,'children')
	if DEBUG:print children
	if DEBUG:print thischild
	for i in range(len(children)):
	    if children[i][1]==thischild:
		'''if len(children) <= self.fanout_minmax: #check for underflow of the internal nodes
		    print 'NOT YET DONE...move on pls..'
		    #dosomething to fix it
		else:
		    #children.pop(i)
		    #self.setAttr(parent,['children',children])
		    if i==0: #if this is the first child , then we need to update its parent of the new key!
			gparent=path[-1]
			self.update_keys(path,(children[0][0],parent)) #here
			print 'grandpa is ',gparent
			gchildren=self.getAttr(gparent,'children')
			for g in range(len(gchildren)):
			    if gchildren[g][1]==parent: #this wont work for all cases..esp the skewed case of the first key ******
				print 'the occurence of the parent in gparent is ',g #NEEDS WORK! 
				ovpath.append(gchildren[g-1][1])
				prevchild=self.getAttr(gchildren[g-1][1],'children')[-1][1]
				break
		    else:
			ovpath.append(parent)
			print 'simple prev child'
			prevchild=children[i-1][1]'''
                if len(path) == 0 and i == 0: #this is the very left node of the 1st level..there is no prev before this
                  nextchild = children[i+1][1]
                  nextchildtype = self.getAttr(nextchild,'type')
                  if nextchildtype == 'leaf':
                    nextchildren = self.getAttr(nextchild,'children')
                    if len(nextchildren)+len(kv_tuples) > self.fanout_maxxed:
                      #in this case.. adding the kv_tuples to the next would cause an overflow... so don't do that..instead.. let the underflow of this node exist as such..until a point where adding the kv_tuples to the next would not cause it to overflow
                      if DEBUG: print("since adding to the next node will cause it to overflow.. keep this node underflowed until a point where adding its children does not cause the next node to overflow")
                      if children[0][0] != kv_tuples[0][0]: # in case the left most key was removed..propagate it to the root
                        children[0][0] = kv_tuples[0][0]
                        self.setAttr(parent,['children',children])
                      return
                    else: #since it won't overflow the next node..add kv_tuples to it
                      if DEBUG: print("adding to next node",len(nextchildren)+len(kv_tuples),self.fanout_maxxed)
                      nextchildren = kv_tuples+nextchildren #prepend is..since we are adding the values from the Prev node.. which should be added first to maintain ascending order
                      self.setAttr(nextchild,['children',nextchildren])
                      children.pop(i)
                      children[0][0] = kv_tuples[0][0] #this would be the very first key value(leftmost) of the entire tree
                      self.setAttr(parent,['children',children])
                      return
                  else:
                    if DEBUG: print("Expecting a leaf node.. but got an internal node for NextNode..Not sure what to do now.. maybe will keep the current node in underflow state??")
                    return
		    
		prevpath=self.getPrev(ovpath,len(ovpath))
		children.pop(i)
		self.setAttr(parent,['children',children])
		self.update_keys(path,(children[0][0],parent))
		if DEBUG:print 'prev path is ',prevpath
		prevchild=prevpath[-1]
		if DEBUG:print 'previous child for re-inserts is ',prevchild
		prevchildren=self.getAttr(prevchild,'children')
		prevchildren.extend(kv_tuples)
		if len(prevchildren) > self.fanout_maxxed:
			
		    if DEBUG:print 'overflow control in progress'
		    if DEBUG:print prevpath
		    (newtuple,oldtuple)=self.split(prevpath,prevchildren,self.getAttr(prevchild,'type'))
	#self.debug(newtuple,oldtuple)
		    if DEBUG:print (newtuple,oldtuple)
		    self.add_to_node(prevpath,newtuple,oldtuple)
		else:
		    self.setAttr(prevchild,['children',prevchildren])
		children=self.getAttr(parent,'children') #need to get a fresh copy of the children in case there the prev node had overflowed and split within the same parent
		if len(children) < self.fanout_minmax:
		    if parent!=self.root:
			self.fix_underflow(recpath,parent,children)
		    else:
			if DEBUG:print 'Its the root after all..so dont bother abt underflow'
			pass

			
		return
	print 'I SHOULD DEFINITELY NOT BE PRINTED AT ALL'

  def getPrev(self,path,level):
      thischild=path.pop()
      pchildren=self.getAttr(path[-1],'children')
      #print pchildren
      for i in range(len(pchildren)):
	  if pchildren[i][1]==thischild:
	      if i==0:
		  return self.getPrev(path,level)
	      else:
		  prevchild=pchildren[i-1][1]
		  #print 'prevchild is ',prevchild
		  path.append(prevchild)
		  while len(path)!=level:
		      prevchild=self.getAttr(prevchild,'children')[-1][1]
		      path.append(prevchild)
		  return path

  def update_keys(self,path,keyvaltuple):
    if DEBUG:print('iam in update_keys now ',path,keyvaltuple)
    if len(path)==0 : #this happens, when the root is just a leaf and its firt key,val pair gets deleted.. rare..but possible
	return
    (key,value)=keyvaltuple
    thischild=path.pop()
    children=self.getAttr(thischild,'children')
    for i in range(len(children)):
	if children[i][1]==value:
	    if DEBUG:print(children[i])
	    children[i][0]=key
	    self.setAttr(thischild,['children',children])
	    if i==0: # if this happens to the first key of this node...propagate the change to its parent..
		return self.update_keys(path,(key,thischild,))
	    return
    print('I shouldnt be printed at all.. hmn')
    return
    
if __name__=='__main__':
    r=repos.Repository('joshua3.maya.com:8888')
    #stoplist=['','for','in','pa','dcnr','of','the']
    def do_inserts(r):
	stoplist=['']
	stb=stringIndex(r,check_duplicates=1,fanout_max=5,fanout_min=2)
	sc=uuid._('~0172db78801a3b11da8507125551393ce4') #list of country names
	mem=scalablecoll.getAllMembers(r,sc)
    #mem=r.getAttr(sc,'members')
	print 'len of mem is ',len(mem)
	for i in mem[0:6]:
	    na=r.getAttr(i,'name')
	#print i,na
	    if na!=None:
		na=na.lower()
		for j in na.split(' '):
		    if j not in stoplist:
			
			stb.terminal_insert((j,i))
	print ' inserts done'
	print 'flusing cache'
	stb.flush_cache(1)
    #stb.makeIndex(r,resultslist_max_length=3,source_dataset=sc,name='String Index of Venture Outdoors Organizations')
    
	print 'index creation done'

	def do_deletes(r,stindex,keyval):
	    std=stringIndex(r,st_index=stindex)
	    std.delete(keyval)

    #do_inserts(r)    
    print 'delete phase'
    #stindex=uuid._('~018246c7a61a3c11da974361cc489c300f')
    #stindex=uuid._('~012f1556641af611da9b6f0afe4b247453')
    stindex=uuid._('~01eaeef83e1bbb11daa62b445d72e26bab')
    std=stringIndex(r,st_index=stindex)
    #print std.fanout_minmax
    kv_list=[('insert3','None')]
    #kv_list=[('insert6','None'),('insert4','None'),('insert48','None')]
    for keyval in kv_list:
	print 'deleting ',keyval
	std.terminal_delete(keyval)
    #std.terminal_insert(('insert6','None'))
    std.flush_cache(1)


	
	
	
	
	

  
  
 
  
    
    
	
	
    	
	
    

