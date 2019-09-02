# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 08:58:45 2019

@author: Reuben

This module provides mix-in classes to facilitate the decoration of methods.

"""

from .decorate import ensure_signal_obj

class Wired():
    ''' The mix-in class that enables method decoration to work '''
    
    def __new__(cls, *args, **kwargs):
        ''' Called at instance creation '''
        def register_signals(inst):
            try:
                sigs = inst.__getattribute__('_connected_signals')
            except AttributeError:
                return
            for name, s, box, container, receiver_kwargs in sigs:
                if 'receiver_limit' in receiver_kwargs:
                    receiver_limit = receiver_kwargs['receiver_limit']
                else:
                    receiver_limit = None
                s = ensure_signal_obj(s, box, container, receiver_limit)
                s.connect(inst.__getattribute__(name), **receiver_kwargs)
        
        try:
            inst = super().__new__(cls, *args, **kwargs)
        except TypeError:
            inst = super().__new__(cls)
        register_signals(inst)
        return inst
        