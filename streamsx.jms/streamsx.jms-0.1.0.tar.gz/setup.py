from setuptools import setup
import streamsx.jms
setup(
  name = 'streamsx.jms',
  packages = ['streamsx.jms'],
  include_package_data=True,
  version = streamsx.jms.__version__,
  description = 'IBM Streams JMS integration',
  long_description = open('DESC.txt').read(),
  author = 'IBM Streams @ github.com',
  author_email = 'schulz2@de.ibm.com',
  license='Apache License - Version 2.0',
  url = 'https://github.com/IBMStreams/streamsx.jms',
  keywords = ['streams', 'ibmstreams', 'streaming', 'analytics', 'streaming-analytics', 'jms'],
  classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  install_requires=['streamsx', 'streamsx.toolkits'],
  
  test_suite='nose.collector',
  tests_require=['nose']
)
