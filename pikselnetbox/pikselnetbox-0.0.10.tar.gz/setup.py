from setuptools import setup

setup(name='pikselnetbox',
      version='0.0.10',
      description='Module to automate Netbox',
      url='http://gitlab.com/joshrchrds/piksel-netbox',
      author='Josh Richards',
      author_email='joshua.richards135@gmail.com',
      license='MIT',
      packages=['pikselnetbox'],
      dependencies = ['logmatic-python', 'netifaces'],
      zip_safe=False)

