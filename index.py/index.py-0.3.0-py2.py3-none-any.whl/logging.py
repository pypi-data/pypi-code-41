from gunicorn.glogging import Logger as _Logger

CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,

    root={"level": "INFO", "handlers": ["console"]},
    loggers={
        "index.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": True,
            "qualname": "index.error"
        },

        "index.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": True,
            "qualname": "index.access"
        }
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout"
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr"
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        }
    }
)


class Logger(_Logger):

    def __init__(self, cfg):
        self.error_log = logging.getLogger("index.error")
        self.error_log.propagate = False
        self.access_log = logging.getLogger("index.access")
        self.access_log.propagate = False
        self.error_handlers = []
        self.access_handlers = []
        self.logfile = None
        self.lock = threading.Lock()
        self.cfg = cfg
        self.setup(cfg)


logger = Logger(CONFIG_DEFAULTS)
