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

from MAYA.VIA import uuid,uform,vsmf
from MAYA.utils import date
from MAYA.utils.shepherding import waitForPresence
import _btdb,os,math,random


TIMEOUTSECS=0 #time-out in seconds for the waitForPresence. O defaults to wait until true

class Rtreebuilder:

# def  __init__(self,r,dimension,rtree_prefix=None,filename=None,keygenfunc=None,add_priority=0,priority_limit=10,spread=0,sequential=0):
#Initial Values:
#r- repository object. Required
#dimension- integer representing the dimensionality of the source data. Required
#rtree_prefix- UUID. If 'sequential' is true, this UUID would be used as the prefix if specified. Default is None
#filename - string. Name of the temporary db file the code creates to store the data. Defaults to 'tempbtree.btdb'
#add_priority-Boolean. If true, builds the prioirty_items for the internal nodes and also adds the parent attribute of the index nodes. Default if False. When false, only the parent attribute if added to the index nodes
#priority_limit. Integer. Specifies the number of priority_items for the internal nodes. Default is 10. Relevant only when add_priority is True
#spread- Boolean. If True, picks the priority_items for the index randomly, thereby providing a spread of values. Default is False.Relevant only when add_priority is True. NOTE: use this only when there is no possible way to determine priority but at the same time priority_items is needed.
#sequential- Boolean. If True, is used to generate computed UUIDs for the index nodes. Default is False which would generate random UUIDs.
#keygenfunc-fucntion. Uses this function to generate the key,value pair. Default is None, which would make use of built-in functions to compute the key,value pair


  def  __init__(self,r,dimension,rtree_prefix=None,filename=None,keygenfunc=None,add_priority=0,priority_limit=10,spread=0,sequential=0, new_rev_num=None):
    self.count=0
    self.r=r
    self.add_priority=add_priority
    self.dimension=dimension
    access = _btdb.CREATE
    self.fname=filename or 'tempbtree.btdb'
    self.btree = _btdb.new(self.fname, 0666, access, _btdb.DEFAULT_BLKSIZE, 250 ,2000)
    self.sequential=sequential
    if self.sequential:
      self.uidcount=0
      if rtree_prefix==None:
        self.rtree_prefix=uuid.UUID() #generate random UUID and use this as prefix
        self.rev_num = 1 #set revision number to 1
      else:
        self.rtree_prefix=rtree_prefix
        waitForPresence(self.r, self.rtree_prefix, TIMEOUTSECS)
        self.rev_num = self.r.getAttr(rtree_prefix, 'revision_number')
      if new_rev_num:
        self.rev_num = new_rev_num
      else:
        if self.rev_num:
          self.rev_num = self.rev_num + 1 #increment the revision number
        else:
          self.rev_num = 1 #set to 1
      print('rtree prefix is ',self.rtree_prefix)
      self.pre=self.rtree_prefix.getBuf()
      
    self.rtreeRole=uuid._('~01d37ae72c119311d99a7239eb19bd68fc')
    self.rtreeHeader=uuid._('~0189112434c7c911d98e2c34db737a4e2a')
    self.aggCountRole=uuid._('~01cbe877d00e8211daafb968fe26f651dc')
    self.srcdescRole=uuid._('~010a685574d02011d89f8179ba7fb44707') #the IndexRoot Role
    self.allow_dup=0
    self.pad_len=30 # padding used to make the value always have the same number of MSDs (digits before the decimal place)
    if add_priority:
        self.priorityLimit=priority_limit
        self.spread=spread
        self.genkeyval=keygenfunc or self.genKeyValuePairWithPriority
    else:
        self.genkeyval=keygenfunc or self.genKeyValuePair

# Public Methods and their description:
# Method: insert(self,u):
# input u is a list or tuple where u[0] is the UUID and u[1] is bbox and u[2] if present is the priority value
# This inserts the values into the local file
# output: None

# Method: makeIndex(self,count=None,leafmaxfanout=25,nodemaxfanout=7)
# Once all the inserts are done, use this method to carve out uforms from the local dbfile.
# The count input is 'required'.If left as None, would generate a error msg and halt. Its needed to maximize the space utilization and ordering of the index and at the very least provide an approximation of the total number of inserts. The other two values set the fanout max limits.
# Output: Creates the whole index in Uform space and returns the root UUID.

# Method: genHeader(self,root,source,attribs=None,hash=None,node_kinds=['leaf','internal node'],name='Generic Rtree Index',description=None):
# This method created the Header Uform. The root in the input should be the value returned by the makeIndex method. attribs is a list of strings where the strings are the attribute names of the data that form the dimensions of the index. Source is the UUID pointing to the source dataset
# Output: The header UUID

# Method: delDbFile(self,file=None):
# This deletes the local temporary db file that was created. setting file=None, would delete the default file that was used if no file was specified during the onject instantiation.
# Output: returns None


  def set(self, key, values):
      #key = vsmf.serialize(key)
      values = vsmf.serialize(values)
      self.btree.set(0,key,values,0,_btdb.MAX_VAL)

  def get(self, key):
      #key = vsmf.serialize(key)
      v,l = self.btree.get(0,key,0,200)
      if l == 0: return None
      if l > 200:
          v, l = self.btree.get(0,key,0,l)
      return vsmf.reconstitute(v)

  def add(self, key, item):
      x = self.get(key)
      if x == None: x = []
      x.append(item)
      self.set(key,x)

  def nextkey(self,key=''):
      return self.btree.next(0,key)

  def delDbFile(self,file=None):
    if file==None: file=self.fname
    if self.btree:
	self.btree.close()
    os.remove(file)
  

  #This is the default function used in case of no priority and is specific to index UUIDs with bboxes
  #Inputs: Its a list or tuple u, where u[0] is the UUID and u[1] is its bounding box
  #Output: Its a two tuple (key,value), where key is computed from a combination of UUID and bbox. Value is an eform with attributes 'anchor','value' and 'bbox'. In this function, the 'anchor' is the centroid of the bbox and 'value' in the uuid that is to be indexed and 'bbox' is the bounding box
  def genKeyValuePair(self,u): # This function would be specific to the dataset
    anchor=self.centroid(u[1])    
    key=' '*self.pad_len+"%f"%(anchor[0])+u[0].toString()[1:]
    value={'anchor':anchor,'value':u[0],'bbox':u[1]}
    return (key,value)


  #This if the default function used in case where priority values are present.
  #Inputs: Its a list or tuple u, where u[0] is the UUID and u[1] is its bounding box and u[2] is the priority value( a float between 0 and 1)
  #Output: Its same as the above function but also adds another attribute 'priority' to the eform
  def genKeyValuePairWithPriority(self,u):
    anchor=self.centroid(u[1])
    key=' '*self.pad_len+"%f"%(anchor[0])+u[0].toString()[1:]
    value={'anchor':anchor,'value':u[0],'bbox':u[1],'priority':u[2]}
    return (key,value)
    

  def insert(self,kvtuple):
    	(key,value)=self.genkeyval(kvtuple)
	#print(value)
       	#self.add(key,value) ### modified the key to be unique.. so no more fetch and add.. just add always
        if self.allow_dup:
          self.add(key,value)
        else:
	  self.set(key,[value])
	

	
	
  def makeUforms(self,ulist,type,degreeToSort):
    print('Next dimension sort.............')
    if type=='leaf':
      bucketsize=int((self.leafsplits**(self.dimension-1-degreeToSort))*self.leafmaxfanout)
	#bucketsize=int(self.leafsplits[degreeToSort]*self.leafmaxfanout)
    else:
      bucketsize=int((self.nodesplits**(self.dimension-1-degreeToSort))*self.nodemaxfanout)
	#bucketsize=int(self.nodesplits[degreeToSort]*self.nodemaxfanout)
    #print(bucketsize,degreeToSort)
    print degreeToSort 
    if degreeToSort != 1:
      def sortByDegree(a,b) :
        a,b = a[0][degreeToSort],b[0][degreeToSort]
        return cmp(a,b)

      ulist.sort(sortByDegree)


    
    #if type=='internal node': print(ulist)
    lc=0
    thislevel=[]
    nextlevel=[]
    while lc < len(ulist):
      thislevel=ulist[lc:lc+bucketsize]
       #print('------'+str(len(thislevel))+'--------')
      if degreeToSort < self.dimension-1 :
        nextlevel.extend(self.makeUforms(thislevel,type,degreeToSort+1))
      else:
        nextlevel.append(self.writetoUforms(thislevel,type))
      lc+=bucketsize
    ulist=[]
    return nextlevel
    
	

  def union(self,box1, box2):
    if box1 is None: return box2
    if box2 is None: return box1
    (s1, e1) = box1
    (s2, e2) = box2

    i = 0
    min_s = []
    max_e = []
    while i < len(s1):
        min_s.append(min(s1[i], s2[i], e1[i], e2[i]))
        max_e.append(max(s1[i], s2[i], e1[i], e2[i]))
        i = i + 1
    return (tuple(min_s), tuple(max_e))

  def centroid(self,box):
    (min_pt, max_pt) = box
    N = len(min_pt)
    i = 0
    c = []
    while i < N:
        pt = min_pt[i] + ((max_pt[i] - min_pt[i]) / 2.0)
        c.append(pt)
        i = i + 1
    return c
    

  def genUForm(self):
    if self.sequential:
      u= uuid.UUID(self.pre+vsmf.writeEint(self.uidcount))
      self.uidcount+=1
      return uform.UForm(u, {'revision_number': self.rev_num})
    else:
      #generates a UForm with random UUID
      return uform.UForm(uuid.UUID()) #, {'revision_number': self.rev_num})


  def writetoUforms(self,ulist,type):
        uf=self.genUForm() # replace with extenduu if want computed uuids
	uf['roles']=[self.rtreeRole,self.aggCountRole]
	uf['children']=[]
	uf['bbox']=None
        child_count=0
        if type=='leaf':
            uf['type']='leaf'
            for i in range(len(ulist)):
              listentry=[]
              listentry.append(ulist[i][1]['value'])
              del ulist[i][1]['value']
	      listentry.append(ulist[i][1]['bbox'])
              uf['bbox']=self.union(uf['bbox'],ulist[i][1]['bbox'])
              del ulist[i][1]['bbox']
              if self.add_priority:
                listentry.append(ulist[i][1]['priority'])
                del ulist[i][1]['priority']
	      for k in ulist[i][1].keys(): # this should do nothing for now, since all the relevant keys would have been deleted already
                listentry.append(ulist[i][1][k])
	      uf['children'].append(listentry)
	      
            if self.add_priority:
                def sortByAttr(a,b):
                  a,b=a[-1],b[-1]
                  return -(cmp(a,b))
                uf['children'].sort(sortByAttr)
            child_count=len(uf['children'])
	else: 
	    uf['type']='internal node'
            for i in range(len(ulist)):
              listentry=[]
              listentry.append(ulist[i][1]['uuid'])
              del ulist[i][1]['uuid']
	      listentry.append(ulist[i][1]['bbox'])
              uf['bbox']=self.union(uf['bbox'],ulist[i][1]['bbox'])
              del ulist[i][1]['bbox']
              child_count+=ulist[i][1]['child_count']
              del ulist[i][1]['child_count']
	      for k in ulist[i][1].keys(): # this should do nothing for now, since all the relevant keys would have been deleted already
                listentry.append(ulist[i][1][k])
	      uf['children'].append(listentry)
        uf['aggregate_child_count']=child_count
	self.r.setAttr(uf)
	center=self.centroid(uf['bbox'])
	return [center,{'uuid':uf.uuid,'bbox':uf['bbox'],'child_count':child_count}]
              

  # added the 'spread' option to select the priority list randomly if there appears to be no priority ordering in the dataset.
  def add_node_priorities(self,node,parent=None,spread=0):
	#print(node)
        nodeuf=uform.UForm(node)
        nodeuf['type']=None
        nodeuf['children']=None
        waitForPresence(self.r,node,TIMEOUTSECS)
	nodeuf=self.r.getUForm(nodeuf)
	
	if nodeuf['type']=='leaf':
	    uf=uform.UForm(node)
	    uf['parent']=parent
	    uf['priority']=None
	    self.r.setAttr(uf)
            if spread==1:
              randchild=[]
              if len(nodeuf['children']) <= self.priorityLimit:
                return nodeuf['children']
              while len(randchild) < self.priorityLimit:
                randval=nodeuf['children'][random.randint(0,len(nodeuf['children'])-1)]
                if randval not in randchild: randchild.append(randval)
              return randchild
            else:
	      return nodeuf['children'][0:self.priorityLimit]
	else:
	    nodePrioritylist=[]
	    for child in nodeuf['children']:
		nodePrioritylist.extend(self.add_node_priorities(child[0],node,spread))
            uf=uform.UForm(node)
            if spread==1:
              if len(nodePrioritylist) <= self.priorityLimit:
                uf['priority_items']=nodePrioritylist
              else:
                randchild=[]
                while len(randchild) < self.priorityLimit:
                  randval=nodePrioritylist[random.randint(0,len(nodePrioritylist)-1)]
                  if randval not in randchild: randchild.append(randval)
                uf['priority_items']=randchild
            else:
	      def sortByPriority(a,b):
		a,b=a[-1],b[-1]
		return -cmp(a,b)
              nodePrioritylist.sort(sortByPriority)
	      uf['priority_items']=nodePrioritylist[0:self.priorityLimit]
	    #uf['priority']=None
	    uf['parent']=parent
	    self.r.setAttr(uf)
	    return uf['priority_items']

  def add_parent(self,node,parent=None):
       waitForPresence(self.r,node,TIMEOUTSECS)
       type=self.r.getAttr(node,'type')
       if type=='leaf':
         self.r.setAttr(node,'parent',parent)
         return
       else:
         children=self.r.getAttr(node,'children')
         for child in children:
           self.add_parent(child[0],node)
         self.r.setAttr(node,'parent',parent)
         return
	    
  def recurse_levels(self,ulist):
    print('entering next node level...............')
    nodecount=len(ulist)
    if nodecount <= 1 : 
	#print(ulist)
	#ulist.sort()
	#root=self.makeUforms(map(lambda a: (a[1],a[0],a[2],a[3]),ulist),'internal node',self.nodemaxfanout)
	print('--------the root is-------')
	print(ulist[0])
	self.root=ulist[0][1]['uuid']
	
	# do something
    else:
	degree=0
	nextlevel=[]
        numnodes=math.ceil(float(nodecount)/self.nodemaxfanout)
	#self.sqroot=math.ceil(self.nthRoot(numnodes/2,2))
	#self.nodesplits=[self.sqroot*2,self.sqroot,1]
	#nodebucketsize=int(self.nodesplits[degree]*self.nodemaxfanout)

        self.nodesplits=math.ceil(self.nthRoot(numnodes,self.dimension))
        nodebucketsize=int((self.nodesplits**(self.dimension-1-degree))*self.nodemaxfanout)
	print(nodecount,numnodes,self.nodesplits,nodebucketsize)
	nextlevel.extend(self.makeUforms(ulist,'internal node',degree))
        
	#print(len(nextlevel))
    	self.recurse_levels(nextlevel)
	    
  def nthRoot(self,P,n,d=10,x=1.0):
       # P -- find nth root of this number
       # n -- whole number root
       # d -- level of depth for recursion (default 10)
       # x -- initial value of x (default 1)
        if d>1: 
           newx = ((n+1.0)*P*x + (n-1)*(x**(n+1)))/((n-1)*P + (n+1)*x**n)
           return self.nthRoot(P,n,d-1,newx)    
        else:
           return x  
    	    
  def genHeader(self,root,source,dimension,attribs=None,hash=None,node_kinds=['leaf','internal node'],name='Generic Rtree Index',description=None):
    if self.sequential:
      uf=uform.UForm(self.rtree_prefix)
    else:
      uf=uform.UForm()
    #uf['revision_number'] = self.rev_num
    uf['rtree_root']=root
    uf['source_dataset']=source
    uf['roles']=[self.rtreeHeader,self.srcdescRole]
    uf['node_kinds']=node_kinds
    uf['name']=name
    uf['description']=description
    uf['source_member_hash']=hash
    uf['fanout_max_leaf']=self.leafmaxfanout
    uf['fanout_max_node']=self.nodemaxfanout
    uf['fanout_min_leaf']=int(0.4*self.leafmaxfanout)
    uf['fanout_min_node']=int(0.4*self.nodemaxfanout)
    if type(attribs)==type(''):
      attribs=[attribs]
    uf['key_attributes']=attribs

    uf['dimension']=dimension
    self.r.setAttr(uf)
    return uf.uuid
 
  def makeIndex(self,count=None,leafmaxfanout=25,nodemaxfanout=6):
    
    nextlevel=[]
    degree=0
    self.count=count
    if count==None:
        print 'Need the total count value to proceed. An approximation would suffice in actual data in unavailable, but would result in poor Rtree build!!'
        return
    print 'received count value is ',self.count
    self.total=self.count
    self.leafmaxfanout=leafmaxfanout
    self.nodemaxfanout=nodemaxfanout
    self.numleaves=math.ceil(float(self.count)/self.leafmaxfanout)
    #self.sqroot=math.ceil(self.nthRoot(self.numleaves/2,2))
    #self.leafsplits=[self.sqroot*2,self.sqroot,1]
    #bucketsize=int(self.leafsplits[degree]*self.leafmaxfanout)

    self.leafsplits=math.ceil(self.nthRoot(self.numleaves,self.dimension))
    bucketsize=int((self.leafsplits**(self.dimension-1-degree))*self.leafmaxfanout)
    print(self.count,self.leafmaxfanout,self.numleaves,self.leafsplits,bucketsize)
    k=''
    t=0
    tot=0
    bucket=[]
    print('starting to read from btree')
    #while t < self.count:
    while 1:
	t+=1
	k=self.nextkey(k)
	if k == '': break
	value=self.get(k)
	newval=[]
	for v in value:
	    #center=[float(k)-281.0,v[0],self.revdict[v[1]]]
	    #bbox=[[float(k)-281.0,v[0],self.revdict[v[3]]],[float(k)-281.0,v[0],self.revdict[v[4]]]]
	    #nv=[center,uuid.fromString(v[2]),bbox]
	    anchor=v['anchor']
	    #center[-1]=self.revdict[center[-1]]
	    del v['anchor']
	    #center=self.revdict[center[-1]]
	    #v['bbox'][0][-1]=self.revdict[v['bbox'][0][-1]]
	    #v['bbox'][1][-1]=self.revdict[v['bbox'][1][-1]]
	    #v['uuid']=uuid.fromString(v['uuid'])
	    nv=[anchor,v]
	    newval.append(nv)
	
	#newval=map(lambda a: (float(a[0]),float(k)-281.0,uuid.fromString(a[1])),value)
	tot+=len(newval)	
        
	bucket.extend(newval)
        #print(bucket)
        if len(bucket) > bucketsize:
	    #print(len(bucket))
            if self.dimension==1: #This check works for one dimensional data where it bypasses muliple sorts and directly creates the leaf uforms
              nextlevel.append(self.writetoUforms(bucket[0:bucketsize],'leaf'))
            else:
              temp=self.makeUforms(bucket[0:bucketsize],'leaf',degree+1)
	    #print(temp[0],temp[-1])
              nextlevel.extend(temp)		
	    #print('---------------------------------------------')
	    
	    #print(tot)
	    bucket=bucket[bucketsize:]
	    #print('emptying bucket')
	    #print(len(bucket))
    #print('last run')
    if len(bucket)!=0: 
      if self.dimension==1:
        nextlevel.append(self.writetoUforms(bucket[0:bucketsize],'leaf'))
      else:
        nextlevel.extend(self.makeUforms(bucket,'leaf',degree+1)) # the last bunch
    print('all done..going to next level')
    print(tot,self.count)
    if tot==self.count:
      print '***********Hooray, all entries added successfully******'
    else:
      print '***********Oops! the numbers dont match! something;s wrong*************'
    #print(len(nextlevel))
    #print(nextlevel)
    
    #handle the case of empty index here
    if tot==0:
      print 'Empty index!! creating the empty root'
      root_uf=uform.UForm()
      root_uf['roles']=[self.rtreeRole,self.aggCountRole]
      root_uf['children']=[]
      root_uf['type']='leaf'
      root_uf['aggregate_child_count']=0
      root_uf['bbox']=[[0.0 for i in range(self.dimension)],[0.0 for i in range(self.dimension)]]
      if self.add_priority:
        root_uf['priority_items']=[]
      self.r.setAttr(root_uf)
      self.root=root_uf.uuid
      return self.root
    self.recurse_levels(nextlevel)
    if self.add_priority:
        print('adding priority and parent info to nodes........')
        self.add_node_priorities(self.root,spread=self.spread)
    else:
        print('adding parent attribs')
        self.add_parent(self.root)
    print('Done')
    return self.root

    
