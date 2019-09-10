# coding: utf-8
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'secret-key'
INSTALLED_APPS = [
    "tests",
]


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Redis
REDIS_CONF = {
    'default': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'decode_responses': True,
    },
    'test': {
        'host': 'localhost',
        'port': 6379,
        'db': 1,
        'password': None,
        'decode_responses': True,
    },
}
