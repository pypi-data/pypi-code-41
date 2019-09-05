from distutils.core import setup
import setuptools
setuptools.setup(
  name = 'matialvarezs_charge_controller',
  packages = setuptools.find_packages(),#['matialvarezs_charge_controller'], # this must be the same as the name above
  version = '0.0.149',
  install_requires = [
    'matialvarezs-handlers-easy==0.1.26',
    'matialvarezs_node_configurations==0.0.22',
    'matialvarezs-request-handler==0.1.6',
    'python-crontab==2.3.6',
    'django-ohm2-handlers-light==0.4.1',
    'pymodbus==2.2.0'
  ],
  include_package_data = True,
  description = 'Charge controller data',
  author = 'Matias Alvarez Sabate',
  author_email = 'matialvarezs@gmail.com',  
  classifiers = [
    'Programming Language :: Python :: 3.5',
  ],
)