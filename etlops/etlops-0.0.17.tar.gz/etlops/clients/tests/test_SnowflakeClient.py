import unittest
from unittest.mock import Mock
from itertools import product
from etlops.clients.mpp import SnowflakeClient
from pandas import DataFrame

MockCredentials = {'user': 'blabla',
                   'account': 'bloblo',
                   'password': 'yadayada',
                   'insecure_mode': False}


class SnowflakeClientTest(unittest.TestCase):
    valid_warehouse_states = ('STARTED', 'SUSPENDING', 'SUSPENDED')

    def setUp(self):
        self.SFClient = SnowflakeClient(config=MockCredentials)
        self.SFClient.dml_query = Mock()
        self.SFClient.select_query = Mock()

    def test_check_warehouse_state_dispatchs_correct_warehouse_state(self):
        for valid_warehouse_state in self.valid_warehouse_states:
            self.SFClient.select_query.return_value = DataFrame({'name':'MEDIUM_QUERY','state': valid_warehouse_state,'type':None,'size':None} , index = [0])
            self.assertTrue(self.SFClient._SnowflakeClient__check_warehouse_state(warehouse = 'medium_query') in self.valid_warehouse_states)

    def test_AlterWarehouse_resumes_and_suspends_only_when_it_should(self ,):
        alter_warehouse_test_params = tuple([Pair for Pair in product(['STARTED','SUSPENDED','SUSPENDING'],['resume','suspend'])])
        for warehouse_status, action in alter_warehouse_test_params:
            self.SFClient._SnowflakeClient__check_warehouse_state = Mock(return_value = warehouse_status)
            self.SFClient.alter_warehouse(warehouse = 'MEDIUM_QUERY' , action = action)
            if (action == 'suspend' and warehouse_status not in ('SUSPENDED','SUSPENDING')) or (action == 'resume' and warehouse_status in ('SUSPENDED','SUSPENDING')):
                self.SFClient.dml_query.assert_called_with('Alter warehouse {warehouse} {ACTION};'.format(warehouse = 'MEDIUM_QUERY' , ACTION = action))
                self.SFClient.dml_query.reset_mock()
            else:
                self.SFClient.dml_query.assert_not_called()


