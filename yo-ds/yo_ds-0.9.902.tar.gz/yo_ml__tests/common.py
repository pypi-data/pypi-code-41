from yo_extensions.misc import IO
from yo_extensions import *
import os


def get_path(*args):
    folder = IO.find_root_folder('yo.root')
    temp = os.path.join(folder, 'yo_ml__tests', 'temp', *args)
    os.makedirs(os.path.dirname(temp), exist_ok=True)
    return temp