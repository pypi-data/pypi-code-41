from unittest import TestCase
from dk_api_helpers import *

class test_dk_api_helpers(TestCase):
    def test_getTypeOfTestLine(self):
        self.assertEquals(getTypeOfTestLine(''), None)
        self.assertEquals(getTypeOfTestLine('skjasdljkdskdsjlkdasjkl'), None)
        typ,val  = getTypeOfTestLine('Tests: Warning')
        self.assertEquals(typ, "Level")
        self.assertEquals(val, "Warning")
        typ,val  = getTypeOfTestLine('Step (put-dispense)')
        self.assertEquals(typ, "Step")
        self.assertEquals(val, "put-dispense")
        typ,val  = getTypeOfTestLine('7. test-confirmationnum-mismatch-2010 (6624 num_dupes_confnum == 0)')
        self.assertEquals(typ, "Test")
        self.assertEquals(val, "test-confirmationnum-mismatch-2010")

    def test_parseTestString(self):
        with open('./tests/static/PlatformTestResults1.txt','r') as f:
            testData = f.read()
        expected = [(u'test_check_Veeva_Beghou_file_dates_invalid_date', u'check_Veeva_Beghou_file_dates', u'Passed'), (u'test_check_Veeva_Beghou_duplicate_file_types', u'check_Veeva_Beghou_file_dates', u'Passed'), (u'test_check_Veeva_Beghou_files', u'check_Veeva_Beghou_file_dates', u'Passed'), (u'test_create_redshift_schema', u'create_schema', u'Passed'), (u'test_copy_Veeva_HCPS', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_AccountGroupOverview', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_Interaction', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_AddressChanges', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_Pathways', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_HCPOverview', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_Interaction_FRS_HEOR', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_InteractionReprints', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_InteractionHCP', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_HCPAffiliations', u'put_Veeva_Beghou', u'Passed'), (u'test_copy_Veeva_ActiveAccounts', u'put_Veeva_Beghou', u'Passed')] 
        self.assertListEqual(parseTestString(testData), expected)
