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

from MAYA.VIA import uuid,uform,repos,vsmf
import _btdb
KEYVAL_SEP='\x00'
from MAYA.utils import scalablecoll
class stBuilder:
  def __init__(self,filename,check_duplicates=0,uuid_only=1,unsafe=0) :
    self.count=0
    self.filename=filename
    self.checkdup=check_duplicates #enable this to 1, if you want to prevent redundant data to be added to the index.. might make the indexing slow though
    self.uuid_only=uuid_only
    if self.filename==None:
	self.debug('DB error! No filename given')
    	self.message('error','Local BTree file creation error! - Invalid filename '+self.filename)
	return
    access = _btdb.CREATE
    if unsafe: 
        access |= _btdb.NOSYNC
    self.btree = _btdb.new(self.filename, 0666, access, _btdb.DEFAULT_BLKSIZE, 250 ,2000)
    if self.uuid_only==1:
	self.insert=self.insert_uuid
    else:
	self.insert=self.insert_gen
    

  def set(self, name, values):
      a = name.encode('utf8')
      svalues = vsmf.serialize(values)
      self.btree.set(0,a,svalues,0,_btdb.MAX_VAL)

  def get(self, name):
      a = name.encode('utf8')
      v,l = self.btree.get(0,a,0,200)
      if l == 0: return None
      if l > 200:
          v, l = self.btree.get(0,a,0,l)
      return vsmf.reconstitute(v)

  def add(self, name, item):
      x = self.get(name)
      if x == None: x = []
      if self.checkdup==1 and (item not in x):
	  x.append(item)
	  self.set(name,x)
      else:
          x.append(item)
          self.set(name,x)

  def nextkey(self,name=''):
      a = name.encode('utf8')
      return self.btree.next(0,a).decode('utf8')

  def insert_gen(self,m) :
    if type(m)==type(()) or type(m)==type([]):
	if len(m)==2: # input must be of syntax (key,value) or [key,value]
	    self.add(m[0],m[1])
	else :
	    print 'Insert Message syntax error!- List of length greater than 2',m
    else: 
	print 'Insert Message syntax error! - Message is not a list',m

    # the following message can be sent if needed for credit based flow control
    return
	
  def insert_uuid(self,m):
      #print m.encode('utf8')
     if type(m)==type(()) or type(m)==type([]):
	if len(m)==2: # input must be of syntax (key,value) or [key,value]
          key=m[0]+KEYVAL_SEP+m[1].toString()
          #print m,key
          self.btree.set(0,key.encode('utf8'),' ',0,_btdb.MAX_VAL)
	else :
          print 'Insert Message syntax error!- List of length greater than 2',m
     else: 
       print 'Insert Message syntax error! - Message is not a list',m

    # the following message can be sent if needed for credit based flow control
     return
      
  def extenduu(self,prefix,bytes):
	return prefix.rightExtend(vsmf.serialize(bytes))

  def create_resultset(self,value,type=None,version=None):
	if self.uprefix!=None :
	    newid=self.extenduu(self.uprefix,self.ucount)
	    self.ucount+=1
	    uf=uform.UForm(newid)
	else: uf=uform.UForm()

	if type=='leaf':
	    uf['children']=tuple(value)
            uf['type']='leaf'
	    uf['roles']=[self.bTreerole]
	else:
	    uf['members']=tuple(value)
	    uf['roles']=[self.collectionrole]
	if version: 
	    uf['revision_number'] = version
        self.r.setAttr(uf)
        return uf.uuid
	
  def gen_keyval(self,prev=None,val=[],k=''):
      #prev=None
      #key=None
      
      while 1:
	  #value=[]
	  k=self.nextkey(k)
	  if k == '':
	      return ((prev,val),(k,k),k)
	  sep=k.rindex(KEYVAL_SEP)
	  key=k[0:sep]
	  if prev==None:
	      prev=key #bootstrap
	  if key==prev:
	  #k=self.nextkey(k)
	      val.append(uuid.fromString(k[sep+1:]))
	      prev=key
	  else:
	      return ((prev,val),(key,[uuid.fromString(k[sep+1:])]),k)
	  
	    
  def makeIndex(self,r,fanout_max=50,btree_prefix=None,fanout_min=None,resultslist_max_length=None,name=None,source_dataset=None,description=None,version=None) :
	#if m=='start':
            self.r=r
            self.count=0
	    self.ucount=0
	    self.fanout_max=fanout_max
	    if self.fanout_max==None:
		self.message('error','fanout_max value is invalid. Enter a value')
		return
	    self.fanout_min=fanout_min
	    if self.fanout_min==None: self.m=int(0.5*float(self.fanout_max))
	    self.source_dataset=source_dataset
	    self.name=name
	    if self.name==None: self.name='Generic B-Tree Index'
	    self.label='_'.join(self.name.upper().split(' '))
	    self.description=description
	    if self.description==None and uuid.isa(self.source_dataset): self.description='This is a string index of the dataset pointed by '+ self.source_dataset.toString()
	    else: self.description='This is a string index'
	    self.resultslist_max_length=resultslist_max_length
	    if self.resultslist_max_length==None: self.resultslist_max_length=1
	    self.uprefix=btree_prefix
	    print(self.uprefix)
    #self.uprefix=uuid._('~01b852894c7f6a11d9add619e5408e77a0'
	    if self.filename==None:
		self.message('status','Invalid local Btree file given. Halting')
		print('Invalid local Btree file given. Halting')
		return
	    self.bTreerole=uuid._('~fd000b70d47403627472')
	    self.btreeHeadRole=uuid._('~01f3a6213c8c2811d9a1b0045f7750463a')
	    self.collectionrole=uuid._('~fd000a02510bfd17204424')
	  
	  
	    self.lenbucket={}
	    leafpointers=[]
	    nodepointers=[]
	    k=''
	    prev=None
	    z=0
	    prev=None
	    val=[]
	    while 1 :
		z+=1
                if self.uuid_only==1:
                  (a,b,k)=self.gen_keyval(prev,val,k)
		#print a
		#print b
                  (key,value)=a
                  (prev,val)=b
                else:
                  k=self.nextkey(k)
                  if k=='':
                    break
                  key=k
                  value=self.get(k)
		#val=[val]
		
		
		

		#newval=[]	  # This is to remove any duplicates. If duplicates are	
		#for j in value:	  # tolerated remove these lines
	 	#    if j not in newval: newval.append(j)
		#value=newval
	
		if len(leafpointers) == self.fanout_max :
		    nodepointers.append((leafpointers[0][0],self.create_resultset(leafpointers,'leaf',version=version)))
		    leafpointers=[]

		lenv=len(value)
		if lenv > self.resultslist_max_length :
		    leafpointers.append((key,self.create_resultset(value,'resultset',version=version),lenv))
		else : leafpointers.append((key,tuple(value),lenv))
		
		    
		
		if self.lenbucket.has_key(lenv): self.lenbucket[lenv]+=1
		else :self.lenbucket[lenv]=1  # statistics gathering code..can be ignored
		if self.uuid_only==1 and prev=='':
		    break
	    if len(leafpointers) > 0:
		nodepointers.append((leafpointers[0][0],self.create_resultset(leafpointers,'leaf',version=version)))
	    #print(self.lenbucket)
	    
	    if len(nodepointers) > 1:
	        self.packNodes(nodepointers,version)
	    else:
		self.btree_root=nodepointers[0][1]
		
	    if self.uprefix==None:
		self.uprefix=uuid.UUID()
	    uf=uform.UForm(self.uprefix)
	    uf['btree_root']=self.btree_root
	    uf['name']=self.name
	    uf['label']=self.label
	    uf['description']=self.description
	    if self.source_dataset!=None:
	        uf['source_dataset']=self.source_dataset
	    uf['fanout_min']=self.fanout_min
	    uf['fanout_max']=self.fanout_max
	    uf['resultslist_max_length']=self.resultslist_max_length
	    uf['node_kinds']=['internal node','leaf']
	    #uf['results_types']={'0': 'instance list',
	    #			 '1': 'instance collection'}
	    uf['roles']=[self.btreeHeadRole]
	    if version:
		uf['revision_number'] = version
	    self.r.setAttr(uf)
	    ##print uf
	    return uf.uuid	
		
	    

  def packNodes(self,nodelist,version=None):
    if len(nodelist)> self.fanout_max :
	j=0
	newlist=[]
	nlen=len(nodelist)
	#self.debug(nlen)
	while j < nlen:
		if self.uprefix!=None:
	            newid=self.extenduu(self.uprefix,self.ucount)
		    self.ucount+=1
		    uf=uform.UForm(newid)
		else: uf=uform.UForm()
		
		
		endval=j+self.fanout_max
		
		if endval >= nlen :
		    endval=nlen
		
				
		uf['children']=nodelist[j:endval]
		uf['type']='internal node'
		uf['roles']=[self.bTreerole]
		if version:
			uf['revision_number'] = version
        	self.r.setAttr(uf)
        	
        
		newlist.append((nodelist[j][0],uf.uuid))
		j=endval
		#self.debug(j)
		
	self.packNodes(newlist,version)
    else:
	if self.uprefix!=None:
	   rootid=self.extenduu(self.uprefix,self.ucount)
	   self.ucount+=1
	   uf=uform.UForm(rootid)
	else: uf=uform.UForm()
	uf['children']=nodelist
	uf['type']='internal node'
	uf['roles']=[self.bTreerole]
	if version:
		uf['revision_number'] = version
	self.r.setAttr(uf)
	print 'Root Id is ...'
	print uf.uuid
	self.btree_root=uf.uuid
	return 
    return  


if __name__=='__main__':
    r=repos.Repository('joshua3.maya.com:8888')
    stoplist=['','for','in','pa','dcnr','of','the']
    stb=stBuilder('VO_org.btdb')
    sc=uuid._('~0160173984a6d511d99ab41cd552a85861')
    mem=scalablecoll.getAllMembers(r,sc)
    print 'len of mem is ',len(mem)
    for i in mem:
	na=r.getAttr(i,'name')
	#print i,na
	if na!=None:
	    na=na.lower()
	    for j in na.split(' '):
		if j not in stoplist:
		    stb.insert((j,i))
    print 'local insert done'
    stb.makeIndex(r,resultslist_max_length=3,source_dataset=sc,name='String Index of Venture Outdoors Organizations')
    
    print 'index creation done'
		
		




