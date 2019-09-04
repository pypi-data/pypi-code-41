from unittest import TestCase, skip
from ..app import create_app

class APITestCase(TestCase):

    def setUp(self):
        self.app = create_app()
        self.context = self.app.app_context()
        self.context.push()
        self.client = self.app.test_client()
        # self.app.mq.run()

    def tearDown(self):
        pass
