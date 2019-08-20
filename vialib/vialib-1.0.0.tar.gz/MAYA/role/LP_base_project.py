#######################################################################
#
#       COPYRIGHT 2005 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
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

LP Base Project
UUID:  ~018b91914016f111d5b49328e73b2043f2

"""



###############################################################################
#
#
#
###############################################################################
import MAYA.uuid
import MAYA.role




###############################################################################
#
#
#
###############################################################################
UUID = MAYA.uuid.fromString("~018b91914016f111d5b49328e73b2043f2")

attributes = ["labor", "status", "start date", "end date", "project manager",
              "expenses", "billing time allowed", "acceptance probability",
              "relationship manager", "rate", "budget"]

name = "LP Base Project"


_OPEN_PROJECT_ = MAYA.uuid.fromString("~01f67c952afda311d49f2118ef0bb531b3")
_CLOSED_PROJECT_ = MAYA.uuid.fromString("~01004e9e2cfda411d49f2154de306c3be1")

