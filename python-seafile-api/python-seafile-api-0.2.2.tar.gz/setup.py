from setuptools import setup, find_packages

__version__ = '0.2.2'


setup(name='python-seafile-api',
      version=__version__,
      license='BSD',
      description='Client interface for Seafile Web API',
      author='Igor Rumyantsev',
      author_email='igorrum@mail.ru',
      url='https://github.com/Widly/python-seafile',
      platforms=['Any'],
      packages=find_packages(),
      install_requires=['requests'],
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      )
