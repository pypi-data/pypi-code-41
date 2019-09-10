from django.test import TestCase
from psu_base.services import utility_service


class UtilTestCase(TestCase):
    def setUp(self):
        pass

    def test_fake_session(self):
        """
        Since the session does not exist while unit testing, a dict is used in its place.
        This tests that the dict is functioning as expected
        """
        fake_session = utility_service.get_session()
        self.assertTrue(type(fake_session) is dict, 'Session should be a dict')

        test_var_1 = 'unit_test_value'
        test_val_1 = 'This is a unit test...'
        utility_service.set_session_var(test_var_1, test_val_1)
        self.assertTrue(utility_service.get_session_var(test_var_1) == test_val_1, 'Session var not set or retrieved')

        test_var_2 = 'unit_test_temp_value'
        test_val_2 = 'This is another unit test...'
        utility_service.set_temp_session(test_var_2, test_val_2)
        self.assertTrue(utility_service.get_temp_session(test_var_2) == test_val_2, 'Temp session var not set or retrieved')
        utility_service.clear_temp_session()
        self.assertTrue(utility_service.get_temp_session(test_var_2) is None, 'Temp session not cleared')
        self.assertTrue(utility_service.get_session_var(test_var_1) == test_val_1, 'Regular session mistakenly cleared')
