'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import unittest
from PyQt5.QtWidgets import QApplication, QTableWidgetSelectionRange
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from minixs.gui.qtcalibrator.calibratorexposureselector import CalibratorExposureSelector
import logging
from logging import StreamHandler
LOGGER_NAME = 'testcalibratorexposureselector'
app = QApplication(sys.argv)
LOG_FORMAT='F- %(asctime)-15s - %(name)s - %(funcName)s- %(levelname)s - %(message)s'

class Test(unittest.TestCase):
    logger = logging.getLogger(LOGGER_NAME)
    handler = StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    def setUp(self):
        self.old_column_count = 8
        self.filename_olddet = "../data/Cuecal.0001"
        self.new_column_count = 23
        self.filename_newdet = "../data/mini2CrCali.0001"
        self.empty_scan_file = "../data/Cuecal.0001.empty"
        self.not_a_scan_file = "../data/notAScanFile"
        self.ces = CalibratorExposureSelector()

    def tearDown(self):
        pass


    def testAppendRow(self):
        appendButton = self.ces.appendRowButton
        self.assertEqual(self.ces.table.rowCount(), 0, "Test start at zero")
        rowCountBefore = self.ces.table.rowCount()
        # test one Mouse Click
        QTest.mouseClick(appendButton, Qt.LeftButton)
        rowCountAfter = self.ces.table.rowCount()
        self.assertEqual(self.ces.table.rowCount(), 1)
        self.assertEqual(rowCountBefore, rowCountAfter-1, "Test one click append")
        # Test 3 more clicks on append
        rowCountBefore = self.ces.table.rowCount()
        QTest.mouseClick(appendButton, Qt.LeftButton)
        QTest.mouseClick(appendButton, Qt.LeftButton)
        QTest.mouseClick(appendButton, Qt.LeftButton)
        rowCountAfter = self.ces.table.rowCount()
        self.assertEqual(rowCountBefore, rowCountAfter-3, "Test three more clicks append")
        
    def testDeleteRows(self):
        deleteButton = self.ces.deleteRowsButton
        appendButton = self.ces.appendRowButton
        
        #add a blank roww0
        self.assertEqual(self.ces.table.rowCount(), 0, "testDelete add an empty row")
        QTest.mouseClick(appendButton, Qt.LeftButton) 
        
        self.assertEqual(self.ces.table.rowCount(), 1, "testDelete add an empty row")
        
        # now try removing it:
        self.ces.table.setRangeSelected(QTableWidgetSelectionRange(0,0, 0, 1), True)
        selectedRanges = self.ces.table.selectedRanges()
        self.logger.debug ("selectedRanges %s" % selectedRanges)
        self.logger.debug ("selectedRanges.rowCount() %s" % selectedRanges[0].rowCount())
        self.logger.debug ("selectedRanges.topRow() %s" % selectedRanges[0].topRow())
        self.logger.debug ("selectedRanges.leftCoolumn() %s" % selectedRanges[0].leftColumn())
        self.logger.debug ("selectedRanges.bottomRow() %s" % selectedRanges[0].bottomRow())
        self.logger.debug ("selectedRanges.rightColumn() %s" % selectedRanges[0].rightColumn())
        QTest.mouseClick(deleteButton, Qt.LeftButton) 
        
        self.assertEqual(self.ces.table.rowCount(), 0, "testDelete add an empty row rowCount %s, expected %s" % (self.ces.table.rowCount(), 0))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger(LOGGER_NAME).setLevel(logging.DEBUG)
    unittest.main()