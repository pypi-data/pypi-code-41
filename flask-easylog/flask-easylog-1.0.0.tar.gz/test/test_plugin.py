import unittest
from flask import Flask, request, json, current_app
from flask.logging import default_handler
from flask_easylog import EasyLog, SpecificLevelLog
from flask_easylog.plugin import key_request_id, keys_request, keys_timestamp

from util import ListHandler

from logging import Logger, DEBUG, INFO, CRITICAL, ERROR, WARNING, Formatter

levels = [DEBUG, INFO, WARNING, ERROR, CRITICAL]

fmts = ['requestId']


def hello():
    current_app.logger.critical("critical from hello")
    current_app.logger.error("error from hello")
    current_app.logger.warning("warning from hello")
    current_app.logger.info("info from hello")
    current_app.logger.debug("debug from hello")
    return "Hello World!"

class TestPlugin(unittest.TestCase):
    """
        Class for Unitaire Test for flask_easylog.plugin
    """
    def setUp(self):
        self.app = Flask(__name__)
        for hdl in self.app.logger.handlers:
            self.app.logger.removeHandler(hdl)
        self.hdl = ListHandler()
        self.app.logger.addHandler(self.hdl)
        self.app.testing = True
        self.app.add_url_rule('/hello', 'hello', hello, methods=['GET'])
        EasyLog(self.app)

    def test_connection(self):
        with self.app.test_client() as c:
            rv = c.get('/hello')
            self.assertEqual(rv.status_code, 200)

    def test_level(self):
        with self.app.test_client() as c:
            for level in levels:
                if 'hello' in SpecificLevelLog:
                    del SpecificLevelLog['hello']
                self.app.logger.setLevel(level)
                c.get('/hello')
                self.assertEqual(len(self.hdl), len(levels)-levels.index(level))
                self.hdl.clear()
    
    def test_level_specific(self):
        with self.app.test_client() as c:
            for levellogger in levels:
                self.app.logger.setLevel(levellogger)
                for levelspec in levels:
                    SpecificLevelLog['hello']=levelspec
                    c.get('/hello')
                    self.assertEqual(len(self.hdl), len(levels)-levels.index(levelspec))
                    self.hdl.clear()

    def test_formatter(self):
        with self.app.test_client() as c:
            self.app.logger.setLevel(CRITICAL)
            if 'hello' in SpecificLevelLog:
                del SpecificLevelLog['hello']
            fmts = [fmt for fmt in key_request_id().keys()]
            fmts = fmts + [fmt for fmt in keys_request().keys()]
            fmts = fmts + [fmt for fmt in keys_timestamp().keys()]
            for fmt in fmts:
                self.hdl.setFormatter(Formatter("%("+fmt+")s"))
                c.get('/hello')
                self.assertEqual(len(self.hdl), 1)
                self.hdl.clear()

if __name__ == '__main__':
    unittest.main()