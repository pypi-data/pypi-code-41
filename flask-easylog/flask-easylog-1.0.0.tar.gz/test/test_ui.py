import unittest
from flask import Flask, request, json

from flask_easylog import Ui

class TestUi(unittest.TestCase):
    """
        Class for Unitaire Test for flask_easylog.ui
    """
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.app.register_blueprint(Ui(url_prefix='/ui'))

    def test_connection(self):
        with self.app.test_client() as c:
            rv = c.get('/ui')
            self.assertNotEqual(rv.status_code, 404)

    def test_connection_index(self):
        with self.app.test_client() as c:
            rv = c.get('/ui/index.html')
            self.assertNotEqual(rv.status_code , 404)

if __name__ == '__main__':
    unittest.main()