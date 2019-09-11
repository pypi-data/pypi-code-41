#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.user import Names, Mobile, Address, Consents
from trivoreid.models.email import EmailAddress

class Profile(object):

    def __init__(self, data={}):
        '''
        Args:
            data (dict): profile fields
        Dictionary keys:
            'addresses'
            'legalAddresses'
            'emails'
            'mobiles'
            'name'
            'nickName'
            'dateOfBirth'
            'locale'
            'consents'
            'minor' (bool) Is user a legal minor (client defined age). Can be
                           used as alternative to dateOfBirth.
            'timeZone'
            'lastModified'
            'domicileCode'
            'legalDomicileCode'
        '''
        self.mobiles = []
        for m in data.pop('mobiles', []):
            self.mobiles.append(ProfileMobile(m))

        self.addresses = []
        for a in data.pop('addresses', []):
            self.addresses.append(Address(a))

        self.legal_addresses = []
        for l in data.pop('addresses', []):
            self.legal_addresses.append(Address(l))

        self.emails = []
        for e in data.pop('emails', []):
            self.emails.append(ProfileEmail(e))

        self.name = Names(data.pop('name', {}))
        self.nickName = data.pop('nickName', None)
        self.dateOfBirth = data.pop('dateOfBirth', None)
        self.locale = data.pop('locale', None)
        self.consents = Consents(data.pop('consents', {}))
        self.minor = data.pop('minor', None)
        self.timeZone = data.pop('timeZone', None)
        self.lastModified = data.pop('lastModified', None)
        self.domicileCode = data.pop('domicileCode', None)
        self.legalDomicileCode = data.pop('legalDomicileCode', None)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''

        mobiles = []
        for m in self.mobiles:
            mobiles.append(m.serialize())

        addresses = []
        for a in self.addresses:
            addresses.append(a.serialize())

        legal_addresses = []
        for a in self.addresses:
            legal_addresses.append(a.serialize())

        emails = []
        for e in self.emails:
            emails.append(e.serialize())

        return {
            'dateOfBirth'       : self.dateOfBirth,
            'nickName'          : self.nickName,
            'emails'            : emails,
            'mobiles'           : mobiles,
            'name'              : self.name.serialize(),
            'locale'            : self.locale,
            'addresses'         : addresses,
            'legalAddresses'    : legal_addresses,
            'consents'          : self.consents.serialize(),
            'minor'             : self.minor,
            'timeZone'          : self.timeZone,
            'lastModified'      : self.lastModified,
            'domicileCode'      : self.domicileCode,
            'legalDomicileCode' : self.legalDomicileCode
        }

class ProfileMobile(object):
    '''
    Wrapper for a single profile mobile.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict, str) : mobile fields, or single mobile number.
        Dictionary keys:
            'number' (str) - mobile number
            'verified' (boolean) - verification status
        '''
        self.number = data.pop('number', None)
        self.verified = data.pop('verified', False)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'number'    : self.number,
            'verified'  : self.verified
        }

class ProfileEmail(object):
    '''
    Wrapper for a single profile email.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict, str): email fields or a single email address
        Dictionary keys:
            'address'       : email address
            'verified'      : verification status
        '''
        self.address = data.pop('address', None)
        self.verified = data.pop('verified', False)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'address'       : self.address,
            'verified'      : self.verified
        }
