import unittest
from dictbook.database import Database
import datetime


class DBTest(unittest.TestCase):

    def setUp(self):
        self.db = Database('test.db', 'words')
        pass

    @unittest.skip
    def test_insert(self):
        self.db.insert('love none', 'fuck your vagina', str(datetime.date.today()))
        self.db.insert('love to', 'fuck your vagina', str(datetime.date.today()))
        self.db.insert('love you', 'fuck your vagina', str(datetime.date.today()))
        self.db.insert('love me', 'fuck your vagina', str(datetime.date.today()))
        self.db.insert('love never', 'fuck your vagina', str(datetime.date.today()))

    def test_db_content(self):
        self.db.content()
        pass

    @unittest.skip
    def tearDown(self):
        self.db = None


if __name__ == '__main__':
    unittest.main()
