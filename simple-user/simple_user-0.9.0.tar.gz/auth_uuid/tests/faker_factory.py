from django.conf import settings

from faker import Faker

faker = Faker(settings.FAKER_SETTINGS_LOCALE)
