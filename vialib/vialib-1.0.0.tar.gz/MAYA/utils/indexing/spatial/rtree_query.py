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

from MAYA.VIA import uform,uuid,repos
import math,random,time,cPickle
from MAYA.utils.shepherding import waitForPresence
TIMEOUTSECS=0

#test
class RtreeQuery:

#BBOX geometry
# True if box1 intersects box2

  def intersects(self,box1, box2):
    (min1, max1) = box1
    (min2, max2) = box2
    i = 0
    outside = False
    while i < len(min1):
        # we need box1 to either be less than box2
        # or box1 to be greater than box2

        # less-than
        coord1 = max1[i]
        coord2 = min2[i]
        min_outside = (coord1 < coord2)
        outside = outside or min_outside
        if outside: break

        # greater-than
        coord1 = min1[i]
        coord2 = max2[i]
        max_outside = (coord1 > coord2)
        outside = outside or max_outside
        if outside: break

        i = i + 1

    return not outside


  def getAttr_repos(self,uf,attr=None):
	if uuid.isa(uf):
	    uf=uform.UForm(uf)
            uu=uf.uuid
            waitForPresence(self,self.r,uu,TIMEOUTSECS)
	    if attr==None:
		attr=self.rtree_attrs #if no attributes are specified,get all Rtree Index Node Role attrs
		for i in attr:
			uf[i]=None
		return self.r.getAttr(uf)
    		 
	    elif type(attr)==type('') or type(attr)==type(u''):
		rs=self.r.getAttr(uu,attr)
		return rs
    	    else:
		for i in attr:
			uf[i]=None
		return self.r.getAttr(uf)
    		
	else:
            waitForPresence(self,self.r,uf.uuid,TIMEOUTSECS)
	    return self.r.getAttr(uf)
    	   

  def getAttr_cache(self,uuid,attr) :
    if len(self.myrepos) < self.cachemaxsize:
	if self.myrepos.has_key(uuid) and self.myrepos[uuid].has_key(attr) :
	    self.myrepos[uuid]['time']=int(time.time())
	    return self.myrepos[uuid][attr]
	    
	else:
	    uf=uform.UForm(uuid)
	    for i in self.rtree_attrs:
		uf[i]=None
	    m=self.r.getAttr(uf)
	    if self.myrepos.has_key(m.uuid):
		for attr in m.keys():
		    self.myrepos[m.uuid][attr]=m[attr]
	    else: 
		rdict={}
		for k in m.keys():
		    rdict[k]=m[k] 
		self.myrepos[m.uuid]=rdict
	    self.myrepos[uuid]['time']=int(time.time())
	    #print (m)
    	    return m[attr]
    else:
	self.clearcache()
	return self.getAttr(uuid,attr)
  
  def clearcache(self):
	self.debug('clearing cache')
	thistime=time.time()
	tulist=[]
	for u in self.myrepos.keys():
	    tulist.append((thistime-self.myrepos[u]['time'],u))
	tulist.sort()
	self.debug(len(tulist))
	tulist=tulist[self.cacheminsize:] #list of uuids to be removed from cache
	for i in tulist:
		del self.myrepos[i[1]]
	self.debug(len(self.myrepos))
	tulist=[]
	    
 

  def setAttr(self,uf):
	uu=uf.uuid
	attr=[]
	for attribs in uf.keys() :
		attr.append(attribs)
		attr.append(uf[attribs])
    	self.message("p_req",("value",uu,attr))

  def setAttr1(self,uuid,key,val) :
	self.message("p_req",("value",uuid,key,val))



  def getRoots(self,idxhead):
    self.root=[]
    if idxhead==None:
	    print 'Empty Index Head...waiting for Index Head UUIDs..'
	    return
	
    if uuid.isa(idxhead): idxhead=[idxhead]
    for idx in idxhead:
	    root=self.r.getAttr(idx,'rtree_root')
	    if root==None:
		print 'Not a valid root for '+idx.toString()
	    else:
		self.root.append(root)
	

  def __init__(self,r,spindex,usecache=1,cachemaxsize=15000,cachestorefactor=0.6,stat=0):
	self.r = r
	self.spindex=spindex
	print spindex
	self.getRoots(self.spindex)
	print self.root
	self.priority='priority_items'
	# bunch of initializations
	self.rtree_attrs=['children','type','parent',self.priority]
	self.usecache=usecache
        self.stat=stat
	#self.usecache=self.context.get('usecache') or 0 #default is to NOT to use RAM cache
	if self.usecache:
	    self.myrepos={} #initialize cache dictionary
	    self.getAttr=self.getAttr_cache  # use the cached getAttr function
	    print'using cached getAttrs'
	    self.cachemaxsize=cachemaxsize #number of max uforms to be cached
	    self.cachestorefactor= cachestorefactor #the factor of cache max size that needs to be retained
	    self.cacheminsize=int(self.cachestorefactor*self.cachemaxsize)
	else:
	    print 'Note: Not using RAM cache...query processing time will be high!! Turn on "usecache" to get better performance.'
	    self.getAttr=self.getAttr_repos #use the non cached repository function for getAttrs
	
 
  def winq(self, w):
        if self.stat:
          t1=time.time()
          self.lfcount=0
          self.ndcount=0
	results=self.query(self.root,w,self.intersects)
        if self.stat:
          t2=time.time()
          return {'results':results,'time':t2-t1,'nodes':self.ndcount,'leaves':self.lfcount}
	return results

  def priorityq(self, w,rnum=10):
	#print w
	self.nodecount=self.resultcount=0
	t1=time.time()
	results=self.priorityQuery(self.root,w,rnum,self.intersects)
	t2=time.time()
	if results==None: results=[]
	reslist=(len(results),self.resultcount,self.nodecount,t2-t1) #used for statitics
	
	return results
	
	
	#mem=[]			#use these to store the results in the speciall uform to view in geobrowser
	#map(lambda a: mem.append(a[0]),results)
	#self.debug(len(results),self.resultcount,self.nodecount)
	#self.setAttr1(uuid._('~01e3f286808ce211d9acbd778d39c34a7f'),'members',mem)
        
 

  def query(self,nodelist,p,predicate):
	#print nodelist
        
        results=[]
	children=[]
    	for node in nodelist:
	    if self.getAttr(node,'type')=='leaf':
                if self.stat:
                  self.lfcount+=1
		for k in self.getAttr(node,'children'):
		    if predicate(p,k[1]): #k[1] is the bbox of the node
			results.append(k) #should I just add the uuid or the whole tuple??
		
	    else:
                if self.stat:
                  self.ndcount+=1
		for k in self.getAttr(node,'children'):
		    if predicate(p,k[1]):
			children.append(k[0])
	if len(children)!=0 :
	    results.extend(self.query(children,p,predicate))
	return results
		
		
	    
  
  def sortByPriority(self,a,b) : #sort in descending order based on priority
	a,b = a[-1],b[-1] #this assumes that the priority is the last value of a N-tuple
	return -cmp(a,b)


  def priorityQuery(self,nodelist,p,m,predicate) :
	self.nodecount+=len(nodelist)
	priorityQueue=[]
	inodes=[]
	childlist=[]
	for node in nodelist :
	    ntype=self.getAttr(node,'type')
	    if ntype=='leaf':
		results = self.getAttr(node,'children')
	    else:
		results = self.getAttr(node,self.priority)
		inodes.append(node)
	
            for i in results:
		if predicate(i[1],p) : priorityQueue.append(i)
	
	
	if len(priorityQueue) < m:
	    if len(inodes)==0:
		if len(priorityQueue)==0 : return None #No matching results
	 	#self.debug('Last level reached...no more levels to recurse..returning results..',len(priorityQueue))
		priorityQueue.sort(self.sortByPriority)
		self.resultcount=len(priorityQueue)
		return priorityQueue[0:m]
	    #self.debug('entering next level......')
	    
	    for node in inodes:
	        children=self.getAttr(node,'children')
		for i in children:
		    bbox = i[1]
                    if predicate(bbox, p):
		        childlist.append(i[0])
	    #self.debug(len(nodelist),len(inodes),len(childlist))
	    if len(childlist)==0 : return None # No matching bboxes
	    return self.priorityQuery(childlist,p,m,predicate)
	else:
	    #self.debug(len(priorityQueue))
	    self.resultcount=len(priorityQueue)
            priorityQueue.sort(self.sortByPriority)
            return priorityQueue[0:m]

  def traversal(self, node, p, predicate):
        #print "Traverse:", node

        results = []

        if self.isLeaf(node): return [node]
        cps = self.getAnnotations(node)
        for (e, ef) in cps:
            bbox = ef['bbox']
	    
            if predicate(bbox, p):
                results.extend(self.traversal(e, p, predicate))
        return results

if __name__ == '__main__':
  # define the respository to talk with
  r=repos.Repository('joshua.maya.com:9889') 
  
  #define the indices to query with, this can be a list too.
  spindex=uuid._('~fd000efddada48')
  #spindex=uuid._('~01313c34ece26811d9a11c0e0761837379')
  myq=RtreeQuery(r,spindex)

  w=[(50.78,9.2,-10000),(51.6,9.3,730657)]	#window query of form ((lat1,long1,time1),(lat2,long2,time2)), where 1 unit of time=1 day, meaning a time value of '1000' means 1000 days from 0001-01-01
  w1=[(20,-10),(45,60)]
  #res=myq.priorityq(w1,20) # this is the priority based query. The second parameter specified the number of results requested( optional, default is 10)
  
  #res=myq.winq(w1) 	# this is the regular window query in N-dimensions and returns all the items that match the query window. Warning ! Do Not use a large window as it may take a long time to run and give out thousands of records!

  prwin=[(-81.0,-176.0,-10000),(89.0,179.3,730657)]
  res=myq.priorityq(prwin,100)
  print 'Number of matching results :',len(res)
  for i in res:
    print [i[0],i[2],r.getAttr(i[0],'name')]
  #print res
  
  
  #since using stat, the returned value is a dict
  print 'Number of matching results :',len(res['results'])
  print 'Time taken :',res['time']
  print 'Nodes fetched :',res['nodes']
  print 'Leaves fetched: ',res['leaves']


