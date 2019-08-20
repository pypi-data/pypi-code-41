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

"""

Lazy UForm

Tries to fetch uform attributes lazily

Seung Chan Lim ( slim@maya.com )

"""
###############################################################################
#
###############################################################################
import types
import thread
from MAYA.VIA import uform
from MAYA.VIA.uform import UForm
from MAYA.VIA import uuid





###############################################################################
#
###############################################################################
class LazyUform(UForm):
    """
    An experimental class
    
    Lazy UForm is basically a proxy to a real uform that gets populated
    as the user of the object requests for attributes. Think of it
    as an on-demand uform
    """
    
    class ValueProxy:
        """
        Acts as a proxy object to the types of values that a uform can 
        contain.

        This isn't complete, but it's good enough for now
        """
        _container_types = (types.ListType,
                            types.DictionaryType)
        

        class Iterator:
            def __init__(self, val):
                self._index = -1
                self.val = val

            def __iter__(self):

                return self

            def next(self):
                self._index += 1

                try:
                    return self.val[self._index]
                except IndexError:

                    raise StopIteration
            
        def __init__(self, repos, uu, name):
            self.name = name # attribute name
            self.uuid = uu
            self._repos = repos
            self._value_retrieved = 0

        def load(self, val):
            """
            loads a python native value as the value of the proxy
            """
            
            if uuid.isa(val):
                # if it's a relation, replace it with a lazy uform
                self.value = LazyUform(val, self._repos)
            else:
                self.value = val
                    
            self.type = type(val)
                    
            assert(self.type != type(())) # we'll never get tuples
            
            self._value_retrieved = 1

            return 
        def __getattr__(self, name):
            if name in ("value", "type"):
                if not self._value_retrieved:
                    # lazy value retrieval
                    val = self._repos.getAttr(self.uuid, self.name)
                    
                    self.load(val)

                # now that we have the attributes filled out, this special
                # method will no longer be called upon a getattr request
                return getattr(self, name)
            # -----------------------------------------------------------------
            else:
                # type-specific methods/attributes?
                if hasattr(self.value, name):

                    return getattr(self.value, name)
                else:
                    """
                    if name == "_implements_uform":
                    if uform.isa(self.value):
                    
                    return self.value._implements_uform
                    """
                    raise AttributeError, name

                
        def __iter__(self):
            if self.type == types.ListType:
                
                return self.Iterator(self)
            else:

                raise TypeError
            
        def __getitem__(self, key):
            try:
                if type(key) == types.SliceType:

                    slice_str = "%s:%s%s"%(key.start != None and key.start or "",
                                           key.stop != None and key.stop or "",
                                           key.step != None and ":%d"%(key.step) or "")

                    val = eval("self.value[%s]"%(slice_str))
                else:
                    val = self.value[key]
            except:
                # reraise exception - specific to value type
                # print "%s [%s] : %s"%(self.value, type(self.value), key)

                raise
            # -----------------------------------------------------------------
            else:
                assert(type(val) != type(())) # we'll never get tuples

                val = self._lazyifyRelations(val)

                # we need to reflect the changes in our internal data structure
                if type(key) == types.SliceType:
                    # right now we don't save back slices, if step is involved
                    # cuz I don't have time to deal with it
                    if key.step == None:
                        exec "self.value[%s] = val"%(slice_str) in locals()
                    else:
                        
                        raise NotImplemented, "saving back slices with step"
                    # ---------------------------------------------------------
                else:
                    self.value[key] = val

                return val

             
        def __len__(self):
            if not self._value_retrieved:
                # try to be efficient and load length without
                # getting the entire thing
                length = self._repos.chunkLength(self.uuid,
                                                 self.name, [1, -1, "", 0])
                
                if length >= 0:

                    return length
                # -------------------------------------------------------------
                else:
                    # failed chunkLenth, so try chunkCount
                    length = self._repos.chunkCount(self.uuid,
                                                    self.name, [1, -1, "", 16])

                    return length
                # -------------------------------------------------------------

                raise TypeError, "unsized object"
            # -----------------------------------------------------------------
            else:

                return len(self.value)
        
        def __nonzero__(self):
            
            # defer the nonzero evaluation to the value itself
            return (self.value and 1 or 0)

        def __contains__(self, val):
            try:

                return (val in self.value)
            # -----------------------------------------------------------------
            except TypeError:

                raise TypeError, "value cannot be iterated"

        def _lazyifyRelations(self, val):
            if type(val) == type([]):
                # make sure each relation in it are lazy uforms
                val = map(self._lazyifyRelations, val)
            elif type(val) == type({}):
                # make sure each relation in it are lazy uforms
                for key in val.keys():
                    val[key] = self._lazyifyRelations(val[key])
            elif uuid.isa(val):
                # if it's a relation we replace it with
                # a lazy uform
                val = LazyUform(val, self._repos)

            return val
        
        def sort(self, *args):
            if self.type == types.ListType:
                # first make sure we convert all the items appropriately
                for i in range(len(self.value)):
                    self.value[i] = self._lazyifyRelations(self.value[i])
                # then apply sorting
                apply(self.value.sort, args)
            else:

                raise AttributeError, "no such method %s"%("sort")

        def preFetch(self, attrs):
            assert(self.type, type([]))

            # we use the raw value for iteration
            # so as not to invoke repository fetches
            # while we're prefetching
            l = self.value
            self._repos.setBatchMode(batch=1)
            
            try:
                num_attrs = range(len(attrs))
                
                ef = {}
                
                for attr in attrs:
                    ef[attr] = None

                num_items = range(len(self))

                for i in num_items:
                    self._repos.getAttr(uform.UForm(l[i], ef))
                        
                replies = self._repos.commit(retain_order=True)
                                       
            finally:
                self._repos.commit()
                self._repos.setBatchMode(batch=0)

            num_replies = range(len(replies))
            for i in num_replies:
                #print "loading %d with %s"%(i, replies[i])
                self[i].load(replies[i])
                
        prefetch = preFetch
        
    def __init__(self, uu, repos, eform=None):
        UForm.__init__(self, uu, eform or {})
        
        if type(repos) == type(()):
            from MAYA.VIA.repos import Repository
            
            self._repos = Repository(string.join(repos, ":"))
        else:
            self._repos = repos
            
        self._list_retrieved = False
        self._prepop_eform = eform or {}


    def load(self, eform):
        for attr, val in eform.items():
            val_proxy = LazyUform.ValueProxy(self._repos,
                                         self.uuid,
                                         attr)
            val_proxy.load(val)
            self[attr] = val_proxy

            
    def refresh(self, attr_list=None):
        #print "REFRESH"
        self.clear()
        
        if not attr_list:
            attr_list = self._repos.listAttr(self.uuid)

        eform = self._prepop_eform
            
        
        try:
            for attr in attr_list:
                # we don't touch what has been populated by the "eform" argument
                if not eform.has_key(attr):
                    assert(attr == attr.lower())
                    self[attr] = LazyUform.ValueProxy(self._repos, 
                                                      self.uuid,
                                                      attr)
        except TypeError:
            print "-"
            print self.uuid
            print attr_list
            print "-"
        else:
            self.update(eform)
            self._list_retreived = True
            

    def __str__(self):

        return "<lazy: %s>"%(self.uuid.toString())
    
    def __repr__(self):
        
        return "uform.LazyUform("+ repr(self.uuid)+ ", " + \
               repr(self._repos.s.getpeername()) + ")"

    def __nonzero__(self):

        return (self.uuid and 1 or 0)
    
    def __getitem__(self, key):
        key = key.lower()
        #print
        #print "Retrieving %s from %s"%(key, self.uuid)
        
        try:
            val = UForm.__getitem__(self, key)
        except KeyError:
            # we may not have yet retrieved the list
            if not self._list_retrieved:
                self.refresh()

                try:
                    val = UForm.__getitem__(self, key)
                except KeyError:
                    # this means the uform doesn't have this attribute at all
                    
                    raise KeyError, key
                # -------------------------------------------------------------
            else:

                raise KeyError, key

        if isinstance(val, LazyUform.ValueProxy):
            # on-demand loading
            if val.type not in LazyUform.ValueProxy._container_types:
                
                return val.value
            # -----------------------------------------------------------------
                
        # either we have a container type value proxy or it's
        # a value filled in by the original argument to the
        # constructor
        #print "VAL: ",
        #print val
        return val

    def keys(self):

        if not self._list_retrieved:
            self.refresh()

        return UForm.keys(self)
        
    def preFetch(self, attrs):
        
        if not self._list_retrieved:
            self.refresh()
            
        try:
            num_attrs = range(len(attrs))

            uf = uform.UForm(self.uuid)
            
            for attr in attrs:
                uf[attr] = None

            uf = self._repos.getAttr(uf)

            for attr in attrs:
                try:
                    UForm.__getitem__(self, attr).load(uf[attr])
                except KeyError:
                        
                    # this means we were trying to prefetch an attribute
                    # which we don't believe exists
                    # user may have to refresh the uform if a
                    # change was made recently and try again
                    # or should it do that for you?
                    # is that too magical?
                    #
                    # for now I'll just ignore it
                    pass
                    
                
        finally:
            pass

    prefetch = preFetch

    def lock(self):
        self._repos.lockUForm()

    def unlock(self):
        self._repos.unlockUForm()
    
    def get(self, key, default=None):
            
        if self.has_key(key):

            return self[key]
        else:
            
            if not self._list_retrieved:
                self.refresh()

            if self.has_key(key):

                return self[key]
            else:
                return default
        
    def values(self):
        values =  self.eform.values()

        return map(lambda i, u=self.uuid, r=self._repos: getattr(i, "value"),
                   values)

