import os
import json


def config(path):
    filename = os.path.join(path, 'config.json')
    out = {'default': 'link'}
    if os.path.exists(filename):
        cfg = read_json(filename)
        if not set(cfg.values()).issubset({'link', 'copy'}):
            raise ValueError('Invalid transfer option in config: {}'
                             .format(set(cfg.values()) - {'link', 'copy'})
                             )
        for key, value in cfg.items():
            if not key == 'default':
                key = os.path.join(path, key)
            out[key] = value
    return out


def read_json(filename):
    with open(filename) as f:
        return json.load(f)
