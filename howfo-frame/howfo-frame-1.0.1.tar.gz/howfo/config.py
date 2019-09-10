import os
from .helpers import folder_files, load_file, merge_dicts
from flask.helpers import get_root_path
from howfo.helpers import get_env

# basedir = os.path.abspath(os.path.dirname(__file__))
basedir = get_root_path('app')
print(basedir)

class FrameConfig():
    frame_config = {'app': {}}

    # 组装全部配置
    def __init__(self):
        FrameConfig.from_folder()

    @staticmethod
    def from_folder(config_path=None, rule='*.json'):
        app_config = {}
        if config_path is None:
            config_path = get_root_path('config')
        config_files = folder_files(config_path, rule)
        print('24', config_path)
        for config_file in config_files:
            file_name = config_file.split('.')[0]
            config_file_path = os.path.join(config_path, config_file)
            config_content = load_file(config_file_path, True)
            env = get_env() or 'product'
            env_config = config_content.get(env, {})
            product_config = config_content.get('product')
            if env != 'product':
                app_config[file_name] = merge_dicts(product_config, env_config)
            else:
                app_config[file_name] = product_config

        FrameConfig.frame_config = app_config


config = FrameConfig()
config_dict = config.frame_config
# log.info('config info:{}'.format(config_dict))
# print('45', conf_info)
