import logging


def console_handler(level=logging.WARNING):
    h = logging.StreamHandler()
    fmt = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    h.setLevel(level)
    h.setFormatter(fmt)
    return h


def file_handler(level=logging.WARNING, filename='klisch.log'):
    h = logging.FileHandler(filename)
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h.setLevel(level)
    h.setFormatter(fmt)
    return h


def get(name, level):
    log = logging.getLogger(name)
    log.addHandler(console_handler(level))
    log.setLevel(level)
    return log
