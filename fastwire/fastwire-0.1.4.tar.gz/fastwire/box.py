# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:56:25 2019

@author: Reuben
"""

import weakref
import functools

from . import decorate

class Box():
    ''' A collection of containers 
    
    It's used to allow client classes to create sets of signals for specific
    instances. Other classes instantiated can call an instance of this class
    to get signals within the appropriate set. This can help to avoid
    signals getting mixed up.
    '''
    def __init__(self, container_cls):
        self._container_cls = container_cls
        self._cs = {}
        self.add('default')
        self.receive = functools.partial(decorate.receive, box=self)
        self.supply = functools.partial(decorate.supply, box=self)
        
    @property
    def containers(self):
        return self._cs
        
    def add(self, cid=None, activate=True, remove_with=None):
        ''' Add a new container referenced with cid
        
        Args:
            cid (int, str): A reference for the container
            activate (bool): Set the container as the active one
            remove_with (object): An object to associate the container with.
                When the object is garbage collected, its container and
                all signals within it will also be removed. This can be useful
                to avoid objects accumulating in memory.
        '''
        c = self._container_cls()
        cid = len(self._cs) if cid is None else cid
        self._cs[cid] = c
        if remove_with is not None:
            self.remove_with(remove_with, cid=cid)
        if activate:
            self.set_active(cid)
        return c
        
    def remove_with(self, obj, cid=None):
        cid = self._active if cid is None else cid
        weakref.finalize(obj, self.remove, cid=cid)

    def remove(self, cid):
        ''' Remove a container
        
        Note:
            This sets the active container to 'default'.
        
        Args:
            cid (int, str): The container reference '''
        try:
            del self._cs[cid]
        except KeyError:
            pass
        self.set_active('default')
        
    def set_active(self, cid):
        ''' Set the active container 
        
        Args:
            cid(int, str): The container reference
        '''
        self._active = cid
        
    @property
    def active(self):
        return self._active
        
    def get_active(self):
        ''' Return the currently active container '''
        if self._active is None:
            return None
        return self._cs[self._active]
        
    def get(self, name=None, doc=None, attrs=None, **kwargs):
        ''' Create or get a new wire/signal instance in the active container
        
        Args:
            name (str): A name of the wire/signal [optional]
            doc (str): A documentation string for the wire/signal [optional]
            attrs (dict): Optional diction of signal attributes.
        '''
        c = self.get_active()
        return c.get(name=name, doc=doc, attrs=attrs, **kwargs)
    
    def __getitem__(self, name):
        ''' Get or create a signal in the currently active container '''
        return self._cs[self._active][name]
    
    def reset_all(self):
        ''' Reset all wires in the contain '''
        for key, container in self._cs.items():
            container.reset_all()