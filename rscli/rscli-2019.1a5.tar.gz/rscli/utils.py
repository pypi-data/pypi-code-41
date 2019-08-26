import logging
from shutil import which

import requests

NODE = 'Node'
PYTHON = 'Python'

abcfp = set('abcfp')  # Alpha, Beta, release Candidate, Final, Post
LANGUAGES = [PYTHON, NODE]
LOG_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger('rscli')


def ensure_gitignore(language):
    resp = requests.get(
        'https://raw.githubusercontent.com/github/'
        'gitignore/master/%s.gitignore' % language)
    with open('.gitignore', 'w') as f:
        f.write(resp.content.decode())


def check_command(cmd):
    cmd_path = which(cmd)
    if cmd_path is None:
        logger.error("[ERROR] Missing Command: %s" % cmd)
    else:
        logger.info("[INFO] Using command: %s" % cmd_path)
    return cmd_path


'''
class Dict2Obj:
    """Convert a dict of object.

    constraint: kwargs can't contain `keys` and `values`."""

    def __init__(self, **kwargs):
        self.keys = []
        self.values = []
        for key, value in kwargs.items():
            self.keys.append(key)
            self.values.append(value)
            setattr(self, key, value)
        super(Dict2Obj, self).__init__()


RELEASES = Dict2Obj(
    a='alpha', b='beta', c='candidate-release', f='final', p='post'
)
'''
