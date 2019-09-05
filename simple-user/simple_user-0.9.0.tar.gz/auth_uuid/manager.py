import requests
import logging

from django.contrib.auth.models import UserManager
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from auth_uuid import settings as app_settings


class SimpleUserManager(UserManager):

    def get_by_natural_key(self, username):
        try:
            user = self.get(uuid=username)
        except self.model.DoesNotExist:
            user = self.retrieve_remote_user_by_uuid(username)
        return user

    def create_new_user(self, response):
        # In order to keep backward compatibility: firstly camelcase, otherwise underscore
        return self.update_or_create(
            uuid=response.get('uuid'),
            defaults={
                'is_active': response.get('isActive', response.get('is_active')),
                'is_superuser': response.get('isSuperuser', response.get('is_superuser')),
                'is_staff': response.get('isStaff', response.get('is_staff')),
            }
        )

    def retrieve_remove_user_data_by_uuid(self, uuid):
        import warnings
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn(
            'This method "retrieve_remove_user_data_by_uuid" is deprecated use \
"retrieve_remote_user_data_by_uuid" instead.',
            DeprecationWarning
        )
        return self.retrieve_remote_user_data_by_uuid(uuid)

    def retrieve_remote_user_data_by_uuid(self, uuid):
        logger = logging.getLogger(app_settings.LOGGER_NAME)
        url = settings.URL_VALIDATE_USER_UUID.format(uuid)
        response = None
        try:
            response = requests.get(
                url,
                headers={'USERNAME': settings.AUTH_SECRET_KEY})
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
            response = None

        if response and response.status_code == requests.codes.ok:
            return response.json()
        return None

    def retrieve_remote_user_by_uuid(self, uuid, retrieve_response=False):
        user = AnonymousUser()
        response = self.retrieve_remote_user_data_by_uuid(uuid)

        if response is not None:
            user, _ = self.create_new_user(response)

        if retrieve_response:
            return user, response
        else:
            return user

    def retrieve_remove_user_data_by_cookies(self, cookies):
        logger = logging.getLogger(app_settings.LOGGER_NAME)
        url = settings.URL_VALIDATE_USER_COOKIE
        response = None
        try:
            response = requests.get(url, cookies=cookies)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
            response = None

        if response and response.status_code == requests.codes.ok:
            try:
                return response.json()[0]
            except IndexError:
                return None
        return None

    def retrieve_remote_user_by_cookie(self, cookies):
        if cookies == {}:
            return AnonymousUser()
        response = self.retrieve_remove_user_data_by_cookies(cookies)
        if response is not None:
            user, _ = self.create_new_user(response)
            return user
        return AnonymousUser()
