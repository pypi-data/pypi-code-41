from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='Some_Sonar',
    version='1.02',
    install_requires=[
          'RPi.GPIO',
      ],
    packages=find_packages(),
    author_email='zarubinilia@yabdex.ru',
    include_package_data=True,
    zip_safe=False
)
