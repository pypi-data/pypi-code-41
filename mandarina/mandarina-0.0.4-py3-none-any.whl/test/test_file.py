from mandarina.file import *
import unittest

class FileTest(unittest.TestCase):
    def test(self):
        pass

    def test_create_dir_if_doesnt_exist(self):
        dir_path = "./test"
        create_dir_if_doesnt_exist(dir_path)
        self.assertTrue(os.path.exists(dir_path))
        delete_dir(dir_path)
