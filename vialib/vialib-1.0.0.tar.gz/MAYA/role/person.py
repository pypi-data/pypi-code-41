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
Person role

UUID:   ~fd000a0251-0b-fd0cada40f


Implied Roles:

-=-=-=-
Entity
-=-=-=-


The real deal:

Family_Name
Name
Given_Name
Additional_Names
Name_Prefix
Name_Suffix
Photograph
EMAIL
Addresses
Birthdate
Telephone
"""


###############################################################################
#
#
#
###############################################################################
import MAYA.uuid
import MAYA.role
import re
import string





###############################################################################
#
#
#
###############################################################################
UUID = MAYA.uuid.fromString("~fd000a0251-0b-fd0cada40f")
attributes = ["family name", "name", "given name", "additional names",
              "name prefix", "name suffix", "photograph", "email",
              "addresses", "birthdate", "telephone"]

name       = "Person"

_EMAIL_REGEX_ = "^[\w\.]+\+?\w*@\w+\.\w+[\w\.]*$"




###############################################################################
#
#
#
###############################################################################
def isValidEmail(email_str, delim=None):
    assert(type(email_str) == type(""))
    
    delim = delim or ","
    emails = string.split(email_str, delim)
    
    for email in emails:
        email = string.strip(email)
        
        if re.match(_EMAIL_REGEX_, email, re.I) == None:
    
            return 0
        elif email_str[-1] == ".":
    
            return 0
            
    return 1
