import os

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

updated_version = '0.0.1'

if updated_version == '0.0.1':
    __version__ = "0.0.0"
else:
    __version__ = updated_version
