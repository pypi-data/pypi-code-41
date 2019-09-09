from distutils.core import setup
from setuptools import find_packages

setup(name='jpostcode-python',
      version='0.0.6',
      description='Japanese postcode utils',
      author='uehara1414',
      author_email='akiya.noface@gmail.com',
      url='https://github.com/uehara1414/jpostcode-python',
      packages=find_packages(),
      install_requires=[
      ],
      include_package_data=True,
      package_data={
            'jpostcode-python': ['data/*'],
      }
      )
