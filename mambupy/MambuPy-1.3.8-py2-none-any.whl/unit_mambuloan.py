# coding: utf-8

import mock
import unittest

import mambuloan

class MambuLoanTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from mambuutil import getloansurl
        self.assertEqual(mambuloan.mod_urlfunc, getloansurl)

    def test_class(self):
        l = mambuloan.MambuLoan(urlfunc=None)
        self.assertTrue(mambuloan.MambuStruct in l.__class__.__bases__)

    def test___init__(self):
        l = mambuloan.MambuLoan(urlfunc=None)
        self.assertEqual(l.customFieldName, 'customFieldValues')

    @mock.patch('mambuloan.MambuStruct')
    def test_getDebt(self, mambustruct):
        l = mambuloan.MambuLoan(urlfunc=lambda x:x)
        self.assertEqual(l.getDebt(), 0)
        l['principalBalance'] = 1
        l['interestBalance'] = 1
        l['feesBalance'] = 1
        l['penaltyBalance'] = 1
        self.assertEqual(l.getDebt(), 4)


if __name__ == '__main__':
    unittest.main()
