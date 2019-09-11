import unittest
from looqbox.integration.integration_links import get_sso_attributes


class TestSQLIn(unittest.TestCase):

    def test_sso_attributes(self):
        """
        Test get_sso_attributes function
        """
        par = {
            "originalQuestion": "teste",
            "cleanQuestion": "teste",
            "residualQuestion": "",
            "residualWords": [""],
            "entityDictionary": None,
            "userlogin": "user",
            "userId": 666,
            "companyId": 0,
            "userGroupId": 0,
            "language": "pt-br",
            "apiVersion": 2
        }

        par2 = {
            "originalQuestion": "teste",
            "cleanQuestion": "teste",
            "residualQuestion": "",
            "residualWords": [""],
            "entityDictionary": None,
            "userlogin": "user",
            "userId": 666,
            "companyId": 0,
            "userGroupId": 0,
            "userSsoAttributes": {"group": ["Looqbox", "Test", "Group"], "user": ["looqbox@looqbox.com"]},
            "language": "pt-br",
            "apiVersion": 2
        }

        self.assertEqual([], get_sso_attributes(par))
        self.assertEqual({"group": ["Looqbox", "Test", "Group"], "user": ["looqbox@looqbox.com"]},
                         get_sso_attributes(par2))
