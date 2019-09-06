import logging
import os


class LogProvider:
    @staticmethod
    def get_logger(name: str):
        log_level = os.environ.get("LOG_LEVEL")
        if not log_level:
            log_level = logging.INFO
        logging.basicConfig(level=log_level, format='%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')

        return logging.getLogger(name)
