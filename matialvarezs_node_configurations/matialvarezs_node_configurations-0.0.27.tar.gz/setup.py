from distutils.core import setup
import setuptools
setuptools.setup(
  name = 'matialvarezs_node_configurations',
  packages = setuptools.find_packages(),#['matialvarezs_node_configurations'], # this must be the same as the name above
  version = '0.0.27',
  install_requires = [
    'django-ohm2-handlers-light==0.4.1',
    'matialvarezs_node_accounts==0.0.1',
  ],
  include_package_data = True,
  description = 'Nodes configurations - model and api',
  author = 'Matias Alvarez Sabate',
  author_email = 'matialvarezs@gmail.com',  
  classifiers = [
    'Programming Language :: Python :: 3.5',
  ],
)