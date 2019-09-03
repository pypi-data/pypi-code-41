from setuptools import setup

setup(
   name='lamdata-arias',
   version='0.1',
   description='A useful module',
   author='Soy Gael',
   author_email='foomail@foo.com',
   packages=['lamdata_arias'],  #same as name
   install_requires=['numpy', 'pandas'], #external packages as dependencies
   license="MIT"
)
