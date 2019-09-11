#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta

class Target(object):
    '''
    Class that represents a Target object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict) : target fields
        Dictionary keys:
            'id' (str)
            'nsCode' (str)
            'name' (str)
            'locationSite' (str)
            'targetClass' (str)
            'contact' (str)
            'group' (str)
            'parent' (str)
            'alertOnMaintenanceGroups' (list)
            'alertOnIncidentGroups' (list)
            'alertOnMajorIncidentGroups' (list)
            'alertOnDangerNoticeGroups' (list)
            'alertOnHaltNoticeGroups' (list)
            'meta' (Meta) meta data
        '''
        self.id = data.pop('id', None)
        self.nsCode = data.pop('nsCode', None)
        self.name = data.pop('name', None)
        self.locationSite = data.pop('locationSite', None)
        self.targetClass = data.pop('targetClass', None)
        self.contact = data.pop('contact', None)
        self.group = data.pop('group', None)
        self.parent = data.pop('parent', None)
        self.alertOnMaintenanceGroups = data.pop('alertOnMaintenanceGroups', [])
        self.alertOnIncidentGroups = data.pop('alertOnIncidentGroups', [])
        self.alertOnMajorIncidentGroups = data.pop('alertOnMajorIncidentGroups', [])
        self.alertOnDangerNoticeGroups = data.pop('alertOnDangerNoticeGroups', [])
        self.alertOnHaltNoticeGroups = data.pop('alertOnHaltNoticeGroups', [])
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self):
        return {
            'id'                            : self.id,
            'nsCode'                        : self.nsCode,
            'name'                          : self.name,
            'locationSite'                  : self.locationSite,
            'targetClass'                   : self.targetClass,
            'contact'                       : self.contact,
            'group'                         : self.group,
            'parent'                        : self.parent,
            'alertOnMaintenanceGroups'      : self.alertOnMaintenanceGroups,
            'alertOnIncidentGroups'         : self.alertOnIncidentGroups,
            'alertOnMajorIncidentGroups'    : self.alertOnMajorIncidentGroups,
            'alertOnDangerNoticeGroups'     : self.alertOnDangerNoticeGroups,
            'alertOnHaltNoticeGroups'       : self.alertOnHaltNoticeGroups,
            'meta'                          : self.meta.serialize()
        }
