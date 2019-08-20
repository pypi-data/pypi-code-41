from yo_extensions.misc import IO
from yo_extensions import *
import os


def path(*args):
    folder = IO.find_root_folder('yo.root')
    return os.path.join(folder, 'tests', 'ml', *args)