import os

BASE_DIR = os.path.dirname(__file__)
SOURCE_PATH = os.path.join(BASE_DIR, 'nicknames')
COMMANDS_PATH = os.path.join(BASE_DIR, 'commands')

SUPPORT_LANG_LIST = [
    'ko',
]

PREFIX_WORDS = ('p', 'pre', 'prefix', 'pr')
SUFFIX_WORDS = ('s', 'suf', 'suffix', 'su')
