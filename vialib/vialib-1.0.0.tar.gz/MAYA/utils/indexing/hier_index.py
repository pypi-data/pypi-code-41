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
from MAYA.VIA import uuid, uform
from types import StringTypes
# also relies on a synchronous repository interface ala MAYA/repos.py

#
# Example classes used to access hierarchical indices
#
# An index is identified by a UUID that identifies it's "root"
# This UUID is "right-extended" to form child nodes of the index
#
# The right extensions are concatenations of the (utf8) string values
# used to represent the children at each node.  Each string is prefixed
# by its length to avoid aliasing.
#
# The empty string is used to indicate the root node.  (Typically each node
# uses the non-extended root UUID u-form as the role that each node plays.)
#
# An index may have multiple dimensions: for the "default" dimension the
# children are indicated by the "idx" attribute and the instances are held
# in "members".  For alternate dimension XXX the children are indicated
# by the "idx_XXX" attribute and instances are found in "XXX".
#

# 05/15/03 -rt.
# changed HIndexWriter.addMember to use chunks making it safe for concurrent use.
# Note that members are not sorted and may be redundantly added.

# 06/03/03 -rt.
# Added clean method to HIndexWriter. It recursively removes duplicate nodes,
# duplicate members, and dead branches, and also sorts the lists starting from
# any point in the tree.

# 11/06/03 -rt.
# lowercase all node names.

role_for_role = uuid._('~fd000a02510bfd1d650a97')
role_for_entity = uuid._('~fd000a02510bfd0a96b73e')
role_for_collection = uuid._ ( '~fd000a02510bfd17204424' )

REPOS_OP_SETCOND = 119

def _extenduuid(indexuu,path):
   ext = chr(0)
   if path != None:
     e = []
     for s in path:
       su = s.encode('utf8')      # this is not necessary if we know they are ASCII
       e.append(chr(len(su))+su)
     ext += ''.join(e)
   return uuid.UUID(indexuu.getBuf()+ext)

def _uniq(list):
  # assumes all strings (or hashable objects) in list; if not, does nothing.
  try:
    nd={} 
    for e in list: nd[e]=None
    return nd.keys()
  except:
    return list

def _canonicalizeSignature(sig):
   if type(sig) == type([]) or type(sig) == type(()):
      sig = sig[0]
   return sig

class HIndexReader:
   def __init__(self,repository,index_root_uuid):
     self.repos = repository
     self.root = index_root_uuid
     
   def getChildren(self,path=None,dimension='members', conn=None):
     "get child nodes.  'path' should be a list of strings (or None)"
     if dimension.lower() == 'members': idx = 'idx'
     else: idx = 'idx_'+dimension
     if not conn:
        v = self.repos.getAttr(_extenduuid(self.root,path),idx)
     else:
        v = self.repos.getAttr(_extenduuid(self.root,path),idx, conn=conn)
        
     return v

   def getMembers(self,path=None,dimension='members', conn=None):
     "get instances stored in the index at 'path'.  'dimension' indicates which partition of members"
     def lowstr(a):
       if type(a) == type(u''): return a.lower()
       return str(a).lower()
     if path:
        path = map(lowstr, path)

     if not conn:
        v = self.repos.getAttr(_extenduuid(self.root,path),dimension)
     else:
        v = self.repos.getAttr(_extenduuid(self.root,path),dimension, conn=conn)
        
     return v
  
   def getNode(self, path=None):

     return _extenduuid(self.root, map(str.lower, path))


class HIndexWriter(HIndexReader): #extend with writable interface

   def __init__(self,repository,index_root_uuid,index_name="Hier Index"):
     self.repos = repository
     self.root = index_root_uuid
     self.index_name = index_name
     self.paths = []
     while True:
        uf = uform.UForm(self.root, ['roles', 'shepherd_signature'])
        uf = self.repos.getAttr(uf)
        roles = uf['roles'] or []
        if role_for_role not in roles:
           sig = _canonicalizeSignature(uf['shepherd_signature'])
           roles.append(role_for_role)
           uf = uform.UForm(self.root, {'roles':roles,
                                        'implied_roles':[role_for_entity],
                                        'name':self.index_name+' Role',
                                        'label':self.index_name+' Role',
                                        'attributes':('idx','idx_')})
           rv = self.repos.request(REPOS_OP_SETCOND, [uf, sig])[1]
           if rv == 0:
              break
        else:
           break

   def removeChild(self, path, dimension=None, conn=None):
      if conn:
         raise Exception, "not supported"

      if dimension == None:
         idx = "idx"
      else:
         assert(type(dimension) in StringTypes)
         idx = "idx_%s"%(dimension)

      uu = _extenduuid(self.root, path[:-1])
      while True:
         uf = uform.UForm(uu, [idx, 'shepherd_signature'])
         uf = self.repos.getAttr(uf)
         orig_m = uf[idx]
         sig = _canonicalizeSignature(uf['shepherd_signature'])
         m = [o.lower() for o in orig_m]
         try:
            i = m.index(path[-1].lower())
         except (ValueError, AttributeError):
            raise LookupError, "%s not found"%(repr(path))
         assert(m.count(path[-1].lower()) == 1)
         del orig_m[i]
         rv = self.repos.request(REPOS_OP_SETCOND, [uform.UForm(uu, {idx:orig_m}), sig])[0]
         if rv == 0:
            break
   
   def removeMember(self,path,member,dimension='members', conn=None):

      if conn:
         raise Exception, "not supported"

      # lower case all nodes
      def lowstr(a):
         if type(a) == type(u''): return a.lower()
         return str(a).lower()
     
      path = map(lowstr, path)
        
      uu = _extenduuid(self.root,path)
     
      while True:
         uf = uform.UForm(uu, [dimension, 'shepherd_signature'])
         uf = self.repos.getAttr(uf)
         v = uf[dimension]
         sig = _canonicalizeSignature(uf['shepherd_signature'])
         try:
            v.remove(member)
         except AttributeError:
            raise "Path %s resulted in an empty collection (%s)"%(repr(path),
                                                                  uu.toString())
         v.sort()
         rv = self.repos.request(REPOS_OP_SETCOND, [uform.UForm(uu, {dimension:v}), sig])[1]
         if rv == 0:
            break

   def addMember(self,path,member,dimension='members', preserve_case=0, conn=None):
      """
      preserve_case keeps the idx attribute contain the original
      case-sensitive strings, but when it comes to generate the uuid
      the lower-case version is used
      """

      if conn:
         raise Exception, "not supported"

      # lower case all nodes
      def lowstr(a):
         if type(a) == type(u''): return a.lower()
         return str(a).lower()

      if preserve_case:
         # keep the original around
         c_path = tuple(path)
      else:
         c_path = None
        
      path = map(lowstr, path)
     
      # ensure that each intermediate node exists
      if not uuid.isa(member) and not type(member) == type('') and not type(member) == type(u''):
         raise "Illegal index member type"

      if path not in self.paths:
         self.paths.append(path)
         for i in range(len(path)):
            ppath = path[:i]
            uu = _extenduuid(self.root,ppath)
            if dimension.lower() == 'members':
               idx = 'idx'
            else:
               idx = 'idx_'+dimension
            while True:
               uf = uform.UForm(uu, [idx, 'roles', 'label', 'name', 'shepherd_signature'])
               uf = self.repos.getAttr(uf)
               ch = uf[idx]
               roles = uf['roles'] or []
               sig = _canonicalizeSignature(uf['shepherd_signature'])
               label = uf['label']
               name = uf['name']
               if ch == None or \
                      (preserve_case and (c_path[i] not in ch)) or \
                      (not preserve_case and (path[i] not in ch)):
                  uf_to_set = uform.UForm(uu)
                  if ch == None:
                     ch=[]
                     # check for valid role and name
                     if self.root not in roles:
                        roles.append(self.root)
                        uf_to_set['roles'] = roles

                     if label == None:
                        uf_to_set['label'] = self.index_name

                     if name == None:
                        uf_to_set['name'] = self.index_name+' - level:'+str(ppath)

                  if preserve_case:
                     chm = c_path[i]
                  else:
                     chm = path[i]
                  ch.append(chm)
                  uf_to_set[idx] = ch
                  rv = self.repos.request(REPOS_OP_SETCOND, [uf_to_set, sig])[1]
                  if rv == 0:
                     break
               else:
                  break

      uu = _extenduuid(self.root,path)
      while True:
         uf_to_set = uform.UForm(uu)
         uf = uform.UForm(uu, [dimension, 'roles', 'shepherd_signature'])
         uf = self.repos.getAttr(uf)
         members = uf[dimension] or []
         sig = _canonicalizeSignature(uf['shepherd_signature'])
         # check for valid role
         roles = uf['roles'] or []
         if role_for_collection not in roles:
            roles.append(role_for_collection)
            uf_to_set['roles'] = roles
         members.append(member)
         uf_to_set[dimension] = members
         rv = self.repos.request(REPOS_OP_SETCOND, [uf_to_set, sig])[1]
         if rv == 0:
            break
     
   def clean(self,path=[],dimension='members', conn=None):

      if conn:
         raise Exception, "not supported"

      # lower case all nodes
      def lowstr(a):
         if type(a) == type(u''): return a.lower()
         return str(a).lower()

      path = map(lowstr, path)
     
      # Removes duplicate nodes, duplicate members, and dead branches, and sorts the lists
      uu = _extenduuid(self.root,path)
      if dimension.lower() == 'members':
         idx = 'idx'
      else:
         idx = 'idx_'+dimension

      while True:
         uf_to_set = uform.UForm(uu)
         uf = uform.UForm(uu, [dimension, idx, 'shepherd_signature'])
         uf = self.repos.getAttr(uf)
         members = uf[dimension] or []
         subnodes = uf[idx]
         sig = _canonicalizeSignature(uf['shepherd_signature'])
         if members:
            members = _uniq(members)
            members.sort()
            uf_to_set[dimension] = members

         if subnodes:
            subnodes = _uniq(subnodes)
            subnodes.sort()

            list = subnodes[:]
            for e in list:
               ppath = path+[e]
               self.clean(ppath,dimension)

               nuu = _extenduuid(self.root,ppath)
              
               uf = uform.UForm(nuu, [idx, dimension])
               uf = self.repos.getAttr(uf)
               nidx = uf[idx]
               nmem = uf[dimension]
              
               if not (nidx or nmem):
                  # prune dead branch
                  del subnodes[subnodes.index(e)]

            uf_to_set[idx] = subnodes

         if uf_to_set:
            rv = self.repos.request(REPOS_OP_SETCOND, [uf_to_set, sig])[1]
            if rv == 0:
               break
         else:
            break

#
######################################################################## 
###########
#

# A generic example depth-first traversal of an index
def example_depth_traverse(repository,index_root,dimension='members'):
   def recursive_helper(index,path,dimension):
     print "Path: ",path
     ch = index.getMembers(path,dimension)
     if ch != None:
       print "Number of Members: ",len(ch)
     re = index.getChildren(path,dimension)
     if re != None:
       for p in re:
         recursive_helper(index,path+[p],dimension)
     return
   hi = HIndexReader(repository,index_root)
   recursive_helper(hi,[],dimension)

## test specific to the "Hotels Index"
def test():
   from MAYA.VIA import repos

   r = repos.Repository('10.10.10.1:8888')
   index_root_uuid = uuid.fromString('~fd000efddada06')

   print "Find hotels in Mackay Australia..."
   hi = HIndexReader(r,index_root_uuid)
   path = ['au', 'mackay']
   print hi.getMembers(path)

   print "Traverse all index and count members at each node..."
   example_depth_traverse(r,index_root_uuid)

## use to test writer
def write_test():
   from MAYA.VIA import repos

   #r = repos.Repository('10.10.10.1:8888')
   r = repos.Repository('kongamato.maya.com:9201')
   root_uid = uuid.UUID()
   print 'root=', root_uid

   hw = HIndexWriter(r, root_uid)
   path = ['3']
   hw.addMember(path, "3b")
   hw.addMember(path, "3a")
   hw.addMember(path, "3a")
   path = ['3','1']
   hw.addMember(path, "3.1b")
   hw.removeMember(path, "3.1b")
   path = ['3','1','1']
   hw.addMember(path, "3.1.1b")
   hw.removeMember(path, "3.1.1b")
   path = ['1','1']
   hw.addMember(path, "1.1b")
   hw.addMember(path, "1.1c")   
   hw.addMember(path, "1.1a")   
   path = ['1','3','1']
   hw.addMember(path, "1.3.1a")
   hw.removeMember(path, "1.3.1a")
   path = ['1','3']
   hw.addMember(path, "1.3a")
   path = ['1','2']
   hw.addMember(path, "1.2b")
   hw.addMember(path, "1.2c")   
   hw.addMember(path, "1.2a")   
   hw.addMember(path, "1.2b")   
   path = ['2', '1']
   hw.addMember(path, "2.1a")
   hw.addMember(path, "2.1c")
   hw.addMember(path, "2.1a")
   hw.addMember(path, "2.1c","dim")
   hw.addMember(path, "2.1c","dim")
   hw.addMember(path, "2.1b","dim")
   path = []
   hw.addMember(path, "0b")
   hw.addMember(path, "0a")
   hw.addMember(path, "0a")
   hw.addMember(path, "0c")
   path = ['1','2','1','1']
   hw.addMember(path, "1.2.1.1b")
   hw.addMember(path, "1.2.1.1a")

def remove_test():
   from MAYA.VIA import repos

   r = repos.Repository('10.10.10.1:8888')
   root_uid = uuid.fromString('~0125355910872211d7a6e620bb0ad86410')

   hi = HIndexReader(r, root_uid)
##   path = ['foo', 'qux']
##   print hi.getMembers(path)
##   
   hw = HIndexWriter(r, root_uid)
##   path = ['foo', 'qux']
##   hw.removeMember(path, "QUX QUX")    
   
if __name__ == '__main__':
   from MAYA.VIA import repos
   r = repos.Repository('joshua.maya.com:8888')
   example_depth_traverse(r,uuid._('~fd000efddada09'))
