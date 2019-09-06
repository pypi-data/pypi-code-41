from setuptools import find_packages, setup
import os
import io

# Package meta-data.
NAME = 'ukchurn_classification_model'
DESCRIPTION = 'A library for predicting pannelist churn.'
URL = 'https://github.com/diogo22santos/churn_model.git'
EMAIL = 'diogo.santos@kantar.com'
AUTHOR = 'Lisbon Data Science Hub'
REQUIRES_PYTHON = '>=3.7.4'
EXCLUDED_FOLDERS = ['ukchurn_classification_model.tests', 'ukchurn_classification_model.tests.model_quality_tests', 'ukchurn_classification_model.tests.unit_tests']


# Required packages for modules execution
def list_reqs(fname='requirements.txt'):
    with open(fname) as fd:
        return fd.read().splitlines()


# Import the README and use it as the long-description.
here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


setup(name=NAME,
      version='0.1',
      description=DESCRIPTION,
      long_description=long_description,
      long_description_content_type='text/markdown',
      url=URL,
      author=AUTHOR,
      author_email=EMAIL,
      python_requires=REQUIRES_PYTHON,
      license='MIT',
      packages=find_packages(exclude=EXCLUDED_FOLDERS),
      install_requires=list_reqs(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)

