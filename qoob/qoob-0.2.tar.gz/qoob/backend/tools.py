#!/usr/bin/python3
import json
import logging
import logging.config
import os

try:
    from ..__id__ import ID
except ValueError:
    from __id__ import ID

DB_DIR = os.path.expanduser(f"~/.config/{ID}/")


class Database(object):
    def __init__(self, dbFile):
        self.dbFile = DB_DIR + dbFile + ".json"
        if not os.path.isdir(DB_DIR):
            os.mkdir(DB_DIR)
        if os.path.isfile(self.dbFile) and os.stat(self.dbFile).st_size > 0:
            self.load()
        else:
            self.db = {}
            with open(self.dbFile, "w") as f:
                f.write(json.dumps(self.db, indent=2, sort_keys=False))

    def load(self):
        with open(self.dbFile, "r") as f:
            self.db = json.load(f)

    def save(self):
        with open(self.dbFile, "w") as f:
            f.write(json.dumps(dict(self.db), indent=2, sort_keys=False))


class Logger:
    def __init__(self, name, path):
        if not os.path.isdir(f"{path}"):
            os.mkdir(f"{path}")
        LOGGER_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters':
            {
                'default':
                {
                    'format': "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                    'datefmt': "%H:%M:%S",
                },
            },
            'handlers':
            {
                'file':
                {
                    'level': 'DEBUG',
                    'formatter': 'default',
                    'class': 'logging.FileHandler',
                    'filename': f'{path}{name}.log',
                    'mode': 'w',
                },
                'screen':
                {
                    'level': 'INFO',
                    'formatter': 'default',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers':
            {
                '':
                {
                    'handlers': ['file', 'screen'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
            }
        }
        logging.config.dictConfig(LOGGER_CONFIG)
        #sys.excepthook = self._exceptHook

    def _exceptHook(self, type_, error, traceback):
        tb = traceback
        logging.critical(f"{type_} {error}".rstrip())
        while "tb_next" in dir(tb):
            logging.critical(f"{tb.tb_frame}")
            tb = tb.tb_next
        sys.__excepthook__(type_, error, traceback)  # Call default hook

    def new(self, name):
        return logging.getLogger(name)
