import unittest
import json
from flask import Flask, request, json, current_app

from flask_easylog import Api, SpecificLevelLog
from flask_easylog.util import _levelToName
from util import ListHandler

from logging import Logger, DEBUG, INFO, CRITICAL, ERROR, WARNING

def hello():
    current_app.logger.critical("critical from hello")
    current_app.logger.error("error from hello")
    current_app.logger.warning("warning from hello")
    current_app.logger.info("info from hello")
    current_app.logger.debug("debug from hello")
    return "Hello World!"

class TestApi(unittest.TestCase):
    """
        Class for Unitaire Test for flask_easylog.api
    """
    def setUp(self):
        self.app = Flask(__name__)
        for hdl in self.app.logger.handlers:
            self.app.logger.removeHandler(hdl)
        self.hdl = ListHandler()
        self.app.logger.addHandler(self.hdl)
        self.app.testing = True
        self.app.add_url_rule('/hello', 'hello', hello, methods=['GET'])
        self.app.register_blueprint(Api(url_prefix='/api'))

    def test_connection(self):
        with self.app.test_client() as c:
            rv = c.get('/hello')
            self.assertEqual(rv.status_code, 200)
    
    def test_basic(self):
        with self.app.test_client() as c:
            rv = c.get('/api/logs')
            self.assertEqual(rv.status_code, 200)
            rv = c.get('/api/log/hello')
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.get_data().decode('utf-8'))
            self.assertEqual(data['level'], _levelToName[self.app.logger.getEffectiveLevel()])
            self.app.logger.setLevel(DEBUG)
            rv = c.get('/api/log/hello')
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.get_data().decode('utf-8'))
            self.assertEqual(data['level'], _levelToName[self.app.logger.getEffectiveLevel()])
 
    def test_get_logs(self):
         with self.app.test_client() as c:
            self.app.logger.setLevel(DEBUG)
            for level in _levelToName.keys():
                SpecificLevelLog['hello'] = level
                rv = c.get('/api/logs')
                self.assertEqual(rv.status_code, 200)
                data = json.loads(rv.get_data().decode('utf-8'))
                self.assertEqual(data[0]['level'], _levelToName[level])
 
    def test_get_log(self):
         with self.app.test_client() as c:
            self.app.logger.setLevel(DEBUG)
            for level in _levelToName.keys():
                SpecificLevelLog['hello'] = level
                rv = c.get('/api/log/hello')
                self.assertEqual(rv.status_code, 200)
                data = json.loads(rv.get_data().decode('utf-8'))
                self.assertEqual(data['level'], _levelToName[level])
     
    def test_set_log(self):
        with self.app.test_client() as c:
            self.app.logger.setLevel(DEBUG)
            for level in _levelToName.keys():
                rv = c.put('/api/log/hello', data=json.dumps({'endpoint':'hello', 'level':_levelToName[level]}), headers={'content-type': 'application/json'})
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(SpecificLevelLog['hello'], level)

    def test_set_log_error_endpoint(self):
        with self.app.test_client() as c:
            rv = c.put('/api/log/hello', data=json.dumps({'endpoint':'notHello', 'level':'DEBUG'}), headers={'content-type': 'application/json'})
            self.assertEqual(rv.status_code, 405)
 
    def test_set_log_error_data(self):
        with self.app.test_client() as c:
            rv = c.put('/api/log/hello', data=json.dumps(['endpoint', 'level']), headers={'content-type': 'application/json'})
            self.assertEqual(rv.status_code, 405)
 
    def test_rm_log(self):
        with self.app.test_client() as c:
            self.app.logger.setLevel(DEBUG)
            for level in _levelToName.keys():
                rv = c.put('/api/log/hello', data=json.dumps({'endpoint':'hello', 'level':_levelToName[level]}), headers={'content-type': 'application/json'})
                self.assertEqual(SpecificLevelLog['hello'], level)
                rv = c.delete('/api/log/hello')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(SpecificLevelLog['hello'], DEBUG)
    
    def test_rm_log_double(self):
        with self.app.test_client() as c:
            self.app.logger.setLevel(DEBUG)
            for level in _levelToName.keys():
                rv = c.put('/api/log/hello', data=json.dumps({'endpoint':'hello', 'level':_levelToName[level]}), headers={'content-type': 'application/json'})
                self.assertEqual(SpecificLevelLog['hello'], level)
                rv = c.delete('/api/log/hello')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(SpecificLevelLog['hello'], DEBUG)
                rv = c.delete('/api/log/hello')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(SpecificLevelLog['hello'], DEBUG)
   
if __name__ == '__main__':
    unittest.main()