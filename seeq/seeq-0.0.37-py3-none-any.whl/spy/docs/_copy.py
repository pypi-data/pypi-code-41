import os

from distutils import dir_util


def copy(directory=None):
    if not directory:
        directory = os.path.join(os.getcwd(), 'Spy Documentation')

    if os.path.exists(directory):
        dir_util.remove_tree(directory)

    dir_util.copy_tree(os.path.join(os.path.dirname(__file__), 'Documentation'), directory)

    print('Copied Spy library documentation to "%s"' % directory)
