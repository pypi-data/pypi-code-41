from setuptools import setup

setup(name='mendelai_ipc',
      version='0.5',
      description='Simple IPC module that supports communicating over stdin/stdout while chunking messages if they are too large',
      url="https://github.com/mendelhealth/python_ipc",
      author='Karim Tarabishy',
      author_email='k.eltarabishy@gmail.com',
      packages=['mendelai_ipc'],
      test_suite='nose2.collector.collector',
      tests_require=['nose2'],
      zip_safe=False)
