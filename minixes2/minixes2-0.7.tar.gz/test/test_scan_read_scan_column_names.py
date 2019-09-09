'''
Created on Mar 25, 2019

@author: hammonds
'''
import unittest
from minixs.gui import util

class Test(unittest.TestCase):


    def setUp(self):
        self.old_column_count = 8
        self.filename_olddet = "../data/Cuecal.0001"
        self.new_column_count = 23
        self.filename_newdet = "../data/mini2CrCali.0001"



    def testOldDetFile(self):
        column_names = util.read_scan_column_names(self.filename_olddet)
        self.assertEqual(len(column_names), self.old_column_count)
        print(column_names)
        
    def testNewDetFile(self):
        column_names = util.read_scan_column_names(self.filename_newdet)
        self.assertEqual(len(column_names), self.new_column_count)
        print(column_names)
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()