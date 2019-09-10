import logging

from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate as activate_translation

from allauth.account import app_settings as allauth_settings
from allauth.utils import get_username_max_length
from allauth.account.models import EmailAddress

from rest_auth.registration.serializers import RegisterSerializer as rest_authRegisterSerializer
from rest_auth.serializers import LoginSerializer as rest_authLoginSerializer
from rest_auth.serializers import PasswordResetSerializer as rest_authPasswordResetSerializer
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError

from ..common import PROFILE_FIELDS
from ..apps.users.serializers import UserSerializer
from ..functions import get_country_language

logger = logging.getLogger('backend')


class LoginSerializer(rest_authLoginSerializer):
    username = serializers.CharField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    password = serializers.CharField(style={'input_type': 'password'})
    fingerprint = serializers.CharField()

    def _validate_fingerprint(self, fingerprint):
        if fingerprint is None:
            msg = _('Must include valid "fingerprint".')
            raise exceptions.ValidationError(msg)

        return fingerprint


class RegisterSerializer(rest_authRegisterSerializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=False, default='')

    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    picture = serializers.CharField(required=False, allow_null=True)
    birthdate = serializers.DateField(required=False, allow_null=True)

    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)

    country = serializers.CharField(required=True)
    address = serializers.CharField(required=False, allow_null=True)

    language = serializers.CharField(required=False, allow_null=True)

    referrer = serializers.CharField(required=True)

    def get_cleaned_data(self):
        super(RegisterSerializer, self).get_cleaned_data()
        
        d = {
            'username': self.validated_data.get('username', None),
            'password1': self.validated_data.get('password1', None),
            'password2': self.validated_data.get('password2', None),
            'referrer': self.validated_data.get('referrer', None)
        }
        
        for f in PROFILE_FIELDS:
            d[f] = self.validated_data.get(f, None)

        if d['language'] is None:
            d['language'] = get_country_language(d['country'])

        return d

    def custom_signup(self, request, user):
        referrer = self.cleaned_data.get('referrer')
        user.subscribe_to_service(referrer)

    def save(self, request):
        try:
            with transaction.atomic():
                return super(RegisterSerializer, self).save(request)

        except Exception as e:
            logger.error('Error registering user: {}'.format(e), exc_info=True)
            raise

class PasswordResetSerializer(rest_authPasswordResetSerializer):
    """
    Uses allauth default email templates
    """
    def validate_email(self, value):
        value = super(PasswordResetSerializer, self).validate_email(value)
        saved_email = EmailAddress.objects.get(email=value)
        if not saved_email.verified:
            raise ValidationError(
                _('E-mail address not verified: %(value)s'),
                code='invalid',
                params={'value': value},
            )

        user = saved_email.user
        user_language = user.language
        logger.info('Rendering mail for {0} with language {1}'.format(user, user_language))
        activate_translation(user_language)

        return value

    def get_email_options(self):
        """Override this method to change default e-mail options"""

        return {
            'email_template_name': 'account/email/password_reset_key_message.txt',
            'html_email_template_name': 'account/email/password_reset_key_message.html',
            'use_https': settings.ENABLE_HTTPS,
            'extra_email_context': {
                'EMAILS_DOMAIN': settings.EMAILS_DOMAIN,
                'EMAILS_SITE_NAME': settings.EMAILS_SITE_NAME
            }
        }

class CsrfTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    token = serializers.CharField()
    user = UserSerializer()
    passepartout_redirect_url = serializers.CharField(required=False)
