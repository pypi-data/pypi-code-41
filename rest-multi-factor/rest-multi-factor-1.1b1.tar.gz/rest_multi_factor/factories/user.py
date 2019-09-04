from factory import lazy_attribute
from factory import DjangoModelFactory, Faker

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = Faker("first_name")
    last_name = Faker("last_name")

    password = make_password("password")

    @lazy_attribute
    def username(self):
        return "{0}-{1}".format(self.first_name, self.last_name).lower()

    @lazy_attribute
    def email(self):
        return "{0}@example.com".format(self.username).lower()
