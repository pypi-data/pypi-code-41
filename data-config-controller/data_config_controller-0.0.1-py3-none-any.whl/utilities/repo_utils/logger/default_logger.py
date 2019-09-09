""" Class to control the standard logging
CREATED: 2/3/19
UPDATED: 6/26/19
"""

import utils
import logging
import os
import datetime


class DefaultLogger:
    def __init__(self, env='default'):
        """ Configure Class Variables """
        if env == 'windows':
            self.config_file = utils.get_project_file('\\json_libraries\\logger.json')
        elif env == 'default':
            self.config_file = utils.get_project_file('/json_libraries/logger.json')
        else:
            self.config_file = utils.get_project_file('\\json_libraries\\logger.json')
        self.log_name = self.__default_log_filename()

    def info(self, msg):
        """
        INFO level log message to default log file
        :param msg: Log message in string format
        :return: *NONE*
        """
        assert msg is not None
        chk = self.__write_log_message('INFO', msg)
        assert chk is True

    def warn(self, msg):
        """
        WARNING level log message to default log file
        :param msg: Log message in string format
        :return: *NONE*
        """
        assert msg is not None
        chk = self.__write_log_message('WARN', msg)
        assert chk is True

    def err(self, msg):
        """
        ERROR level log message to default log file
        :param msg:
        :return:
        """
        assert msg is not None
        chk = self.__write_log_message('ERROR', msg)
        assert chk is True

    def crit(self, msg):
        """
        CRITICAL level log message to default log file
        :param msg:
        :return:
        """
        assert msg is not None
        chk = self.__write_log_message('CRIT', msg)
        assert chk is True

    def debug(self, msg):
        """
        DEBUG level log message to default log file
        :param msg:
        :return:
        """
        assert msg is not None
        chk = self.__write_log_message('DEBUG', msg)
        assert chk is True

    def __write_log_message(self, lvl, msg):
        """
        Write log line at set level
        :param lvl: Level that log message should be set
        :param msg: Message that is written to logs
        :return: Boolean check value to validate successfully written log file
        """
        file_name = self.log_name
        file_hdlr = logging.FileHandler(file_name)
        stream_hdlr = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s || [%(levelname)-8.8s] :: %(message)s')
        file_hdlr.setFormatter(formatter)
        stream_hdlr.setFormatter(formatter)
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[
                file_hdlr,
                stream_hdlr
            ]
        )
        logger = logging.getLogger()
        if lvl is None:
            return False
        elif lvl == 'INFO':
            logger.info(msg)
        elif lvl == 'WARN':
            logger.warning(msg)
        elif lvl == 'ERROR':
            logger.error(msg)
        elif lvl == 'CRIT':
            logger.critical(msg)
        elif lvl == 'DEBUG':
            logger.debug(msg)
        else:
            return False
        file_hdlr.close()
        return True

    def __default_log_filename(self):
        """
        Get default log file path
        :return: String of default log file path
        """
        today = datetime.datetime.today()
        date_str = datetime.datetime.strftime(today, '%Y-%m-%d')
        file = utils.get_json(self.config_file)['logger']['file']  # utils.get_properties()['logger']['file']
        file = file + '-' + date_str + '.log'
        project_path = utils.get_root_directory()
        file_path = os.path.join(project_path + "/logs/", file)
        return file_path

    def __check_file_age(self):
        """
        Method to check current age of log file, if it's over one day old, generate a new one
        :return: *NONE*
        """
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(1)
        file_name = self.__default_log_filename()
        date_str = datetime.datetime.strftime(yesterday, '%Y-%m-%d')
        f = open(file_name)
        if date_str in f.read():
            os.rename(file_name, file_name + '-' + date_str)
            f.close()
            chk = True
        else:
            print('No changes...')
            chk = False
            f.close()
        if chk:
            w = open(file_name, 'w')
            w.close()
            print('New file created for %s' % date_str)
