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



###############################################################################
#
###############################################################################
version='$Revision: 117844 $'.split()[1].split('.')

from MAYA.VIA import vsmf
import types
import operator
import socket
import time # only for waitForPresence
from struct import pack,unpack
#from string import *
from MAYA.VIA import uuid
from MAYA.VIA import uform


# Anukul and Slim's python repository library
#
# todo:
#  comprehensible exceptions
#  notification model (threads? polling? both!)
#  chunking
#  multiple operations in one request (batch mode with commit/flush?)
#  some sort streaming model so everything doesn't have to go through RAM


###############################################################################
#
###############################################################################
# repository constants
# unabashedly stolen from maya/include/MRP_Services.h
INVALID             = 0;
CONNECT             = 1;
DISCONNECT          = 2;
GETUFORM            = 3;
SETUFORM            = 4;
FORGETUFORM         = 5;
LISTATTR            = 6;
GETATTR             = 8;
SETATTR             = 9;
REMOVEATTR          = 110;
CHUNK_SELECT        = 10;
CHUNK_DELETE        = 11;
CHUNK_REPLACE       = 12;
CHUNK_INSERTAFTER   = 13;
CHUNK_INSERTBEFORE  = 14;
CHUNK_SPLIT         = 15;
CHUNK_COUNT         = 16;
CHUNK_LOC           = 17;
CHUNK_LENGTH        = 18;
QUERY		        = 117;
SETATTR_COND        = 119;
GETLOCALID          = 201;
GETUUID             = 202;
APPENDATTR          = 209;
APPENDATTR_COND     = 219;
UFORMKNOWN          = 301;
REGISTER_NOTIFY     = 21;
NOTIFY_AND_GETUFORM = 121;
NOTIFY_AND_GETATTR  = 122;
CANCEL_NOTIFY       = 22;
NOTIFY              = 23;
GETNEXT             = 31;
FLUSH               = 1001;
LOCKUFORM           = 2001;
UNLOCKUFORM         = 2002;
GETATTR_PART        = 210;
SETATTR_PART        = 212;

MAYA_REPOS_REQUIRED      =   0x1;
MAYA_REPOS_WRITEABLE     =   0x2;
MAYA_REPOS_SEARCHABLE    =   0x4;
MAYA_REPOS_SHORT_REPLY   =   0x8;
MAYA_REPOS_EXTENDED_LIST =  0x10;
MAYA_REPOS_PARTIAL_VALUE =  0x20;
MAYA_REPOS_COLLECTION    =  0x40;
MAYA_REPOS_RELATION_SRCH =  0x80;
MAYA_REPOS_SHAREABLE     = 0x100;
MAYA_REPOS_AGG_SHAREABLE = 0x200;

DEFAULT_HOST = "pegasus.maya.com"
DEFAULT_PORT = 6200
DEFAULT_SSLPORT = 6243

# util functions

reqid = 1





###############################################################################
#
###############################################################################
def isValidChunkSelector(selector):
    
    if type(selector) in (type(()), type([])):
        if type(selector[0]) in (type([]), type(())):
            # Assuming that if the first item is a tuple/list, then
            # all the items are.
            # So we make sure all the selectors within are valid
            
            return not filter(lambda i: i == 0, map(isValidChunkSelector, selector))
        else:

            return (type(selector[0]) in (type(1), type(1L))) and \
                   (type(selector[1]) in (type(1), type(1L))) and \
                   (type(selector[2]) in (type(""), type(u""))) and \
                   (type(selector[3]) == type(1))
    else:

        return 0
    
def request(opcode):
    global reqid
    ri = reqid
    reqid = reqid + 1
    return [ri,0,opcode]


# this is a lame crutch so I can use strings, uuid.UUIDs, and UForms
# in all the repository functions

def makeUForm(uf):
    if uform.isa(uf):
        
        return uf
    elif uuid.isa(uf) or type(uf) == type(""):
        return uform.UForm(uf)
    else:
        
        raise Exception("RepositoryError: (%s) invalid UForm or uuid"%(repr(uf)))


def makeUUID(uu):
    if uuid.isa(uu):
        
        return uu
    elif uform.isa(uu):

        return uu.uuid
    elif type(uu) in (type(""), type(u"")):
        
        return uuid.fromString(uu)
    else:
        
        raise Exception("RepositoryError: [%s] invalid uuid"%(repr(uu)))


def deepGetAttr(repos, uf):
    """
    ex) uf = {"members" : {"name" : ""} }
    """
    
    # temporarily store the attribute which we need to recursively grab
    tmp_fmt = filter(lambda i: type(i[1]) == type({}) , uf.eform.items())
    uf = repos.getAttr(uf)
    # now uf should have its relation fields filled with
    # a relation, multiple relations, or None. We iterate through
    # and recurse for those relations
    for attr, fmt in tmp_fmt:
        uus = uf[attr]
        
        if type(uus) == type([]):
            # we have more than one relations
            for i in range(len(uus)):
                assert(uuid.isa(uus[i]))
                uus[i] = deepGetAttr(repos, uform.UForm(uus[i], fmt))
            uf[attr] = uus
                
        elif uuid.isa(uus):
            # we have one relation
            uf[attr] = deepGetAttr(repos, uform.UForm(uus, fmt))
        else:
            uf[attr] = None

    return uf          




###############################################################################
#
###############################################################################
class RepositoryArgumentOfWrongTypeError:
    pass

class TimeoutError(RuntimeError):
    pass

#
# you can either initiate the repository with the batch flag
# or you can enable batch mode by calling .setBatchMode(1)
# and you can disable batch mode by calling .setBatchMode(0)
# you'll have to call .commit() at the end if you want the batch
# request to be sent to the repository
#
class Repository:
    def __init__(self,hostport=DEFAULT_HOST+":"+str(DEFAULT_PORT),authUF=None,connection=None,batch=0,ssl_conn=False):
        self.parseForms = 1

        if connection==None:
            try:
                host,port = hostport.split(':')
            except ValueError:

                raise Exception("%s is an invalid repository connection string"%(hostport))
            # -----------------------------------------------------------------
            else:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if ssl_conn:
                    import ssl
                    #self.s = ssl.create_default_context().wrap_socket(self.s)
                    self.s = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(self.s)

                self.s.connect((host,int(port))) # bug fix for python 1.6
        else:
            self.s=connection

        self._hostport = hostport
        self._batch=batch
        self._req_arr=[] # opcode, uform sequence
        self._resp_arr=[] # an het-array of function or (function,arg1,arg2,argN)

        if not uform.isa(authUF):
            authUF = None

        self.portal = self.authenticate(authUF)

        if self._batch:
            self.commit()

    def fileno(self):
        return self.s.fileno()

    def disconnect(self):
        
        self.s.close()
        
    def setParseForms(self,p):
        self.parseForms = p

    def setBatchMode(self,batch): # 1 to batch, 0 to disable batch
        if len(self._req_arr) > 0:

            raise Exception("cannot change batch mode while there are pending requests")
        else:
            self._batch=batch

            if not batch:
                self._req_arr=[]
                self._resp_arr=[]
    
    # returns the string of the form <hostname>:<port_number> that specifies
    # the network location of the repository server
                
    def getHostAndPort(self):
        return self._hostport

    def commit(self, retain_order=0):

        try:
            req_id = 0
            response = []
            
            for req in self._req_arr:
                new_req = [req_id, 0] + req
                self.send(new_req)
                req_id = req_id + 1
                
                # response = [ None ] * 3
                
            
            num_reqs = req_id
            resps = []
            for i in range(num_reqs):
                resps.append(self.recv())

            if retain_order:
                resps.sort()
            
            for i in range(num_reqs):
                resp = resps[i]
                req_id = resp[0]
                resp = resp[1:]
                func_pt = self._resp_arr[req_id]
                
                if type(func_pt) == type(()):
                    arg = func_pt[1]
                    func_pt = func_pt[0]
                    response.append(func_pt(resp[1:], arg))
                    # response[req_id] = func_pt(resp[1:], arg)
                else:
                    response.append(func_pt(resp[1:]))
                    # response[req_id] = func_pt(resp[1:])

            return response

        finally:
            self._req_arr=[]
            self._resp_arr=[]

    def send(self,req):
        vsmfreq = vsmf.serialize(req)
        self.s.send(pack(">i",len(vsmfreq)) + vsmfreq)

    def recv(self):
        data = ""
        while(len(data) < 4):
            s = self.s.recv(4-len(data))
            if s == None or len(s) == 0: raise Exception("closed connection")
            data += s
            
        length = unpack(">i",data)[0]
        data = ""
        while(length - len(data) > 0):
            s = self.s.recv(length-len(data))
            if s == None or len(s) == 0: raise Exception("closed connection")
            data += s

        return vsmf.reconstitute(data,parseForms=self.parseForms)

    def request(self, opcode, args):            
        req = [opcode] + args

        if self._batch:
            self._req_arr.append(req)
            #self._req_arr=self._req_arr+[opcode]+args
            
            return 1 #batch successful
        else:
            # this relies on the short form of repository requests
            self.send(req)
            resp = self.recv()
            
            return resp[1:] # sending the result, succescode

    def authenticateFormatResult(self,resp):

        return resp[0]
    
    def authenticate(self,authUF=None):
        if authUF==None:
            authUF = uform.UForm()
            
        resp= self.request(CONNECT,[authUF])
        
        if self._batch:
            self._resp_arr.append(self.authenticateFormatResult)
            
            return resp
        else:
            
            return self.authenticateFormatResult(resp)

    def authenticateWithReturnCodeFormatResult(self,resp):
        
        return resp
    
    def authenticateWithReturnCode(self,authUF=None):
        if not authUF:
            authUF = uform.UForm()
            
        resp= self.request(CONNECT,[authUF])
        
        if self._batch:
            self._resp_arr.append(authenticateWithReturnCodeFormatResult)
            
            return resp
        else:
            
            return self.authenticateWithReturnCodeFormatResult(resp)

    def flush(self):
        resp = self.request(FLUSH,[])
        
        return resp[0] #I'm not sure what it should return
        
    def queryFormatResult(self,resp):
        
        return resp[0]
   
    def query(self,uf):
        
	uf=makeUForm(uf)
        resp = self.request(QUERY,[uf])
        
        if self._batch:
            self._resp_arr.append(self.queryFormatResult)
            
            return resp
        else:
            
            return self.queryFormatResult(resp)

    def getUFormFormatResult(self,resp):
        
        return resp[0]
    
    def getUForm(self, uf):
        '''This takes a UUID, String, or UForm and returns a UForm'''
        uf = makeUForm(uf)
        resp=self.request(GETUFORM,[uf])
        
        if self._batch:
            self._resp_arr.append(self.getUFormFormatResult)
            
            return resp
        else:
            
            return self.getUFormFormatResult(resp)

    def setUFormFormatResult(self,resp):
        return resp[1]

    def newUFormFormatResult(self,resp):
        if resp[1] == 0: return 0, resp[0].uuid
        return resp[1], None
    
    def setUForm(self, uf):
        '''This takes a UForm and returns an int'''
        resp=self.request(SETUFORM,[uf])
        if self._batch:
            self._resp_arr.append(self.setUFormFormatResult)
            return resp
        else:
            return self.setUFormFormatResult(resp)

    def newUForm(self, ef):
        '''This takes a EForm and returns status, uuid'''
        resp=self.request(SETUFORM,[ef])
        if self._batch:
            self._resp_arr.append(self.newUFormFormatResult)
            return resp
        else:
            return self.newUFormFormatResult(resp)

    # returns True if a uform with this UUID is in this repository,
    # False otherwise
    # Unlike listAttr() and getAttr(), does not trigger a shepherding operation

    def knowsFormatResult(self, resp):
        return resp[1] == 0

    def knows(self, uf):
	uf = makeUForm(uf)
        resp = self.request(UFORMKNOWN, [uf])
        if self._batch:
            self._resp_arr.append(self.knowsFormatResult)
            return resp
        else:
            return self.knowsFormatResult(resp)

    def listAttrFormatResult(self,resp):
        result=resp[0]
        if result:
            return result.keys()
        else:
            return []
        
    def listAttr(self, uf):
        uf = makeUForm(uf)
        resp = self.request(LISTATTR,[uf])
        if self._batch:
            self._resp_arr.append(self.listAttrFormatResult)
            return resp
        else:
            return self.listAttrFormatResult(resp)

    def listAttrInfoFormatResult(self,resp):
        return resp[0]
        
    def listAttrInfo(self, uf):
        uf = makeUForm(uf)
        resp = self.request(LISTATTR, [uf])
        
        if self._batch:
            self._resp_arr.append(self.listAttrInfoFormatResult)
            
            return resp
        else:
            
            return self.listAttrInfoFormatResult(resp)
        
    def getAttrFormatResult(self,resp,attr):
        if attr:
            return resp[0][attr]
        else:
            return resp[0]
        
    def getAttr(self, uf, attr=""):
        uf = makeUForm(uf)
        if attr:
            uf[attr] = None
        resp=self.request(GETATTR, [uf])
        if self._batch:
            self._resp_arr.append((self.getAttrFormatResult,attr))
            return resp
        else:
            return self.getAttrFormatResult(resp,attr)

    def getName(self, uf):
        uf = makeUForm(uf)
        return self.getAttr(uf, 'name') or self.getAttr(uf, 'label') or uf.uuid.getBuf()

    def setAttrFormatResult(self,resp):
        return resp[1]

    def setAttr(self, uf, attr="", val=None, append=False):
        uf = makeUForm(uf)
        if attr:
            uf[attr] = val
        if append:
            op = APPENDATTR
        else:
            op = SETATTR
        resp = self.request(op, [uf])
        if self._batch:
            self._resp_arr.append(self.setAttrFormatResult)
            return resp
        else:
            return self.setAttrFormatResult(resp)

    def setAttrCond(self, uf, attr="", val=None, cksum=None, append=False):
        uf = makeUForm(uf)
        if attr:
            uf[attr] = val
        if append:
            op = APPENDATTR_COND
        else:
            op = SETATTR_COND            
        resp = self.request(op, [uf, cksum])
        if self._batch:
            self._resp_arr.append(self.setAttrFormatResult)
            return resp
        else:
            return self.setAttrFormatResult(resp)                

    def removeAttrFormatResult(self,resp):
        return resp[1]
    
    def removeAttr(self,uf,attr=""):
        uf = makeUForm(uf)
        if attr:
            uf[attr] = None
        resp=self.request(REMOVEATTR, [uf])
        if self._batch:
            self._resp_arr.append(self.removeAttrFormatResult)
            return resp
        else:
            return self.removeAttrFormatResult(resp)




    ###########################################################################
    # chunk ops
    def chunkDefaultFormatResult(self, resp):
        return resp[2]
    
    def chunkSelect(self, uu, attr, selectors):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_SELECT, [uu, attr, selectors])
        
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            
            return resp
        else:
            
            return self.chunkDefaultFormatResult(resp)

    def chunkDelete(self, uu, attr, selectors):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_DELETE, [uu, attr, selectors])
        
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)

    def chunkSplit(self, uu, attr, selectors):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_SPLIT, [uu, attr, selectors])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)

    def chunkCount(self, uu, attr, selectors):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_COUNT, [uu, attr, selectors])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)

    def chunkLocation(self, uu, attr, selectors):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_LOC, [uu, attr, selectors])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)

    def chunkLength(self, uu, attr, selectors):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_LENGTH, [uu, attr, selectors])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)


    def chunkReplace(self, uu, attr, selectors, chunk):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_REPLACE, [uu, attr, [selectors, chunk]])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)

    def chunkInsertAfter(self, uu, attr, selectors, chunk):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_INSERTAFTER, [uu, attr, [selectors, chunk]])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)

    def chunkInsertBefore(self, uu, attr, selectors, chunk):
        assert(isValidChunkSelector(selectors))
        
        uu = makeUUID(uu)
        resp = self.request(CHUNK_INSERTBEFORE, [uu, attr, [selectors, chunk]])
        if self._batch:
            self._resp_arr.append(self.chunkDefaultFormatResult)
            return resp
        else:
            return self.chunkDefaultFormatResult(resp)        
    #
    ###########################################################################





    def lockFormatResult(self,resp):
        return resp[1]

    def lockUForm(self, uf):
        uf = makeUForm(uf)
        resp = self.request(LOCKUFORM, [uf])
        if self._batch:
            self._resp_arr.append(self.lockFormatResult)
            return resp
        else:
            return self.lockFormatResult(resp)

    def unlockUForm(self, uf):
        uf = makeUForm(uf)
        resp = self.request(UNLOCKUFORM, [uf])
        if self._batch:
            self._resp_arr.append(self.lockFormatResult)
            return resp
        else:
            return self.lockFormatResult(resp)

    def nextUFormFormatResult(self,resp):
        if resp[1] != 0:
            return None
        else:
            return resp[0].uuid

    # alias for nextUForm
    def getNext(self,uf=''):
        return self.nextUForm(uf)

    def nextUForm(self,uf=''):
        if not uf:
            uf = uform.UForm()
            uf.uuid.setBuf("")
        else:
            uf = makeUForm(uf)
        resp=self.request(GETNEXT, [uf])
        if self._batch:
            self._resp_arr.append(self.nextUFormFormatResult)
            return resp
        else:
            return self.nextUFormFormatResult(resp)

    def forgetUFormFormatResult(self,resp):
        return resp[0]
    
    def forgetUForm(self,uf):
        uf = makeUForm(uf)
        resp=self.request(FORGETUFORM, [uf])
        if self._batch:
            self._resp_arr.append(self.forgetUFormFormatResult)
            return resp
        else:
            return self.forgetUFormFormatResult(resp)

    def getAttrPartFormatResult(self, resp):
        return resp[4]
            
    def getAttrPart(self, uu, attr, start, length):
        uu = makeUUID(uu)
        resp = self.request(GETATTR_PART, [uu, attr, start, length])
        if self._batch:
            self._resp_arr.append(self.getAttrPartFormatResult)
            return resp
        else:
            return self.getAttrPartFormatResult(resp)
        
    def setAttrPartFormatResult(self, resp):
        return resp[4]
            
    def setAttrPart(self, uu, attr, start, length, part):
        uu = makeUUID(uu)
        resp = self.request(SETATTR_PART, [uu, attr, start, length, part])
        if self._batch:
            self._resp_arr.append(self.setAttrPartFormatResult)
            return resp
        else:
            return self.setAttrPartFormatResult(resp)
        
    def customOpcode(self,opcode,uf):
        uf = makeUForm(uf)
        return self.request(opcode, [uf])

    # these are experimental prototype methods for dealing with UForms

    def updateFormatResult(self,resp,uf):
        uf.eform=resp[0].eform
        return uf
    
    def update(self, uf):
        if uform.isa(uf):
            resp = self.request(GETATTR,[uf])
            if self._batch:
                self._resp_arr.append((self.updateFormatResult,uf))
                return resp
            else:
                return self.updateFormatResult(resp,uf)
        else:
            raise RepositoryArgumentOfWrongTypeError

    def updateAllFormatResult(self,resp,uf):
        uf.eform=resp[0].eform
        return uf
    
    def updateAll(self, uf):
        if uform.isa(uf):
            resp = self.request(GETUFORM,[uf])
            if self._batch:
                self._resp_arr.append((self.updateAllFormatResult,uf))
                return resp
            else:
                return self.updateAllFormatResult(resp,uf)
        else:
            return RepositoryArgumentOfWrongTypeError

    def saveFormatResult(self,resp):
        return resp[1]
    
    def save(self, uf):
        if uform.isa(uf):
            resp=self.request(SETATTR,[uf])
            if self._batch:
                self._resp_arr.append(self.saveFormatResult)
                return resp
            else:
                return self.saveFormatResult(resp)
        else:
            return None

    def saveAllFormatResult(self,resp):
        return resp[1]
    
    def saveAll(self, uf):
        if uform.isa(uf):
            resp=self.request(SETUFORM,[uf])
            if self._batch:
                self._resp_arr.append(self.saveAllFormatResult)
                return resp
            else:
                return self.saveAllFormatResult(resp)
        else:
            return None
        
    def waitForPresence(self, uu, timeoutSecs = 30, testInterval = 1):
        if uu == '': raise Exception("Empty UUID in waitForPresence")
        if uu == None: raise Exception("UUID cannot be None in waitForPresence")
        start = time.time()
        if not self.knows(uu): self.getAttr(uu,'foobar')
        else: return
        while not self.knows(uu):
            if (timeoutSecs > 0) and ((time.time() - start) > timeoutSecs):
                raise TimeoutError('timed out after waiting for UUID %s to be present in repository %s for %d seconds' % (uu.toString(), self.getHostAndPort(), int(timeoutSecs)))
            time.sleep(testInterval)
 

class RepositoryDictMisbehviorError:
    pass

class RepositoryDict:
    def __init__(self,hostport="pegasus:6200",authUF=None,connection=None):
        self.r = Repository(hostport,authUF,connection)

    def __getattr__(self, key):
        if key in ["len","keys","items","clear","copy","update","values"]:
            raise RepositoryDictMisbehaviorError

    def __getitem__(self, key):
        if uuid.isa(key) or type(key) == type(""):
            return self.r.getUForm(key)
        elif type(key) == type((1,1)) and len(key) == 2 and \
               (uuid.isa(key[0]) or type(key[0]) == type("")):
            u,a = key
            return self.r.getAttr(u,a)
        else:
            raise RepositoryDictMisbehaviorError

    def __setitem__(self, key, value):
        if (uuid.isa(key) or type(key) == type("")) and uform.isa(value):
            return self.r.setUForm(key,value)
        elif type(key) == type((1,1)) and len(key) == 2 and \
               (uuid.uform(key[0]) or type(key[0]) == type("")):
            u,a = key
            return self.r.setAttr(u,a,value)
        else:
            raise RepositoryDictMisbehaviorError

    def __delitem__(self, key):
        if (uuid.isa(key) or type(key) == type("")):
            return self.r.forgetUForm(key)
        elif type(key) == type((1,1)) and len(key) == 2 and \
               (uuid.isa(key[0]) or type(key[0]) == type("")):
            u,a = key
            return self.r.removeAttr(u,a)
        else:
            raise RepositoryDictMisbehaviorError

###
# Here's a version of Repository that uses M2Crypto to
# connect over SSL.  Of course you'll need M2Crypto somewhere in your path.
#
# At the moment it doesn't do any sort of certificate verification
# or any of that stuff --- please feel free to add it 
###
class SSLRepository(Repository):
    def __init__(self,hostport=DEFAULT_HOST+":"+str(DEFAULT_SSLPORT),authUF=None,connection=None,batch=0):
        if connection == None:
            host,port = hostport.split(':')
            try:
                from M2Crypto import Rand, SSL, X509
            except:
                raise Exception("M2Crypto not installed")
            ctx = SSL.Context()
            Rand.load_file('randpool.dat', -1) 
            s = SSL.Connection(ctx)
            s.connect((host,int(port)))
            print 'Cipher =', s.get_cipher().name()
            v = s.get_verify_result()
            if v != X509.V_OK:
                print 'Server verification failed'
            peer = s.get_peer_cert()
            print 'Server =', peer.get_subject().CN
            Rand.save_file('randpool.dat')
            connection = s
        Repository.__init__(self,'',authUF,connection,batch)
