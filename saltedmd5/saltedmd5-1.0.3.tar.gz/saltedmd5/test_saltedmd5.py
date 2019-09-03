## SaltedMD5 UnitTesting
import unittest
from saltedmd5 import Salting


class TestSalting(unittest.TestCase):
    ''' UnitTesting for SaltedMD5 '''
    
    def setUp(self):
        print('Setting up multiple objects')
        self.user_1 = Salting('password', 10)
        self.user_2 = Salting(12345, 20)
        self.user_3 = Salting(-5, -9)
        self.user_4 = Salting('incomplete', 999)
        self.user_1.seasoning(), self.user_2.seasoning(), self.user_3.seasoning()

    def tearDown(self):
        print('Tearing down the objects\n')
    
    def test_seasoning(self):
        print('Testing seasoning()')
        self.assertEqual(self.user_1.is_seasoned, True)
        self.assertEqual(self.user_2.is_seasoned, True)
        self.assertEqual(self.user_3.is_seasoned, True)

    def test_show_info(self): 
        print('Testing show_info()')
        self.assertEqual(self.user_1.show_info(), self.user_1.data)
        self.assertEqual(self.user_2.show_info(), self.user_2.data)
        self.assertEqual(self.user_3.show_info(), self.user_3.data)
        self.assertEqual(self.user_4.show_info(), 'Please use "seasoning" before showing information.')

    def test_authentication(self):
        ''' Test the correctness of salted passwords '''
        print('Testing check_authentication()')
        self.assertEqual(self.user_1.check_authentication(self.user_1.password), True)
        self.assertEqual(self.user_2.check_authentication(self.user_2.password), True)
        self.assertEqual(self.user_3.check_authentication('gibberish'), False)
        self.assertEqual(self.user_4.check_authentication('123'), 'Please use "seasoning" before showing information.')
    
    def test_create_json(self):
        print('Testing create_json()')
        self.assertEqual(self.user_1.create_json('user_1'), True)
        self.assertEqual(self.user_4.create_json('user_1'), 'Please use "seasoning" before showing information.')



if __name__ == '__main__':
    unittest.main()
