#!/usr/bin/env python
# coding: utf-8

class LocationSite(object):
    '''
    Class that represents a Location/Site object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict) : location/site fields
        Dictionary keys:
            'id' (str)
            'name' (str)
            'description' (str)
            'country' (str)
            'state' (str)
            'city' (str)
            'postal' (str)
            'street' (str)
            'building' (str)
            'room' (str)
            'uri' (str)
            'phone' (str)
            'subnets' (list)
            'parent' (str)
            'coordinates' (list)
            'geoLatitude' (str)
            'geoLongitude' (str)
            'inRoomPosition' (str)
            'contact' (str)
            'group' (str)
            'nsCode' (str)
        '''

        self.coordinates = []
        for c in data.pop('coordinates', []):
            self.coordinates.append(Coordinate(c))

        self.id = data.pop('id', None)
        self.name = data.pop('name', None)
        self.description = data.pop('description', None)
        self.country = data.pop('country', None)
        self.state = data.pop('state', None)
        self.city = data.pop('city', None)
        self.postal = data.pop('postal', None)
        self.street = data.pop('street', None)
        self.building = data.pop('building', None)
        self.room = data.pop('room', None)
        self.uri = data.pop('uri', None)
        self.phone = data.pop('phone', None)
        self.subnets = data.pop('subnets', [])
        self.parent = data.pop('parent', None)
        self.geoLatitude = data.pop('geoLatitude', None)
        self.geoLongitude = data.pop('geoLongitude', None)
        self.inRoomPosition = data.pop('inRoomPosition', None)
        self.contact = data.pop('contact', None)
        self.group = data.pop('group', None)
        self.nsCode = data.pop('nsCode', None)

    def serialize(self):

        coordinates = []
        for c in self.coordinates:
            coordinates.append(c.serialize())

        return {
            'id'                : self.id,
            'name'              : self.name,
            'description'       : self.description,
            'country'           : self.country,
            'state'             : self.state,
            'city'              : self.city,
            'postal'            : self.postal,
            'street'            : self.street,
            'building'          : self.building,
            'room'              : self.room,
            'uri'               : self.uri,
            'phone'             : self.phone,
            'subnets'           : self.subnets,
            'parent'            : self.parent,
            'geoLatitude'       : self.geoLatitude,
            'geoLongitude'      : self.geoLongitude,
            'inRoomPosition'    : self.inRoomPosition,
            'contact'           : self.contact,
            'group'             : self.group,
            'nsCode'            : self.nsCode,
            'coordinates'       : coordinates
        }

class Coordinate(object):
    '''
    Class that represents a Coordinate object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict) : coordinate fields
        Dictionary keys:
            'system' (str)
            'x' (int)
            'y' (int)
            'z' (int)
        '''
        self.system = data.pop('system', None)
        self.x = data.pop('x', None)
        self.y = data.pop('y', None)
        self.z = data.pop('z', None)

    def serialize(self):
        return {
            'system' : self.system,
            'x'      : self.x,
            'y'      : self.y,
            'z'      : self.z
        }
