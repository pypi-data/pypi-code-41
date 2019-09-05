from django.contrib.auth import get_user_model
from django.conf import settings

import stringcase


class UserWrapper:

    user = None
    user_data = {}

    def __init__(self, uuid=None, user=None):
        assert uuid is not None or user is not None

        if user is None:
            self.user, _ = get_user_model().objects.get_or_create(
                uuid=uuid.__str__())
        else:
            self.user = user
            uuid = self.user.uuid

        try:
            self.user_data = self.user.wrapper
        except AttributeError:
            self.get_user(uuid.__str__())
            self.user.wrapper = self.user_data

    def get_user(self, uuid):
        self.user_data = get_user_model().objects.retrieve_remote_user_data_by_uuid(uuid)

    @property
    def is_consultant(self):
        return self.consultant_id is not None

    def get_full_name(self):
        return self.full_name if self.full_name else self.short_name

    @property
    def groups(self):
        return [group['name'] for group in self.user_data.get('groups')]

    @property
    def is_delivery_manager(self):
        return settings.OPPORTUNITIES_DELIVERY_MANAGER_GROUP in self.groups

    @property
    def profile_picture_96(self):
        return [value for key, value in self.user_data.get('profilePicture') if key[0] == 96][0]

    def get_profile_picture(self, size):
        return list(filter(lambda x: x[0][0] == size, self.profile_picture,))[0][1]

    def __getattr__(self, name):
        name = stringcase.camelcase(name)
        if name in self.user_data:
            return self.user_data.get(name)
        else:
            raise AttributeError