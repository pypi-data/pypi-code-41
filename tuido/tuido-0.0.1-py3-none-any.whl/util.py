import yaml
import tempfile

tempfile.tempdir = "/tmp"


def read_yaml(fn):
    ''' Read yaml from file '''
    try:
        with open(fn) as f:
            return yaml.safe_load(f.read())
    except yaml.YAMLError as e:
        raise e


def write_yaml(fn, config):
    ''' Write dict to file as yaml '''
    try:
        with open(fn, 'w') as f:
            f.write(yaml.dump(config))
    except yaml.YAMLError as e:
        raise e


def dump_yaml(config):
    ''' Dump dict to yaml '''
    return yaml.safe_dump(config, indent=2)


def write_to_tmp(contents, prefix=''):
    ''' Write message to temporary file '''
    temp = tempfile.NamedTemporaryFile(mode='w+t', prefix=prefix)
    temp.writelines(contents)


class IdGenerator:

    ''' Simple ID generator '''

    def __init__(self):
        self.id = 0

    def get_id(self):
        ''' Increment and return ID '''
        self.id += 1
        return self.id

    def sub_id(self):
        ''' Decrement and return ID '''
        self.id -= 1
        return self.id

    def reset_id(self):
        ''' Reset ID to 0 '''
        self.id = 0

DEFAULT_CONFIG_DICT = {
    'config': {
        'indent': 2,
        'spacing': 2
    },
    'list': []
}
