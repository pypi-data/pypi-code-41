import logging

from django.apps import AppConfig

from .. import settings

logger = logging.getLogger("profiles")


class ProfilesConfig(AppConfig):
    name = 'django_sso_app.app.profiles'

    def ready(self):
        from .utils import get_profile_model

        profile_model = get_profile_model()

        for el in settings.DJANGO_SSO_REQUIRED_PROFILE_FIELDS:
            if getattr(profile_model, el, None) is None:
                raise Exception(
                    'App profile {0} is missing {1} field'.format(profile_model,
                                                                  el))

        super(ProfilesConfig, self).ready()
        logger.info("django-sso-app profiles app ready!")
