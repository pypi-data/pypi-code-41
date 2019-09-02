# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:59:51 2019

@author: Reuben
"""

import functools

from . import decorate

class Container(dict):
    ''' A dictionary-like collection of Signal instances '''
    
    def __init__(self, signal_cls):
        self._signal_cls = signal_cls
        self.receive = functools.partial(decorate.receive, container=self)
        self.supply = functools.partial(decorate.supply, container=self)

    
    def get(self, name=None, doc=None, attrs=None, must_exist=False, **kwargs):
        ''' Get or create a new Signal or Wire instance 
        
        Args:
            name (str): A name of the wire [optional]
            doc (str): A documentation string for the wire [optional]
            attrs (dict): Optional diction of signal attributes.
            must_exist (bool): True if the signal must already exist
        '''
        name = len(self) if name is None else name
        if name in self:
            return self[name]
        else:
            if must_exist:
                raise KeyError('Signal "' + str(name) + '" must exist ' +
                               'already.')
        s = self._signal_cls(name=name, doc=doc, attrs=attrs, **kwargs)
        self[name] = s
        return s
    
    def mute_all(self):
        ''' Mute all signals in the container '''
        for key, signal in self.items():
            signal.mute()

    def unmute_all(self):
        ''' Unmute all signals in the container '''
        for key, signal in self.items():
            signal.unmute()

    def reset_all(self):
        ''' Reset all wires in the contain '''
        for key, signal in self.items():
            signal.reset()
    
    def __getitem__(self, name):
        ''' Get or create a Signal instance 
        
        Args:
            key: The name of the signal
        '''
        try:
            return super().__getitem__(name)
        except KeyError:
            s = s = self._signal_cls(name=name)
            super().__setitem__(name, s)
            return s
            