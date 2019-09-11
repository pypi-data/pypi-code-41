#!/usr/bin/env python
# coding: utf-8

class DataStorage(object):
    '''
    Class that represents a datastorage object.
    '''

    def __init__(self, storage_fields={}, data=None):
        '''
        Args:
            data (dict)           : Data storage data. Any model.
            storage_fields (dirt) : Data storage fields
        Dictionary keys for the storage fields:
            'id' - Data Storage ID
            'name' - Data Storage name
            'description' description
            'ownerId' - Data Storage owner ID
        '''
        self.id = storage_fields.pop('id', None)
        self.description = storage_fields.pop('description', None)
        self.owner_id = storage_fields.pop('ownerId', None)
        self.name = storage_fields.pop('name', None)
        self.admin_access = storage_fields.pop('adminAccess', None)
        self.read_access = storage_fields.pop('readAccess', None)
        self.write_access = storage_fields.pop('writeAccess', None)
        self.size = storage_fields.pop('size', None)

        self.data = data

    def serialize(self):
        '''
        Returns JSON serializable object.
        '''
        return {
            'id'            : self.id,
            'description'   : self.description,
            'owner_id'      : self.owner_id,
            'name'          : self.name,
            'readAccess'    : self.read_access,
            'writeAccess'   : self.write_access,
            'adminAccess'   : self.admin_access,
            'size'          : self.size
        }
