#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta

class Group(object):
    '''
    Class that represents a Group object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict)         : group fields
        Dictionary keys:
            'id' (str) - group ID
            'name' (str) - group name
            'description' (str) - group description
            'nsCode' (str) - namespace code. Use only when creating group, must
                             be among allowed Namespaces.
            'disallowUsers' (bool) disallow user accounts
            'disallowContacts' (bool) disallow contacts
            'disallowGroups' (bool) disallow groups
            'memberOf' (list) set of Group IDs this group is member of
            'meta' (dict) meta data
        '''
        self.id = data.pop('id', None)
        self.name = data.pop('name', None)
        self.description = data.pop('description', None)
        self.nsCode = data.pop('nsCode', None)
        self.disallowUsers = data.pop('disallowUsers', None)
        self.disallowContacts = data.pop('disallowContacts', None)
        self.disallowGroups = data.pop('disallowGroups', None)
        self.memberOf = data.pop('memberOf', [])
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self):
        return {
            'id'                : self.id,
            'name'              : self.name,
            'description'       : self.description,
            'nsCode'            : self.nsCode,
            'disallowUsers'     : self.disallowUsers,
            'disallowContacts'  : self.disallowContacts,
            'disallowGroups'    : self.disallowGroups,
            'memberOf'          : self.memberOf,
            'meta'              : self.meta.serialize()
        }
