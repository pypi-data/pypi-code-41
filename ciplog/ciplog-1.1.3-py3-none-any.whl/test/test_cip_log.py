import unittest
import os
from ciplog import CipLog, LOG_PATH
from datetime import datetime


class TestCipLog(unittest.TestCase):

    def setUp(self):

        self._logger = CipLog()
        self._file_name_expected = datetime.now().strftime('%d-%m-%Y.log')

        file_path = 'logs/{0}'.format(self._file_name_expected)
        self._logger.warning(1, message="this is a warning")

        try:
            f = open(file_path)
            if f.readable():
                f.close()
                os.remove(file_path)
        except FileNotFoundError:
            self._logger.debug('file not found!')

    def test_create_a_log_file_with_the_current_date_pattern(self):
        self._logger.warning(1, "test_minimal-template", "this is a warning")
        self._logger.info(200, "test_minimal-template", "this is an info")
        self._logger.error(4, 500, "test_minimal-template", "this is an error")

        file = self._logger.get_log_files()[0]
        base_name = os.path.basename(file)
        self.assertEqual(self._file_name_expected, base_name)

    def test_when_not_set_path(self):
        self.assertEqual(self._logger.path(), LOG_PATH)

    def test_when_set_path(self):
        PATH = os.getcwd()
        self._logger = CipLog(log_path=PATH)
        self.assertEqual(self._logger.path(), PATH)

    def test_set_name(self):
        self._logger = CipLog('name_test')
        self.assertEqual(self._logger.service_name_log(), "name_test")

    def test_when_not_set_name(self):
        self._logger = CipLog()
        self.assertEqual(self._logger.service_name_log(), "cip_log")

    def test_set_service_version(self):
        os.environ['GIT_TAG'] = "1.0.0"
        self._logger = CipLog()
        self.assertEqual(self._logger.service_version_log(), "1.0.0")
        del os.environ['GIT_TAG']

    def test_when_not_set_service_version(self):
        os.environ.unsetenv('GIT_TAG')
        self._logger = CipLog()
        self.assertEqual(self._logger.service_version_log(), "0.0.0")

    def tearDown(self):
        self._logger.delete_log_files()


if __name__ == '__main__':
    unittest.main()
