import logging
import uuid

from django.conf import settings
from django.contrib.auth.hashers import identify_hasher, get_hasher
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import transaction
from django.db.models import F
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from ..api_gateway.functions import (create_consumer, delete_consumer,
                                        create_consumer_jwt,
                                        create_consumer_acl)
from ..devices.models import Device
from ..services.models import Service, Subscription
from ..utils import get_random_string

from ...models import CreatedAtModel, UpdatableModel, DeactivableModel
from ...common import PROFILE_FIELDS

logger = logging.getLogger('users')


class AbstractUserModel(CreatedAtModel, UpdatableModel, DeactivableModel):
    """
    Abstract user model, the fields below should be defined by 'django.contrib.auth.models.AbstractUser'

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    """

    class Meta:
        abstract = True

    sso_id = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)
    sso_rev = models.PositiveIntegerField(default=1)

    apigw_consumer_id = models.CharField(max_length=36, null=True, blank=True)

    role = models.SmallIntegerField(null=True, blank=True)

    description = models.TextField(_('description'), null=True, blank=True)
    picture = models.TextField(_('picture'), null=True, blank=True)
    birthdate = models.DateField(_('birthdate'), null=True, blank=True)

    latitude = models.FloatField(_('latitude'), null=True, blank=True)
    longitude = models.FloatField(_('longitude'), null=True, blank=True)

    country = models.CharField(_('country'), max_length=46, null=True,
                               blank=True)

    address = models.TextField(_('address'), null=True, blank=True)
    language = models.CharField(_('language'), null=True, blank=True)

    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    language = models.CharField(max_length=3, null=True, blank=True)

    @property
    def is_unsubscribed(self):
        return self.unsubscribed_at is not None

    @is_unsubscribed.setter
    def is_unsubscribed(self, value):
        self.unsubscribed_at = timezone.now()

    def __str__(self):
        return '{}:{}'.format(self.username, self.id)

    def serialized_as_string(self):
        serialized = ''
        for f in PROFILE_FIELDS:
            field = getattr(self, f, None)
            if f == 'password':
                pass
                """
                if field and len(field):
                    print('PASS', f, field)
                    (algorithm, iterations, salt, hash) = field.split('$')
                    print('PASS', (algorithm, iterations, salt, hash))
                    serialized += hash
                else:
                    serialized += str(field)
                """
            else:
                serialized += str(field)


        # logger.debug('serialized_as_string {}'.format(serialized))
        return serialized

    def __init__(self, *args, **kwargs):
        super(AbstractUserModel, self).__init__(*args, **kwargs)
        setattr(self, '__serialized_as_string', self.serialized_as_string())

    def save(self, *args, **kwargs):
        if self._state.adding:
            if not self.first_name:
                self.first_name = ''
            if not self.last_name:
                self.last_name = ''
        return super(AbstractUserModel, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        # password is hashed, checking if will be runtime hardened
        # taken from django.contrib.auth.hashers.check_password
        old_hashed_password = self.password

        preferred = get_hasher('default')
        hasher = identify_hasher(old_hashed_password)

        hasher_changed = hasher.algorithm != preferred.algorithm

        if hasher_changed:
            logger.info(
                '!!! Password hasher for {} changed from {} to {}'.format(self,
                                                                          hasher.algorithm,
                                                                          preferred.algorithm))

        must_update = hasher_changed or hasher.must_update(old_hashed_password)

        if must_update:
            setattr(self, '__password_hardened', True)

        return super(AbstractUserModel, self).check_password(raw_password)

    def create_apigw_consumer(self):
        logger.info('Adding apigw consumer for User {0}'.format(self))
        if not settings.TESTING_MODE:
            status_code_1, consumer = create_consumer(self)
            if status_code_1 != 201:
                logger.error('Error ({0}) creating apigw consumer, {1}'.format(
                    status_code_1, consumer))
                raise Exception(
                    "Error ({0}) creating apigw consumer, {1}".format(
                        status_code_1, consumer))

            status_code_2, acl = create_consumer_acl(self)
            if status_code_2 != 201:
                # delete_apigw_consumer(username)
                logger.error(
                    'Error ({0}) creating apigw consumer acl, {1}'.format(
                        status_code_2, acl))
                raise Exception(
                    "Error {0} creating apigw consumer acl, {1}".format(
                        status_code_2, acl))
            self.apigw_consumer_id = consumer['id']

        else:
            self.apigw_consumer_id = get_random_string(36)

        self.save()

    def add_user_device(self, fingerprint, user_agent=None):
        logger.info(
            'Adding User Device for user {0} with fingerprint {1}'.format(self,
                                                                          fingerprint))

        device = Device(user=self, fingerprint=fingerprint)

        if not settings.TESTING_MODE:
            status_code, r1 = create_consumer_jwt(self)
            if status_code != 201:
                # delete_apigw_consumer(username)
                logger.error(
                    'Error ({0}) creating apigw consumer JWT, {1}'.format(
                        status_code, r1))
                raise Exception(
                    "Error creating apigw consumer jwt, {}".format(status_code))

            device.apigw_jwt_id = r1.get('id')
            device.apigw_jwt_key = r1.get('key')
            device.apigw_jwt_secret = r1.get('secret')

        else:
            device.apigw_jwt_id = get_random_string(36)
            device.apigw_jwt_key = get_random_string(32)
            device.apigw_jwt_secret = get_random_string(32)

        device.save()

        return device

    def remove_user_device(self, device):
        logger.info('Removing Device {0}'.format(device.id))
        device.delete()
        return 1

    def remove_all_user_devices(self):
        logger.info('Removing All User Devices for {0}'.format(self))
        removed = 0
        for d in self.devices.all():
            removed += self.remove_user_device(d)
        return removed

    def update_rev(self, commit=False):
        logger.info('Updating rev for User {0}'.format(self))
        self.sso_rev = F('sso_rev') + 1
        if commit:
            self.save()
            self.refresh_from_db()

    def unsubscribe(self):
        logger.info('Unsubscribing User {0}'.format(self))
        try:
            with transaction.atomic():
                self.unsubscribed_at = timezone.now()
                self.is_active = False
                self.update_rev(True)

        except Exception as e:
            logger.error(
                'Unsubscription error {0} for User {1}'.format(e, self),
                exc_info=True)

    def subscribe_to_service(self, referrer, update_rev=False, commit=True):
        logger.info('Subscribinig {0} to service {1}'.format(self, referrer))

        service = Service.objects.get(url=referrer)

        subscription, _subscription_created = \
            Subscription.objects.get_or_create(
            user=self, service=service)

        if _subscription_created:
            logger.info('Created service subscrption for {0}'.format(self))
            if update_rev:
                setattr(self, '__subscription_updated', True)
                self.update_rev(commit)
        else:
            logger.info(
                'User {0} already subscribed to {1}'.format(self, service))

        return _subscription_created

    def unsubscribe_from_service(self, subscription, update_rev=False,
                                 commit=True):
        logger.info('Unubscribinig {0} form service {1}'.format(self,
                                                                subscription.service))
        setattr(self, '__subscription_updated', True)

        subscription.unsubscribed_at = timezone.now()
        subscription.save()

        if update_rev:
            self.update_rev(commit)


class User(AbstractUser, AbstractUserModel):
    """
    User class
    """

    def get_absolute_url(self):
        return reverse("user:detail", args=[self.sso_id])


# Signals

@receiver(pre_save, sender=User)
def check_upated_fields(sender, instance, **kwargs):
    if not instance._state.adding:  # if instance.pk:
        email_updated = hasattr(instance, '__email_updated')
        subscription_updated = hasattr(instance, '__subscription_updated') or instance.is_unsubscribed
        password_updated = hasattr(instance, '__password_updated')
        field_updated = instance.__serialized_as_string != \
                        instance.serialized_as_string()

        update_rev = False

        if field_updated:
            logger.info('User {0} updated PROFILE_FIELDS \n{1}\n{2}'.format(instance, instance.__serialized_as_string, instance.serialized_as_string()))
            update_rev = True

        if email_updated:
            logger.info('User {0} updated email'.format(instance))

        if password_updated:
            logger.info('User {0} updated password'.format(instance))

        if subscription_updated:
            logger.info('User {0} updated subscription'.format(instance))

        if email_updated or password_updated or field_updated or subscription_updated:
            # __password_hardened attribute set by
            # backend.serializers.LoginSerializer on runtime password hardening
            update_rev = True

        if hasattr(instance, '__password_hardened'):
            update_rev = False

        if update_rev:
            instance.update_rev()  # updating rev
            setattr(instance, '__rev_updated', True)

            logger.info('rev updated, removing all devices for user {}.'.format(instance))
            instance.remove_all_user_devices()


@receiver(post_save, sender=User)
def fetch_from_db_if_updated(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '__rev_updated'):
        logger.info('User {0} updated rev, refreshing instance from DB'.format(instance))
        instance.refresh_from_db()


@receiver(pre_delete, sender=User)
def delete_apigw_user_consumer(sender, instance, **kwargs):
    logger.info('Deleting apigw Consumer for User {0}'.format(instance))
    if not settings.TESTING_MODE:
        status_code, r1 = delete_consumer(instance)
        logger.info('Kong consumer deleted ({0}), {1}'.format(status_code, r1))
        if status_code >= 300:
            if status_code != 404:
                # delete_apigw_consumer(username)
                logger.error(
                    'Error ({0}) Deleting apigw consumer for User {1}, {2}'.format(
                        status_code, instance, r1))
                raise Exception(
                    "Error deleting apigw consumer, {}".format(status_code))
