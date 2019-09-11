#!/usr/bin/env python
# coding: utf-8

class AccessControl(object):
    '''
    Class that represents an Access Control object. Access Control object
    contains lists of users and clients who have read or write access to
    other entities.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict)         : access control fields
        Dictionary keys:
            'id' (str)
            'title' (str) short title for object
            'description' (str) description for object
            'usage' (list) usages for this access control. Does not prevent other uses,
                    is used as a hint in UIs if this applies to a specific
                    purpose.
            'userIdRead' (list)   IDs of users who have read-only access
            'userIdWrite' (list)  IDs of users who have read+write access
            'groupIdRead' (list)  IDs of user groups whose members have
                                  read-only access
            'groupIdWrite' (list) IDs of user groups whose members have
                                  read+write access.
            'apiClientIdRead' (list) client IDs of Management API Clients who
                                     have read-only access.
            'apiClientIdWrite' (list) client IDs of Management API Clients who
                                      have read+write access.
        '''
        self.id = data.pop('id', None)
        self.title = data.pop('title', None)
        self.description = data.pop('description', None)
        self.usage = data.pop('usage', [])
        self.userIdRead = data.pop('userIdRead', [])
        self.userIdWrite = data.pop('userIdWrite', [])
        self.groupIdRead = data.pop('groupIdRead', [])
        self.groupIdWrite = data.pop('groupIdWrite', [])
        self.apiClientIdRead = data.pop('apiClientIdRead', [])
        self.apiClientIdWrite = data.pop('apiClientIdWrite', [])

    def serialize(self):
        return {
            'id'               : self.id,
            'title'            : self.title,
            'description'      : self.description,
            'usage'            : self.usage,
            'userIdRead'       : self.userIdRead,
            'userIdWrite'      : self.userIdWrite,
            'groupIdRead'      : self.groupIdRead,
            'groupIdWrite'     : self.groupIdWrite,
            'apiClientIdRead'  : self.apiClientIdRead,
            'apiClientIdWrite' : self.apiClientIdWrite
        }
