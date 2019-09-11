#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta
from trivoreid.models.email import EmailAddress
from trivoreid.exceptions import TrivoreIDSDKException

class User(object):
    '''
    The User class that represents a user.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): user fields
        Dictionary keys:
            'id' - user ID
            'username' - sign in name
            'userAccountType' - PERSON or LEGAL_ENTITY
            'nsCode' - namespace code
            'emails' - list of emails. Object of 'EmailAddresses' class
            'mobiles' - list of mobiles. Object of 'Mobiles' class
            'name' - user names. Object of 'Names' class
            'memberOf' - the list of group IDs (when creating new user or
                         modifying existing - can be group names)
            'addresses' - list of addresses. Object of 'Addresses' class

            'locale' - user's preferred locale
            'preferredLanguage' - user's preferred language
            'timeZone' - user's preferred timezone
            'mfaMethod' - multi-factor authentication method (TOTP, SMS or NONE)
            'nickName' - user's nickname or preferred name
            'locked' - user's locked status
            'minor' - is user a legal minor (client defined age). Can be used
                      as alternative to dateOfBirth.
            'websiteMain' - main website
            'websiteAux' - auxiliary website
            'domicileCode' -
            'strongIdentification' - information about last strong
                                     identification event
            'customerGroupInfo' - customer service entered data regarding
                                  customer's special statuses
            'dateOfBirth' - date of birth
            'meta' - meta data

            'gender' - Free-form field for gender
            'sex' - The juridical sex of the user. 'FEMALE', 'MALE', 'OTHER',
                    'UNDISCLOSED'.
            'nationality' - Represents the user's nationality in format
                            ISO 3166-1 Alpha-2, e.g. DE
            'salutation' - End-user’s salutation, e.g. "Mr."
            'title' - End-user’s title, e.g. "Dr."
            'birthFirstName' - First name someone has when they are born, or at
                               least from the time they are a child. This term
                               can be used by a person, who changes the first
                               name later in life for any reason.
            'birthMiddleName' - Middle name someone has when they are born, or
                                at least from the time they are a child. This
                                term can be used by a person, who changes the
                                middle name later in life for any reason.
            'birthLastName' - Last name someone has when he or she is born, or
                              at least from the time he or she is a child. This
                              term can be used by a person who changes the
                              family name later in life for any reason.
            'place_of_birth' - End-user’s place of birth.
        '''

        mobiles = []
        for m in data.pop('mobiles', []):
            mobiles.append(Mobile(m))

        addresses = []
        for a in data.pop('addresses', []):
            addresses.append(Address(a))

        emails = []
        for e in data.pop('emails', []):
            emails.append(EmailAddress(e))

        self.id = data.pop('id', None)
        self.username = data.pop('username', None)
        self.userAccountType = data.pop('userAccountType', None)
        self.nsCode = data.pop('nsCode', None)
        self.memberOf = data.pop('memberOf', [])
        self.metaData = data.pop('meta', None)
        self.name = Names(data.pop('name', {}))
        self.mobiles = mobiles
        self.emails = emails
        self.addresses = addresses
        self.consents = Consents(data.pop('consents', {}))
        self.password = None
        self.locale = data.pop('locale', None)
        self.preferredLanguage = data.pop('preferredLanguage', None)
        self.timeZone = data.pop('timeZone', None)
        self.mfaMethod = data.pop('mfaMethod', None)
        self.nickName = data.pop('nickName', None)
        self.locked = data.pop('locked', False)
        self.minor = data.pop('minor', False)
        self.websiteMain = data.pop('websiteMain', None)
        self.websiteAux = data.pop('websiteAux', None)
        self.domicileCode = data.pop('domicileCode', None)
        self.dateOfBirth = data.pop('dateOfBirth', None)
        self.strongIdentification = StrongIdentification(
                                           data.pop('strongIdentification', {}))
        self.customerGroupInfo = CustomerGroupInfo(
                                           data.pop('customerGroupInfo', {}))
        self.meta = Meta(data.pop('meta', {}))
        self.gender = data.pop('gender', None)
        self.sex = data.pop('sex', None)
        self.nationality = data.pop('nationality', None)
        self.salutation = data.pop('salutation', None)
        self.title = data.pop('title', None)
        self.birthFirstName = data.pop('birthFirstName', None)
        self.birthMiddleName = data.pop('birthMiddleName', None)
        self.birthLastName = data.pop('birthLastName', None)
        self.placeOfBirth = PlaceOfBirth(data.pop('place_of_birth', {}))

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

        emails = []
        for e in self.emails:
            emails.append(e.serialize())

        user_serializable = {
            'id': self.id,
            'username': self.username,
            'userAccountType': self.userAccountType,
            'nsCode': self.nsCode,
            'emails': emails,
            'mobiles': mobiles,
            'addresses': addresses,
            'name':  self.name.serialize(),
            'consents': self.consents.serialize(),
            'memberOf': self.memberOf,
            'locale': self.locale,
            'preferredLanguage': self.preferredLanguage,
            'timeZone': self.timeZone,
            'mfaMethod': self.mfaMethod,
            'nickName': self.nickName,
            'locked': self.locked,
            'minor': self.minor,
            'websiteMain': self.websiteMain,
            'websiteAux': self.websiteAux,
            'domicileCode': self.domicileCode,
            'dateOfBirth': self.dateOfBirth,
            'customerGroupInfo': self.customerGroupInfo.serialize(),
            'strongIdentification': self.strongIdentification.serialize(),
            'meta': self.meta.serialize(),
            'gender': self.gender,
            'sex': self.sex,
            'nationality': self.nationality,
            'salutation': self.salutation,
            'title': self.title,
            'birthFirstName': self.birthFirstName,
            'birthMiddleName': self.birthMiddleName,
            'birthLastName': self.birthLastName,
            'place_of_birth': self.placeOfBirth.serialize()
        }

        if self.password is not None:
            user_serializable['password'] = self.password

        return user_serializable

class Names(object):
    '''
    The object containing user's given, middle and family names.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): name fields
        Dictionary keys:
            'givenName' - user's given name
            'middleName' - user's middle name
            'familyName' - user's family name
        '''
        self.givenName = data.pop('givenName', None)
        self.middleName = data.pop('middleName', None)
        self.familyName = data.pop('familyName', None)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'givenName'  : self.givenName,
            'middleName' : self.middleName,
            'familyName' : self.familyName,
        }

class Mobile(object):
    '''
    The object containing the mobile data.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict, str) : mobile fields, or single mobile number.
        Dictionary keys:
            'number' (str) - mobile number
            'verified' (boolean) - verification status
        '''
        if type(data) is dict:
            self.name = data.pop('name', None)
            self.number = data.pop('number', None)
            self.verified = data.pop('verified', False)
            self.tags = data.pop('tags', [])
        elif type(data) is str:
            self.number = data
            self.name = None
            self.verified = None
            self.tags = None
        else:
            raise TrivoreIDSDKException('Wrong type of the mobile!')

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'name'      : self.name,
            'number'    : self.number,
            'verified'  : self.verified,
            'tags'      : self.tags
        }

class Address(object):
    '''
    The object containing the user address.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): address fields
        Dictionary keys:
            'addressName'
            'name'
            'country'
            'locality'
            'postalCode'
            'region'
            'streetAddress'
            'type' PERMANENT or TEMPORARY
            'organisation'
            'verified'
            'source'
            'language' ISO 639 2-letter language code.
        '''
        self.addressName = data.pop('addressName', None)
        self.name = data.pop('name', None)
        self.country = data.pop('country', None)
        self.locality = data.pop('locality', None)
        self.region = data.pop('region', None)
        self.postalCode = data.pop('postalCode', None)
        self.streetAddress = data.pop('streetAddress', None)
        self.type = data.pop('type', None)
        self.organisation = data.pop('organisation', None)
        self.verified = data.pop('verified', None)
        self.source = data.pop('source', None)
        self.language = data.pop('language', None)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'addressName': self.addressName,
            'name': self.name,
            'country': self.country,
            'locality': self.locality,
            'postalCode': self.postalCode,
            'region': self.region,
            'streetAddress': self.streetAddress,
            'type': self.type,
            'organisation': self.organisation,
            'verified': self.verified,
            'source': self.source,
            'language': self.language
        }

class Consents(object):
    '''
    Wrapper for the user's marketing consents.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): user's consents
        Dictionary keys:
            'marketingPost' (bool)
            'marketingEmail' (bool)
            'marketingPhone' (bool)
            'marketingMobileMessage' (bool)
            'marketingPushNotification' (bool)
            'marketingOther' (bool)
            'locationing' (bool)
            'profiling' (bool)
        '''
        self.marketingPost = data.pop('marketingPost', False)
        self.marketingEmail = data.pop('marketingEmail', False)
        self.marketingPhone = data.pop('marketingPhone', False)
        self.marketingMobileMessage = data.pop('marketingMobileMessage', False)
        self.marketingPushNotification = data.pop('marketingPushNotification', False)
        self.marketingOther = data.pop('marketingOther', False)
        self.locationing = data.pop('locationing', False)
        self.profiling = data.pop('profiling', False)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'marketingPost': self.marketingPost,
            'marketingEmail': self.marketingEmail,
            'marketingPhone': self.marketingPhone,
            'marketingMobileMessage': self.marketingMobileMessage,
            'marketingPushNotification': self.marketingPushNotification,
            'marketingOther': self.marketingOther,
            'locationing': self.locationing,
            'profiling': self.profiling,
        }

class CustomerGroupInfo(object):
    '''
    Wrapper for the user's customer group info.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): user's consents
        Dictionary keys:
            'student' (bool)
            'studentIdentifier' (str)
            'studentValidFrom' (str)
            'studentValidTo' (str)
            'studentUpdated' (str)
            'senior' (bool)
            'seniorIdentifier' (str)
            'seniorUpdated' (str)
            'disabilities' (bool)
            'disabilitiesIdentifier' (str)
            'disabilitiesUpdated' (str)
            'studentValidNow' (bool)
        '''

        self.student = data.pop('student', None)
        self.studentIdentifier = data.pop('studentIdentifier', None)
        self.studentValidFrom = data.pop('studentValidFrom', None)
        self.studentValidTo = data.pop('studentValidTo', None)
        self.studentUpdated = data.pop('studentUpdated', None)
        self.senior = data.pop('senior', None)
        self.seniorIdentifier = data.pop('seniorIdentifier', None)
        self.seniorUpdated = data.pop('seniorUpdated', None)
        self.disabilities = data.pop('disabilities', None)
        self.disabilitiesIdentifier = data.pop('disabilitiesIdentifier', None)
        self.disabilitiesUpdated = data.pop('disabilitiesUpdated', None)
        self.studentValidNow = data.pop('studentValidNow', None)

    def serialize(self):
        return {
            'student': self.student,
            'studentIdentifier': self.studentIdentifier,
            'studentValidFrom': self.studentValidFrom,
            'studentValidTo': self.studentValidTo,
            'studentUpdated': self.studentUpdated,
            'senior' : self.senior,
            'seniorUpdated': self.seniorUpdated,
            'seniorIdentifier': self.seniorIdentifier,
            'disabilities': self.disabilities,
            'disabilitiesIdentifier': self.disabilitiesIdentifier,
            'disabilitiesUpdated': self.disabilitiesUpdated,
            'studentValidNow': self.studentValidNow
        }

class StrongIdentification(object):
    '''
    Wrapper for the user's strong identification info.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): user's strong identification fields
        Dictionary keys:
            'method' (str) method used to strongly identify user. One of:
                           IN_PERSON, SUOMI_FI, SUOMI_FI_VALTUUDET, USER_API
            'identificationDocuments' (list) documents used during
                                             identification.
            'otherExplanation' (str) other explanation related to identification.
            'personalId' (str) user's personal ID. May be censored if viewer
                               doesn't have permission ACCOUNT_VIEW_PERSONAL_ID.
            'remarks' (str) remarks related to last strong identification event.
            'identifier' (str) user name, client ID, or other who performed last
                               identification.
            'time' (str) timestamp when user was strongly identified.
            'firstTime' (str) first time when user was strongly identified.
            'count' (int) number of times user has been strongly identified.
            'identified' (bool) has user been strongly identified.
        '''

        self.method = data.pop('method', None)
        self.identificationDocuments = data.pop('identificationDocuments', None)
        self.otherExplanation = data.pop('otherExplanation', None)
        self.personalId = data.pop('personalId', None)
        self.remarks = data.pop('remarks', None)
        self.identifier = data.pop('identifier', None)
        self.time = data.pop('time', None)
        self.firstTime = data.pop('firstTime', None)
        self.count = data.pop('count', None)
        self.identified = data.pop('identified', None)

    def serialize(self):
        return {
            'method': self.method,
            'identificationDocuments': self.identificationDocuments,
            'otherExplanation': self.otherExplanation,
            'personalId': self.personalId,
            'remarks': self.remarks,
            'identifier': self.identifier,
            'time': self.time,
            'firstTime': self.firstTime,
            'count': self.count,
            'identified': self.identified
        }

class PasswordUpdateResult(object):
    '''
    Wrapper for the user's password update result.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): user's password update result fields
        Dictionary keys:
            'success' (bool)
            'validationErrors' (list) list of ValidationError objects
        '''

        self.validationErrors = []
        for v in data.pop('validationErrors', []):
            self.validationErrors.append(ValidationError(v))

        self.success = data.pop('success', None)

    def serialize(self):

        validationErrors = []
        for v in self.validationErrors:
            validationErrors.append(v.serialize())

        return {
            'success': self.success,
            'validationErrors' : validationErrors
        }

class PlaceOfBirth(object):
    '''
    Wrapper for the user’s place of birth.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): user’s place of birth fields
        Dictionary keys:
            'country'
            'locality'
            'region'
        '''
        self.country = data.pop('country', None)
        self.locality = data.pop('locality', None)
        self.region = data.pop('region', None)

    def serialize(self):
        return {
            'country': self.country,
            'locality': self.locality,
            'region': self.region
        }

class ValidationError(object):
    '''
    Wrapper for the validation error.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): validation error
        Dictionary keys:
            'message' (str)
            'code' (str) validation error code
        '''
        self.message = data.pop('message', None)
        self.code = data.pop('code', None)

    def serialize(self):
        return {
            'message': self.message,
            'code' : self.code
        }
