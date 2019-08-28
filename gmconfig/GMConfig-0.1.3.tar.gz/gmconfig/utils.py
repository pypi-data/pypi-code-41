import logging
import platform


def createLogger(name, debug: bool = False):
    logger = logging.getLogger(name)

    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    # remove all handlers
    logger.handlers = []

    # file
    logpath = "/tmp/" + name + ".log"
    if platform.system() == "Windows":
        logpath = "C:\\Temp\\" + name + ".log"
    fhandle = logging.FileHandler(logpath)
    fhandle.setLevel(logging.DEBUG)
    fhandle.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fhandle)

    # stdout
    stdout = logging.StreamHandler()
    stdout.setLevel(level)
    stdout.setFormatter(logging.Formatter("[+] %(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(stdout)

    logger.debug("Log file for {} :: {}".format(name, logpath))

    return logger
