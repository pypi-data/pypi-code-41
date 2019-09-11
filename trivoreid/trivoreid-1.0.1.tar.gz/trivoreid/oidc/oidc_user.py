#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.user import Consents, Address

class OIDCUser(object):
    '''
    OIDC User wrapper.
    '''

    _NAMESPACE_CLAIM = 'https://oneportal.trivore.com/claims/namespace'
    _GROUPS_CLAIM = 'https://oneportal.trivore.com/claims/groups'
    _CONCENTS_CLAIM = 'https://oneportal.trivore.com/claims/consents'
    _MINOR_CLAIM = 'https://oneportal.trivore.com/claims/minor'

    def __init__(self, data):
        '''
        Args:
            data (dict): user fields
        '''

        self.id = data.pop('sub', None)
        self.email = data.pop('email', None)
        self.email_verified = data.pop('email_verified', None)
        self.phone = data.pop('phone_number', None)
        self.phone_number_verified = data.pop('phone_number_verified', None)
        self.preferred_username = data.pop('preferred_username', None)
        self.groups = data.pop(self._GROUPS_CLAIM, None)
        self.nsCode = data.pop(self._NAMESPACE_CLAIM, None)
        self.minor = data.pop(self._MINOR_CLAIM, None)
        self.consents = Consents(data.pop(self._CONCENTS_CLAIM, {}))
        self.locale = data.pop('locale', None)
        self.nickname = data.pop('nickname', None)
        self.zoneinfo = data.pop('zoneinfo', None)

        address = data.pop('address', {})
        self.address = Address()
        self.address.country = address.pop('country', None)
        self.address.locality = address.pop('locality', None)
        self.address.region = address.pop('region', None)
        self.address.postalCode = address.pop('postal_code', None)
        self.address.streetAddress = address.pop('street_address', None)

    def serialize(self):
        return {
            'id' : self.id,
            'email' : self.email,
            'email_verified' : self.email_verified,
            'phone' : self.phone,
            'phone_number_verified' : self.phone_number_verified,
            'address' : self.address.serialize(),
            'preferred_username' : self.preferred_username,
            'groups' : self.groups,
            'nsCode' : self.nsCode,
            'minor' : self.minor,
            'consents' : self.consents.serialize(),
            'locale' : self.locale,
            'nickname' : self.nickname,
            'zoneinfo' : self.zoneinfo
        }
