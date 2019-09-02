import logging

from rest_framework import authentication

from .settings import (DJANGO_SSO_CONSUMER_USERNAME_HEADER,
                       DJANGO_SSO_ANONYMOUS_CONSUMER_USERNAME,
                       DJANGO_SSO_ANONYMOUS_CONSUMER_HEADER,
                       DJANGO_SSO_HAS_EXTERNAL_USER_PROFILE_MODEL)
from .utils import get_profile_model, create_local_profile_from_headers, get_sso_id

logger = logging.getLogger('django_sso_app')
UserProfileModel = get_profile_model()


def get_apigw_user(request):
    is_anonymous = request.META.get(DJANGO_SSO_ANONYMOUS_CONSUMER_HEADER, None) is not None
    apigw_consumer_id = get_sso_id(
        request.META.get(DJANGO_SSO_CONSUMER_USERNAME_HEADER, DJANGO_SSO_ANONYMOUS_CONSUMER_USERNAME))

    logger.debug('Got apigw_consumer_id: {}'.format(apigw_consumer_id))

    # Consumer is anonymous
    if is_anonymous or apigw_consumer_id == DJANGO_SSO_ANONYMOUS_CONSUMER_USERNAME:
        logger.info('Apigw says user is anonymous')
        return

    try:
        user_profile = UserProfileModel.objects.get(sso_id=apigw_consumer_id)
        user = user_profile
        if DJANGO_SSO_HAS_EXTERNAL_USER_PROFILE_MODEL:
            user = user_profile.user

    except UserProfileModel.DoesNotExist:
        logger.info(
            'User with sso_id: {} does not exists, creating new one'.format(apigw_consumer_id))
        user = create_local_profile_from_headers(request)

    finally:
        return user


class DjangoSsoAppAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user = get_apigw_user(request)
        logger.info('DjangoSsoAppAuthentication: authenticated as {}'.format(user))
        return user, None
