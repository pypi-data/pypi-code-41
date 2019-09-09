from setuptools import setup, find_packages
from os.path import abspath, dirname, join

PROJECT_NAME = "motorframework"
SOURCE_DIR = PROJECT_NAME
AUTHOR_NAME = "super-mario-x"
PROJECT_GIT_URL = "https://github.com/" + AUTHOR_NAME + "/" + PROJECT_NAME
AUTHOR_EMAIL = "xmario@hotmail.com"

CLASSIFIERS = '''
Development Status :: 3 - Alpha
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()
DESCRIPTION = 'Robot Framework Library'
KEYWORDS = ['motor', 'motorframework', 'soap', 'rest', 'selenium']
CURRENT_DIR = dirname(abspath(__file__))

with open(
  join(CURRENT_DIR, SOURCE_DIR, '__init__.py')) as f:
  for line in f:
    if line.startswith("__version__"):
      VERSION = line.strip().split("=")[1].strip(" '\"")
      break
    else:
      VERSION = "0.0.1"

DOWNLOAD_URL = PROJECT_GIT_URL + "/archive/v" + VERSION + ".tar.gz"
REQUIREMENTS = ['robotframework']
setup(
  name = PROJECT_NAME,
  packages = ['motorframework', 'motorframework.co'], 
  scripts=['bin/build.bat'],
  version = VERSION,
  license='MIT',
  author=AUTHOR_NAME,
  author_email=AUTHOR_EMAIL,
  description = DESCRIPTION, 
  url = PROJECT_GIT_URL,
  download_url = DOWNLOAD_URL,
  keywords = KEYWORDS,
  install_requires=REQUIREMENTS,
  classifiers=CLASSIFIERS
)