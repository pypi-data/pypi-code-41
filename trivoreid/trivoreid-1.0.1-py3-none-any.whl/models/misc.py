#!/usr/bin/env python
# coding: utf-8

class Meta(object):
    '''
    Class that represents a Meta Data in TrivoreID.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict)         : group fields
        Dictionary keys:
            'created' (str) time when resource was created
            'lastModified' (str) time when resource was last modified
            'location' (str) resource's location URI
        '''
        self.created = data.pop('created', None)
        self.lastModified = data.pop('lastModified', None)
        self.location = data.pop('location', None)

    def serialize(self):
        return {
            'created'      : self.created,
            'lastModified' : self.lastModified,
            'location'     : self.location
        }
