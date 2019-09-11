#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.objectid import ObjectId

class MyDataPackage(object):
    '''
    Class that represents MyData Package.
    '''

    def __init__(self, data):
        '''
        Args:
            data (dict): MyData package fields
        Dictionary keys:
            'id' (str)              : package ID
            'userId' (str)          : user ID
            'status' (MyDataStatus) : status
            'dataEntries' (list)    : list of MyDataEntry objects
            'collectedOn'           : time when the package was collected
            'collectingStartedOn'   : time when collecting started
        '''

        self.id = data.pop('id', None)
        self.userId = data.pop('userId', None)
        self.status = data.pop('status', None)
        self.data_entries = []
        self.collectedOn = data.pop('userId', None)
        self.collectingStartedOn = data.pop('userId', None)

        for entry in data.pop('dataEntries', []):
             self.data_entries.append(MyDataEntry(entry))

    def serialize(self):

        data_entries = []
        for d in self.data_entries:
            data_entries.append(d.serialize())

        return {
            'id'                    : self.id,
            'userId'                : self.userId,
            'status'                : self.status,
            'data_entries'          : data_entries,
            'collectedOn'           : self.collectedOn,
            'collectingStartedOn'   : self.collectingStartedOn
        }

class MyDataEntry(object):
    '''
    Class that represents MyData entry.
    '''

    def __init__(self, data):
        '''
        Args:
            data (dict): MyData entry fields
        Dictionary keys:
            'code' (str)                    : entry code
            'dataId' (str)                  : data ID
            'status' (str)                  : status
            'data' (MyData)                 : MyData object
            'document' (dict)               : document
            'backendSystemName' (str)
            'mimeType' (str)
            'account' (str)
            'updatedOn' (str)
            'dataIdAsObjectId' (ObjectId)
            'backendSystem' (str)
        '''
        self.code = data.pop('code', None)
        self.status = data.pop('status', None)
        self.document = data.pop('document', {})
        self.data = MyData(data.pop('data', {}))
        self.backendSystemName = data.pop('backendSystemName', None)
        self.mimeType = data.pop('mimeType', None)
        self.account = data.pop('account', None)
        self.updatedOn = data.pop('updatedOn', None)
        self.dataIdAsObjectId = ObjectId(data.pop('dataIdAsObjectId', None))
        self.dataId = data.pop('dataId', None)
        self.backendSystem = data.pop('backendSystem', None)

    def serialize(self):
        return {
            'code'              : self.code,
            'dataId'            : self.dataId,
            'status'            : self.status,
            'document'          : self.document,
            'data'              : self.data.serialize(),
            'backendSystemName' : self.backendSystemName,
            'mimeType'          : self.mimeType,
            'account'           : self.account,
            'updatedOn'         : self.updatedOn,
            'dataIdAsObjectId'  : self.dataIdAsObjectId.serialize(),
            'backendSystem'     : self.backendSystem,
        }

class MyData(object):
    '''
    Class that represents MyData object.
    '''

    def __init__(self, data):
        '''
        Args:
            data (dict): MyData fields
        Dictionary keys:
            'id' (str)              : entry ID
            'data' (bytes)          : MyData
        '''
        self.id = data.pop('id', None)
        self.data = data.pop('data', None)

    def serialize(self):
        return {
            'id'   : self.id,
            'data' : self.data
        }
