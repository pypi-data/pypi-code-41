import pprint

from pconf import Pconf
import os

from ioflow.configure.get_configure_path_from_argv import get_configure_path_from_argv


def read_configure(
        return_empty=False,
        default_configure='./configure.json',
        builtin_configure='./builtin_configure.json') -> dict:
    # set return_empty to True for not read config from env
    # which can prevent unexpected result
    # e.g. './configure.json' is not for this app, but for other using
    if return_empty:
        return {}

    active_configure_file = get_configure_path_from_argv()
    if not active_configure_file:
        active_configure_file = os.getenv('_DEFAULT_CONFIG_FILE', default_configure)

    builtin_configure_file = os.getenv('_BUILTIN_CONFIG_FILE', builtin_configure)

    # disable read configure from environment
    # Pconf.env()

    Pconf.file(active_configure_file, encoding='json')

    # try loading builtin configure file
    if os.path.exists(builtin_configure_file):
        print("loading builtin configure from {}".format(builtin_configure_file))
        Pconf.file(builtin_configure_file, encoding='json')
    else:
        print(">>> builtin configure file is not found!")

    # Get all the config values parsed from the sources
    config = Pconf.get()

    print("++" * 8, "configure", "++" * 8)
    pprint.pprint(config)

    return config

    # sys.exit(0)

    # return {
    #     'corpus': {
    #         'train': './data/train.conllz',
    #         'test': './data/test.conllz'
    #     },
    #     'model': {
    #         'shuffle_pool_size': 10,
    #         'batch_size': 32,
    #         'epochs': 20,
    #         'arch': {}
    #      }
    # }


read_config = read_configure  # alias
