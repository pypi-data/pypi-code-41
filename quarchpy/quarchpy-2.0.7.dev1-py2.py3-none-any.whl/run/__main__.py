'''
This script allows execution of select quarchpy scripts with out needing the full address.
'''

import sys
from quarchpy.debug.SystemTest import main as systemTestMain
from quarchpy.disk_test.driveTestCore import main as driveTestCoreMain
from quarchpy.calibration.calibrationUtil import main as calibrationUtilMain
from quarchpy.qis.qisFuncs import startLocalQis
from quarchpy.qps.qpsFuncs import startLocalQps
from quarchpy.debug.upgrade_quarchpy import main as uprade_quarchpy_main

def main(argstring):

    if "debug_info" in argstring[0].lower():
        systemTestMain() #quarchpy.debug.SystemTest
    elif "qcs" in argstring[0].lower():
        driveTestCoreMain(argstring[1:])#driveTestCore Backend
    elif "calibration_tool" in argstring[0].lower(): 
        calibrationUtilMain(argstring[1:])#Calibration Tool
    elif "qis" in argstring[0].lower():
        startLocalQis()  #QIS
    elif "qps" in argstring[0].lower():
        startLocalQps()  #QPS
    elif "upgrade_quarchpy" in argstring[0].lower():
        uprade_quarchpy_main(argstring[1:])#Upgrade Quarchpy


if __name__ == "__main__":
    print(sys.argv)
    main (sys.argv[1:])