#!/usr/bin/env python
# coding: utf-8

class ObjectId(object):
    '''
    Class that represents a Object ID.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): objectId fields
        Dictionary keys:
            'timestamp'
            'counter'
            'machineIdentifier'
            'processIdentifier'
            'timeSecond'
            'time'
            'date'
        '''

        self.timestamp = data.pop('timestamp', None)
        self.counter = data.pop('counter', None)
        self.machineIdentifier = data.pop('machineIdentifier', None)
        self.processIdentifier = data.pop('processIdentifier', None)
        self.timeSecond = data.pop('timeSecond', None)
        self.time = data.pop('time', None)
        self.date = data.pop('date', None)


    def serialize(self, creating=False):
        '''
        Return JSON serializable dictionary.
        '''
        return {
            'timestamp'         : self.timestamp,
            'counter'           : self.counter,
            'machineIdentifier' : self.machineIdentifier,
            'processIdentifier' : self.processIdentifier,
            'timeSecond'        : self.timeSecond,
            'time'              : self.time,
            'date'              : self.date
        }
