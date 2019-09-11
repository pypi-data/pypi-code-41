import logging
from django.contrib.auth.models import Group as GroupModel
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse

from ..api_gateway.functions import create_consumer_acl, delete_consumer_acl

logger = logging.getLogger('groups')


class Group(GroupModel):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("group:detail", args=[self.pk])


# signals

def create_user_group(user, group):
    logger.info('creating user group {} for {}'.format(group, user))
    if not settings.TESTING_MODE:
        status_code, resp = create_consumer_acl(user, group.name)
        print('CREATED', status_code, resp)

def delete_user_group(user, group):
    logger.info('deleting user group {} for {}'.format(group, user))
    if not settings.TESTING_MODE:
        status_code, resp = delete_consumer_acl(user, group.name)
        print('DELETED', status_code)


@receiver(m2m_changed)
def signal_handler_when_user_is_added_or_removed_from_group(action, instance, pk_set, model, **kwargs):
    if model == GroupModel:
        user = instance
        user_updated = False
        if action == 'pre_add':
            user_updated = True
            for pk in pk_set:
                group = Group.objects.get(id=pk)
                create_user_group(user, group)
        elif action == 'pre_remove':
            user_updated = True
            for pk in pk_set:
                group = Group.objects.get(id=pk)
                delete_user_group(user, group)
        if user_updated:
            user.update_rev(True)
