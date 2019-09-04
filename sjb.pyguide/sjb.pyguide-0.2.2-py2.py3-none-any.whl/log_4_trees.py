import logging
import logging.handlers
import logging.config
import os
import sys
from setuptools import setup


class LoggerOfTrees(logging.Logger):
    """Great Software has Great Logging.

        https://www.google.com/search?q=logging

            log·ging     noun
            /ˈlôɡiNG,ˈläɡiNG/

            the activity or business of felling trees and cutting and preparing the timber.
            \"measures to counter illegal logging of the country's tropical rainforests\"

        Originally created to deal with writing log files to directories (and creating that directory etc), I
        encapsulated the Python standard logging into my logging_of_trees project.  By default this class can
        create the logging file and add the handler to direct logs to it.  In addition we set logging to the
        stdout so that it can be used instead of print statements."""
    def __init__(self, allow_log_file=True):
        super(LoggerOfTrees, self).__init__(name=__name__)

        # self.log = logging.getLogger(__name__)
        self.allow_log_file = allow_log_file
        self.add_handler_stdout()
        self.add_handler_file()
        # The base logger should receive all messages so as to re-route to handlers what they need.
        self.setLevel(logging.DEBUG)

    def add_handler_stdout(self, msg_format="%(levelname)s | %(message)s"):
        """This method could have been called send logs to stdout like a print() statement.  It will create a logging
            \"handler\" which is the Python term for where to write the log.  It's cool because logging can have
            more than one handler.  Such as by default with this class, there is all a handler to write logs to a
            file"""
        # By default write the stdout for INFO level and above; better than print()
        stdout_log = logging.StreamHandler(sys.stdout)
        stdout_log.setFormatter(logging.Formatter(fmt=msg_format))
        stdout_log.setLevel(logging.INFO)

        self.addHandler(stdout_log)

    def add_handler_file(self):
        """This method could have been called create log file.  It will create a logging \"handler\" which is the
        Python term for where to write the log.  It's cool because logging can have more than one handler.  Such as
        by default with this class, there is all a handler to put things to stdout like a print() statement."""
        if self.allow_log_file:
            # By default write the file log for DEGUG level and above
            file_log = logging.handlers.TimedRotatingFileHandler(
                filename=r"{0}\{1}.log".format(self.log_directory, __name__),
                when="D", interval=1, backupCount=30)
            file_log.setFormatter(logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s"))
            file_log.setLevel(logging.DEBUG)

            self.addHandler(file_log)

    @staticmethod
    def make_directory_log_file(self, directory=None):
        """Create directory on the local file system for the log file"""
        if not os.path.exists(directory):
            try:
                os.mkdir(directory)
            except OSError:
                print("Error creating log directory {0}".format(directory))

    @property
    def log_directory(self):
        if self.allow_log_file:
            try:
                return self._log_directory
            except AttributeError:
                directory = os.path.join(os.getcwd(), "logs")
                self.make_directory_log_file(self=self, directory=directory)

                self._log_directory = directory
                pass
        else:
            return None

        return self._log_directory

    @log_directory.setter
    def log_directory(self, value):
        self._log_directory = value

    @property
    def allow_log_file(self):
        """Property create_log_file is True if we want to write a log file.  Originally for containers this flag was
        add for those cases where we don't want a file log.  Normally we still log to standard out."""
        return self._allow_log_file

    @allow_log_file.setter
    def allow_log_file(self, value):

        self._allow_log_file = value
