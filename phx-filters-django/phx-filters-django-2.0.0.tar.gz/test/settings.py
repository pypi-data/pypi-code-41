"""
Minimal Django settings, just enough to get unit tests to run.
"""
from os.path import join
from tempfile import mkdtemp
from uuid import uuid4

BASE_DIR = mkdtemp()
DEBUG = True
INSTALLED_APPS = ['django_nose', 'test']
SECRET_KEY = uuid4().hex
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

DATABASES = {
    'default': {
        # You do not need to set up a database server for unit tests;
        # SQLite will work just fine.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   join(BASE_DIR, 'db.sqlite3'),
    }
}
