import os, pickle, json

__all__ = ['Cache']

def __read__(f):
    return f.read()

def __write_str__(data, f):
    f.write('{}'.format(data))

def __write_bin__(data, f):
    f.write(data)

__file_op__ = {
    'str': {
        'suffix': 'txt', 'r': 'r', 'w': 'w', 
        'load': __read__, 'dump': __write_str__,
    }, 
    'pkl': {
        'suffix': 'pkl', 'r': 'rb', 'w': 'wb', 
        'load': pickle.load, 'dump': pickle.dump,
    },
    'json': {
        'suffix': 'json', 'r': 'r', 'w': 'w',
        'load': json.load, 'dump': json.dump,
    },
    'bin': {
        'suffix': 'bin', 'r': 'rb', 'w': 'wb',
        'load': __read__, 'dump': __write_bin__,
    },
}

class Cache(object):
    def __init__(self, path):
        self.path = path
        self.file_op = __file_op__
        if not os.path.isdir(path):
            os.makedirs(path)

    def items(self):
        return sorted(os.listdir(self.path))

    def remove(self, name):
        path = os.path.join(self.path, name)
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False

    def dump(self, data, name, file_type='pkl'):
        """
            Args:
                data: data to save
                name: filename
                file_type: type of cache, one of 'str', 'pkl', 'json', 'bin'
                    default 'pkl'
        """
        assert file_type in self.file_op.keys(),\
                'key error: {} not found in {}'.\
                format(file_type, list(self.file_op.keys()))

        path = os.path.join(self.path, name)
        file_op = self.file_op[file_type]
        with open(path, file_op['w']) as f:
            file_op['dump'](data, f)

    def load(self, name, file_type='pkl'):
        """
            Args:
                name: filename
                file_type: type of cache, one of 'str', 'pkl', 'json', 'bin'
                    default 'pkl'
        """
        assert file_type in self.file_op.keys(),\
                'key error: {} not found in {}'.\
                format(file_type, list(self.file_op.keys()))

        path = os.path.join(self.path, name)
        file_op = self.file_op[file_type]
        with open(path, file_op['r']) as f:
            return file_op['load'](f)

if __name__ == '__main__':
    cache = Cache('/tmp/x')
    cache.dump('hi.bin', 'a.pkl')
    print(cache.load('a.pkl', file_type='str'))
