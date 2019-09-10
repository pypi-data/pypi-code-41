import logging

import os
import psycopg2 as pg
import subprocess
import time

from pkg_resources import resource_filename

h2_jar = resource_filename(__name__, "jar/h2-1.4.199.jar")


class H2DbManager:

    def __init__(self, db_path: str, user: str, password: str, host: str = 'localhost', port: str = '5435'):
        """

        :param db_path: path to database file
        :param user: user name
        :param password: password to use
        :param host: host address
        :param port: port in usage
        """
        self._logger = logging.getLogger(__name__)
        self._db_dir, self._db_filename = self.split_db_path(db_path)
        self._user = user
        self._passwd = password
        self._host = host
        self._port = port
        self.check_java_is_in_system()

    def __enter__(self):
        """Spool up H2 server."""
        self._url = '{}:{}'.format(self._host, self._port)
        self._logger.info("Spooling up H2 server at '{}'".format(self._url))
        self._cp = subprocess.Popen(('java', '-cp', h2_jar, 'org.h2.tools.Server',
                                     '-pg', '-baseDir', self._db_dir, '-pgPort', self._port))
        time.sleep(.5)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Shut down the H2 server process."""
        self._logger.info("Shutting down the H2 server at '{}'".format(self._url))
        self._cp.terminate()
        return_code = self._cp.wait()  # wait until the server shuts down,
        self._logger.info("Server returned {}".format(return_code))

    def __repr__(self):
        return "H2DbManager({}, user={}, password={}, host={}, port={})".format(
            os.path.join(self._db_dir, self._db_filename) + ".mv.db",
            self._user, self._passwd, self._host, self._port)

    def get_connection(self):
        """Return a new connection to the database."""
        cstring = "dbname={} user={} password='{}' host={} port={}".format(self._db_filename,
                                                                           self._user,
                                                                           self._passwd,
                                                                           self._host,
                                                                           self._port)
        return pg.connect(cstring)

    @staticmethod
    def split_db_path(db_path: str):
        if os.path.isfile(db_path):
            if db_path.endswith(".mv.db"):
                # remove .mv.db suffix, if present
                db_path = db_path[:-6]
            return os.path.split(db_path)
        else:
            raise ValueError("'{}' does not point to a file".format(db_path))

    @staticmethod
    def check_java_is_in_system():
        process = subprocess.run(('which', 'java'), capture_output=True)
        return process.returncode == 0
