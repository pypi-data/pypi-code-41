#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta
from trivoreid.models.user import Address

class Contact(object):
    '''
    Class that represents an Contact object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict)         : access control fields
        Dictionary keys:
            'id' (str)
            'firstName' (str)
            'middleName' (str)
            'lastName' (str)
            'nickName' (str)
            'organisation' (str) free form organisation information
            'uniqueName' (str) automatically generated unique name used for
                               LDAP 'cn' attribute.
            'nsCode' (str)
            'email' (str)
            'mobile' (str)
            'locationSite' (str)
            'dataStoreCountry' (str) two letter country code
                                     (ISO 3166-1 alpha-2) for the country where
                                     the contact data should be stored
            'timeZone' (str) time zone of the contact. Example: Europe/Helsinki.
            'notes' (str) free form notes for this contact.
            'recoveryEmail' (str)
            'recoveryMobile' (str)
            'addresses' (list) list of trivoreid.models.user.Address objects
            'locale' (str) contact locale code. Example: en-GB
            'type' (str) PERSON or LEGAL_ENTITY
            'meta' (dict) meta data
        '''

        self.addresses = []
        for a in data.pop('addresses', []):
            self.addresses.append(Address(a))

        self.id = data.pop('id', None)
        self.firstName = data.pop('firstName', None)
        self.middleName = data.pop('middleName', None)
        self.lastName = data.pop('lastName', None)
        self.nickName = data.pop('nickName', None)
        self.organisation = data.pop('organisation', None)
        self.uniqueName = data.pop('uniqueName', None)
        self.nsCode = data.pop('nsCode', None)
        self.email = data.pop('email', None)
        self.mobile = data.pop('mobile', None)
        self.locationSite = data.pop('locationSite', None)
        self.dataStoreCountry = data.pop('dataStoreCountry', None)
        self.timeZone = data.pop('timeZone', None)
        self.notes = data.pop('notes', None)
        self.recoveryEmail = data.pop('recoveryEmail', None)
        self.recoveryMobile = data.pop('recoveryMobile', None)
        self.locale = data.pop('locale', None)
        self.type = data.pop('type', None)
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self):

        addresses = []
        for a in self.addresses:
            addresses.append(a.serialize())

        return {
            'id'               : self.id,
            'firstName'        : self.firstName,
            'middleName'       : self.middleName,
            'lastName'         : self.lastName,
            'nickName'         : self.nickName,
            'organisation'     : self.organisation,
            'uniqueName'       : self.uniqueName,
            'nsCode'           : self.nsCode,
            'email'            : self.email,
            'mobile'           : self.mobile,
            'locationSite'     : self.locationSite,
            'dataStoreCountry' : self.dataStoreCountry,
            'timeZone'         : self.timeZone,
            'notes'            : self.notes,
            'recoveryEmail'    : self.recoveryEmail,
            'recoveryMobile'   : self.recoveryMobile,
            'addresses'        : addresses,
            'locale'           : self.locale,
            'type'             : self.type,
            'meta'              : self.meta.serialize()
        }
