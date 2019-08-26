from invoke import Collection, Program
from invoke.config import Config  # , merge_dicts

from rscli import tasks

__VERSION__ = '0.2.0'


class RSConfig(Config):

    prefix = 'rscli'

    '''
    @staticmethod
    def global_defaults():
        their_defaults = Config.global_defaults()
        my_defaults = {
            'debug': True,
            'run': {
                'echo': True,
            },
        }
        return merge_dicts(their_defaults, my_defaults)
    '''


program = Program(
    version=__VERSION__,
    config_class=RSConfig,
    namespace=Collection.from_module(tasks)
)
