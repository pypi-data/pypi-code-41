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

################################################
"""A file based UForm repository

 Jeff Senn -- (C) 2000 MAYA Design Group -- Proprietary
 
"""
import MAYA.datatypes
from MAYA.VIA import vsmf,uuid,uform
try:
    import sha
except: pass
import os,os.path,struct,sys
#
# bsddb stuff no longer depends on py files only on DLL
# You need a not-yet-released version of bsddb
#
try:
  import _bsddb
  _db = _bsddb
except:
  try:
    import _db
  except:
    from bsddb3 import _db

try:
  import thread
  del thread
except ImportError:
  _db.DB_THREAD = 0

DEBUG_FM = 0

class error(Exception): pass
class ACCESS_VIOL(Exception): pass

# note the following is a text uuid even though it doesn't look it
ROOT_UUID = '09728860-e1ef-11d2-917a-0040055663c5'
ROOT_ATTR = 'repos_uform'

PORTAL_ROLE = uuid._('~fd000a0251-0b-fd12f26a82')
REPOS_ROLE =  uuid._('~fd000a0251-0b-fd15095753')

#prefix for file uuids:
FILE_UUID_PREFIX = uuid._('~FD000A02511C')

# for mapped file:
MAPPED_DIRECTORY_ROLE = uuid._('~FD000A0251.0B.30335DF0')
MAPPED_FILE_ROLE =      uuid._('~FD000A0251.0B.36782463')

#
CREDENTIAL_ROLE =        uuid._('~fd000a0251.0b.fd6ab544cc')
ACCESS_CONTROLLED_ROLE = uuid._('~fd000a0251.0b.fd4301b149')
ACL_ROLE =               uuid._('~fd000a0251.0b.fd6ccc319d')

CRED_PASS = 'encrypted_password'
ACL = 'acu_acl'
ACL2 = 'acu_acl_change'
RDACC= 'acu_read'
WRACC= 'acu_write'

#localize symbols
DBNotFoundError = _db.DBNotFoundError
    
# returns eint, len
def read_eint(s,off):
    byte0 = ord(s[off])
    if byte0 < 0xfc:
        return byte0,1
    elif byte0 == 0xfc:
        return struct.unpack(">H",s[off+1:off+3])[0],3
    elif byte0 == 0xfd:
        return struct.unpack(">i",s[off+1:off+5])[0],5
    elif byte0 == 0xfe:
        return struct.unpack(">L",s[off+1:off+9])[0],9
    elif byte0 == 0xff:
        byte1 = ord(s[off+1])
        result = long(0)
        for n in range(0,byte1):
            result = result << 8 | ord(s[off+n+1])
        return result,2+byte1

#ubiquitous helper
def _isseq(a): return type(a) == type([]) or type(a) == type(())
    
class AccessControlledPortal:
    def __init__(self,repos):
      self.r = repos
      u_r = repos.connect(None).uuid
      pu = uuid.UUID()
      repos.setAttr(pu,ROOT_ATTR,u_r)
      repos.setAttr(pu,ACL,u_r)
      repos.setAttr(pu,ACL2,[])
      repos.setAttr(pu,'roles',(ACCESS_CONTROLLED_ROLE, PORTAL_ROLE,))  
      ps = repos.getAttr(u_r,'portals')
      if not _isseq(ps): ps = []
      ps.append(pu)
      repos.setAttr(u_r,"portals",ps)
      self.p = pu
      self.creds = []
    def _check_cred(self,l):
      if l == None: return 1 # no attr is WORLD
      if not _isseq(l): return 0
      for c in self.creds:
        if c in l: return 1
      return 0
    def _check_access2(self,uu,level=0):
      if not uuid.isa(uu): return None
      r = self.r.getAttr(uu,'roles')
      if not _isseq(r) or ACL_ROLE not in r: return 0
      s = RDACC
      if level: s = WRACC
      a = self.r.getAttr(uu,s)
      return self._check_cred(a)
    def _check_access1(self,uu,level=0):
      if level > 1:
        a = self.r.getAttr(uu,ACL2)
        return self._check_cred(a)
      a = self.r.getAttr(uu,ACL)
      if a == None: return 1
      if _isseq(a):
        for k in a:
          if self._check_access2(k,level): return 1
      else:
        return self._check_access2(a,level)
    def _check_access(self,uu,level=0):
      ret = self._check_access1(uu,level)
      ## comment out next 3 lines to restore access control
      if not ret:
        print "FILEREPOS: no access",level,uu.toString()
        ret = 1
      return ret
    
    def flush(self):
      return self.r.flush()
    def authenticate(self,uu,v):
      if uu in self.creds:
        self.creds.remove(uu)
      p = self.r.getAttr(uu,CRED_PASS)
      if isinstance(p,MAYA.datatypes.Binary): p = p.getBuf()
      #passwords are sha encrypted
      if sha.new(v).digest() == p:
        self.creds.append(uu)
        return 1
      return 0
    def connect(self,uu):
      ru = self.r.connect(uu)
      return uform.UForm(self.p)
        
    def getNext(self,uu):
      return self.r.getNext(uu)
    def hasUForm(self,uu):
      return self.r.hasUForm(uu)
    def getAttr(self,uu,a,chunk=None,raw=None):
      if self._check_access(uu):
        return self.r.getAttr(uu,a,chunk,raw)
      raise ACCESS_VIOL, 'no read '+uu.toString()
    def listAttr(self,uu,sha=1):
      if self._check_access(uu):
        return self.r.listAttr(uu,sha)
      raise ACCESS_VIOL, 'no read '+uu.toString()
    def getUForm(self,uu):
      if self._check_access(uu):
        return self.r.getUForm(uu)
      raise ACCESS_VIOL, 'no read '+uu.toString()
    def setAttr(self,uu,a,v,chunk=None):
      level = 1
      if a.lower() == ACL or \
         a.lower() == ACL2: level = 2
      if self._check_access(uu,level):
        if a.lower() == 'roles':
           # add access control if necessary
           # v could be serialized already...sigh
           cv = v
           serialized = isinstance(v,vsmf.serializedvsmf)
           if serialized: cv = vsmf.reconstitute(v.getBuf())
           #if ACCESS_CONTROLLED_ROLE not in cv:
           #  v = [ACCESS_CONTROLLED_ROLE] + cv
        elif not self.r.hasUForm(uu):
            self.r.setAttr(uu,'roles',[ACCESS_CONTROLLED_ROLE])
        return self.r.setAttr(uu,a,v,chunk)
      raise ACCESS_VIOL, 'no write '+uu.toString()
    def setUForm(self,uu,v,merge=0):
      level = 1
      if not merge: level = 2
      else:
        kl = map(lambda a: a.lower(),v.keys())
        if ACL in kl or ACL2 in kl: level = 2
      if self._check_access(uu,level):
        if not merge or v.has_key('roles') or not self.r.hasUForm(uu):
          oldv = v.get('roles',[])
          serialized = isinstance(oldv,vsmf.serializedvsmf)
          cv = oldv
          if serialized: cv = vsmf.reconstitute(oldv.getBuf())          
          #if ACCESS_CONTROLLED_ROLE not in cv:
          #  v['roles'] = [ACCESS_CONTROLLED_ROLE] + cv
        return self.r.setUForm(uu,v,merge)
      raise ACCESS_VIOL, 'no write '+uu.toString()

def util_recover_db_file(oldname,newname):
  def open_src():
    src = _db.DB()
    src.set_flags(0)
    src.open(oldname, _db.DB_BTREE, _db.DB_THREAD + _db.DB_RDONLY , 0666)
    return src
  dst = _db.DB()
  dst.set_flags(0)
  dst.open(newname, _db.DB_BTREE, _db.DB_CREATE + _db.DB_THREAD , 0666)
  bad_uuids = {}
  good_uuids = {}
  good_keys = {}
  num = 0
  print "Phase 1: Copying records..."
  src = None
  last_done = None
  while 1:
    if src == None: 
      print "(Re)opening src..."
      src = open_src()
      c = src.cursor()
      if last_done == None:
        try:
          k = c.first(doff=-1,dlen=-1)
        except DBNotFoundError: break
      else:
        try:
          k = c.set_range(last_done,doff=-1,dlen=-1)
        except DBNotFoundError: break
    if good_keys.has_key(k[0]):
      print "Duplicate(not copied):",uuid.UUID(k[0][1:ord(k[0][0])+1]).toString(),k[0][ord(k[0][0])+1:]
    else:
      uu = k[0][1:ord(k[0][0])+1]
      if not good_uuids.has_key(uu): good_uuids[uu] = None
      dst[k[0]] = k[1] 
      good_keys[k[0]] = (k[0],k[1],num)
      num += 1
    try:
      k = c.next(flags=0,doff=-1,dlen=-1)
    except DBNotFoundError: break
    if k == None: break
  print "Phase 1: Copied",num,"records in",len(good_uuids),"u-forms."
  print "Done."


class Repository:
    def __init__(self,filename,create=1,readonly=0,lock=None):
        self.mapped_roles = None #for compatibility with FileMappedRepository
        self.venue = None        #for compatibility with FileMappedRepository
        access = _db.DB_CREATE + _db.DB_THREAD 
        if readonly: access = _db.DB_RDONLY + _db.DB_THREAD 
        self.lock = lock
        exists = os.path.isfile(filename)
        if  exists and os.stat(filename)[6] < 1 and not readonly:
            self.warning("FileStore Warning: empty file, deleting...")
            os.remove(filename)
            exists = 0
        if readonly and not exists:
            raise "file empty or non-existent"
        ## ensure exclusive access
        if not readonly:
          try:
            lfnam = filename+".lock"
            if os.path.isfile(lfnam): os.remove(lfnam)
            self.r_lock = os.open(lfnam,os.O_EXCL + os.O_CREAT + os.O_WRONLY)
          except:
            raise "could not open lock file for exclusive access"
        else: self.r_lock = None
        self.r = None
        try:
          d = _db.DB()
          d.set_flags(0)
          d.open(filename, _db.DB_BTREE, access, 0666)
          self.r = d
        except: pass
        if self.r == None:
          raise error,"no known database file method works"

        #lately moved from connect to here...
        ru = uuid._(ROOT_UUID)
        self.repos_uform = self.getAttr(ru, ROOT_ATTR)
        if not self.repos_uform and not readonly:
          r = uuid.UUID()
          self.setAttr(ru, ROOT_ATTR,r)
          self.setAttr(ru, ACL, r)
          self.setAttr(ru, ACL2, [])
          self.setAttr(r,ROOT_ATTR,r)
          self.setAttr(r, ACL, r)
          self.setAttr(ru, ACL2, [])                    
          self.setAttr(r, WRACC, [])
          self.setAttr(r, 'roles',(ACCESS_CONTROLLED_ROLE,ACL_ROLE,REPOS_ROLE))
          self.repos_uform = r
        if self.repos_uform and not readonly:
          try:
            prs = self.getAttr(self.repos_uform,'portals')
            if _isseq(prs): map(lambda u: self.setUForm(u,None),prs)
          except:
            print "Error removing old portals"
          self.setAttr(self.repos_uform,'portals',[])    

    def connect(self,uf):
      if self.repos_uform:
        return uform.UForm(self.repos_uform)
      else:
        raise "Cannot connect. Repository has no root uform"  
    
    def warning(self,w):
        print w
        
    def __del__(self):
        self.flush()
        if self.lock: self.lock.acquire()
        try:
          self.r.close()
          self.r = None
        finally:
          if self.lock: self.lock.release()
          if self.r_lock: os.close(self.r_lock)

    def flush(self):
      try:
        if self.r:
          if self.lock: self.lock.acquire()
          try:
            try:          
              self.r.sync()
            except:
              print "FILEREPOS: Ignoring weird flush/sync error!"
          finally:
            if self.lock: self.lock.release()
      except:
        print "Filerepos: DB Flushed failed. (hopefully it will work next time)"
          
    def _deserialize(self, v):
        try:
          r = vsmf.reconstitute(v)
        except:
          print "Error fetching",repr(v)
          raise error,"VSMF intern failed"
        return r
    def _serialize(self, v):
        return vsmf.serialize(v)
        
    def _key(self, uu, attr=''):
      if uuid.isa(uu):
        u = uu.getBuf()
      elif type(uu) == type(''):
        u = uu
      else:
        raise error, "suspicious key type: "+str(type(uu))+" "+repr(uu)
      a = attr.lower()
      return chr(len(u))+u+a

    # op 0=list, 1=list/sha, 2=getuform, 3=remove_some, 4=uform_exists
    def _forAttr(self,uu,op,uf=None):
          k = self._key(uu,'')
          if uf == None and op != 4: uf = uform.UForm(uu)
          kl = len(k)
          darg = 0
          if op > 0 and op < 3: darg = -1
          c = self.r.cursor()
          #NOTE: Jeff has modified _db.pyd so that this will work!
          try:
            k2 = c.set_range(k,dlen=darg,doff=darg)
            if k2 != None:
              k2,v = k2
          except DBNotFoundError: #off end of database keys
            k2 = None
            v = None
          while 1:
            if k2 == None or k != k2[:kl]: break
            if op==4:
              uf = 1
              break
            a = k2[kl:]
            a = a.decode('utf8')
            try: a = str(a)
            except: pass
            if op==1:
              uf[a] = [MAYA.datatypes.Binary(sha.new(v).digest()),len(v)]
            elif op==2:
              uf[a] = self._deserialize(v)
            elif op==3:
                ok2 = k2
                try:
                  k2 = c.next(flags=0,dlen=darg,doff=darg)
                except DBNotFoundError:
                    del self.r[ok2]
                    break
                if k2 != None:
                  k2,v = k2
                del self.r[ok2]
                continue
            else:
              uf[a] = None
            try:
              k2 = c.next(flags=0,dlen=darg,doff=darg)
              if k2 != None:
                k2,v = k2
            except DBNotFoundError:
              k2 = None
          del(c)
          return uf
    
    def getNext(self,uu):
        self.flush()
        if uu == None:
          pass
        elif uuid.isa(uu):
          uu = uu.getBuf()
        elif uform.isa(uu):
          uu = uu.uuid.getBuf()
        if self.lock: self.lock.acquire()
        try:
          if uu == None:
            c = self.r.cursor()
            try:
              ret = c.first(doff=0,dlen=0)[0]
            except DBNotFoundError: return None
            del c
            return uuid.UUID(ret[1:ord(ret[0])+1])
          else:
            c = self.r.cursor()
            # Note: the previous implementation suffered from the fact
            # that corrupted db files could have duplicates in the btree
            # (I've demonstrated that...:-( )  so this version has to
            # seek to the current key and the step forward through the records
            # until it finds a key that is > than the current...
            initial_key = self._key(uu,'')
            try:
              k = c.set_range(initial_key,doff=0,dlen=0)[0]
            except DBNotFoundError: return None
            while k== None or k[0:len(initial_key)] <= initial_key:
              try:
                k = c.next(flags=0,doff=0,dlen=0)
                if k == None: return None
                k = k[0]
              except DBNotFoundError: return None
            del c
            return uuid.UUID(k[1:ord(k[0])+1])                      
        finally:
          if self.lock: self.lock.release()          

    def hasUForm(self,uu):
      if self.lock: self.lock.acquire()
      try:
        return self._forAttr(uu,4)
      finally: 
        if self.lock: self.lock.release()
        
    #chunk = (start, end)  
    def getAttr(self,uu,a,chunk=None,raw=None):
        if a == '': return self.listAttr(uu,0).keys()
        if type(a) == type(u''): a = a.encode('utf8')        
        k = self._key(uu,a)
        if self.lock: self.lock.acquire()
        try:
         if chunk:
          #fetch type and record size
          try:
            v = self.r.get(k,doff=0,dlen=200)
          except DBNotFoundError:
            return None
          if raw:
            s,e = chunk
            if e >= s:
              e = e - s + 1
            else:
              raise error, "invalid chunk"
            try:
              v = self.r.get(k,doff=s,dlen=e+1)
            except:
              v = None
            return v
          else:
            # chunk only support binary/string/mime at the moment
            # and the mime support is a little wierd -- chunks act only
            # on the mime value and that value reads as type 'binary'
            t = v[0]
            if t == vsmf.TC_MIME:
                t = vsmf.TC_BINARY
                l,el = read_eint(v,1)
                l2,el2 = read_eint(v,el+1)
                o = 1+el+el2+l2
            elif t == vsmf.TC_STRING or t == vsmf.TC_BINARY:
                l,el = read_eint(v,1)
                o = 1+el
            else:
                raise error, "not a chunkable type"
            s,e = chunk
            if e >= s:
              e = e - s
            else:
              raise error, "invalid chunk"
            v = self.r.get(k,doff=s+o,dlen=e+1)
            return t + vsmf.writeEint(len(v)) + v
         else:
          v = None
          try:
            v = self.r[k]
          except KeyError:
            return None
          if v == None: return None
          if raw != None: return vsmf.serializedvsmf(v)
          return self._deserialize(v)
        finally:
          if self.lock: self.lock.release()                

    def listAttr(self,uu,sha=1):
        if sha: op = 1
        else: op = 0
        if self.lock: self.lock.acquire()
        try:
          return self._forAttr(uu,op)
        finally:
          if self.lock: self.lock.release()                
    
    def getUForm(self,uu):
        if self.lock: self.lock.acquire()
        try:
          return self._forAttr(uu,2)
        finally:
          if self.lock: self.lock.release()
        
    def setAttr(self,uu,a,v,chunk=None):
        a = a.lower()
        if type(a) == type(u''): a = a.encode('utf8')        
        k = self._key(uu,a)
        if a == '': raise error, "not implemented"
        if self.lock: self.lock.acquire()
        try:
         if chunk:
          #fetch type and record size
          try:
            ev = self.r.db.get(k,doff=0,dlen=200)
          except DBNotFoundError:
            ev = None
          e,s = chunk
          if e >= s:
              e = e - s
          else:
              raise error, "invalid chunk"
          raise error, "not-yet-implemented"
          if ev == None: #initialize record
            if type(v) == type(''):
              ev = self._serialize('')  
            elif isinstance(v,MAYA.datatypes.Binary):
              ev = self._serialize(vmsf.binary(''))                  
            self.r[k] = ev
            todo()
         else:
          if v == None:
            try:
              del self.r[k]
            except DBNotFoundError: pass
          else:
            self.r[k] = self._serialize(v)
        finally:
          if self.lock: self.lock.release()            
        return 0

    def setUForm(self,uu,v,merge=0):
        if self.lock: self.lock.acquire()
        try:
          if not merge: #delete everything first
            self._forAttr(uu,3,None)
        finally:
          if self.lock: self.lock.release()                        
        if v != None:
          for k in v.keys():
            self.setAttr(uu,k,v[k])
        return 0

# This version has additional support for mapping files in the
# file system to attributes.
#
# The repository u-form have UUIDs of the form:
#  FILE_UUID_PREFIX 20-byte-sha-hashed-file-path venue-id

# The repository u-form has these attributes:
#  mapped_roles:  { role : { attr : mapping, ...}, ...}
#  mapped_venues: { other_venue: [root,in,this,venue] }
#  mapped_extensions: { file_extension : role(s), ... }
#
# Any mapped uforms must have the attributes:
#  mapped_filename: [components,of,directory,path,and,filename]
#  roles: [...some_role_from_mapped_roles...]

class FileMappedRepository(Repository):
    def connect(self,uf):
        self.mapped_roles = None
        ret = Repository.connect(self,uf)
        self.venue = ret.uuid
        self._load_mapping()
        return ret

    def _load_mapping(self):
        self.mapped_roles = Repository.getAttr(self,self.venue,'mapped_roles')
        self.mapped_venues = Repository.getAttr(self,self.venue,'mapped_venues')
        self.mapped_extensions = Repository.getAttr(self,self.venue,'mapped_extensions')
        self.mime_file_mapping = Repository.getAttr(self,self.venue,'mime_file_mapping')
        
    #returns file_path of mapped file (None if not mapped)
    def _file_path(self,uu):
        if not self.mapped_roles: return None
        if uuid.isa(uu): uu = uu.getBuf()
        if uu[0:6] != FILE_UUID_PREFIX.getBuf(): return None
        vid = uu[26:]
        if vid == self.venue.getBuf():
           return Repository.getAttr(self,uu,'mapped_file')
        elif self.mapped_venues:
           prefix = self.mapped_venues.get(uuid.UUID(vid).toString())
           if prefix:
             v = Repository.getAttr(self,uu,'mapped_file')
             if _isseq(v):
               return prefix + v
        return None

    def _file_attrs(self,uu,attr=None):
        roles = Repository.getAttr(self,uu,'roles')
        ret = []
        if uuid.isa(uu): uu = uu.getBuf()
        if roles:
         for r in roles:
          if not uuid.isa(r): continue
          x = self.mapped_roles.get(r.toString())
          #print "MR: role is mapped",x,self.mapped_roles
          if x:
            if attr == None:
               for k in x.keys():
                 v = x[k]
                 if (v == 'names' or v == 'members') and not uu[26:] == self.venue.getBuf():
                   #print "MR:Passing on non-matching venue"
                   pass
                 else:
                   ret.append((k,v))

            else:
               if x.has_key(attr):
                 v = x[attr]                 
                 #if venues don't match then handle members/name specially
                 if (v == 'names' or v == 'members') and not uu[26:] == self.venue.getBuf():
                   #print "MR:Passing on non-matching venue"                     
                   pass
                 else:
                   ret.append(v)
        #print "MR: file attrs",repr(uu),attr,ret
        return ret

    def _path_to_uuid(self,p):
        s = sha.new(self._serialize(p)).digest()
        return uuid.UUID(FILE_UUID_PREFIX.getBuf() + s + self.venue.getBuf())
    
    def _file_attr(self,path,attr,chunk=None):
        fn = self._path_to_file(path)
        if DEBUG_FM: print "FMR: file attr",fn,attr
        isdir = os.path.isdir(fn)
        if attr == 'members' and isdir:
           names = map(lambda b,a=path: a+[b], os.listdir(fn))            
           uus = map(self._path_to_uuid,names)
           map(self._map_file,uus,names)
           return uus
        elif attr == 'names' and isdir:
           names = map(lambda b,a=path: a+[b], os.listdir(fn))
           return names
        elif attr == 'content':
           if os.path.isfile(fn):
             v = open(fn,'rb').read()
             # process mime extension
             if type(self.mime_file_mapping) == type({}):
               ext = os.path.splitext(fn)[1]
               mt = self.mime_file_mapping.get(ext)
               if mt: v = vsmf.mimeVal(mt,v)
             return v
        return None

    def _ensure_file(self,fn):
        if os.path.isfile(fn): return
        d = os.path.dirname(fn)
        if os.path.isdir(d): return
        os.makedirs(d)

    def _file_set_attr(self,path,attr,v,chunk=None):
        # make sure the file exists
        fn = self._path_to_file(path)
        if DEBUG_FM: print "FMR: file set attr",fn,attr        
        if attr == 'content':
           self._ensure_file(fn)
           if hasattr(v,'getBuf'): v = v.getBuf()
           open(fn,'wb').write(v) 
           return 0
        elif attr == 'names':
           return -1
        return -1

    def _path_to_file(self,path):
        if os.sep == '\\':
           return path[0]+":\\"+os.sep.join(path[1:])
        else:
           return os.sep+os.sep.join(path)
       
    def _map_file(self,uu,name):
        # skip if already mapped
        fp = Repository.getAttr(self,uu,'mapped_file')
        rl = Repository.getAttr(self,uu,'roles')
        if rl == None: rl = []
        if fp == None:
          # map file
          Repository.setAttr(self,uu,'mapped_file',name)
          # set appropriate roles
          fn = self._path_to_file(name)
          isdir = os.path.isdir(fn)
          if isdir:
            rl.append(MAPPED_DIRECTORY_ROLE)
          else:
            ext = os.path.splitext(fn)[1].lower()
            nrl = None
            if type(self.mapped_extensions) == type({}):
              nrl = self.mapped_extensions.get(ext)
            if nrl != None:
              if _isseq(nrl):
                rl.extend(nrl)
              else:
                rl.append(nrl)
            else:
              rl.append(MAPPED_FILE_ROLE)
          Repository.setAttr(self,uu,'roles',rl)
       
    def getAttr(self,uu,a,chunk=None,raw=None):
        x = self._file_path(uu)
        if x:
          if DEBUG_FM: print "FMR: is mapped",x
          aa = self._file_attrs(uu,a)
          if len(aa) > 0:
            if DEBUG_FM: print "FMR: attrs",a,aa
            ret = self._file_attr(x,aa[0])
            if DEBUG_FM: print "FMR: val",repr(ret)[0:100],"..."
            if raw: ret = vsmf.serializedvsmf(self._serialize(ret))
            return ret
        return Repository.getAttr(self,uu,a,chunk,raw)

    # op 0=list, 1=list/sha, 2=getuform, 3=remove all/set, 4=set-merge
    def _forxattr(self,uu,op,uf):
        x = self._file_path(uu)
        if x:
          aa = self._file_attrs(uu)
          for a1,a2 in aa:
            v = self._file_attr(x,a2)
            if op == 0:
              uf[a1] = None
            elif op == 1:
              v = self._serialize(v)
              uf[a1] = [MAYA.datatypes.Binary(sha.new(v).digest()),len(v)]
            elif op == 2:
              uf[a] = v
            elif op == 3:
              v = uf.get(a1)
              self._file_set_attr(x,a2,v)
              if uf.has_key(a1):
                del uf[a1]
            elif op == 4:
              if uf.has_key(a1):
                v = uf.get(a1)
                self._file_set_attr(x,a2,v)
                del uf[a1]                

    def listAttr(self,uu,sha=1):
        ret = Repository.listAttr(self,uu,sha)
        if sha:
          self._forxattr(uu,1,ret)
        else:
          self._forxattr(uu,0,ret)            
        return ret
    
    def getUForm(self,uu):
        ret = Repository.getUForm(self,uu)
        self._forxattr(uu,2,ret)        
        return ret
        
    def setAttr(self,uu,a,v,chunk=None):
        a = a.lower()
        x = self._file_path(uu)
        if x:
          aa = self._file_attrs(uu,a)
          if len(aa) > 0:
            return self._file_set_attr(x,aa[0],v,chunk)
        elif uu == self.venue:
          #print "MR: reloading mapping"
          if a == 'mapped_roles' or a == 'mapped_venues' or a == 'mapped_extensions' or a == 'mime_file_mapping':
            self._load_mapping()
        ret = Repository.setAttr(self,uu,a,v,chunk)
        if a == 'mapped_file' and not x:
          #move any special attrs from DB to file
          x = self._file_path(uu)
          if x:
            aa = self._file_attrs(uu)
            for a in aa:
              if DEBUG_FM: print "FMR: moving attr",repr(uu),a
              v = Repository.getAttr(self,uu,a)
              if v != None:
                Repository.setAttr(self,uu,a,None)
                self._file_set_attr(x,a,v)
        return ret

    def setUForm(self,uu,uf,merge=0):
        uf2 = {}
        if uform.isa(uf) and hasattr(uf,'eform'): uf = uf.eform
        if uf != None:
         uf2.update(uf)
         #set mapped_file attr first!
         mf = uf.get('mapped_file')
         if mf:
          if not merge:
            Repository.setUForm(self,uu,{}) #delete the old one
          Repository.setAttr(self,uu,'mapped_file',mf)
          if merge:
            pass
            #technically here we should do something smart if merge!=0
        op = 3
        if merge: op = 4
        self._forxattr(uu,op,uf2)
        return Repository.setUForm(self,uu,uf2,merge)
