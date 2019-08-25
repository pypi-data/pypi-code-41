import unittest
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)


from mailroom.Email import Email, EmailMessage
from mailroom.email_client import exchange

class TestEmail(unittest.TestCase):
    pass
    # def test_output(self):
    #     logger.info(f'test_output 3x4 = {timesfour(3)}')
    #     self.assertEqual(timesfour(3), 12)
    #     # with self.assertRaises(TypeError):
    #     #     timesfour('string')

    # def test_output_check(self):
    #     with self.assertRaises(TypeError):
    #         timesfour('two')


    # def test_variable_type_check(self):

    #     logger.debug(f'variable type is f{}')
    #     self.assertFalse(timesfour("string"), )

unittest.main(module=__name__)
