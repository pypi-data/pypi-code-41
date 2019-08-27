from django.conf import settings
from django.contrib.auth import get_user_model
from .models import KV

class GlobalUser:

    @property
    def key(self):
        object_key = getattr(settings, 'NOSQL_USER_OBJECT_KEY', 'user')
        return "{}:{}".format(object_key, self.id)

    def __init__(self, id):
        self.id = id
        key =  self.key
        self.data = KV.get(key, {})
        self.spaces = self.data.get("permissions", {}).get("spaces", [])

    def set(self, serialized_data):
        return KV.set(self.key, serialized_data)

    def get(self):
        return KV.get(self.key)

    def get_permissions(self, key):
        return self.data.get("permissions", {}).get(key, [])

    @property
    def as_django_user(self):
        """
        Create a transient django user (not saved to database)
        """
        user = get_user_model()
        user.id = self.id
        user.key = self.key
        user.data = self.data
        user.spaces = self.spaces
        return user