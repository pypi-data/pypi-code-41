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

# UForm class (Py2.0+ only)

# sort of has strange operational semantics
# the attribute space is flattened into lowercase strings
#  (doh - tuples and numbers?)
# it returns None if an attr doesn't exist
# otherwise it looks like a dictionary with a "uuid" attribute

###############################################################################
#
###############################################################################
from __future__ import absolute_import

try:
  from _warnings import warn
except:
  from warnings import warn
from copy import deepcopy #I hate that we have to do this...
from MAYA.VIA import uuid
JSON_PREFIX=uuid.JSON_PREFIX

class EFormImmutableException(Exception): pass
class EFormInvalidKey(Exception): pass

# Lockable dict with (case-independent) string keys
class baseForm(dict):
    __slots__ = ('_lock',)
    def __init__(self,e=()):
      # for some reason the dict __init__ does not use the class's __setitem__
      map(lambda a: dict.__setitem__(self,a.lower(),e[a]),e)
      if self.has_key(''):
        dict.__delitem__(self,'')
        raise EFormInvalidKey
    def lock(self):
      self._lock = 1
    def lockperm(self):
      self._lock = 2
    def unlock(self):
      if hasattr(self,'_lock'):
          if self._lock == 2: raise EFormImmutableException
          del self._lock
    def get(self,a,d=None):
      return dict.get(self,a.lower(),d)
    def __getitem__(self,a):
      return dict.__getitem__(self,a.lower())
    def __setitem__(self,a,b):
      if hasattr(self,"_lock"): raise EFormImmutableException
      aa = a.lower()
      if len(aa) == 0: raise EFormInvalidKey
      return dict.__setitem__(self,aa,b)
    def __delitem__(self, a):
      if hasattr(self,"_lock"): raise EFormImmutableException
      return dict.__delitem__(self,a.lower())
    def pop(self,item,default=None):
      if hasattr(self,"_lock"): raise EFormImmutableException
      return dict.pop(self,item,default)
    def popitem(self):
      if hasattr(self,"_lock"): raise EFormImmutableException
      return dict.popitem(self)
    def clear(self):
      if hasattr(self,"_lock"): raise EFormImmutableException
      return dict.clear(self)
    def update(self,d):
      if hasattr(self,"_lock"): raise EFormImmutableException
      ret = dict.update(self,d)
      if self.has_key(''):
        dict.__delitem__(self,'')
        raise EFormInvalidKey
      return ret
    def __repr__(self):
        return "EForm(" + dict.__repr__(self) + ")"
    def __contains__(self, key):
        return dict.has_key(self, key.lower())
    def has_key(self, key):
        return dict.has_key(self, key.lower())
    
class EForm(baseForm):
    __slots__ = ('_lock',)
    def _implements_eform(self):
      return 1
    def copy(self):
      return EForm(self)
    def __copy__(self):
      return EForm(self)
    def __deepcopy__(self,memo=None):
      x = EForm()
      for k in self.keys(): x[k] = deepcopy(self[k],memo)
      return x

###############################################################################
#
###############################################################################
# Lockable, universally identified dict with (case-independent) string keys
class UForm(baseForm):
    __slots__ = ('_lock','uuid',)
    def __init__(self,uu=None,eform=()):
        # this should be a uuid.UUID
        #if type(uu) == type("") and len(uu)>0:
        #    uu = uuid.fromString(uu)
        if type(uu) == type(u''): uu = str(uu) # allow ASCII for now...
        if type(uu) == type(""):
            uu = uuid.UUID(uu)
        elif uu == None:
            uu = uuid.UUID()
        elif not hasattr(uu,"_implements_uuid"):
            raise Exception("UForm construction error: Invalid UUID.")
        self.uuid = uu
        
        # this should be a python dictionary
	# bwcompat case of a list of attrs
        if type(eform) == type([]): # if we were passed a list of attrs 
            dict.__init__(self)
            map(lambda i: self.__setitem__(i.lower(),None),eform)
        else:
            baseForm.__init__(self,eform)

    # only for backwards compat:
    def geteform(self):
        warn("Deprecated use of the 'eform' attribute",
                 category=DeprecationWarning,
                 stacklevel=3)
        d = {}
        d.update(self)
        return d
    
    eform = property(geteform)
        
    def copy(self):
        return UForm(self.uuid,self)

    def __repr__(self):
        return "UForm("+repr(self.uuid)+"," + dict.__repr__(self) + ")"

    def __copy__(self):
      return UForm(self.uuid,self)

    def __deepcopy__(self,memo=None):
      x = UForm(self.uuid)
      for k in self.keys(): x[k] = deepcopy(self[k],memo)
      return x

    # a hack to let vsmf.py know that this object can be
    # considered a uform
    def _implements_uform(self):
        return 1

    def toJSON(self):
        return {JSON_PREFIX:['UForm',self.uuid.toString(),dict(self)]}


    
###############################################################################
#
###############################################################################
def isa_eform(u):
    return hasattr(u,"_implements_eform")

def isa_uform(u):
    return hasattr(u,"_implements_uform")

def isa(u):
    return isa_uform(u)
