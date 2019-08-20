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
CMS Client role

UUID:   ~FD000A0251.0B.2C05844E



Implied Roles:

-=-=-=-
Entity
-=-=-=-

The real deal:

Address_type - String or String array
PO_Box       - String
Street       - String
Extended_Adr - String
Locality     - String
Region       - String
Postal_Code  - String
Country      - String

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
UUID       = MAYA.uuid.fromString("~FD000A0251.0B.2C05844E")
attributes = ["address_type", "po_box", "street", "extended_adr", "locality",
              "region", "postal_code", "country"]
name       = "Address"


_WORK_ = "WORK" # work address
_HOME_ = "HOME" # home address
_DOM_ = "DOM" # domestic address
_INTL_ = "INTL" # international address
_POSTAL_ = "POSTAL" # postal address
_PARCEL_ = "PARCEL" # parcel address