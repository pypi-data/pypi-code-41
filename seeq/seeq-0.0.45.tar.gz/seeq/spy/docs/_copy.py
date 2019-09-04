import os

from distutils import dir_util


def copy(directory=None, overwrite=False):
    if not directory:
        directory = os.path.join(os.getcwd(), 'Spy Documentation')

    if os.path.exists(directory):
        if not overwrite:
            raise RuntimeError('The "%s" folder already exists. If you would like to overwrite it, supply the '
                               'overwrite=True parameter. Make sure you don\'t have any of your own work in that '
                               'folder!' % directory)

        dir_util.remove_tree(directory)

    library_doc_folder = os.path.join(os.path.dirname(__file__), 'Documentation')

    dir_util.copy_tree(library_doc_folder, directory)

    print('Copied Spy library documentation to "%s"' % directory)
