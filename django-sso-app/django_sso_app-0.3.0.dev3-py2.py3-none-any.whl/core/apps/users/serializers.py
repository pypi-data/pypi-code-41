import logging

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.utils import (get_username_max_length)

from rest_framework import serializers
from rest_framework.reverse import reverse

from django.conf import settings

from ...serializers import AbsoluteUrlSerializer
from ...functions import get_country_language

from .models import PROFILE_FIELDS, User

logger = logging.getLogger('users')


class CheckUserExistenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('sso_id',)
        read_only_fields = ('sso_id',)


class UserSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField(required=False)
    email_verified = serializers.SerializerMethodField(required=False)

    groups = serializers.SerializerMethodField(required=False)

    class Meta:
        model = User
        read_only_fields = (
        'sso_id', 'sso_rev', 'date_joined', 'username', 'is_unsubscribed',
        'is_active', 'subscriptions', 'email_verified', 'groups')
        fields = read_only_fields + PROFILE_FIELDS

    def get_subscriptions(self, instance):
        serialized = []
        for el in instance.subscriptions.all():
            serialized.append({
                'url': el.service.url,
                'is_unsubscribed': el.is_unsubscribed
            })
        return serialized

    def get_email_verified(self, instance):
        email_address = instance.emailaddress_set.get(email=instance.email)
        return email_address.verified

    def get_groups(self, instance):
        groups = list(instance.groups.values_list('name', flat=True))

        if instance.is_staff:
            groups.append('staff')

        return groups

    def update(self, instance, validated_data):
        user = instance
        request = self.context.get("request")
        requesting_user = request.user
        skip_confirmation = request.GET.get('skip_confirmation', None)
        must_confirm_email = True

        logger.info(
            'User {0} wants to update user {1}'.format(requesting_user, user))

        if skip_confirmation is not None and requesting_user.is_staff:
            must_confirm_email = False

        new_email = validated_data.get('email', None)
        if (new_email is not None):

            if new_email == user.email:  # !! because of app shitty logic (
                # always sends all fields)
                logger.info('{0} is has same email'.format(user))

            else:
                logger.info(
                    '{0} is changing email for user {1}, email confirmation '
                    'is {2}'.format(
                        requesting_user, user, must_confirm_email))

                adapter = get_adapter()

                created_email = EmailAddress.objects.add_email(request, user,
                                                               new_email,
                                                               confirm=must_confirm_email)
                logger.info(
                    'A new EmailAddress for {0} has been created with id {1}'
                    ''.format(
                        new_email, created_email.id))

                if not must_confirm_email:
                    adapter.confirm_email(None, created_email)

                setattr(user, '__email_updated', True)

        new_password = validated_data.get('password', None)
        if (new_password is not None):
            logger.info(
                '{0} is changing password for user {1}'.format(requesting_user,
                                                               user))
            validated_data.pop(
                'password')  # serializer must NOT save the received plain
            # password, password update logic performed by user.set_password

            user.set_password(new_password)

            setattr(user, '__password_updated', True)

        # devices will be removed by signal
        # actual_devices = user.devices.all()
        # actual_devices_count = actual_devices.count()
        # deleted_devices = user.remove_all_user_devices()

        return super(UserSerializer, self).update(instance, validated_data)

    def to_representation(self, obj):
        # get the original representation
        ret = super(UserSerializer, self).to_representation(obj)
        req = self.context.get('request', None)

        if req is not None:
            # remove field if password if not asked
            with_pass = req.query_params.get('with_password',
                                             not settings.DJANGO_SSO_HIDE_PASSWORD_FROM_USER_SERIALIZER)

            if not with_pass:
                ret.pop('password')

        # return the modified representation
        return ret


class NewUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=True)

    referrer = serializers.CharField(required=True)

    class Meta:
        model = User
        read_only_fields = ('sso_id', 'sso_rev')
        fields = PROFILE_FIELDS + ('username', 'referrer') + read_only_fields

    def create(self, validated_data):
        vd = validated_data.copy()  # must remove referrer because
        # NewUserSerializer has no referrer field
        vd.pop('referrer', None)

        logger.debug('VALIDATED DATA NEW USER {}'.format(vd))
        user_language = vd.get('language', None)
        if user_language is None:
            user_country = vd.get('country')
            vd['language'] = get_country_language(user_country)

        # creating user from cleaned validated data
        new_user = super(NewUserSerializer, self).create(vd)

        user_email = validated_data.get('email')
        request = self.context.get("request")
        requesting_user = request.user
        skip_confirmation = request.query_params.get('skip_confirmation', None)
        must_confirm_email = True
        user_password = validated_data.get('password')
        password_is_hashed = request.query_params.get('password_is_hashed',
                                                      None)
        referrer = validated_data.get('referrer')

        if password_is_hashed is None:
            new_user.set_password(user_password)

            new_user.save()

        if skip_confirmation is not None and requesting_user != new_user and \
                requesting_user.is_staff:
            must_confirm_email = False

        email_address = EmailAddress.objects.add_email(request, new_user,
                                                       user_email,
                                                       confirm=must_confirm_email)

        if not must_confirm_email:
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()

        logger.info(
            '{0} has created user {1}'.format(requesting_user, new_user))

        new_user.subscribe_to_service(referrer)

        return new_user


class UserUnsubscriptionSerializer(serializers.Serializer):
    password = serializers.CharField()


class UserRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ('sso_id', 'sso_rev')
        fields = read_only_fields
