#!/usr/bin/env python
# coding: utf-8

import requests

import trivoreid.utils.service_utils as su

from trivoreid.oidc.oidc_user import OIDCUser

from trivoreid.services.user_service import UserService
from trivoreid.services.namespace_service import NamespaceService
from trivoreid.services.group_service import GroupService
from trivoreid.services.datastorage_service import DataStorageService
from trivoreid.services.mydata_service import MyDataService
from trivoreid.services.profile_service import ProfileService
from trivoreid.services.paycard_service import PaycardService
from trivoreid.services.email_service import EmailService
from trivoreid.services.sms_service import SMSService
from trivoreid.services.authorisation_service import AuthorisationService
from trivoreid.services.contract_service import ContractService
from trivoreid.services.subscription_service import SubscriptionsService
from trivoreid.services.locationsites_service import LocationSiteService
from trivoreid.services.target_service import TargetService
from trivoreid.services.access_control_service import AccessControlService
from trivoreid.services.contact_service import ContactService
from trivoreid.services.access_right_service import AccessRightService
from trivoreid.services.sales_service import SalesService

class TrivoreID:
    '''
    Main class to perform REST API requests to TrivoreID.
    '''

    def __init__(self,
                 path='/etc/trivoreid/client_sdk.properties',
                 oauth=None,
                 access_token=None,
                 server=None,
                 client_id=None,
                 client_secret=None):
        '''
        Args:
            path (str)               : path to the properties file with the
                                       Management API credentials if OAuth was
                                       not used. Default:
                                       /etc/trivoreid/client_sdk.properties
            oauth (OAuth2Session)    : if None, then ManagementAPI credentials
                                       or access token will be used,
            access_token (str)       : when the password grant authorisation
                                       was used.
            server (str)             : server URL. If None, then value from
                                       properties file will be used.
            client_id (str)          : Management API client id. If None, then
                                       value from properties file will be used.
            client_secret (str)      : Management API client secret. If None,
                                       then value from properties file will be
                                       used.

        Example of the properties file:
            service.address=<placeholder>
            mgmtapi.id=<placeholder>
            mgmtapi.secret=<placeholder>
        '''

        USER_INFO = 'openid/userinfo'

        properties = su.get_properties(path)

        if server is None:
            server = properties.pop('service.address', None)

        if server[-1] != '/':
            server += '/'

        self.oidc_user = None

        if access_token is not None:
            access_token = {'Authorization': 'Bearer ' + access_token}
            response = requests.get(server + USER_INFO, headers=access_token)
            if response.status_code is 200:
                self.oidc_user = OIDCUser(response.json())

        if oauth is None and access_token is None:
            if client_id is None:
                client_id = properties.pop('mgmtapi.id', None)
            if client_secret is None:
                client_secret = properties.pop('mgmtapi.secret', None)
        elif oauth is not None:
            response = oauth.get(server + USER_INFO)
            if response.status_code == 200:
                self.oidc_user = OIDCUser(response.json())

        if client_id is None and client_secret is None:
            auth = None
        else:
            auth = (client_id, client_secret)

        creds = self._Credentials(auth, server, oauth, access_token)

        self.group_service = GroupService(creds)
        self.namespace_service = NamespaceService(creds, self.group_service)
        self.user_service = UserService(creds, self.group_service)
        self.datastorage_service = DataStorageService(creds)
        self.mydata_service = MyDataService(creds)
        self.paycard_service = PaycardService(creds)
        self.authorization_service = AuthorisationService(creds)
        self.contract_service = ContractService(creds)
        self.subscription_service = SubscriptionsService(creds)
        self.locationsites_service = LocationSiteService(creds)
        self.target_service = TargetService(creds)
        self.accesscontrol_service = AccessControlService(creds)
        self.contact_service = ContactService(creds)
        self.profile_service = ProfileService(creds, self.oidc_user)
        self.access_right_service = AccessRightService(creds)
        self.sales_service = SalesService(creds)
        self.email_service = EmailService(creds, self.group_service,
                                                        self.user_service)
        self.sms_service = SMSService(creds, self.group_service,
                                                        self.user_service)

    class _Credentials(object):

        def __init__(self, auth, server, oidc_client, access_token):

            self.auth = auth
            self.server = server
            self.oidc_client = oidc_client
            self.access_token = access_token
