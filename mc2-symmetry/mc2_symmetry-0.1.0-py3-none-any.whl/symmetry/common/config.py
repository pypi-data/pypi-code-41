from os import path, listdir


def guess_root_path():
    if 'etc' in listdir(path.curdir):
        return path.abspath(path.curdir)

    if 'etc' in listdir('../..'):
        return path.abspath('../..')

    if 'etc' in listdir('..'):
        return path.abspath('..')

    raise ValueError('Did not find root directory with etc dir')


def get_nodes_config():
    return path.join(guess_root_path(), 'etc', 'nodes.ini')
