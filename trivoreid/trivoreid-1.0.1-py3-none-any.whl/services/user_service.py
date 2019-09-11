#!/usr/bin/env python
# coding: utf-8

import requests
import string
import random
import logging

from random import SystemRandom
import trivoreid.utils.service_utils as su
from trivoreid.utils.criteria import Filter
from trivoreid.models.groups import Group
from trivoreid.models.page import Page
from trivoreid.models.pass_requirements import PasswordRequirements
from trivoreid.models.enterprise import Enterprise
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException
from trivoreid.models.user import (User, StrongIdentification,
                                  PasswordUpdateResult)

class UserService(object):
    '''
    Class to wrap Trivore ID /user APIs
    '''

    _USERS = 'api/rest/v1/user'
    _USER = 'api/rest/v1/user/{}'
    _USER_EMAIL_VERIFY = 'api/rest/v1/user/{}/email/verify'
    _USER_SMS_CODE_VERIFY = 'api/rest/v1/user/{}/sms/verify/send'
    _USER_SMS_CODE_VERIFY_CHECK = 'api/rest/v1/user/{}/sms/verify/check/{}'
    _USER_SMS_LINK_VERIFY = 'api/rest/v1/user/{}/sms/verify/sendLink'
    _INVITE_USER = 'api/rest/v1/invite/user'
    _USER_ENTERPRISE = 'api/rest/v1/user/{}/enterprise'
    _USER_CUSTOM_FIELDS = 'api/rest/v1/user/{}/customfields'
    _PASSWORD_REQUIREMENTS = 'api/rest/v1/user/{}/password/requirements'
    _STRONG_IDENTIFICATION = 'api/rest/v1/user/{}/strongidentification'
    _PASSWORD = 'api/rest/v1/user/{}/password'
    _CUSTOM_PERMISSIONS = 'api/rest/v1/user/{}/permissions/custom'
    _EFFECTIVE_PERMISSIONS = 'api/rest/v1/user/{}/permissions/effective'
    _BUILTIN_ROLES = 'api/rest/v1/user/{}/roles/builtin'
    _CUSTOM_ROLES = 'api/rest/v1/user/{}/roles/custom'

    def __init__(self, credentials, group_service):
        self._group_service = group_service
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._header = credentials.access_token

    def get_all(self,
                filter_fields=None,
                start_index=0,
                count=100):
        '''Get the list of the users.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of users.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        uri = su.uri(self._server, self._USERS)
        response = self._session.get(uri, params=params,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} users'.format(len(response.json()['resources'])))
            users = []
            for user in response.json()['resources']:
                users.append(User(user))
            page = Page(response.json(), users)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self,
               users,
               password_length=15,
               password=None,
               email_verification=False,
               mobile_verification=False):
        '''Create new user.
        Args:
            users (User, list)         : user or a list of users to create.
            password_length (int)      : length of the generated password
            password (str)             : if None, password will be randomly
                                         generated.
            email_verification (bool)  : send email verification after creating
                                         a user account.
            mobile_verification (bool) : send mobile verification after creating
                                         a user account.
        Returns:
            New user object and user's password.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the User is wrong or namespace
                                  code was not defined
        '''
        if 'User' not in str(type(users)) and type(users) != list:
            raise TrivoreIDSDKException('User type is wrong!')
        elif type(users) == list:
            for u in users:
                if 'User' not in str(type(u)):
                    raise TrivoreIDSDKException('User type is wrong!')

        if type(users) != list:
            users = [users]

        result = []

        for user in users:

            if password is None:
                pattern = string.ascii_letters + string.digits
                password = ''
                # to avoid repeating letters
                for i in range (int(password_length/2)):
                    password += ''.join(random.sample(pattern, 2))
                if password_length % 2 == 1:
                    password += random.sample(pattern, 1)[0]

            user.password = password
            if bool(user.memberOf):
                user.memberOf = self._check_groups(user.memberOf, user.nsCode)

            uri = su.uri(self._server, self._USERS)
            response = self._session.post(uri, json=user.serialize(),
                                               headers=self._header,
                                               auth=self._auth)

            if response.status_code == 201:
                usr = User(response.json())
                logging.info('Successfully created user with id {}'.format(
                                    usr.id))
                fails = []
                if email_verification:
                    logging.info('Sending email verification to the user email(s)')
                    for email in usr.emails.emails:
                        try:
                            self.verify_email(usr.id, email.email['address'])
                        except TrivoreIDException as e:
                            fails.append(e.args[0])

                if mobile_verification:
                    logging.info('Sending mobile verification to the user mobile(s)')
                    for mobile in usr.mobiles.mobiles:
                        try:
                            self.verify_sms_link(usr.id,
                                                 mobile['number'])
                        except TrivoreIDException as e:
                            fails.append(e.args[0])

                if len(fails) > 0:
                    raise TrivoreIDException(', '.join(fails))

                usr.password = password
                result.append(usr)

            else:
                raise TrivoreIDException(su.error_response_message(response),
                                         response.status_code)

        if len(result) == 1:
            return result[0]
        else:
            return result

    def get(self, userId):
        '''Get a single user by id.
        Args:
            userId (str) : user's unique identifier
        Returns:
            A user.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._USER).format(userId)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Found user with id {}'.format(userId))
            return User(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, user, userId=None):
        '''Update existing user.
        Args:
            user (User)  : user to modify.
            userId (str) : if None, then user ID from the User object will
                           be used.
        Returns:
            Modified user object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the user is wrong.
        '''
        if 'User' not in str(type(user)):
            raise TrivoreIDSDKException('User type is wrong!')

        # removing user's password
        user.password = None

        user.memberOf = self._check_groups(user.memberOf, user.nsCode)
        if userId is None:
            userId = user.id

        uri = su.uri(self._server, self._USER).format(userId)
        response = self._session.put(uri, json=user.serialize(),
                                          headers=self._header,
                                          auth = self._auth)

        if response.status_code is 200:
            usr = User(response.json())
            logging.info('Successfully modified user with the id {}'
                        .format(usr.id))
            return usr
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, userId):
        '''Delete user by id.
        Args:
            userId (str) : user's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._USER).format(userId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted user with id {}'.format(userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def verify_email(self,
                     userId,
                     email=None,
                     return_url=None,
                     expiration_days=7):
        '''
        Send request to verify user's email address.
        Args:
            userId (str) : user's unique identifier
            email (str) : The email address that shoudld be verified.
            return_url (str) : If not specified, user is directed to
                               identification service front page.
            expiration_days (int) : If not specified, current policies or
                                    default value is used.
        '''
        request_body = {}
        if email is not None:
            request_body['value'] = email
        if return_url is not None:
            request_body['returnURL'] = return_url
        if expiration_days is not None:
            request_body['expirationDays'] = expiration_days

        uri = su.uri(self._server, self._USER_EMAIL_VERIFY).format(userId)
        response = self._session.post(uri, json=request_body,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully sent the email verification request to the' +
                            ' user with id {}'.format(userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def verify_sms_code(self, userId, mobile=None):
        '''
        Send request to verify user's mobile number.
        Args:
            userId (str)     : user's unique identifier
            mobile (str)     : The mobile number that shoudld be verified.
        '''
        params = {}
        if mobile is not None:
            params['mobile'] = mobile

        uri = su.uri(self._server, self._USER_SMS_CODE_VERIFY).format(userId)
        response = self._session.post(uri, params=params,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully sent the mobile verification code to the' +
                'mobile number {} and  user with id {}'.format(mobile, userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def verify_sms_code_check(self, userId, code):
        '''
        Check user's sms verification code.
        Args:
            userId (str)   : user's unique identifier
            code (str) : The code to check.
        Returns:
            retult (bool) : True if correct and False if incorrect
        '''

        uri = su.uri(self._server, self._USER_SMS_CODE_VERIFY_CHECK
                                                    .format(userId, code))

        response = self._session.post(uri, headers=self._header,
                                           auth=self._auth)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def verify_sms_link(self,
                        userId,
                        mobile=None,
                        return_url=None,
                        expiration_days=7):
        '''
        Send request to verify user's mobile number.
        Args:
            userId (str)              : user's unique identifier
            mobile (str)          : The mobile number that shoudld be verified.
            return_url (str)      : If not specified, user is directed to
                                    identification service front page.
            expiration_days (int) : If not specified, current policies or
                                    default value is used.
        '''
        request_body = {}
        if mobile is not None:
            request_body['value'] = mobile
        if return_url is not None:
            request_body['returnURL'] = return_url
        if expiration_days is not None:
            request_body['expirationDays'] = expiration_days

        uri = su.uri(self._server, self._USER_SMS_LINK_VERIFY).format(userId)
        response = self._session.post(uri, json=request_body,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully sent the mobile verification link to the' +
                'mobile number {} and  user with id {}'.format(mobile, userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def invite(self, invite):
        '''Invite new user.
        Args:
            invite (Invite) : invite request.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the invite is wrong.
        '''
        if 'Invite' not in str(type(invite)):
            raise TrivoreIDSDKException('Invite type is wrong!')

        invite.request_body['groups'] = self._check_groups(
                                                invite.request_body['groups'],
                                                invite.request_body['nsCode'])

        uri = su.uri(self._server, self._INVITE_USER)
        response = self._session.post(uri, json=invite.request_body,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully sent the invitation request')
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_enterprise(self, userId):
        '''Get the enterprise by user's id.
        Args:
            userId (str) : user's unique identifier
        Returns:
            An Enterprise.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''

        uri = su.uri(self._server, self._USER_ENTERPRISE).format(userId)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Found enterprise from user with id {}'.format(userId))
            return Enterprise(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_enterprise(self, userId, enterprise):
        '''Update user's enterprise.
        Args:
            userId (str)                : user's unique identifier
            enterprise (Enterprise) : enterprise to modify
        Returns:
            Modified Enterprise.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the enterprise is wrong.
        '''
        if 'Enterprise' not in str(type(enterprise)):
            raise TrivoreIDSDKException('Enterprise type is wrong!')

        uri = su.uri(self._server, self._USER_ENTERPRISE).format(userId)

        response = self._session.put(uri, json=enterprise.serialize(),
                                          headers=self._header,
                                          auth = self._auth)

        if response.status_code is 200:
            ent = Enterprise(response.json())
            logging.info('Successfully modified enterprise with the user id {}'
                                        .format(userId))
            return ent
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_custom_fields(self, userId):
        '''Get the user custom fields.
        Args:
            userId (str) : user's unique identifier
        Returns:
            Custom fields.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''

        uri = su.uri(self._server, self._USER_CUSTOM_FIELDS).format(userId)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Found custom fields of the user with id {}'.format(userId))
            return response.content
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_custom_fields(self, userId, custom_fields):
        '''Update user custom fields.
        Args:
            userId (str)            : user's unique identifier
            custom_fields (dict)    : custom_fields to update. Must be json
                                      serializable.

        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._USER_CUSTOM_FIELDS).format(userId)
        response = self._session.post(uri, json=custom_fields,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully modified custom fields of the user id {}'
                                        .format(userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_custom_fields(self, userId):
        '''Delete ALL user custom fields.
        Args:
            userId (str) : user's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._USER_CUSTOM_FIELDS).format(userId)
        response = self._session.delete(uri, headers=self._header,
                                             auth = self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted custom fields of the user with id {}'
                                                                .format(userId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_password_requirements(self, userId):
        '''Get the password requirements.
        Args:
            userId (str) : user's unique identifier
        Returns:
            Password requirements.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._PASSWORD_REQUIREMENTS).format(userId)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)


        if response.status_code is 200:
            logging.info('Found password requirements of the user with id {}'
                                                            .format(userId))
            return PasswordRequirements(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_strong_identification(self, userId):
        '''Get strong identification info.
        Args:
            userId (str) : user's unique identifier
        Returns:
            Strong identification.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._STRONG_IDENTIFICATION).format(userId)
        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully found strong identification of the user with id {}'
                                                            .format(userId))
            return StrongIdentification(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def report_strong_identification(self, userId, personalId, remarks=None):
        '''Report strong identification.
        Args:
            userId (str) : user's unique identifier
            personalId (str) : personal ID code
            remarks (str) : optional additional remarks about identification
        Returns:
            Updated strong identification.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._STRONG_IDENTIFICATION).format(userId)

        data = { 'personalId' : personalId, 'remarks' : remarks }

        response = self._session.post(uri, json=data,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully reported strong identification of the user with id {}'
                                                            .format(userId))
            return StrongIdentification(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def change_password(self, userId, new_password):
        '''Change user's password
        Args:
            userId (str) : user's unique identifier
            new_password (str) : new password
        Returns:
            Updated password result.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._PASSWORD).format(userId)

        data = {'newPassword' : new_password}

        response = self._session.put(uri, json=data,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            result = PasswordUpdateResult(response.json())
            if result.success:
                logging.info('Successfully changed the password of the user with id {}'
                                                            .format(userId))
                return result
            else:
                logging.info('Failed to change the password of the user with id {}'
                                                            .format(userId))
                return result
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_custom_permissions(self, userId):
        '''Get custom permissions of the user.
        Args:
            userId (str) : user's unique identifier
        Returns:
            List with custom permissions.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CUSTOM_PERMISSIONS).format(userId)

        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully found custom permissions of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_custom_permissions(self, userId, add=None, remove=None):
        '''Get custom permissions of the user.
        Args:
            userId (str)  : user's unique identifier
            add (list)    : list of permissions to add
            remove (list) : list of permissions to remove
        Returns:
            List with updated custom permissions.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CUSTOM_PERMISSIONS).format(userId)

        data = {'add': add, 'remove': remove}

        response = self._session.put(uri, json=data,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully updated custom permissions of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_effective_permissions(self, userId):
        '''Get effective permissions of the user.
        Args:
            userId (str) : user's unique identifier
        Returns:
            List with effective permissions.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._EFFECTIVE_PERMISSIONS).format(userId)

        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully found effective permissions of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_builtin_roles(self, userId):
        '''Get builtin roles of the user.
        Args:
            userId (str) : user's unique identifier
        Returns:
            List with builtin roles.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._BUILTIN_ROLES).format(userId)

        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully found builtin roles of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_builtin_roles(self, userId, add=None, remove=None):
        '''Get builtin roles of the user.
        Args:
            userId (str)  : user's unique identifier
            add (list)    : list of builtin roles to add
            remove (list) : list of builtin roles to remove
        Returns:
            List with updated builtin roles.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._BUILTIN_ROLES).format(userId)

        data = {'add': add, 'remove': remove}

        response = self._session.put(uri, json=data,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully updated builtin roles of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_custom_roles(self, userId):
        '''Get custom roles of the user.
        Args:
            userId (str) : user's unique identifier
        Returns:
            List with custom roles.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CUSTOM_ROLES).format(userId)

        response = self._session.get(uri, headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully found custom roles of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_custom_roles(self, userId, add=None, remove=None):
        '''Get custom roles of the user.
        Args:
            userId (str)  : user's unique identifier
            add (list)    : list of custom roles to add
            remove (list) : list of custom roles to remove
        Returns:
            List with updated custom roles.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CUSTOM_ROLES).format(userId)

        data = {'add': add, 'remove': remove}

        response = self._session.put(uri, json=data,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Successfully updated custom roles of the user with id {}'
                                                            .format(userId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def _check_groups(self,
                      groups,
                      nsCode):
        '''
        Replace corresponding group names with their ids.
        Args:
            groups (list)             : group list
            nsCode (srt)              : namespace code
            include_supervisor (bool) : if supervisor should be included. If
                                        False, excludes it from the list.
        Returns:
            New list with group ids.
        '''

        # get all groups
        all_groups = self._group_service.get_all(
                                Filter(Filter.EQUAL, 'nsCode', nsCode)).resources

        for i in range(len(groups)):
            # if name of the group in the list - get this group id
            is_name = False
            is_id = False
            for group in all_groups:
                if group.name == groups[i]:
                    is_name = True
                elif group.id == groups[i]:
                    is_id = True
            if is_name:
                group = self._group_service.get_all(Filter().and_filters(
                            Filter(Filter.EQUAL, 'name', groups[i]),
                            Filter(Filter.EQUAL, 'nsCode', nsCode)
                        )).resources[0]
                groups[i] = group.id
            elif not is_id:
                group = self._group_service.create(Group({
                            'name' : groups[i],
                            'nsCode' : nsCode
                    }))
                groups[i] = group.id

        return groups
