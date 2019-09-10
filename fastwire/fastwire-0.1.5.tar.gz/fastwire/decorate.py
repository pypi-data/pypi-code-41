# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 08:58:26 2019

@author: Reuben

The decorate module contians a number of decorators which assist with
automatically connecting methods and functions.

"""

def ensure_signal_obj(signal, box, container, receiver_limit=None):
    if isinstance(signal, str) or isinstance(signal, int):
        if box is not None:
            s = box.get(name=signal, receiver_limit=receiver_limit)
        elif container is not None:
            s = container.get(name=signal, receiver_limit=receiver_limit)
        return s
    return signal


def receive(s, box=None, container=None, **receiver_kwargs):
    ''' A decorator to connect methods to Signal instances automatically 
    
    Args:
        s (Signal): A Signal instance, or list of Signal instances.
        box (Box): [Optional] The box for the active container.
        container (Container): [Optional] The container for the signal.
        **receiver_kwargs: Any number of key word arguments. These are passed
            to any Condition instances added to the Signal instance.
    '''
    if not isinstance(s, list):
        s = [s]
        
    class Decorator():
        # See https://stackoverflow.com/questions/2366713/can-a-python-decorator-of-an-instance-method-access-the-class
        def __init__(self, fn):
            self.fn = fn
    
        def __set_name__(self, owner, name):
            # Called at class creation
            if not hasattr(owner, '_connected_signals'):
                owner._connected_signals = []
            cs = owner._connected_signals
            for signal in s:
                cs.append([name, signal, box, container, receiver_kwargs])
            setattr(owner, name, self.fn) # Replace decorator with original function
        
    return Decorator


def supply(s, box=None, container=None, **receiver_kwargs):
    ''' A decorator to set methods to be the sole source for a Signal 
    
    Args:
        s (Signal): A Signal instance, or list of Signal instances.
        box (Box): [Optional] The box for the active container.
        container (Container): [Optional] The container for the signal.
        **receiver_kwargs: Any number of key word arguments. These are passed
            to any Condition instances added to the Signal instance.
    '''
    return receive(s, box, container, **receiver_kwargs)


def fn_receive(s, box=None, container=None, **receiver_kwargs):
    ''' A decorator to connect methods to Signal instances automatically 
    
    Args:
        s (Signal): A Signal instance, or list of Signal instances.
        box (Box): [Optional] The box for the active container.
        container (Container): [Optional] The container for the signal.
        **receiver_kwargs: Any number of key word arguments. These are passed
            to any Condition instances added to the Signal instance.
    '''
    if not isinstance(s, list):
        s = [s]
    def decorator(fn):
        for signal in s:
            signal = ensure_signal_obj(signal, box, container)
            signal.connect(fn, **receiver_kwargs)
        return fn
    return decorator


def fn_supply(s, box=None, container=None, **receiver_kwargs):
    ''' A decorator to set methods to be the sole source for a Signal 
    
    Args:
        s (Signal): A Signal instance, or list of Signal instances.
        **receiver_kwargs: Any number of key word arguments. These are passed
            to any Condition instances added to the Signal instance.
    '''
    s = ensure_signal_obj(s, box, container, receiver_limit=1)
    if s._receiver_limit != 1:
        raise KeyError('Signal must be set to have only 1 supplier.')
    return fn_receive(s, box, container, **receiver_kwargs)
