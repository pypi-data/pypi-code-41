import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings.tests'
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

from django.test.utils import get_runner
from django.conf import settings

def runtests():
    test_runner = get_runner(settings)
    failures = test_runner([], verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
