from setuptools import setup, find_packages
from pyjamaparty.strutils.string_builder import StringBuilder

description = 'Set of casual python utilities'
long_description = StringBuilder('{}, written standing on shoulders of giants.'.format(description))
long_description += ' Tools include a string builder, singleton decorator'

requirements = []
setup(
   name='pyjamaparty',
   version='0.2',
   description=description,
   license="MIT",
   long_description=str(long_description),
   author='Karthik Rajasekaran',
   author_email='krajasek@gmail.com',
   url="http://github.com/krajasek/pyjamaparty",
   install_requires=requirements,
   packages=find_packages(exclude=('pyjamaparty.tests',)),
   python_requires='>=2.7'
)