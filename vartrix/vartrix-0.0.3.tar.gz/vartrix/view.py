# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 20:59:39 2019

@author: Reuben
"""

import uuid
from contextlib import contextmanager

def get_bases(obj):
    def dotkey(c):
        long_name = c.__module__ + '.' + c.__name__
        split = long_name.split('.')
        return '.'.join(split[1:])
        
    bases = [dotkey(obj.__class__)]
    for base_class in obj.__class__.__bases__:
        bases.append(dotkey(base_class))
    return bases


class View(dict):
    ''' Provides a virtual view of a Flat dictionary 
    
    Caches dict values and updates them when set for performance
    '''
    def __init__(self, container, dotkeys=None, live=True, obj=None):
        self.__hash = hash(uuid.uuid4())
        self._container = container
        self.dotkeys = []
        self._live = live
        self.dirty = False
        dotkeys = ['__ROOT__'] if dotkeys is None else dotkeys
        dotkeys = [dotkeys] if isinstance(dotkeys, str) else dotkeys
        dotkeys = get_bases(obj) if obj is not None else dotkeys
        for dotkey in dotkeys:
            self._add_dotkey(dotkey)
    
    @property
    def live(self):
        return self._live
    
    @live.setter
    def live(self, flag):
        assert type(flag) is bool
        self._live = flag
        if self._live:
            self.refresh()
        
    def __hash__(self):
        return self.__hash
        
    def _add_dotkey(self, dotkey):
        if dotkey is None or dotkey in ['', '.']:
            dotkey == '__ROOT__'
        self._hook_to_flat(dotkey)
    
    def _clash_error(self, key, dotkey):
        raise KeyError('Key "' + str(key) + '" defined in '
                       + dotkey + ' when already present in '
                       + 'one of: "' + '"; "'.join(self.dotkeys) + '"')
        
    def _hook_to_flat(self, dotkey):
        self._container.register_observer(dotkey, self)
        self._update(dotkey)
        self.dotkeys.append(dotkey)
        
    def _update(self, dotkey):
        dct = self._container.get_dct(dotkey)
        for key in dct.keys():
            if key in self:
                self._clash_error(key, dotkey)
        self.update(dct)
        for k, v in dct.items():
            setattr(self, k, v)
        
    def refresh(self):
        if not self._live:
            return
        old_keys = self.keys()
        self.clear()
        for dotkey in self.dotkeys:
            self._update(dotkey)
        new_keys = self.keys()
        for old_key in old_keys:
            if old_key not in new_keys:
                delattr(self, old_key)
        self.dirty = False

    def check_refresh(self):
        if self.dirty:
            self.refresh()
        
    def get(self, key):
        return self[key]
        
    def set(self, key, val):
        if not self._live:
            super().__setitem__(key, val)
            return
        container = self._container
        for dotkey in self.dotkeys:
            k = dotkey + '.' + key
            if k in container:
                container.set(k, val)
                return
        raise KeyError(key + ' not found in dotkeys: ' + '; '.join(self.dotkeys))
        
    def __setitem__(self, key, val):
        return self.set(key, val)
    
    def _view_update(self, key, val):
        if self._live:
            super().__setitem__(key, val)
            setattr(self, key, val)
    
    def dset(self, dct):
        for k, v in dct.items():
            self.set(k, v)
            
    @contextmanager
    def context(self, dct):
        originals = {k: self[k] for k in dct.keys()}
        self.dset(dct)
        yield self
        self.dset(originals)