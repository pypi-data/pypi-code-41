import os

PINDA_CONFIGDIR = os.getenv('PINDA_CONFIGDIR', os.path.join(os.getenv('HOME', '/'), '.pinda'))
PINDA_DEFAULT_DATABASE = os.path.join(PINDA_CONFIGDIR, '_default.yaml')
