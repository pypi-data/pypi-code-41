"""Setuptools entry point."""
import codecs
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dirname = os.path.dirname(__file__)
readme_filename = os.path.join(dirname, 'README.rst')

description = 'Python connector module for Node.JS applications'
long_description = description
if os.path.exists(readme_filename):
    readme_content = codecs.open(readme_filename, encoding='utf-8').read()
    long_description = readme_content

setup(name='nodeconnector',
      version='1.0.5',
      description=description,
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='https://github.com/cristidbr/nodeconnector',
      author='Cristian Dobre',
      author_email='cristian.dobre@hbfsrobotics.com',
      license='MIT',
      packages=['nodeconnector'],
      install_requires=[
          'pyzmq',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)