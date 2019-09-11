#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta
from trivoreid.exceptions import TrivoreIDSDKException

class Authorisation(object):
    '''
    The authorisation.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): authorisation fields
        Dictionary keys:
            'id'         Internal id
            'author'     Author of the authorization, a free-form string that
                         the API caller is responsible for maintaining. Not used
                         by the server itself.
            'nsCode'     The namespace, to which the authorization belongs to.
                         Optional - primary namespace is used if value is not
                         specified. Must be one one of the accessible
                         namespaces.
            'authType'*  The type of the authorisation. Must be an existing type
                         in the same namespace as the authorisation. See the
                         authorisation_type endpoint for available types.
            'authSource' Optional external source of the authorisation. Must be
                         one of the authorisation sources in the namespace.
                         See the authorisation_source endpoint for a list of
                         allowed sources.
            'object'     The object of the authorisation. Usually tells the
                         entity on whose behalf the subject entity is allowed
                         to do something.
            'subject'    The subject of the authorisation. Usually tells who
                         will be authorised to do something or act on the
                         object's behalf.
            'validFrom'  Valid From time in ISO 8601 format in UTC timezone.
            'validTo'    Valid To time in ISO 8601 format in UTC timezone.
            'creator'    Information on the creator of the authorisation entry.
                         Readonly.
            'createdAt'  Authorisation created at ISO datetime
            'revoked'    True if the authorisation has been revoked. The
                         authorisation can be revoked at the revoke endpoint.
            'revokedAt'  Authorisation revoked at ISO datetime
            'meta'       Meta data
        '''

        self.id = data.pop('id', None)
        self.author = data.pop('author', None)
        self.nsCode = data.pop('nsCode', None)
        self.authType = data.pop('authType', None)
        self.authSource = data.pop('authSource', None)
        self.validFrom = data.pop('validFrom', None)
        self.validTo = data.pop('validTo', None)
        self.creator = data.pop('creator', None)
        self.createdAt = data.pop('createdAt', None)
        self.revoked = data.pop('revoked', None)
        self.revokedAt = data.pop('revokedAt', None)
        self.meta = Meta(data.pop('meta', {}))
        self.authObject = AuthorisationObject(data.pop('object', {}))
        self.authSubject = AuthorisationSubject(data.pop('subject', {}))

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'id'        : self.id,
            'author'    : self.author,
            'nsCode'    : self.nsCode,
            'authType'  : self.authType,
            'authSource': self.authSource,
            'object'    : self.authObject.serialize(),
            'subject'   : self.authSubject.serialize(),
            'validFrom' : self.validFrom,
            'validTo'   : self.validTo,
            'creator'   : self.creator,
            'createdAt' : self.createdAt,
            'revoked'   : self.revoked,
            'revokedAt' : self.revokedAt,
            'meta'      : self.meta.serialize()
        }

class AuthorisationObject(object):
    '''
     The object of the authorisation.
    '''

    def __init__(self, data = {}):
        '''
        The object of the authorization.
        Args:
            data (dict): authorisation object fields
        Dictionary keys:
            'type'  Object type. Must be one of the following: 'User', 'Group',
                    'String'. 'Target, 'Contact' are not supported in the SDK.
            'value' Object value. Must be an object id of an object of the
                    specified type. If type is 'String', then the value can be
                    anything. The entity, whose id is specifed, must belong to
                    the same namespace as the authorisation
        '''
        self.type = data.pop('type', None)
        self.value = data.pop('value', None)

    def modify(self, object_type = None, value = None):
        '''
        Modify authorization object.
        Args:
            object_type (str)  Object type. Must be one of the following:
                               'User', 'Group', 'String'
            value (str)        Object value. Must be an object id of an object
                               of the specified type. If type is 'String', then
                               the value can be anything. The entity, whose id
                               is specifed, must belong to the same namespace as
                               the authorisation
        '''
        if object_type != None:
            self.type = object_type
        if value != None:
            self.value = value

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'type'  : self.type,
            'value' : self.value
        }

class AuthorisationSubject(object):
    '''
     The subject of the authorisation.
    '''

    def __init__(self, data = {}):
        '''
        The subject of the authorization.
        Args:
            data (dict): authorisation subject fields
        Dictionary keys:
            'type'  Subject type. Must be one of the following: 'User',
                    'Group', 'String'
            'value' Subject value. Must be either User or Group id or if type
                    is 'String', then may be any value. The entity, whose id is
                    specifed, must belong to the same namespace as
                    the authorisation
        '''
        self.type = data.pop('type', None)
        self.value = data.pop('value', None)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'type'  : self.type,
            'value' : self.value
        }

class AuthorisationType(object):
    '''
    Definition for the authorisation type or source.
    '''

    def __init__(self, data = {}):
        '''
        Args:
            data (dict): authorization type fields
        Dictionary keys:
            'id' internal id
            'nsCode' namespace code
            'code'
            'names' authorization type locale specific names
            'names.locale' (str)
            'names.value' (str)
            'description'
            'metadata' (dict) meta data
        '''
        self.id = data.pop('id', None)
        self.nsCode = data.pop('nsCode', None)
        self.code = data.pop('code', None)
        self.description = data.pop('description', None)
        self.meta = Meta(data.pop('metadata', {}))

        names = []
        for d in data.pop('names', []):
            names.append({
                'locale'  : data.pop('locale', None),
                'value'    : data.pop('value', None)
            })
        self.names = names

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'id'            : self.id,
            'nsCode'        : self.nsCode,
            'code'          : self.code,
            'description'   : self.description,
            'names'         : self.names,
            'metadata'      : self.meta.serialize()
        }

class AuthorisationGrantRight(object):
    '''
    Definition for the authorisation grant right.
    '''

    def __init__(self, data = {}):
        '''
        Args:
            data (dict): authorization grant fields
        Dictionary keys:
            'id'                 internal id
            'authorisationTypes' List of authorisation types. Make an HTTP GET
                                 request to the authorisation_type endpoint for
                                 a list of available types.

            'authorisationGrant' Additional information about the authorisation
                                 grant right. It contains read-only information
                                 about possible revocation as well as the
                                 OAuth 2.0 client which has managed the
                                 authorisation grant right. Reanonly.
            'validFrom'          Authorisation grant right valid from. Defaults
                                 to grant right creation time.
            'validTo'            Authorisation grant right valid to. Defaults
                                 to one year after authorisation grant right
                                 creation.
            'principal'          Authorisation principal information.
            'object'             Authorisation object information. Will be
                                 determined automatically. Readonly.
        '''
        self.id = data.pop('id', None)
        self.authorisationTypes = data.pop('authorisationTypes', [])
        self.validFrom = data.pop('validFrom', None)
        self.validTo = data.pop('validTo', None)
        self.object = AuthorisationObject(data.pop('object', {}))
        self.principal = Principal(data.pop('principal', {}))
        self.authorisationGrant = AuthorisationGrant(
                                            data.pop('authorisationGrant', {}))

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'id'                 : self.id,
            'authorisationTypes' : self.authorisationTypes,
            'validFrom'          : self.validFrom,
            'validTo'            : self.validTo,
            'authorisationGrant' : self.authorisationGrant.serialize(),
            'object'             : self.object.serialize(),
            'principal'          : self.principal.serialize()
        }

class AuthorisationGrant(object):
    '''
    'createdAt'              Time of authorisation grant creation.
    'createdByOauthClientId' The id of the OAuth 2.0 client, which
                             created the entry
    'revokedByOauthClientId' If the authorisation is revoked, this field
                             shows the id of the OAuth 2.0 client, which
                             did the revoking on user's behalf
    'revoked'                True if the end-user has revoked this
                             authorisation grant right. The authorisation
                             grant right can be revoked at the revocation
                             endpoint.
    'revokedAt'              Time of authorisation revocation.
    '''

    def __init__(self, data = {}):
        self.createdAt = data.pop('createdAt', None)
        self.createdByOauthClientId = data.pop('createdByOauthClientId', None)
        self.revokedByOauthClientId = data.pop('revokedByOauthClientId', None)
        self.revoked = data.pop('revoked', None)
        self.revokedAt = data.pop('revokedAt', None)

    def serialize(self):
        return {
            'createdAt'                 : self.createdAt,
            'createdByOauthClientId'    : self.createdByOauthClientId,
            'revokedByOauthClientId'    : self.revokedByOauthClientId,
            'revoked'                   : self.revoked,
            'revokedAt'                 : self.revokedAt
        }


class Principal(object):
    '''
     The object of the authorisation.
    '''

    def __init__(self, data = {}):
        '''
        The object of the authorization.
        Args:
            data (dict): authorisation principal fields.
        Dictionary keys:
            'type'  Type of the principal. Can be any of the valid authorisation
                    subject types. ('User', 'Group' or 'String')
            'value' ID of the principal.
        '''
        self.type = data.pop('type', None)
        self.value = data.pop('value', None)

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'type' : self.type,
            'value' : self.value
        }
