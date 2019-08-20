#######################################################################
#
#       COPYRIGHT 2008 RHIZA LABS, LLC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY RHIZA OR
# MAYA DESIGN
#
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY
# RHIZA OR MAYA AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR
# CONSENT OF THE OWNER.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH
# THE TERMS  OF THE APPLICABLE LICENSE AGREEMENT FROM RHIZA. THIS LEGEND MAY
# NOT BE REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY RHIZA LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

# vsmf.py
#
# Anukul Kapoor
# (C) 2000 MAYA Design Group
#
# SJR 07.08.02 -- added vsmf.null class
#
# JAS 11.27.00 -- I added a toVSMF method to the container types
#                 this is safer when modules are reloaded then checking
#                 against the instance type (i.e. the class object may
#                 change but be of the same class)
#
# JAS 04.12.04 -- added Quantity type plus removed all limitations on
#                 eint sizes 
#
# JAS 11.22.06 -- added ERRTOK type
# JAS 09.12.17 -- overhaul with Immutuple type
#
"""
Visage Standard Message Format module for Python

Executive summary:
 vsmf.serialize:
  native python objects -> VSMF encoded character array (string)
 vsmf.reconstitute:
  VSMF encoded character array -> (string) native python objects 

vsmf.serialize only understands:
 strings
 integers
 floats
 lists (becomes Het Arrays)
 dictionaries (becomes an EForm)
 uuid.UUID
 uform.UForm
 vsmf.mimeVal
 vsmf.binary
 vsmf.value (a catchall abstract vsmf represenation)
 vsmf.null
 date.Date
 
vsmf.reconstitute should understand most VSMF typecodes
 uuids become uuid.UUIDs
 null becomes None, except when an attribute value in EForm/UForm,
     when it becomes vsmf.null
 padding becomes None
 true, false, and bool all become 1 or 0
 ascii chars become strings of length 1
 msb, and lsb chars all become integers
 binary becomes a vsmf.binary
 mime values become vsmf.mimeVals (except 'application/x-pickled-python'??)
 eforms becomes python dictionaries
 uforms become a uform.UForm
 structs becomes tuples ****
 homogeneous arrays become lists(arrays)
 heterogeneous arrays become lists(arrays)
 ISO8601 become date.Date
 
 everything else becomes a vsmf.value which should preserve
  values across serialization/reconstitution
 
todo list :
 - specify a # of recursive vsmf parsings to undertake in
   Messages, EForms, & UForms
 - a vsmf.struct type
 - python pickle mime type
 - change all constant type codes to serializeTypeCode([(kind,lenght,id)]) expressions
 - is None handled correctly?
 - make reconstitute(serialize(x)) == x for all x!
    ( for some 'standard interpretation' ??)

 """


###############################################################################
#
###############################################################################
from __future__ import absolute_import
import functools # something imports this repeatedly - so getting it into the namespace is good
import marshal # for compscript only
_codeobjtype = type(compile('','','exec'))
try:
  from _struct import pack,unpack,unpack_from,calcsize
except:
  from struct import pack,unpack,unpack_from,calcsize
from MAYA.utils.date import Date, Date_
from MAYA.VIA import uuid, uform
# figure out if we have the string kind extension
CHECK_SKIND = hasattr('','kind')
def IS_BSTRING(obj):
  return (type(obj) is str and obj.kind() == 1)
try:
   from binascii import a2b_base64, b2a_base64
   try:
       b2a_base64('a',1)
       def b64encode(a): return b2a_base64(a,1) # strip newline
   except:
       def b64encode(a): return b2a_base64(a)[:-1] # strip newline

   JSON_PREFIX=uuid.JSON_PREFIX

   def VSMFJSONEncoder(o): # use for json.dump object hook (hacked version)
      if hasattr(o,'toJSON'): return o.toJSON()
      return o

   def VSMFJSONDecoder(dct): # use for json.load object hook
      if len(dct) == 1 and JSON_PREFIX in dct:
         v = dct[JSON_PREFIX]
         cls = v[0]
         if   cls == 'Binary': return Binary(a2b_base64(v[1]))
         elif cls == 'Message': return Message(a2b_base64(v[1]))
         elif cls == 'MimeVal': return MimeVal(v[1],a2b_base64(v[2]))
         elif cls == 'MimeVal2': return MimeVal2(v[1],a2b_base64(v[2]))                  
         elif cls == 'serializedvsmf': return serializedvsmf(a2b_base64(v[1]))
         elif cls == 'value': return value(v[1],a2b_base64(v[2]))
         elif cls == 'ErrTok': return ERRTOK
         elif cls == 'Null': return NULL
         elif cls == 'Ratio': return Fraction(v[1],v[2])
         elif cls == 'Quantity': return Quantity(v[1],v[2],v[3])
         elif cls == 'UUID': return uuid._(v[1])
         elif cls == 'Date': return Date_(v[1])
         elif cls == 'UForm': return UForm(uuid._(v[1]),v[2])
         elif cls == 'Fragment': return Fragment(v[1],a2b_base64(v[2]))                  
      return dct
except: 
   a2b_base64 = b2a_base64 = None
   pass

try:
   def fromJSON(m):
      import json
      return json.loads(m,object_hook=VSMFJSONDecoder)
   class VSMFJSONEncoderClass(json.JSONEncoder):
      def default(self, obj):
        if hasattr(obj,'toJSON'):
          obj = obj.toJSON()
        return json.JSONEncoder.default(self, obj)
      def encode(self, obj):
        if hasattr(obj,'toJSON'):
          obj = obj.toJSON()
        return json.JSONEncoder.encode(self, obj)
   def toJSON(m):
      return json.dumps(m,cls=VSMFJSONEncoderClass)
except:
   pass

# This controls whether shorter "optimized" vsmf sequences will be generated
# for variable length types (e.g. string) when they have 0,1,2,4,8 lengths.
USE_FIXED_LEN_SHORTCUTS=0

###############################################################################
#
###############################################################################  
UUID = uuid.UUID
UUID_ = uuid._
UForm = uform.UForm
EForm = uform.EForm
UUID_fromBytes = uuid.UUID

# this can be set to a function that takes a binary string
# and generates a terminal object
terminal_constructor = None

# these are old style single byte typecodes
# i still use them for outputting messages
TC_NULL = 0x08
TC_BOOL = 0x2a
TC_ERRTOK = 0x13
TC_CHAR = 0x2c
TC_INT = 0x69
TC_FLOAT = 0x6b
TC_DOUBLE = 0x8b

TC_MSB2B_INT = 0x49
TC_MSB4B_INT = 0x69
TC_MSB8B_INT = 0x89

TC_LSB2B_INT = 0x48
TC_LSB4B_INT = 0x68
TC_LSB8B_INT = 0x88

TC_LSB_FLOAT = 0x6a
TC_LSB_DOUBLE = 0x8a

TC_BINARY = 0xaf
TC_MESSAGE = 0xa7

TC_UUID = 0xa3
TC_EFORM = 0xa6
TC_UFORM = 0xa4

TC_STRING = 0xa5
TC_MIME = 0xb0
TC_MIME2 = 0xb4

TC_TERMINAL = 0xb1

TC_QUANTITY = 0xb2

TC_HOMARRAY = 0xc1
TC_HETARRAY = 0xa2

TC_FRAGMENT = 0xb5

# these are modern style typecode identifiers
# for use in (kind,length,id) codons
TCID_STRUCT = 0
TCID_HOMO_ARR = 1
TCID_HET_ARR = 2
TCID_UUID = 3
TCID_UFORM = 4
TCID_STRING = 5
TCID_EFORM = 6
TCID_MESSAGE = 7
TCID_NULL = 8
TCID_LSB_INT = 8
TCID_TRUE = 9
TCID_MSB_INT = 9
TCID_FALSE = 10
TCID_BOOL = 10
TCID_LSB_FLOAT = 10
TCID_MSB_FLOAT = 11
TCID_ASCII = 12
TCID_LSB_CHAR = 12
TCID_MSB_CHAR = 13
TCID_PAD = 14
TCID_BIN = 15
TCID_MIME = 16 #deprecated
TCID_TERMINAL = 17
TCID_QUANTITY = 18
TCID_ERRTOK = 19
TCID_MIME2 = 20
TCID_FRAGMENT = 21


#convenience
stringTC, binTC = [(0,-1,chr(TCID_STRING))],[(0,-1,chr(TCID_BIN))]

# a placeholder class for a tuple that has previously been ensured to be deeply immutable
class Immutuple(tuple):
  __slots__ = ()  
  def __new__(klass, a): 
    return tuple.__new__(klass, [deeply_immutable(x) for x in a])

# convenience routine for making something deeply immutable
def deeply_immutable(m):
  def _im_form(m):
    if hasattr(m,'_implements_uform'):
      x = UForm(m.uuid)
    else:
      x = EForm()
    for k in m:
      x[k] = deeply_immutable(m[k])
    x.lockperm()
    return x
  if type(m) in (Immutuple,_codeobjtype) or (isinstance(m,uform.baseForm) and hasattr(m,'_lock') and m._lock == 2): 
      pass #already processed, known immutable, or locked
  elif hasattr(m,"has_key"):
      m = _im_form(m)
  elif hasattr(m,"upper"):
    if hasattr(m,"__setitem__"): # this will handle the mutable bytearray
      if isinstance(m,bytearray):
          m = Binary(m)
      else:
          m = str(m) # make immutable copy
    #assume strings and vsmf derived string-like classes are immutable
  elif hasattr(m,"__getslice__"): 
    m = Immutuple(m)
  # other stuff might be safe...(BIG OPEN QUESTION HERE!!!!)
  return m


# reserved for private use
# not to be exposed
#jas: what was this for?!
# TCID_RESERVED = 17

## 3-byte codons
TCID_ISO8601 = 100
TCID_COMPSCRIPT = 129 

STRICT_UTF8 = 0
WARN_UTF8 = 1

# decode from a utf8 buffer, but use regular string if ascii
def py_from_utf8(s):
   try:
      s = s.decode('utf8')
   except:
      if STRICT_UTF8:
         raise Exception("VSMF: non-compliant UTF-8 string " + repr(s))
      elif WARN_UTF8:
         print "VSMF(Warning): non-compliant UTF-8 string " + repr(s)
   try: #convert a unicode string to a regular string if only ASCII
      return str(s)
   except:
      return s

###############################################################################
#
###############################################################################
# only valid for kind=0 and vtc must be first byte of varlen tc
# return a typecode that uses fixed length if len in (0,1,2,4,8) otherwise
# a varlen typecode followed by the length.  'extra' is for type id >= 0x1f
def _var_or_fixed_tc(vtc,l,extra=''): 
  if l <= 8 and USE_FIXED_LEN_SHORTCUTS:
    x = (0x00,0x20,0x40,None,0x60,None,None,None,0x80)[l]
    if x is not None: return chr(vtc - 0xa0 + x) + extra # subtract var len and add in fixed len
  return chr(vtc) + extra + writeEint(l)

class bbuffer(str):
   # someday maybe: __slots__ =  ('buf',) or better: ()
   _mclsname = "bbuffer"
   def __new__(cls,arg=''):
     ret = str.__new__(cls,arg)
     ret.buf = ret #bwcompat
     return ret
   def getBuf(self):
     return self
   def toVSMF(self):
     return _var_or_fixed_tc(self._vsmftc,len(self)) + self
   def toJSON(self):
     return {JSON_PREFIX:[self._mclsname,b64encode(self)]}
   def __repr__(self):
     return self._mclsname+"("+str.__repr__(self)+")"
     #maybe: return self.__class__.__module__+"."+self.__class__.__name__+"("+str.__repr__(self)+")"

def Bin64_(a): 
     return vsmf.Binary(a2b_base64(a))
     
class Binary(bbuffer):
    _mclsname = "Binary"
    _vsmftc = TC_BINARY
    def _implements_binary(self): return 1
    def repr_Bin64(self): return "vsmf.Bin64_(%s)", repr(b2a_base64(self))
    
    def __add__(self, b):
       if isinstance(b, Binary) or (CHECK_SKIND and IS_BSTRING(b)):
          return Binary(bbuffer.__add__(self, b))
       # ----------------------------------------------------------------------
       else:

          raise TypeError, "unsupported operand type(s) for +: %s and %s"%(repr(type(self)),
         repr(type(b)))

# wrapper for embedded VSMF message
class Message(bbuffer):
    _mclsname = "Message"
    _vsmftc = TC_MESSAGE
    def __add__(self, b):
       raise TypeError, "cannot operate on Message"
          
class Fragment(bbuffer):
    #somday maybe: __slots__ = ('type','buf',) #buf is bwcompat
    _mclsname = "Fragment"
    _vsmftc = TC_FRAGMENT
    def __new__(cls,mtyp,buf=''):
      ret = bbuffer.__new__(cls,buf)
      ret.type = mtyp # unfortunately called "type" to be bwcompat with Mimeval
      return ret
    def __getnewargs__(self):
      return (self.type,str(self))
    def getType(self):
        return self.type

    def __repr__(self):
        return self._mclsname+"("+repr(self.type)+","+str.__repr__(self)+")"

    def __cmp__(self, other):
        try:
            if self.__class__ == other.__class__:
                return bbuffer.__cmp__(self,other)
        except:
            pass
        return -1

    def toVSMF(self):
        typ = self.type
        if isinstance(typ, unicode): typ = typ.encode('utf8')
        v = writeEint(len(typ)) + typ + self
        return _var_or_fixed_tc(self._vsmftc, len(v)) + v

    def toJSON(self):
        return {JSON_PREFIX:[self._mclsname,self.type,b64encode(self)]}

class MimeVal2(Fragment):
    _mclsname = "MimeVal2"
    _vsmftc = TC_MIME2
    def _implements_mimeVal(self): return 1
    def getFile(self):
        try:
          import StringIO
          return StringIO.StringIO(self.buf)
        except:
          raise Exception("VSMF: No StringIO on Platform")

# deprecated!
class MimeVal(MimeVal2):
    #somday maybe: __slots__ = ('type','buf',) #buf is bwcompat
    _mclsname = "MimeVal"
    _vsmftc = TC_MIME
    def toVSMF(self):
        typ = self.type
        if isinstance(typ, unicode): typ = typ.encode('utf8')
        v = writeEint(len(typ)) + typ + writeEint(len(self)) + self
        return _var_or_fixed_tc(self._vsmftc, len(v)) + v

    
# for boolean class below
import sys
native_bool = (sys.version_info[0] >= 2 and sys.version_info[1] >= 3)

# jas: I moved the Boolean class into here... we should never be using this anymore
# since there has been a native bool type for a long time
if not native_bool:
  class Boolean:
    def __init__(self,value=0):
        if native_bool:
           print "VSMF: Deprecated use of vsmf.boolean class"
        self.val = value
    def __repr__(self):
        if native_bool:
          if self.val: return "True"
          else: return "False"
        if self.val:
            return "MAYA.VIA.vsmf.Boolean(1)"
        else:
            return "MAYA.VIA.vsmf.Boolean(0)"

    def __nonzero__ (self):
        return self.val != 0

    def __cmp__(self, other):
        if hasattr(other,"_implements_boolean"):
            return not other.val == self.val
        else:
            return -1

    def _implements_boolean(self):
        return 1

    def toVSMF(self):
        x = chr(0)
        if self.val: x = chr(1)        
        return chr(TC_BOOL) + x

  True = Boolean(1)
  False = Boolean(0)
else:
  True = True
  False = False

class ErrTok(object):
    __slots__ = ()
    def __repr__(self):
        return "ERROR"
    def __cmp__(self, other):
      if other is self: return 0
      return -1
    def toVSMF(self):
        return chr(TC_ERRTOK)
    def toJSON(self):
        return {JSON_PREFIX:['ErrTok']}

ERRTOK = ErrTok()
ERROR = ERRTOK
del ErrTok #hacky - remove class so no one can ever make another instance

class Null(object):
    __slots__ = ()
    def __repr__(self):
        return "NULL"

    def __cmp__(self, other):
        if hasattr(other,"_implements_null"):
            return 0
        else:
            return -1

    def _implements_null(self):
        return 1

    def toVSMF(self):
        return chr(TC_NULL)

    def toJSON(self):
        return {JSON_PREFIX:['Null']}
    
    def __nonzero__(self):
        return 0

NULL = Null()
del Null #hacky - remove class so no one can ever make another instance

_strtype = type('')
def ord_if(c):
    if type(c) == _strtype:
        c = ord(c)
    return c

try:
  from fractions import Fraction
  def _quan_helper(r):
    n = r.numerator
    d = r.denominator
    if n < 0:
      sg = 1
      n = -n
    else:
      sg = 0
    if d == 1:
      return sg,1,writeEint(n)
    elif n == 1:
      return sg,2,writeEint(d)
    else:
      return sg,3,writeEint(n)+writeEint(d)
  def _f_toJSON(r):
    if r is None: return None
    if self.denominator == 1: return self.numerator
    return {JSON_PREFIX:['Ratio',self.numerator,self.denominator]}
except ImportError:
 def _quan_helper(r):
   return r.quan_helper()
 def _f_toJSON(r):
   if r is None: return None
   return r.toJSON()
 class Fraction(object):
   __slots__ = ('n','d',)
   def ratioize(cls,r):
      if isinstance(r,Fraction): return r.n,r.d
      t = type(r)
      if t == type(0) or t == type(0L): return r,1
      if t == type(0.0): return r.as_integer_ratio()
      raise Exception("could not convert to quantity")
   ratioize = classmethod(ratioize)
   def freduce(cls,n1,d1):
      n,d = n1,d1
      while d != 0: n, d = d, n % d ##get GCD via Euclid's Algorithm.
      ## gcd is n
      return n1/n, d1/n
   freduce = classmethod(freduce)
   def __init__(self,n,d=1):
      self.n,self.d = self.freduce(n,d)
   def __str__(self):
      if self.d == 1: return str(self.n)
      return str(self.n)+"/"+str(self.d)
   def __repr__(self):
      if self.d == 1: return repr(self.n)
      return "Fraction("+str(self.n)+","+str(self.d)+")"
   def __hash__(self):
      return hash((self.n,self.d))
   def __neg__(self):
      return Fraction(-self.n,self.d)
   def __add__(self, r):
      n,d = self.ratioize(r)
      return Fraction(self.n * d + n*self.d, self.d * d)
   __radd__ = __add__   
   def __mul__(self, r):
      n,d = self.ratioize(r)
      return Fraction(self.n * n, self.d * d)
   __rmul__ = __mul__
   def __div__(self, r):
      n,d = self.ratioize(r)      
      return Fraction(self.n * d, self.d * n)
   def __rdiv__(self,r):
      n,d = self.ratioize(r)
      return Fraction(n * self.d, d * self.n)
   def __sub__(self, r):
      n,d = self.ratioize(r)
      return Fraction(self.n * d - n*self.d, self.d * d)
   def __rsub__(self,r):
      n,d = self.ratioize(r)
      return Fraction(n * self.d - self.n*d, d * self.d)
   def __float__(self):
      return self.n / float(self.d)
   def __int__(self):
      return int(round(self.n / float(self.d)))
   def __cmp__(self, r):
      n,d = self.ratioize(r)
      diff = self.n * d - n * self.d #cross mult
      return diff

   def quan_helper(self):
      ## returns: sign, flag_type, serialization
      n,d = self.n,self.d
      if n < 0:
         sg = 1
         n = -n
      else:
         sg = 0
      if d == 1:
         return sg,1,writeEint(n)
      elif n == 1:
         return sg,2,writeEint(d)
      else:
         return sg,3,writeEint(n)+writeEint(d)
   def toJSON(self):
      if self.d == 1: return self.n
      return {JSON_PREFIX:['Ratio',self.n,self.d]}
  
class Quantity(object):
   __slots__ = ('v','d','q',)
   DIMUPACK={1:'m',2:'kg',3:'s',4:'A',5:'K',6:'mol',7:'cd',8:'b'}
   RDIMUPACK={'m':1,'kg':2,'s':3,'A':4,'K':5,'mol':6,'cd':7,'b':8}
   def __getstate__(self):   # for pickling
     return self.v,self.d,self.q
   def __setstate__(self,vdq):
     self.v,self.d,self.q = vdq
     
   def _dim_inv(cls,d):
      if d is None: return d
      return tuple([(a[0],-a[1]) for a in d])
   _dim_inv = classmethod(_dim_inv)

   def _dim_mul(cls,a,b):
      if a is None: return b
      if b is None: return a
      tmp = list(a)
      tmp.extend(b)
      tmp.sort()
      i = 0
      while i<len(tmp)-1:
         if tmp[i][0] == tmp[i+1][0]:
            x = tmp[i][1] + tmp[i+1][1]
            del tmp[i]
            if x == 0:
               del tmp[i]
               i-=1
            else:
               tmp[i] = (tmp[i][0],x)
         i+=1
      return tuple(tmp)
   _dim_mul = classmethod(_dim_mul)
   
   def _dim_str(cls,d):
      def _dim_term(a):
         x = self.DIMUPACK.get(a[0])
         if x is None: x = "%d"%a[0]
         if a[1] == 1: return x
         return x+"^"+str(a[1])
      return '_'.join([_dim_term(a) for a in d])
   _dim_str = classmethod(_dim_str)

   def _str_dim(cls,d):
      def _term_dim(a):
         np = a.split('^')
         if len(np) == 1: n,p = np[0],1
         else: n,p = np
         x = self.RDIMUPACK.get(n)
         if x is None: x = int(n)
         return (x,int(p))
      if d == '': return None
      return tuple(map(_term_dim,d.split('_')))
   _str_dim = classmethod(_str_dim)

   def _dim_vsmf(cls,d):
      def _term(a):
         ret = ''
         d,p = a
         dv,rm = abs(p)/4, abs(p) % 4
         if p < 0:
            if dv > 0: ret += dv * (writeEint(d*8)) #string mult!
            if rm > 0: ret += writeEint(d*8+4-rm)
         else:
            if rm > 0: ret += writeEint(d*8+3+rm)
            if dv > 0: ret += dv * (writeEint(d*8+7)) #string mult!
         return ret
      if d is None: return ''
      return ''.join(map(_term,d))
   _dim_vsmf = classmethod(_dim_vsmf)
   
   def _vsmf_dim(cls,v):
      if len(v) == 0: return None
      i = 0
      od = None
      op = 0
      ret = []
      while i < len(v):
         e,l = readEint(v[i:])
         i+=l
         d = e>>3
         p = (e&7)-3
         if p <= 0: p-=1
         if od is None: od = d
         if d == od:
           op += p
         else:
            ret.append((od,op))
            od,op = d,p
      ret.append((od,op))
      return tuple(ret)     
   _vsmf_dim = classmethod(_vsmf_dim)

   def fromVSMF(cls,b):
      def read_num(ty,b):
         if ty == 0: return None,0
         n,d = 1,1
         l1,l2 = 0,0
         if ty < 4:             
           if ty & 1:
             n,l1 = readEint(b)
           if ty & 2:
             d,l2 = readEint(b[l1:])
         elif ty < 6:
             n,l1 = readEint(b) #matissa
             p,l2 = readEint(b[l1:]) #exponent-base2
             if ty == 4: 
               n = n * pow(2,p)
             else: 
               d = pow(2,p)
         elif ty < 8:
             e,l1 = readEint(b) #exponent base 10 or -10
             e = pow(10,e)
             if ty == 6: n = e
             else: d = e
         else: raise Exception("bad encoding")
         return Fraction(n,d),l1+l2
      flg = ord_if(b[0])
      v,l1 = read_num((flg>>3) & 7, b[1:])
      q,l2 = read_num((flg) & 7, b[1+l1:])
      d = cls._vsmf_dim(b[1+l1+l2:])
      return cls(v,d,q)
   fromVSMF = classmethod(fromVSMF)
   
   def __init__(self,v,dim=None,quant=None):
      if not isinstance(v,Fraction): v = Fraction(v)
      self.v,self.d,self.q = v,dim,quant
      if type(self.d) == _strtype:
         self.d = self._str_dim(self.d)

   def dimquantize(self,r):
      if isinstance(r,Quantity): return r.v,r.d,r.q
      t = type(r)
      if t == type(0) or t == type(0L): return r,None,None
      raise Exception("could not convert to quantity")
   def check_quanta(self,q):
      if q is None or self.q is None: return 1
      if q != self.q: raise Exception("incompatible quanta")
         
   def __repr__(self):
      return "Quantity( %s, %s, %s )"%(repr(self.v),repr(self.d),repr(self.q))
   def toVSMF(self):
    # flag [value] [quant] [dim]
    neg,flag1,v1 = self.v.quan_helper()
    if self.q is None:
       tmp,flag2,v2 = 0,0,''
    else:
       tmp,flag2,v2 = self.q.quan_helper()
    if tmp: raise Exception("illegal negative quanta")
    flags = flag2 | (flag1<<3) | (neg<<7)
    x = chr(flags) + v1 + v2
    if self.d != None:
      x += self._dim_vsmf(self.d)
    return _var_or_fixed_tc(TC_QUANTITY, len(x)) + x

   def toJSON(self):
      return {JSON_PREFIX:['Quantity',_f_toJSON(self.v),_f_toJSON(self.q),self.d]}
   
   def __deepcopy__(self):
     return self.__copy__()
   def __copy__(self):
      if type(self) == Quantity: return self
      return self.__class__(self.n, self.d)
   def __str__(self):
      t = str(self.v)
      if self.d != None: t += " "+self._dim_str(self.d)
      if self.q != None: t += "["+str(self.q)+"]"
      return t
   def __hash__(self):
      return hash((self.v,self.d,self.q))
   def __neg__(self):
      return Quantity(-self.v,self.d,self.q)
   def __add__(self, r):
      v,d,q = self.dimquantize(r)
      if d != self.d: raise Exception("incompatible dimensions")
      self.check_quanta(q)
      return Quantity(v + self.v, self.d, min(q,self.q))
   __radd__ = __add__   
   def __mul__(self, r):
      v,d,q = self.dimquantize(r)
      self.check_quanta(q)
      return Quantity(self.v * v, self._dim_mul(self.d,d))
   __rmul__ = __mul__
   def __div__(self, r):
      v,d,q = self.dimquantize(r)
      self.check_quanta(q)
      return Quantity(self.v / v, self._dim_mul(self.d,self._dim_inv(d)))
   def __rdiv__(self,r):
      v,d,q = self.dimquantize(r)
      self.check_quanta(q)      
      return Quantity(v / self.v, self._dim_mul(d,self._dim_inv(self.d)))
   def __sub__(self, r):
      v,d,q = self.dimquantize(r)            
      if d != self.d: raise Exception("incompatible dimensions")
      self.check_quanta(q)
      return Quantity(self.v - v, self.d, min(q,self.q))
   def __rsub__(self,r):
      v,d,q = self.dimquantize(r)            
      if d != self.d: raise Exception("incompatible dimensions")
      self.check_quanta(q)
      return Quantity(v - self.v, self.d, min(q,self.q))
   def __eq__(self, r):
      try:
        x = cmp(self,r)
      except:
        return False
      return x == 0
   def __cmp__(self, r):
      v,d,q = self.dimquantize(r)            
      if d != self.d: raise Exception("incompatible dimensions")
      return cmp(self.v,v)
   def __float__(self):
      return float(self.v)
   def __int__(self):
      return int(self.v)
   def __nonzero__(a):
     return a.n != 0

#a holder for a non-disturbed value (e.g. on the inside of a un-parsed uform)
class serializedvsmf(bbuffer):
    _mclsname = "serializedvsmf"
    def toVSMF(self): return self
       

# this class lets me preserve vsmf.values of types
# i cannot understand. hopefully.
class value(object):
    __slots__ = ('tc','buf')
    def __init__(self,typecode,buf):
        self.tc = typecode
        if buf is None: buf = ''
        self.buf = buf
    def __repr__(self):
        return "value("+repr(self.tc)+"," + repr(self.buf) + ")"

    def toJSON(self):
        return {JSON_PREFIX:['value',self.tc,b64encode(self.buf)]}

    def toVSMF(self):
        # todo: decide if this should use a fixed length TC if possible....
        return serializeTypeCode(self.tc) + writeEint(len(self.buf)) + self.buf

class streamBuf(object):
    __slots__ = ('index','buf')
    """This is a class that encapsulates a buffer and a read index into it
    Jeff thinks this is lame, and I should just use tuples to return how many bytes
    a given parsing routine ate. whatever"""
    def __init__(self,buf):
        self.index = 0
        self.buf = buf

    def readEint(self):
      e,self.index = readEint(self.buf,self.index)
      return e

    def ord_if(self):
      ret = ord_if(self.buf[self.index])
      self.index += 1
      return ret
        
    def unpack_from(self,format):
      ret = unpack_from(format,self.buf,self.index)
      self.index += calcsize(format)
      return ret
  
    def read(self,n=-1):
        if n == 0: return '' #jas- this didn't used to be here so there was a bug in the next line 
        if self.index >= len(self.buf):
            return None
        elif (n == -1):
            temp,self.index = self.index,len(self.buf)
            return self.buf[temp:]
        else:
            temp, self.index = self.index, min(self.index + n,len(self.buf))
            ret = self.buf[temp:self.index]
            if len(ret) != n: raise Exception("Short Read")
            return ret
    def len(self):
        return len(self.buf)








###############################################################################
#
###############################################################################

# this is exported for UUID
def vsmf_serialize_uuid(obj):
    return _var_or_fixed_tc(TC_UUID,obj.getLen()) + obj.getBuf()
    
# this is exported for date
def vsmf_serialize_date(obj):
    s = obj.toString()
    return _var_or_fixed_tc(0xBF,len(s),'\x01d') + s

def vsmf_serialize_code(obj):
    s = "0" + marshal.dumps(obj)
    return _var_or_fixed_tc(0xBF,len(s),'\x01\x81') + s
   
# also used as helper for vsmf_serialize_uform                 
def vsmf_serialize_eform(obj,uu=None,sflags=0):
    if uu is None:
       buf = []
       tc = TC_EFORM
    else:
       buf = [writeEint(uu.getLen()),uu.getBuf()]
       tc = TC_UFORM
    items = obj.items()
    items.sort() 
    # technically this should be sorted by utf-8 lexical order to be canonical
    for attr,val in items:
        if val is None: # distinguish None from vsmf.null
            valBuf = ""
        else:
            valBuf = serialize(val,sflags)
        if isinstance(attr,unicode): attr = attr.encode('utf8')   
        buf.extend([writeEint(len(attr)),attr,writeEint(len(valBuf)),valBuf])
    buf = ''.join(buf)
    return _var_or_fixed_tc(tc,len(buf)) + buf

# this is exported for UFORM
def vsmf_serialize_uform(obj,sflags):
    return vsmf_serialize_eform(obj,obj.uuid,sflags)

def hexdump(s):
    """This function just makes a buffer into a more-prettily printed hexdump.
    Proof that python can be an ugly language.
    jas: HAH! how's this:"""
    def hexNumRows(s,n):
        a = len(s)
        d,m = a//n, a%n
        if m != 0:
            return d+1
        else:
            return d
    lines = ["\n"]
    for subStr in map(lambda x,buf=s: buf[x*16:(x+1)*16], range(0,hexNumRows(s,16))):
        lines.append(' '.join(map(lambda x: "%02x" % ord_if(x), subStr)) + (16-len(subStr))*"   " + "  " + ''.join(map(lambda x: chr(46 + (ord_if(x) > 31 and ord_if(x) < 127)*(ord_if(x)-46)),subStr)) + "\n")
    return ''.join(lines)


def readEint(b,i=0):
   """buffer -> eint, new_offset"""
   x = ord_if(b[i])
   i += 1
   if x < 0xfc: return x,i
   elif x == 0xfc: ln = 2
   elif x == 0xfd: ln = 4
   elif x == 0xfe: ln = 8
   else: ln,i = readEint(b,i)
   v = 0
   if ln > 3: v = 0L #make long for py23
   for k in range(ln):
      if type(v) != type(0L) and v&0xFF0000: v = long(v) #curse of python before v2.4
      v = (v<<8) + ord_if(b[i+k])
   return v,ln+i

def writeEint(x):
    """integer -> byte buffer encoding the integer as an E-int"""
    if x < 0xfc:
        if x < 0: raise Exception("Eint must be positive")
        return chr(x)
    elif x <= 0xffff:
        return pack(">BH", 0xfc, x)
    elif x <= 0xffffffffl:
        return pack(">BI", 0xfd, x)
    elif x <= 0xffffffffffffffffl:
        return pack(">BQ", 0xfe, x)
    else:
       v = ''
       while x:
          v = chr(x&0xff)+v
          x = x>>8
          if len(v) > 255: raise Exception("too big")
       return "\xff"+writeEint(len(v))+v

# each codon is a (kind,length,id) tuple

def parseCodonSimple(sbuf,abc, defgh):
    if abc == 7:
        length = sbuf.readEint()
    else:
        length = [0,1,2,4,8,-1][abc]
    kind = 0
    if defgh != 0x1f:
        id = pack(">B",defgh)
    else:
        idLen = sbuf.readEint()
        id = sbuf.read(idLen)
    return (kind,length,id)

def parseCodonComplex(sbuf,defgh):
    d = defgh >> 4
    e = (defgh >> 3) & 1
    fgh = defgh & 7

    if d == 0:
        length = -1
    else:
        length = sbuf.readEint()

    if e == 0:
        kind = 1
    else:
        kind = sbuf.readEint()

    if fgh != 7:
        id = pack(">B",fgh)
    else:
        idLen = sbuf.readEint()
        id = sbuf.read(idLen)

    return (kind,length,id)

def parseCodon(sbuf):
    b1 = sbuf.ord_if()
    abc = b1 >> 5
    defgh = b1 & 0x1f
    if abc != 6:
        return parseCodonSimple(sbuf,abc,defgh)
    else:
        return parseCodonComplex(sbuf,defgh)

# a typecode is a list whose 1st element is a codon (kind,length,id)
# followed by #kind more typecodes
def parseTypeCode(sbuf):
    c = parseCodon(sbuf)
    tc = [c]
    for j in range(0,c[0]):
        tc.append(parseTypeCode(sbuf))
    return tuple(tc)


def serializeCodonSimple(length,id):
    b0 = 0x00
    buf = ''

    if length == -1:
        abc = 5
    elif length in [0,1,2,4,8]:
        abc = {0:0, 1:1, 2:2, 4:3, 8:4}[length]
    else:
        abc = 7
        buf = buf + (writeEint(length))
        
    b0 = (abc << 5)

    if len(id) == 1 and ord_if(id[0]) < 31:
        defgh = ord_if(id[0])
    else:
        defgh = 0x1f
        buf = buf + (writeEint(len(id)) + id)

    b0 = b0 | defgh
        
    return chr(b0) + buf

def serializeCodonComplex(kind,length,id):
    b0 = 0
    buf = ''

    abc = 6
    b0 = b0 | (abc << 5)


    if length == -1:
        d = 0
    else:
        d = 1
        buf = buf + (writeEint(length))

    b0 = b0 | (d << 4)

    if kind == 1:
        e = 0
    else:
        e = 1
        buf = buf + (writeEint(kind))

    b0 = b0 | (e << 3)

    if len(id) == 1 and ord_if(id[0]) < 7:
        fgh = ord_if(id[0])
    else:
        fgh = 7
        buf = buf + (writeEint(len(id)) + id)

    b0 = b0 | (fgh)

    return chr(b0) + buf

def serializeCodon(c):
    kind,length,id = c
    if kind == 0:
        return serializeCodonSimple(length,id)
    else:
        return serializeCodonComplex(kind,length,id)

# this takes my typecode representations
# (an array beginning with (kind,length,id) followed
#  by #kind more typecodes) and converts them
# back to the perverse dense buffer implementations
# this is so i can implement my catchall vsmf.value class

def serializeTypeCode(tc):
    buf = ''
    if tc:
        (kind, length, id) = tc[0]
        buf = buf + (serializeCodon((kind,length,id)))
        for subTC in tc[1:kind+1]:
            buf = buf + (serializeTypeCode(subTC))
    return buf

#flags to serialize
VSMF_SERIALIZE_INT32_LIMIT=1
    
def serialize(obj, sflags=0):
    """attempts to convert a native python object to a VSMF message"""
    # assumption of top-level het-array? i.e. i shouldn't always include length
    objType = type(obj)
    if obj is None:
        return chr(TC_NULL)

    elif hasattr(obj,"toVSMF"):  # do this early to catch derived types with toVSMF methods
        return obj.toVSMF()

    elif objType is _codeobjtype:
        return vsmf_serialize_code(obj)
            
    elif isinstance(obj,basestring):
        if CHECK_SKIND and IS_BSTRING(obj):
          return _var_or_fixed_tc(TC_BINARY,len(obj)) + obj
        enc = obj.encode('utf8')
        return _var_or_fixed_tc(TC_STRING,len(enc)) + enc

    elif objType is int or objType is long:
        #jas: use short ints if possible
        if obj >= -0x8000 and obj <= 0x07fff:
          return chr(TC_MSB2B_INT) + pack(">h",obj)
        elif obj >= -2147483648 and obj <= 0x07fffffff: # -2147483648 is -0x80000000
          return chr(TC_INT) + pack(">i",obj)
        else:
          if sflags & VSMF_SERIALIZE_INT32_LIMIT:
              raise Exception("VSMF: int limit error",obj);
          return chr(TC_MSB8B_INT) + pack(">q",obj)

    elif native_bool and objType is bool:
        return chr(TC_BOOL) + chr(int(obj)) 

    elif objType is float:
        return chr(TC_DOUBLE) + pack(">d",obj)

    elif isinstance(obj,list) or isinstance(obj,tuple):
        buf = ''.join(map(lambda a: serialize(a,sflags),obj))
        return _var_or_fixed_tc(TC_HETARRAY,len(buf)) + buf

    elif objType is dict or hasattr(obj,"_implements_eform"):
       return vsmf_serialize_eform(obj,sflags=sflags)
    elif hasattr(obj,"_implements_uform"):
        return vsmf_serialize_uform(obj,sflags)
    elif hasattr(obj,"_implements_uuid"):
        return vsmf_serialize_uuid(obj)
    elif hasattr(obj,"_implements_date"):
        return vsmf_serialize_date(obj)
    else: # should return some sort of pickled value!
        raise Exception("VSMF: type has no serializer: "+str(obj)+" "+str(type))

def reconstitute(buf,parseForms=1,depth=-1,immutable=False):
    """reconstitutes a native python datastructure from a buffer containing a VSMF message"""
    sbuf = streamBuf(buf)
    return parseTop(sbuf,parseForms=parseForms,depth=depth,immutable=immutable)

def parseTop(sbuf,parseForms=1,depth=-1,immutable=False):
    if sbuf.index >= sbuf.len():
        return None
    topArr = []
    tc = parseTypeCode(sbuf)
    while 1:
        before = sbuf.index
        val = parseType(tc,sbuf,parseForms=parseForms,depth=depth,immutable=immutable)
        topArr.append(val)
        if sbuf.index >= sbuf.len(): 
          break
        if sbuf.index <= before:
          raise Exception("bad VSMF")
    if len(topArr) == 1:
        return topArr[0]
    else:
        if immutable:
            topArr = Immutuple(topArr)
        return topArr

def parse(sbuf,parseForms=1,nullToNone=1,depth=-1,immutable=False):
    tc = parseTypeCode(sbuf)
    val = parseType(tc,sbuf,parseForms=parseForms,nullToNone=nullToNone,depth=depth,immutable=immutable)
    return val

#"constants" for unpacking VSMF of various sizes
I1UPACK = {1: '<b', 2: '<h', 4: '<i', 8: '<q'}
I2UPACK = {1: '>b', 2: '>h', 4: '>i', 8: '>q'}
F1UPACK = {4: '<f', 8: '<d'}
F2UPACK = {4: '>f', 8: '>d'}
C1UPACK = {1: '<c', 2: '<H', 4: '<I', 8: '<Q'}
C2UPACK = {1: '>c', 2: '>H', 4: '>I', 8: '>Q'}

def parseType(tc,sbuf,parseForms=1,nullToNone=1,depth=-1,immutable=False):
    kind,length,id = tc[0]
    if length == -1: # if length is "variable"
        l = sbuf.readEint()
    else: # if length is specified in the typecode
        l = length
    if depth == 0:
       return serializedvsmf(sbuf.read(l))
    elif depth > 0: 
       depth -= 1
    if kind == 0:
        idLen = len(id)
        if idLen == 1:
            tcId = ord_if(id)
        else:
            if idLen > 8:
                return (sbuf.read(l),None)[1]
            else:
                tcId = unpack('>L',('\000' * (8 - idLen) + id))[0]

        if tcId == TCID_HET_ARR:
            maxArrLen = min(sbuf.index+l,sbuf.len())
            result = []
            while sbuf.index < maxArrLen:
                result.append(parse(sbuf,parseForms=parseForms,depth=depth,immutable=immutable))
            if immutable:
                result = Immutuple(result)
            return result
        elif tcId == TCID_UUID:
            if l == 0: 
              ret = UUID(' ')
              ret.setBuf('') #hack to actually return UUID w/ empty string
              return ret
            return UUID(sbuf.read(l))
        elif tcId == TCID_UFORM:
            maxUformLen = min(sbuf.index+l,sbuf.len())
            uuidLen = sbuf.readEint()
            uuid = UUID(sbuf.read(uuidLen))
            eewForm = UForm(uuid)
            while sbuf.index < maxUformLen:
                attrLen = sbuf.readEint()
                attr = py_from_utf8(sbuf.read(attrLen))
                valLen = sbuf.readEint()
                if valLen:
                    if parseForms:
                        eewForm[attr] = parse(sbuf,parseForms=parseForms,nullToNone=0,depth=depth,immutable=immutable)
                    else:
                        eewForm[attr] = serializedvsmf(sbuf.read(valLen))
                else:
                    if parseForms:
                       eewForm[attr] = None
                    else:
                       eewForm[attr] = serializedvsmf('')
            if immutable:
                eewForm.lockperm()
            return eewForm
        elif tcId == TCID_STRING:
            if l == 0: return ''
            ss = py_from_utf8(sbuf.read(l))
            return ss
        elif tcId == TCID_QUANTITY:
           if l == 0: raise Exception("invalid quantity format")
           ss = sbuf.read(l)
           return Quantity.fromVSMF(ss)
        elif tcId == TCID_ISO8601:
            return Date_(str(sbuf.read(l)))
        elif tcId == TCID_COMPSCRIPT:
            cbuf = str(sbuf.read(l))
            if cbuf[0] == '0':
                return marshal.loads(cbuf[1:])
            else:
                # leave serialized if non-compatible version
                return _var_or_fixed_tc(0xBF,len(cbuf),'\x01\x81') + cbuf
        elif tcId == TCID_EFORM:
            maxEformLen = min(sbuf.index+l,sbuf.len())
            # later change this:
            # right now lots of code checks for type(a) == type({})
            #eewForm = EForm()
            eewForm = {}
            while sbuf.index < maxEformLen:
                attrLen = sbuf.readEint()
                attr = py_from_utf8(sbuf.read(attrLen))
                valLen = sbuf.readEint()
                if valLen:
                    if parseForms:
                        eewForm[attr] = parse(sbuf,parseForms=parseForms,nullToNone=0,depth=depth,immutable=immutable)
                    else:
                        eewForm[attr] = serializedvsmf(sbuf.read(valLen))
                else:
                    if parseForms:
                       eewForm[attr] = None
                    else:
                       eewForm[attr] = serializedvsmf('')
            if immutable:
                eewForm.lockperm()
            return eewForm
        elif tcId == TCID_MESSAGE:
            # this code used to suck the message out of it's contents here:
            # return reconstitute(sbuf.read(l),parseForms=parseForms)
            # I'm pretty sure that was dead wrong.
            return Message(sbuf.read(l))
        elif tcId == TCID_NULL or tcId == TCID_LSB_INT:
            if length == 0:
                if nullToNone:
                    return None
                else:
                    return NULL
            else:
                return sbuf.unpack_from(I1UPACK[l])[0]
        elif tcId == TCID_ERRTOK:
            return ERRTOK
        elif tcId == TCID_TRUE and l == 0:
            return True
        elif tcId == TCID_TRUE and tcId == TCID_MSB_INT:
            if l == 0:
                return 1
            else:
                return sbuf.unpack_from(I2UPACK[l])[0]
        elif (tcId == TCID_FALSE or tcId == TCID_BOOL) and l == 0:
            return False
        elif tcId == TCID_BOOL and l == 1:
            if sbuf.unpack_from(">b")[0]:
               return True
            else:
               return False
        elif tcId == TCID_FALSE or tcId == TCID_BOOL or tcId == TCID_LSB_FLOAT:
            if l == 0:
                return None
            elif l == 1:
                return sbuf.unpack_from(">b")[0]
            else:
                return sbuf.unpack_from(F1UPACK[l])[0]
        elif tcId == TCID_MSB_FLOAT:
            return sbuf.unpack_from(F2UPACK[l])[0]
        elif tcId == TCID_ASCII or tcId == TCID_LSB_CHAR:
            return sbuf.unpack_from(C1UPACK[l])[0]
        elif tcId == TCID_MSB_CHAR:
            return sbuf.unpack_from(C2UPACK[l])[0]
        elif tcId == TCID_PAD:
            return (sbuf.read(l),None)[1]
        elif tcId == TCID_BIN:
            return Binary(sbuf.read(l))
        elif tcId == TCID_MIME:
            return MimeVal(parseType(stringTC,sbuf,immutable=immutable),parseType(binTC,sbuf,immutable=immutable).getBuf())
        elif tcId == TCID_MIME2:
            t0 = ''
            if l > 0:
                old = sbuf.index
                tsl = sbuf.readEint()
                t0 = sbuf.read(tsl)
                l -= (sbuf.index-old) # rest is value
            return MimeVal2(t0,sbuf.read(l))
        elif tcId == TCID_FRAGMENT:
            t0 = ''
            if l > 0:
                old = sbuf.index
                tsl = sbuf.readEint()
                t0 = sbuf.read(tsl)
                l -= (sbuf.index-old) # rest is value
            return Fragment(t0,sbuf.read(l))
        elif tcId == TCID_TERMINAL and terminal_constructor:
            return terminal_constructor(sbuf.read(l))
        else:
            return value(tc,sbuf.read(l))
    else: # kind > 0
        tcId = ord_if(id)
        if tcId == TCID_STRUCT:
            structArr = []
            for structType in tc[1:]:
                val = parseType(structType,sbuf,parseForms=parseForms,depth=depth,immutable=immutable)
                structArr.append(val)
            # todo: this is wrong.  Need holder class for struct
            return tuple(structArr)
        elif tcId == TCID_HOMO_ARR:
            if len(tc) != 2: raise Exception('unsupported array; kind > 1')
            memberType = tc[1]
            homArrIdx = sbuf.index+l
            if homArrIdx > sbuf.len(): raise Exception('truncated buffer')
            homArr = []
            if memberType[0][1] == 0: # size 0 exception
              n = sbuf.readEint()
              if n > 0:
                val = parseType(memberType,streamBuf(''),parseForms=parseForms,depth=depth,immutable=immutable)
                for i in xrange(0,n):
                  homArr.append(val)
            while sbuf.index < homArrIdx:
                val = parseType(memberType,sbuf,parseForms=parseForms,depth=depth,immutable=immutable)
                homArr.append(val)
            if sbuf.index != homArrIdx: raise Exception('read off end of array')
            if immutable:
                homArr = Immutuple(homArr)
            return homArr
        else: # egad! i renounce thee! i renounce thee! i renounce thee!
            return value(tc,sbuf.read(l))


###############################################################################
#
###############################################################################

if __name__ == '__main__':
  def test(data):
    serData = serialize(data)
    print "original data:"
    print repr(data)
    print
    print "VSMF message data:"
    print hexdump(serData)
    print
    print "reconstituted data:"
    rec = reconstitute(serData)
    print repr(rec)
    if repr(data) != repr(rec):
        print "(probably) ************************************FAILED!"

  def test_eint_neg():
    try:
      writeEint(-10)
    except:
      return
    raise Exception("negative EINT didn't FAIL", x)

  def runtest_eint():
    s = [0,1,2,3,250,251,252,253,254,255,256,257,35000,65000,66000,5000000,4000000000,23L]
    for x in s:
      w = writeEint(x)
      r = readEint(w,0)
      if r[0] != x or r[1] != len(w):
        raise Exception("EINT FAIL", x)
    
  def runtests():
    import math
    import MAYA.utils.date
    runtest_eint() 
    test_eint_neg()
    print "test1:"
    data = [1,2,math.pi, 'foo', UUID(), [True,False], ("foo","bar","baz"), [UUID(),4.532,"sigh"]]
    test(data)
    print "This is an expected failure on comparing tuple with list..."
    data = [1,2,math.pi, 'foo', UUID(), [True,False], ["foo","bar","baz"], [UUID(),4.532,"sigh"]]    
    test(data)
    print "Uform1:"
    test(UForm(UUID("foo"),{"bar":"bletch","fooble":MimeVal("a","data here")}))
    print "Uform2:"
    test(UForm(UUID("foo"),{"bar":None}))
    print "Eform1:"
    test({"b":"c"})
    print "Eform2:"
    test({"b":"xyz"})
    print "eform w/ list of uuid:"
    test({"r":[UUID()]})
    import time
    d = MAYA.utils.date.fromUnix(time.time())
    print d.toString()
    print Date_(d.toString()).toString()
    test(d)
    print "empty uuid test"
    uu = UUID(' ')
    uu.setBuf('')
    test(uu)

  runtests()


