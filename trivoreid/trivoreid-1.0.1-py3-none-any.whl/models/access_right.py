#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta

class Permission(object):
    '''
    Information about a built-in permission.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict) : built-in permission fields
        Dictionary keys:
            'id' (str)
            'name' (str) permission's English language name
            'dependencies' (list) having this permission also grants all listed
                                  dependency permissions.
            'groupId' (str) ID of permission group. Built in permissions may be
                            grouped for display purposes.
        '''
        self.id = data.pop('id', None)
        self.name = data.pop('name', None)
        self.dependencies = data.pop('dependencies', [])
        self.groupId = data.pop('groupId', None)

    def serialize(self):
        return {
            'id'           : self.id,
            'name'         : self.name,
            'dependencies' : self.dependencies,
            'groupId'      : self.groupId
        }

class BuiltInRole(object):
    '''
    Information about a built-in role.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict) : built-in role fields
        Dictionary keys:
            'id' (str)
            'name' (str) english language name
            'permissions' (list) permissions granted by having this role
        '''
        self.id = data.pop('id', None)
        self.name = data.pop('name', None)
        self.permissions = data.pop('permissions', [])

    def serialize(self):
        return {
            'id'          : self.id,
            'name'        : self.name,
            'permissions' : self.permissions
        }

class CustomRole(object):
    '''
    Information about a custom role.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict) : custom role fields
        Dictionary keys:
            'id' (str)
            'name' (str) english language name
            'permissions' (list) permissions granted by having this role
            'nsCode' (str) code of the namespace this object belongs to
            'memberOf' (list) IDs of the groups this role belongs to
            'meta' (dict) meta data
        '''
        self.id = data.pop('id', None)
        self.name = data.pop('name', None)
        self.permissions = data.pop('permissions', None)
        self.nsCode = data.pop('nsCode', [])
        self.memberOf = data.pop('memberOf', [])
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self):
        return {
            'id'          : self.id,
            'name'        : self.name,
            'permissions' : self.permissions,
            'nsCode'      : self.nsCode,
            'memberOf'    : self.memberOf,
            'meta'        : self.meta.serialize()
        }
