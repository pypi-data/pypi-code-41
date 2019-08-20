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
import math,random,time
TIMEOUTSECS= 0
class Rtree:

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

# The area, volume, or hypervolume of bbox
  def area(self,bbox):
    if not bbox: return 0
    (s, e) = bbox
    i = 0
    m = 1
    while i < len(s):
        d = e[i] - s[i]
        m = m * abs(d)
        i = i + 1
    return m

# Not really the union; actually forms the minimum bounding box of the
# given minimum bounding boxes.  Deals with the case where on box is None.
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
    #return (tuple(min_s), tuple(max_e))
    return [min_s,max_e]


  def getAttr_repos(self,uf,attr=None):
	if uuid.isa(uf):
	    uf=uform.UForm(uf)
	    uu=uf.uuid
	    waitForPresence(self.r,uu,TIMEOUTSECS)
	    if attr==None:
		attr=self.default_attrs #if no attributes are specified,get the default attrs specified during init
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
	    waitForPresence(self.r,uf.uuid,TIMEOUTSECS)
	    return self.r.getAttr(uf)
	

  def getAttr_cache(self,uuid,attr) :
    if len(self.myrepos) < self.cachemaxsize:
	if self.myrepos.has_key(uuid) and self.myrepos[uuid].has_key(attr) :
	    self.myrepos[uuid]['time']=int(time.time())
	    return self.myrepos[uuid][attr]
	    
	else:
	
	    m=self.getAttr_repos(uuid)
	    if self.myrepos.has_key(m.uuid):
		for attr in m.keys():
		    if not self.myrepos[m.uuid].has_key(attr):
		        self.myrepos[m.uuid][attr]=m[attr]
	    else: 
		rdict={}
		for k in m.keys():
		    rdict[k]=m[k] 
		self.myrepos[m.uuid]=rdict
	    self.myrepos[uuid]['time']=int(time.time())
    	    return m[attr]
    else:
	self.clearcache()
	return self.getAttr(uuid,attr)
  
  def clearcache(self,flush=None):
        print 'emptying cache'
	if flush:	# this would flush my entire local cache.. 
	    print ('flusing entire cache')
	    for i in self.myrepos.keys():
	        if self.myrepos[i].has_key('dirty') and self.myrepos[i]['dirty']==1: # if there had been a setAttr for 
		   del self.myrepos[i]['dirty']              #this uuid, then do a setAttr to repository
	           del self.myrepos[i]['time']
		   self.setAttr_repos(i,self.myrepos[i])
                   #print self.myrepos[i]
		   
	    	del self.myrepos[i]

	else:
	    thistime=time.time()
	    tulist=[]
	    for u in self.myrepos.keys():
	        tulist.append((thistime-self.myrepos[u]['time'],u))
	    tulist.sort()
	    print(len(tulist))
	    tulist=tulist[self.cacheminsize:] #list of uuids to be removed from cache
	    for i in tulist:
	        if self.myrepos[i[1]].has_key('dirty') and self.myrepos[i[1]]['dirty']==1: # if there had been a setAttr for 
		    sav=[]							#this uuid, then do a setAttr to repository
		    for a in self.myrepos[i[1]].keys():
 		      if a not in ['time','dirty']:
		        sav.append(a)
		        sav.append(self.myrepos[i[1]][a])
		        self.setAttr_repos(i[1],sav)
	        del self.myrepos[i[1]]		# and then delete it from my local cache, assuming that my setAttr_repos doesnt fail!
	    tulist=[]
	print (len(self.myrepos))
	

  def setAttr_cache(self,uuid,attr):
    if len(self.myrepos) < self.cachemaxsize:
	if self.myrepos.has_key(uuid):
          if type(attr)==type({}):
            for i in attr:
              self.myrepos[uuid][i]=attr[i]
          else:
	    for i in range(len(attr)/2):
	        self.myrepos[uuid][attr[i*2]]=attr[(i*2)+1]
	else:
          if type(attr)==type({}):
            self.myrepos[uuid]=attr
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

  def setAttr_repos(self,uf,attr=None,val=None):
        if uuid.isa(uf):
	    #should I be using waitForPresence here??
	    uu=uf
	    if type(attr)==type({}):
		self.r.setAttr(uform.UForm(uu,attr))
	    elif type(attr)==type(''):
		self.r.setAttr(uu,attr,val)
            elif type(attr)==type([]) or type(attr)==type(()):
                rdict={}
                for i in range(len(attr)/2):
                  rdict[attr[i*2]]=attr[(i*2)+1]
                self.r.setAttr(uform.UForm(uu,rdict))
	    
	else:
	    # should I be using waitForPresence here??
	    self.r.setAttr(uf)

  def isLeaf(self,node):
      return self.getAttr(node,'type')=='leaf'

  def getChildren(self,node):
      return self.getAttr(node,'children')

  def sortByPriority(self,a,b) :
	a,b = a[-1],b[-1]
	return -cmp(a,b)

  def traverse(self, node, p, predicate):
        #print "Traverse:", node

        results = []

        if self.isLeaf(node): return [[node,self.getAttr(node,'bbox'),self.getAttr(node,'aggregate_child_count')]]
        children = self.getChildren(node)
        for i in children:
            if predicate(i[1], p):
                results.extend(self.traverse(i[0], p, predicate))
        #print results
        return results

  def chooseLeaf(self,childlist,bbox):
        enlargements=[]
        for i in childlist:
            bbox1 = i[1]
            try:
                a = self.area(bbox1)
            except:
                print "area crashed on uuid", i[0]
                raise "RTREE BAD AREA"
            large_box = self.union(bbox1, bbox)
	    #self.debug(large_box)
            a_large = self.area(large_box)
            enlargements.append( (a_large,
                                  a,
                                  i[0],i[2]) )
        enlargements.sort()
	#print 'Enlargements are ',enlargements
        choice = enlargements[0][2]
        return choice

  def insertInLeaf(self,node,entry):
        children=self.getChildren(node) or []
        oldcount=len(children)
	#should we check for duplicates or not?? make it an option instead?
	if self.check_dup:
	    if entry not in children:
		children.append(entry)
            else:
                print entry, 'already exists. No duplicates allowed'
                return (False,None)
	else:
	    children.append(entry)
	if self.add_priority:
	    children.sort(self.sortByPriority)
        bbox=self.getAttr(node,'bbox')
        newbbox=self.union(bbox,entry[1])
        if newbbox!=bbox:
          #print 'BBox of leaf ',node,' has changes on insert of ',entry,' from ',bbox,' to ',newbbox
          self.setAttr(node,['children',children,'aggregate_child_count',len(children),'bbox',newbbox])
        else:
          self.setAttr(node,['children',children,'aggregate_child_count',len(children)])
          newbbox=None
	#print('Insert success for', entry)
        #print 'Updated agg count from ',oldcount,' to ',len(children)
	#if self.add_priority and self.now: #self.now is equivalent to use_cache...just another level of freedom added
	    #parent=self.getAttr(node,'parent')
	#    self.propagateUpward(self.getAttr(node,'parent'),entry)
        if self.now:
          if self.add_priority and children.index(entry) < self.priorityLimit:
            #print 'Uses priority and the new insert has higher priority..propagating upwards'
            self.update_count_and_priority(node,len(children)-oldcount,entry,'add')
          else:
            self.update_count_and_priority(node,len(children)-oldcount)
        if len(children) <= self.leafmaxfanout: # checks for overflow condition
          #print 'No need to split, but MAY need to adjustPath'
          return [False,newbbox]
        else:
          #print 'SPLIT happenin...watch out'
          return [True,None]

  def insertInNode(self,node,newentry):
    #print 'inserting the newly created node ',newentry,' from prev split to its parent ',node
    children=self.getChildren(node)
    children.append([newentry,self.getAttr(newentry,'bbox')])
    self.setAttr(node,['children',children])
    if len(children) <= self.nodemaxfanout:
      return False
    else:
      #print 'Oh even this node is overflowing..needs split again'
      return True
    
  
  def propagateUpward(self,uid,new_priority) :
        #print uid,new_priority
	prioritylist=self.getAttr(uid,'priority_items')
	if new_priority[2] > prioritylist[-1][-1] :
			
			prioritylist.append(new_priority)
			prioritylist.sort(self.sortByPriority)
			prioritylist=prioritylist[0:self.priorityLimit]
			self.setAttr(uid,['priority_items',prioritylist])
			getParent=self.getAttr(uid,'parent')
			if getParent!=None :
				#self.debug('upward update in process...')
				self.propagateUpward(getParent,new_priority)
			else :
				return
	else : return

  def quadsplit(self,node):
    children=self.getChildren(node)
    type=self.getAttr(node,'type')
    if type=='leaf':
      minfanout=self.leafminfanout
    else:
      minfanout=self.nodeminfanout
    #print 'entering split mode for node ',node,' with child len of ',len(children),' where the min allowed len for ',type,' is ',minfanout
    worst=None
    expansion=0
    areas=[]
    for ch in children:
      bbox1=ch[1]
      for ch2 in children:
        bbox2=ch2[1]
        bigbbox=self.union(bbox1,bbox2)
        deadspace=(self.area(bigbbox)-self.area(bbox1)-self.area(bbox2))
        if (deadspace is None or deadspace > worst):
          worst=deadspace
          gp1=[ch]
          gp1_bbox=bbox1
          gp2=[ch2]
          gp2_bbox=bbox2
    #print '-------PICK SEED RESULTS-------------'
    #print 'group 1'
    #print gp1,gp1_bbox
    #print 'group 2'
    #print gp2,gp2_bbox
    #print '--------------------------------------'
    try:
      children.remove(gp1[0])
      if gp1[0]!=gp2[0]:
        children.remove(gp2[0])
    except:
      print children
      print "group1",gp1
      print "group2",gp2
      raise "Rtree Error"
    while children:
      best_entry=None
      expansion=0
      for ch in children:
        bbox=ch[1]
        A=self.area(bbox)
        d1=(self.area(self.union(bbox,gp1_bbox))-self.area(gp1_bbox))
        d2=(self.area(self.union(bbox,gp2_bbox))-self.area(gp2_bbox))
        if d2 - d1 > expansion:
          best_group=gp1
          best_entry=ch
          best_bbox=bbox
          expansion=d2 - d1
        if d1 -d2 >=expansion:
          best_group=gp2
          best_entry=ch
          best_bbox=bbox
          expansion=d1 - d2
      if best_entry is None:
        print "ERROR: Couldn't find reasonable split"
        raise "RTREE ERROR"
      best_group.append(best_entry)
      if best_group is gp1:
        gp1_bbox=self.union(gp1_bbox,best_bbox)
      elif best_group is gp2:
        gp2_bbox=self.union(gp2_bbox,best_bbox)
      children.remove(best_entry)
      if len(gp1)==(minfanout-len(children)):
        gp1.extend(children)
        gp1_bbox=None
        for e in gp1:
          gp1_bbox=self.union(gp1_bbox,e[1])
        children=[]
      if len(gp2)==(minfanout - len(children)):
        gp2.extend(children)
        gp2_bbox=None
        for e in gp2:
          gp2_bbox=self.union(gp2_bbox,e[1])
        children=[]
      if self.add_priority and type=='leaf':
        gp1.sort(self.sortByPriority)
        gp2.sort(self.sortByPriority)
    #print 'the len of the two groups split are ',len(gp1),len(gp2), ' with the bounding boxes as ',gp1_bbox,gp2_bbox
    #print '----group 1-----'
    #print gp1
    #print '-----group2------'
    #print gp2
    #print '-----------------'
    
    new_node=uuid.UUID()
    if type=='leaf':
      #print 'since the leaf was split, the aggcount is same as the lengths above'
      self.setAttr(node,['children',gp1,'bbox',gp1_bbox,'aggregate_child_count',len(gp1)])
      self.setAttr(new_node,['children',gp2,'bbox',gp2_bbox,'aggregate_child_count',len(gp2),'type',type,'roles',self.rtree_roles])
    else:
      pr,count=self.get_pr_count_fromchild(map(lambda a:a[0],gp1),self.add_priority)
      #print 'the new agg_count for gp1 is ',count
      #print 'the new prlist for gp1 is',pr
      self.setAttr(node,['children',gp1,'bbox',gp1_bbox,'aggregate_child_count',count,'priority_items',pr])
      pr,count=self.get_pr_count_fromchild(map(lambda a:a[0],gp2),self.add_priority)
      #print 'the new agg_count for gp2 is ',count
      #print 'the new prlist for gp2 is',pr
      self.setAttr(new_node,['children',gp2,'bbox',gp2_bbox,'aggregate_child_count',count,'priority_items',pr,'type',type,'roles',self.rtree_roles])
      for e in gp2:
        self.setAttr(e[0],['parent',new_node])
    return new_node
        
  def get_pr_count_fromchild(self,nodelist,add_priority):
    agcount=0
    if not add_priority:
      for node in nodelist:
        agcount+=self.getAttr(node,'aggregate_child_count')
      return [None,agcount]
      
    pr_items=[]
    for node in nodelist:
      agcount+=self.getAttr(node,'aggregate_child_count')
      if self.getAttr(node,'type')=='leaf':
        pr_items.extend(self.getAttr(node,'children'))
      else:
        pr_items.extend(self.getAttr(node,'priority_items'))
    pr_items.sort(self.sortByPriority)
    return [pr_items[0:self.priorityLimit],agcount]
                  
                     
  
  def createNewRoot(self,n1,n2):
    uf=uform.UForm()
    uf['roles']=self.rtree_roles
    uf['type']='internal node'
    n1_bbox=self.getAttr(n1,'bbox')
    n1_count=self.getAttr(n1,'aggregate_child_count')
    
    
    n2_bbox=self.getAttr(n2,'bbox')
    n2_count=self.getAttr(n2,'aggregate_child_count')
    uf['bbox']=self.union(n1_bbox,n2_bbox)
    uf['children']=[[n1,n1_bbox],[n2,n2_bbox]]
    #print 'split root'
    
    if self.add_priority:
      uf['priority_items']=[]
      if self.isLeaf(n1):
        uf['priority_items'].extend(self.getAttr(n1,'children'))
        uf['priority_items'].extend(self.getAttr(n2,'children'))
      else:
        uf['priority_items'].extend(self.getAttr(n1,'priority_items'))
        uf['priority_items'].extend(self.getAttr(n2,'priority_items'))
      uf['priority_items'].sort(self.sortByPriority)
      uf['priority_items']=uf['priority_items'][0:self.priorityLimit]
    uf['aggregate_child_count']=n1_count+n2_count
    sav=[]
    for i in uf.keys():
      sav.append(i)
      sav.append(uf[i])
    self.setAttr(uf.uuid,sav)
    self.root=uf.uuid
    self.setAttr(n1,['parent',uf.uuid])
    self.setAttr(n2,['parent',uf.uuid])
    self.setAttr_repos(self.spindex,'rtree_root',uf.uuid)
    
    
    
   
  def splitAndAdjust(self,node):
    new_node=self.splitfunc(node)
    if node==self.root:
      self.createNewRoot(node,new_node)
    else:
      parent=self.getAttr(node,'parent')
      self.setAttr(new_node,['parent',parent]) #copy the parent of the old node to the new node
      split=self.insertInNode(parent,new_node)
      self.adjustPath(parent)
      if split:
        self.splitAndAdjust(parent)
    return
  
  def adjustPath(self,node): #
      #print 'adjusting path for node ',node, ' due to inserts of ',ulist
      bbox=self.getAttr(node,'bbox')
      newbbox=None
      children=self.getChildren(node)
      for i in range(len(children)):
        children[i][1]=self.getAttr(children[i][0],'bbox')
        newbbox=self.union(newbbox,children[i][1])
      if bbox==newbbox:
        print 'bbox hasnt changed, jus updated the children bbox entries'
        self.setAttr(node,['children',children])
        return
      else:
        print 'bbox has changed for this node from ',bbox, ' to ',newbbox
        self.setAttr(node,['children',children,'bbox',newbbox])
        if node!=self.root:
          self.adjustPath(self.getAttr(node,'parent'))
        else:
          #pass
          print 'reached root, stopping propagation and returning'
        return
          
      
  
  def update_count_and_priority(self,child,diff,new_priority=None,upd_flag=None):
      if child==self.root:
        #print 'reached root..returning'
        return
      uid=self.getAttr(child,'parent')
      agg_count=self.getAttr(uid,'aggregate_child_count')
      agg_count+=diff
      #print 'updated aggcount of parent ',uid,' from ',agg_count-diff, ' to ',agg_count
      setval=['aggregate_child_count',agg_count]
      if new_priority!=None:
          #print 'checking if the new entry needs to be added to priority'
	  prioritylist=self.getAttr(uid,'priority_items')
          old_count=len(prioritylist)
          if upd_flag=='add':
            if new_priority[2] > prioritylist[-1][-1] :
              #print 'old plist is'
              #print map(lambda a:(a[0],a[2]),prioritylist)
              #print 'new priority ',new_priority[2], 'is greater than the last priority ',prioritylist[-1][-1]
	      prioritylist.append(new_priority)
	      prioritylist.sort(self.sortByPriority)
	      prioritylist=prioritylist[0:self.priorityLimit]
              #print 'new plist is'
              #print map(lambda a: (a[0],a[2]),prioritylist)
              #if new_priority in prioritylist:
              setval.extend(['priority_items',prioritylist])
            else:
              new_priority=None
          elif upd_flag=='remove': # still needs work related to priority items wrt to adding items upto PrLimit
          
            #print 'old prioritylist is'
            #print prioritylist
            for i in new_priority:
              if i in prioritylist:
                prioritylist.remove(i)
            if old_count!=len(prioritylist):
              
              #print 'priority_items has changed from ',old_count,' to ', len(prioritylist)
              (prioritylist,ignorecount)=self.get_pr_count_fromchild([x[0] for x in self.getChildren(uid)],self.add_priority)
              #print 'updated the priority list for ',uid
              #print prioritylist
              setval.extend(['priority_items',prioritylist])
            else:
              new_priority=None
      #print uid,setval
      self.setAttr(uid,setval)
      if uid!=self.root :
	  self.update_count_and_priority(uid,diff,new_priority,upd_flag)
      else :
        #print 'root reached..stopping propagation and returning'
        return

  def update_priority(self,e):
    if not self.add_priority:
      print 'Cant do priority updates as the index has no priorityt info'
      return
    leaves=[x[0] for x in self.traverse(self.root,e[1],self.intersects)]
    if len(leaves)==0:
      print 'couldnt find any leaves containing the value ',value
      return
    else:
      for leaf in leaves:
        children=self.getChildren(leaf)
        ulist=[x[0] for x in children]
        if e[0] in ulist:
          #double check to c if the bbox is same and priority isnt
          if e[1]==children[ulist.index(e[0])][1] and e[2]!=children[ulist.index(e[0])][2]:
            #first delete the old value from pr_items of parents..if necessary
            if ulist.index(e[0]) < self.priorityLimit:
              self.update_count_and_priority(leaf,0,children[ulist.index(e[0])],'remove')
            
            children[ulist.index(e[0])][2]=e[2]
            children.sort(self.sortByPriority)
            self.setAttr(leaf,['children',children])
            
            #now update the new value if necessary  
            if children.index(e) < self.priorityLimit:
              self.update_count_and_priority(leaf,0,e,'add')
            return
          else:
            print 'the bboxes dont match or the priority is already the same'
            return
    print 'couldnt find the value in any of the leaves'
    return
        
        

  def insert(self,e):
    #print '------------------------------------------NEW INSERT---------------------------------'
    leaves=self.traverse(self.root,e[1],self.intersects)
    #print 'The leaf choices are ',leaves
    if len(leaves)==0:
      choice=self.root
      while 1:
        #print choice
        if self.isLeaf(choice):
          break
        newchoice=[]
        for i in self.getChildren(choice):
          newchoice.append([i[0],i[1],self.getAttr(i[0],'aggregate_child_count')])
        #choice=[[choice,self.getAttr(choice,'bbox'),self.getAttr(choice,'aggregate_child_count')]]
        #choice=list(self.getChildren(choice))
        #for i in range(len(choice)):
        #  choice[i].append(self.getAttr(choice[i][0],'aggregate_child_count'))
        #print choice
        choice=self.chooseLeaf(newchoice,e[1])
    elif len(leaves)==1:
      choice=leaves[0][0]
    else:
      choice=self.chooseLeaf(leaves,e[1])
    #print 'Leaf choice is ',choice
    (split,updbbox)=self.insertInLeaf(choice,e)
    if(split):
      #print 'proceeding to split'
      self.splitAndAdjust(choice)
    elif updbbox!=None and choice!=self.root:
      #print 'bbox has changed and is not root, so needs updation'
      self.adjustPath(self.getAttr(choice,'parent'))
    else:
      pass
      #print 'Hooray!!, No splits or need for path adjustments'
  
    

  def deleteValue(self,leaves,bbox,predicate,value): # allows to delete a list of uuids(values) spanning the bbox which if the union of the individual items
    valfound=[]
    underflow=[]
    changed_leaves={}
    for leaf in leaves:
      children=self.getChildren(leaf)
      oldbbox=self.getAttr(leaf,'bbox')
      oldcount=len(children)
      dlist=[]
      for k in children:
        if k[0] in value and predicate(k[1],bbox): #added checking to make sure the value to be deleted actually intersects the bbox
          dlist.append(k)
          if k[0] not in valfound:
            valfound.append(k[0])
      if len(dlist)!=0:
        for d in dlist:
          children.remove(d)
        newbbox=None
        for ch in children:
          newbbox=self.union(newbbox,ch[1])
        self.setAttr(leaf,['children',children,'aggregate_child_count',len(children),'bbox',newbbox])
        if oldbbox!=newbbox:
          lf_parent=self.getAttr(leaf,'parent')
          if not changed_leaves.has_key(lf_parent): #collect the leaves that have changed to update their bboxes
            changed_leaves[lf_parent]=1

        print 'Successfully deleted ',dlist,' from leaf ',leaf
        self.delcount+=len(dlist)
        if self.now:
           if self.add_priority:
            self.update_count_and_priority(leaf,len(children)-oldcount,dlist,'remove')
           else:
            self.update_count_and_priority(leaf,len(children)-oldcount)
        if len(children) < self.leafminfanout:
          #print 'This leaf ',leaf,' has underflowed'
          underflow.append(leaf)
      if self.check_dup and len(value)==len(valfound): #If the index has only unique values and all the values have been already found and deleted..break
        print 'All values found and deleted'
        return underflow
    for v in valfound:
      value.remove(v)
    if len(value)!=0:
      print 'Delete Unsuccessful. No match found for ',value
    #adjust the bbox for the changed_leaves
    print 'changed leaves are ', changed_leaves
    for chl in changed_leaves:
      self.adjustPath(chl)
      
    return underflow # returns the nodes that have underflowed
      
  # this function would delete all data that INTERSECTS the 'bbox' provided.     
  def deleteFromBbox(self,leaves,bbox,predicate): #potential dangerous function..can screw up the index.. not even sure if this is needed at all
    underflow=[]
    changed_leaves={}
    for leaf in leaves:
      children=self.getChildren(leaf)
      oldcount=len(children)
      oldbbox=self.getAttr(leaf,'bbox')
      dlist=[]
      for k in children:
       try: 
        if predicate(k[1],bbox):
          dlist.append(k)
       except IndexError:
         print 'Index Error Exception'
         print leaf,k
      if len(dlist)!=0:
        for d in dlist:
          children.remove(d)
        newbbox=None
        for ch in children:
          newbbox=self.union(newbbox,ch[1])
        self.setAttr(leaf,['aggregate_child_count',len(children),'children',children,'bbox',newbbox])
        if oldbbox!=newbbox:
          lf_parent=self.getAttr(leaf,'parent')
          if not changed_leaves.has_key(lf_parent): #collect the leaves that have changed to update their bboxes
            changed_leaves[lf_parent]=1
        #print 'Successfully deleted ',len(dlist),' entries'
        self.delcount+=len(dlist)
        if self.now:
          if self.add_priority:
            self.update_count_and_priority(leaf,len(children)-oldcount,dlist,'remove')
          else:
            self.update_count_and_priority(leaf,len(children)-oldcount)
        if len(children) < self.leafminfanout:
          #print 'This leaf ',leaf,' has underflowed'
          underflow.append(leaf)
    for chl in changed_leaves:
      self.adjustPath(chl)
    return underflow
        
        
          
          
          

  def delete(self,bbox,value=None):
    print 'value is ',value,' and bbox is ',bbox
    self.delcount=0
    leaves=map(lambda a: a[0],self.traverse(self.root,bbox,self.intersects))
    print 'len of leaves is ',len(leaves)
    if value==None:
      underflowleaves=self.deleteFromBbox(leaves,bbox,self.intersects)
    else:
      underflowleaves=self.deleteValue(leaves,bbox,self.intersects,value)
    #print underflowleaves
    after_cp=self.collapse_children(underflowleaves) #remember, the resulting list can have underflowed Inodes as well...
    #this contains the (parent,child) tuple 
    self.local_insert(after_cp)
    print 'deleted ',self.delcount, ' entries'
    return
    

  def local_insert(self,ulist):
    #print 'Entering LOcal Inserts-----------------------------------------------------------------------'
    if len(ulist)==0:
      #print ' No more underflow nodes...all done..returning'
      return
    pcdict={}
    newudlist=[]
    for i in ulist:
      if pcdict.has_key(i[0]):
        pcdict[i[0]].append(i[1])
      else:
        pcdict[i[0]]=[i[1]]
    for i in pcdict:
      #print 'now dealing with the parent ',i
      candidates=[[x[0],self.getAttr(x[0],'bbox'),self.getAttr(x[0],'aggregate_child_count')] for x in self.getChildren(i) if x[0] not in pcdict[i]] #exclude the underflowed children from the possible insert cabdidates
      #print 'the possible candidates are  ',candidates
      type=self.getAttr(candidates[0][0],'type') #checking for types of insert, either for leaves or for inodes
      if type=='leaf':
        minfanout=self.leafminfanout
        maxfanout=self.leafmaxfanout
      else:
        minfanout=self.nodeminfanout
        maxfanout=self.nodemaxfanout
      inslist=[]
      ovflow=[]
      choicedict={}
      ckdict=choicedict.has_key
      for ch in pcdict[i]:
        uflowchildren=self.getChildren(ch)
        #print 'the node to be deleted is ',ch,' with len and bbox as ', len(uflowchildren), self.getAttr(ch,'bbox')
        #just double checking....
        if len(uflowchildren) <  minfanout:
          inslist.extend(uflowchildren)
        else:
          print('This node is not underflowed',ch,i)
      #print '-----------Number of entries to be re-inserted is ',len(inslist),'------------------'
      for ins in inslist:
        choice=self.chooseLeaf(candidates,ins[1]) #the name chooseLeaf if a misnomer, cos it will work for Inodes too
        #print 'the chosen one for the insert ',ins, ' is ', choice
        if not ckdict(choice):
          choicedict[choice]={'bbox':self.getAttr(choice,'bbox'),'aggregate_child_count':self.getAttr(choice,'aggregate_child_count'),'children':self.getChildren(choice)}
        choicedict[choice]['children'].append(ins)
        choicedict[choice]['bbox']=self.union(choicedict[choice]['bbox'],ins[1])
      
      #print 'the choice dict has entries'
      #print choicedict
      #update priority here if needed.still to work on

       #update parent
      pchildren=[x for x in self.getChildren(i) if x[0] not in pcdict[i]+choicedict.keys()] #remove the underflowed nodes from the parent
      #print 'the nodes of parent minus the choices and uflowed nodes ',pchildren
      for ch in choicedict:
        if type=='leaf':
          choicedict[ch]['children'].sort(self.sortByPriority)
          choicedict[ch]['aggregate_child_count']=len(choicedict[ch]['children'])
        else:
          (choicedict[ch]['priority_items'],choicedict[ch]['aggregate_child_count'])=self.get_pr_count_fromchild([x[0] for x in choicedict[ch]['children']],self.add_priority)
        sav=[]
        for k in choicedict[ch]:
          sav.append(k)
          sav.append(choicedict[ch][k])
        self.setAttr(ch,sav)
        #print ch,choicedict[ch]
        pchildren.append([ch,choicedict[ch]['bbox']])
        if len(choicedict[ch]['children']) > maxfanout:
          #print ch,' has overflowed'
          ovflow.append(ch)
      #print 'the update child list of parent ', i, ' is ',pchildren
      self.setAttr(i,['children',pchildren]) #update the parent of the changes
          
      #now proceed for overflow management of the children, if any
      #print 'the overflow list is ',ovflow
      for ov in ovflow:
        #print 'dealing with overflow of ',ov
        self.splitAndAdjust(ov)
     
      
      #now check for undeflow of the parent..if any..
      if len(self.getChildren(i)) < self.nodeminfanout:
        if i!=self.root:
          newudlist.append((self.getAttr(i,'parent'),i))
        else:
          pass
          #print('root reached.. no need to deal with underlow')
    self.local_insert(newudlist)
        
        
        
          
  
  def collapse_children(self,udlist):
    par_child=[(self.getAttr(x,'parent'),x) for x in udlist]
    pcdict={}
    for i in par_child:
      if pcdict.has_key(i[0]):
        pcdict[i[0]].append(i[1])
      else:
        pcdict[i[0]]=[i[1]]
    newudlist=[]
    #print 'the underflow dict is ',pcdict
    for i in pcdict:
      if len(pcdict[i])==1:
        newudlist.append((i,pcdict[i][0]))
        #print i,pcdict[i],' cannot collapse..as only one child'
      else:
        tot_count=sum(map(lambda a :self.getAttr(a,'aggregate_child_count'),pcdict[i]))
        if tot_count < self.leafminfanout:
            newudlist.extend([(i,x) for x in pcdict[i]])
            #print i,pcdict[i],' cannot collapse as the sum of children also underflows'
        else:
            #do the merge
            #print 'can do the merge for the children of ',i,pcdict[i]
            chlist=list(pcdict[i])
            chosench=chlist.pop(0) #arbitrarily the first one is chosen.. alternate means could be employed such as max children..
            #print 'the chosen child is',chosench
            chbbox=self.getAttr(chosench,'bbox')
            chosenchildren=self.getChildren(chosench)
            #print 'the number of child in ch before merge is ',len(chosenchildren)
            for ch in chlist:
                 chosenchildren.extend(self.getChildren(ch))
                 chbbox=self.union(chbbox,self.getAttr(ch,'bbox'))
            #print 'the number of children after merge is', len(chosenchildren)
            chosenchildren.sort(self.sortByPriority)
            self.setAttr(chosench,['bbox',chbbox,'children',chosenchildren,'aggregate_child_count',tot_count])
            
            #update the parent
            #print 'the pcdict elements for this parent are ',pcdict[i]
            #print 'the children of parent ',i,' before update  is\n', self.getChildren(i)
            pr_children=[x for x in self.getChildren(i) if x[0] not in pcdict[i]] #remove all and add the updated chosen one
            pr_children.append([chosench,chbbox])
            self.setAttr(i,['children',pr_children])
            #print 'children of parent after update is ',pr_children
            # No need to change agg_count and bbox, as the move was local to the parent.
           
             #check for overflow now
            if len(chosenchildren) > self.leafmaxfanout:
              #print 'the chosen one has overflowed with len ',len(chosenchildren)
              self.splitAndAdjust(chosench)
            #Check for underflow for this node, if so.add to the underdlow list
            if len(self.getChildren(i)) < self.nodeminfanout:
              if i!=self.root:
                #print 'the parent has underflowed with length ',len(self.getChildren(i))
                newudlist.append((self.getAttr(i,'parent'),i))
              else:
                pass
                #print 'root reached.. no need to worry about underflow'
    return newudlist
   
            
  def newHead(self,lfmax=None,lfmin=None,ndmax=None,ndmin=None,name=None,source_dataset=None,node_kinds=None,key_attributes=None,dimension=None,source_hash=None):
    rt_roles=[uuid._('~0189112434c7c911d98e2c34db737a4e2a'),uuid._('~010a685574d02011d89f8179ba7fb44707')]
    headuf=uform.UForm()
    headuf['rtree_root']=uuid.UUID()
    headuf['name']=name or 'Generic R-tree Index'
    headuf['source_dataset']=source_dataset
    headuf['node_kinds']=node_kinds or ['leaf','internal node']
    headuf['key_attributes']=key_attributes or []
    headuf['source_member_hash']=source_hash
    headuf['dimension']=len(headuf['key_attributes'])
    headuf['fanout_max_leaf']=lfmax or 25
    headuf['fanout_min_leaf']=lfmin or int(0.4*headuf['fanout_max_leaf'])
    headuf['fanout_max_node']=ndmax or 7
    headuf['fanout_min_node']=ndmin or int(0.4*headuf['fanout_max_node'])
    headuf['roles']=rt_roles
    self.setAttr_repos(headuf)
    self.spindex=headuf.uuid

    self.leafmaxfanout=int(headuf['fanout_max_leaf']*(1+self.expand_factor))
    self.nodemaxfanout=int(headuf['fanout_max_node']*(1+self.expand_factor))
    self.leafminfanout=int(headuf['fanout_min_leaf']*(1-self.expand_factor))
    self.nodeminfanout=int(headuf['fanout_min_node']*(1-self.expand_factor))

    rootuf={}
    if node_kinds!=None:
      rootuf['type']=node_kinds[0]
    else:
      rootuf['type']='leaf'
    rootuf['children']=[]
    rootuf['aggregate_child_count']=0
    self.root=headuf['rtree_root']
    self.setAttr_repos(self.root,rootuf)
    print 'the new head is ',self.spindex
    print ' the new root is ',self.root
    return self.spindex
    
    
    
    
  def __init__(self,r,spindex=None,add_priority=0,use_cache=1,now=1,expand_factor=0.0,check_duplicate=0,priority_limit=10,cachemaxsize=1000,cachestorefactor=0.6):
    self.rtree_roles=[uuid._('~01d37ae72c119311d99a7239eb19bd68fc'),uuid._('~01cbe877d00e8211daafb968fe26f651dc')]
    self.r=r
    self.spindex=spindex
    self.add_priority=add_priority
    self.now=now
    self.expand_factor=expand_factor
    self.check_dup=check_duplicate
    self.use_cache=use_cache
    self.splitfunc=self.quadsplit
    self.default_attrs=['type','children','bbox','parent','priority_items','aggregate_child_count']
    if self.use_cache:
	self.myrepos={} #initialize cache dictionary
	self.getAttr=self.getAttr_cache  # use the cached getAttr function
	self.setAttr=self.setAttr_cache
	print'using cached getAttrs'
	self.cachemaxsize=cachemaxsize #number of max uforms to be cached
	self.cachestorefactor= cachestorefactor #the factor of cache max size that needs to be retained
	self.cacheminsize=int(self.cachestorefactor*self.cachemaxsize)
    else:
	self.getAttr=self.getAttr_repos  # use the direct repos getAttr function
	self.setAttr=self.setAttr_repos
    if self.add_priority:
	self.priorityLimit=priority_limit
    if self.spindex==None:
      print 'No Index Head given... Use newHead to create a new one..returning'
      return None
    rt_head=self.getAttr_repos(spindex,['rtree_root','fanout_max_leaf','fanout_max_node','fanout_min_leaf','fanout_min_node'])
    self.root=rt_head['rtree_root']
    print 'Root is at ',self.root
    self.leafmaxfanout=int(rt_head['fanout_max_leaf']*(1+self.expand_factor))
    self.nodemaxfanout=int(rt_head['fanout_max_node']*(1+self.expand_factor))
    self.leafminfanout=int(rt_head['fanout_min_leaf']*(1-self.expand_factor))
    self.nodeminfanout=int(rt_head['fanout_min_node']*(1-self.expand_factor))
    print self.leafmaxfanout,self.leafminfanout,self.nodemaxfanout,self.nodeminfanout
    


