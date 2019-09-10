# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 08:56:13 2019

@author: Reuben

Signals can be connected to multiple callable receivers. The hold weak
references to those callables, so that when they are garbage collected their
references are removed automatically.

"""


import weakref

from . import box, container

    
class Signal():
    ''' A class that can emit and receive data from multiple callables. 
    
        Args:
            name (str): A name of the wire [optional]
            doc (str): A documentation string for the wire [optional]
            receiver_limit (int): Limit the number of receivers [optional]
            condition (Condition): An optional signal Condition.
            attrs (dict): Optional dictionary of signal attributes.
    '''
    
    def __init__(self,
                 name=None,
                 doc=None,
                 receiver_limit=None,
                 condition=None,
                 attrs=None):
        self.reset()
        self._name = name
        self._doc = doc
        self._receiver_limit = receiver_limit
        self._attrs = attrs
        if condition is not None:
            self.add_condition(condition)
    
    def add_condition(self, condition):
        ''' Add a condition that the signal must pass to be received
        
        Args:
            condition (Condition): A Condition instance
        '''
        self._conditions[condition.name] = condition
        self.emit = self._conditioned_emit
        return True
        
    def remove_condition(self, name):
        ''' Remove a condition that the signal must pass to be received 
        
        Args:
            name (str): The name of the condition to remove.
        '''
        try:
            del self._conditions[name]
        except KeyError:
            pass
        if len(self._conditions) == 0:
            self.emit = self._emit
    
    def connect(self, receiver, **receiver_kwargs):
        ''' Store weakref of receiver function or method to call 
        
        Args:
            receiver (callable): A callable receiver
            kwargs: Optional key word arguments
            
        Returns:
            float: A receiver id that can be used to disconnect
        '''
        if self.n == self._receiver_limit:
            raise KeyError('Limit of receivers (or suppliers) reached.')
        receiver_id = self._next_id
        if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
            ref = weakref.WeakMethod(receiver)
            obj = receiver.__self__
        else:
            ref = weakref.ref(receiver)
            obj = receiver
        self._receivers[receiver_id] = ref
        self._receiver_kwargs[receiver_id] = receiver_kwargs
        weakref.finalize(obj, self.disconnect, receiver_id)
        self._next_id += 1
        return receiver_id
    
    @property
    def n(self):
        ''' Number of recievers '''
        return len(self._receivers)

    @property
    def receivers_present(self):
        ''' A boolean check if receivers are present '''
        return len(self._receivers) > 0
    
    @property
    def name(self):
        ''' The signal name '''
        return self._name

    @property
    def doc(self):
        ''' The signal documentation '''
        return self._doc
    
    @property
    def attrs(self):
        ''' The signal documentation '''
        return self._attrs
    
    def disconnect(self, receiver_id):
        ''' Disconnect a receiver 
        
        Args:
            receiver_id (int): The id of the receiver.
        '''
        try:
            del self._receivers[receiver_id]
            del self._receiver_kwargs[receiver_id]
        except KeyError:
            pass
        return True

    def _emit(self, **kwargs):
        ''' The standard emit method 

        Args:
            **kwargs: Key word arguments.
        
        Note: The 'emit' method is set to this method normally.
        '''
        for receiver_id, ref in self._receivers.items():
            receiver = ref()
            receiver(**kwargs)
            
    def _conditioned_emit(self, **kwargs):
        ''' A conditioned emit method 
        
        Args:
            **kwargs: Key word arguments.
        '''
        for receiver_id, ref in self._receivers.items():
            condition_pass = True
            for condition_name, condition in self._conditions.items():
                rec_kwargs = self._receiver_kwargs[receiver_id]
                all_kwargs = {**rec_kwargs, **kwargs}
                condition_pass &= condition.check(**all_kwargs)
            if condition_pass:
                self._emit(**kwargs)

    def _muted(self, **kwargs):
        pass
            
    def mute(self):
        ''' Prevent receivers from receiving signals '''
        self._prev_emit = self.emit
        self.emit = self._muted

    def unmute(self):
        ''' Allow receivers to receive signals (after a mute) '''
        self.emit = self._prev_emit
        del self._prev_emit
    
    def fetch(self, **kwargs):
        ''' Get a return value from a single supplier 
        
        Args:
            **kwargs: Key word arguments.
        '''
        if self._receiver_limit != 1:
            raise KeyError('Signal must be set to have only 1 supplier.')
        if self.n == 0:
            raise KeyError('No suppliers')
        for receiver_id, ref in self._receivers.items():
            receiver = ref()
            return receiver(**kwargs)

    def fetch_all(self, **kwargs):
        ''' Get return value from all connected callables 
        
        Args:
            **kwargs: Key word arguments.        
        
        Returns:
            list: The list of return values
        '''
        if self.n == 0:
            raise KeyError('No suppliers')
        ret = []
        for receiver_id, ref in self._receivers.items():
            receiver = ref()
            ret.append(receiver(**kwargs))
        return ret

    def reset(self):
        ''' Reset the signal '''
        self._receivers = {}
        self._receiver_kwargs = {}
        self._next_id = 0
        self._conditions = {}
        self.emit = self._emit


class SignalContainer(container.Container):
    ''' A dictionary-like collection of Signal instances '''
    
    def __init__(self):
        super().__init__(signal_cls=Signal)
        
    def signal(self, name=None, doc=None, attrs=None, **kwargs):    
        ''' Create or get a new signal instance
        
        Args:
            name (str): A name of the wire/signal [optional]
            doc (str): A documentation string for the wire/signal [optional]
            attrs (dict): Optional diction of signal attributes.
        '''
        return self.get(name=name, doc=doc, attrs=attrs, **kwargs)
    

class SignalBox(box.Box):
    ''' A collection of SignalContainers'''
    
    def __init__(self):
        super().__init__(container_cls=SignalContainer)
                
    def signal(self, name=None, doc=None, attrs=None, **kwargs):
        ''' Create or get a new signal instance in the active container
        
        Args:
            name (str): A name of the wire/signal [optional]
            doc (str): A documentation string for the wire/signal [optional]
            attrs (dict): Optional diction of signal attributes.
        '''
        return self.get(name=name, doc=doc, attrs=attrs, **kwargs)
    
    
default_container = SignalContainer()
signal = default_container.signal