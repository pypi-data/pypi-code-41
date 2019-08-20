#######################################################################
#
#       COPYRIGHT 2006 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################
"""
"""

###############################################################################
#
###############################################################################
import unittest
import datetime

from MAYA.VIA import vsmf
from MAYA.utils import date






###############################################################################
#
###############################################################################
class Tests(unittest.TestCase):
    def testVsmfBinary(self):

        # make sure concatenating two vsmf.Binary gives you vsmf.Binary
        b = vsmf.Binary("b")
        
        self.assertEquals(type(b + b), type(b))
        self.assert_(isinstance(b + b, vsmf.Binary))
        self.assertEquals(len(b + b), 2)

        b += b
        
        self.assertEquals(type(b), type(b))
        self.assert_(isinstance(b, vsmf.Binary))
        self.assertEquals(len(b), 2)


    def testDateToDatetimeNoTimezone(self):
        d = vsmf.Date((733422, 51088.75))
        exp = datetime.datetime(2009, 1, 15, 14, 11, 28,750000)
        self.assertEqual((exp, None), d.toDatetime())

    def testDateToDatetimeWithTimezone(self):
        d = vsmf.Date((733422, 51088.75), 5)
        exp = datetime.datetime(2009, 1, 15, 14, 11, 28,750000)
        self.assertEqual((exp, -300), d.toDatetime())

    def testDatetimeToDateDateOnly(self):
        dt = datetime.date(2009, 1, 15)
        exp = vsmf.Date((733422, 0))
        self.assertEqual(exp, date.fromDatetime(dt))

    def testDatetimeToDateNoTimezone(self):
        dt = datetime.datetime(2009, 1, 15, 14, 11, 28, 750000)
        exp = vsmf.Date((733422, 51088.75))
        self.assertEqual(exp, date.fromDatetime(dt))

    def testNoneDatetimeToDate(self):
        exp = date.fromUnix()
        actual = date.fromDatetime()
        self.assertEqual(None, actual.tz)
        self.assertAlmostEquals(exp.toUnix(), actual.toUnix(), places = 2)

    def testDatetimeToDateWithTimezone(self):
        class tz(datetime.tzinfo):
            def __init__(self, offset):
                self._offset = datetime.timedelta(hours = offset)
            def utcoffset(self, dt):
                return self._offset
            def tzname(self, dt):
                return 'Test'
            def dst(self, dt):
                return datetime.timedelta(0)

        dt = datetime.datetime(2009, 1, 15, 14, 11, 28, 750000, tz(-3))
        exp = vsmf.Date((733422, 51088.75), 3)
        d = date.fromDatetime(dt)
        self.assertEqual(exp, d)
        self.assertEqual(exp.tz, d.tz)

###############################################################################
#
###############################################################################
if __name__ == "__main__":
    unittest.main()
