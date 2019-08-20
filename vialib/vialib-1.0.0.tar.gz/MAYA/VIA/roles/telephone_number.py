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
Telephone Number role 

UUID:   ~FD000A0251.0B.2E1C711F

 
Implied Roles:

-=-=-=-
Entity
-=-=-=-


The real deal:

Telephone_type   - String or string array 
Telephone_number - String

"""


###############################################################################
#
#
#
###############################################################################
import MAYA.VIA.uuid
import re





###############################################################################
#
#
#
###############################################################################
UUID = MAYA.VIA.uuid.fromString("~FD000A0251.0B.2E1C711F")
attributes = ["telephone_type", "telephone_number"]

name       = "Telephone Number"

_PREF_ = "PREF"
_HOME_ = "HOME"
_WORK_ = "WORK"
_FAX_ = "FAX"
_VOICE_ = "VOICE"
_PAGER_ = "PAGER"
_CELL_ = "CELL"


__REGEX_PATTERN = "^\+\d+-\d+-\d+-\d+$"




###############################################################################
#
###############################################################################
def isValidPhoneNumber(phone_str):
    """
    validates a given string phone number to the format of
    +country_code-area_code-local-number
    """
    
    
    if re.match(__REGEX_PATTERN, str(phone_str)) != None:

        return 1
    else:

        return 0
        
