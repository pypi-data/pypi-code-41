import os
import yaml
from importlib import import_module


DEFAULT_QUWIKI_NAME = 'My QuWiki'
DEFAULT_TEMPLATE = 'templates/default'
DEFAULT_CONFIG_FILE = 'quwiki.yaml'


def initialize(args):
    config = {
        'title': None,
        'template': None,
        'sources': {},
    }

    # Request instance name
    config['title'] = input('Enter QuWiki instance name [{}]: '.format(DEFAULT_QUWIKI_NAME))
    if len(config['title']) == 0:
        config['title'] = DEFAULT_QUWIKI_NAME

    # Request template path
    while config['template'] is None or not os.path.exists(config['template']):
        config['template'] = input('Choose template [{}]: '.format(DEFAULT_TEMPLATE))
        if len(config['template']) == 0:
            config['template'] = DEFAULT_TEMPLATE

    # Request source configuration
    print('You need to configure a source for QuWiki to pull data from')
    print('Officially supported source types are: `quwiki.sources.gdrive` and `quwiki.sources.git`')

    sources_done = 'y'
    while sources_done == 'y':
        # Choose source ID
        counter = 1
        source_idx_auto = None
        while source_idx_auto is None or source_idx_auto in config['sources'].keys():
            source_idx_auto = 'source_{}'.format(str(counter))
            counter += 1
        source_idx = input('Source identifier [{}]: '.format(source_idx_auto))
        if len(source_idx) == 0:
            source_idx = source_idx_auto

        # Source specific configuration
        success = False
        while not success:
            try:
                source_conf = {}
                source_conf['type'] = input('Source type: ')
                source_module = import_module(source_conf['type'])
                source_conf = source_module.initialize(source_conf)
                config['sources'][source_idx] = source_conf
                success = True
            except Exception as e:
                print('Error:', e)

        # Add more sources
        sources_done = 'u'
        while sources_done.lower() not in 'ny':
            sources_done = input('Add more sources [y/n]: ').lower()

    # Save the configuration
    with open(DEFAULT_CONFIG_FILE, 'w+') as f:
        yaml.dump(config, f, allow_unicode=True)
    print('The configuration is written to file {}'.format(DEFAULT_CONFIG_FILE))
