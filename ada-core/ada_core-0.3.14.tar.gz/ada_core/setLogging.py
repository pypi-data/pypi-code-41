import logging, logging.config
import yaml
import os


class AdaLoggingConfig(object):

    FULL_CONF_YAML = """
            version: 1
            disable_existing_loggers: False
            formatters:
                simple:
                    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    datefmt: '%Y-%m-%d %H:%M:%S'
            handlers:
                console:
                    class: logging.StreamHandler
                    level: DEBUG
                    formatter: simple
                    stream: ext://sys.stdout
                file:
                    class: logging.handlers.RotatingFileHandler
                    level: DEBUG
                    formatter: simple
                    filename: ada_core.log
                    maxBytes: 209767
            root:
                level: DEBUG
                handlers: [file,console]
    """

    CONSOLE_CONF_YAML = """
            version: 1
            disable_existing_loggers: False
            formatters:
                simple:
                    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    datefmt: '%Y-%m-%d %H:%M:%S'
            handlers:
                console:
                    class: logging.StreamHandler
                    level: DEBUG
                    formatter: simple
                    stream: ext://sys.stdout
            root:
                level: DEBUG
                handlers: [console]
    """

    DEFAULT_LEVEL = logging.WARNING

    @ staticmethod
    def setLogConfig():
        try:
            try:
                log_dir = os.getcwd()
                logConfig = yaml.load(AdaLoggingConfig.FULL_CONF_YAML)
                logConfig["handlers"]["file"]["filename"] = os.path.join(log_dir, logConfig["handlers"]["file"]["filename"])

            except BaseException:
                logConfig = yaml.load(AdaLoggingConfig.CONSOLE_CONF_YAML)

            logging.config.dictConfig(logConfig)

        except BaseException:
            logging.basicConfig(level=AdaLoggingConfig.DEFAULT_LEVEL)

        finally:
            logger = logging.getLogger(__name__)
            logger.info("The logging config for ada_core has setup, logger name started with 'ada_core.' will be taken")
