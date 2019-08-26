from glutemulo.logger import log

class LoggerBackend:
    def __init__(self, *args, **kwargs):
        log.info(f'init({args}, {kwargs})')

    def consume(self, msg):
        log.warn(msg)
