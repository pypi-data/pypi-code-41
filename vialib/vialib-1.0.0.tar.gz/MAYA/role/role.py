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
#!/usr/local/bin/python

"""

UUID: ~fd000a0251-0b-fd1d650a97

attributes        	List
implied roles         	List
implied roles closure 	List

"""

################################################################################
#
################################################################################
import MAYA.uuid
import MAYA.uform
from MAYA.role import entity




################################################################################
#
################################################################################
_ATTRIBUTES_ATTR_            = "attributes"
_IMPLIED_ROLES_ATTR_         = "implied_roles"
_IMPLIED_ROLES_CLOSURE_ATTR_ = "implied_roles_closure"

_UUID_ = MAYA.uuid.fromString("~fd000a0251-0b-fd1d650a97")
_ATTRIBUTES_ = [_ATTRIBUTES_ATTR_,
                _IMPLIED_ROLES_ATTR_,
                _IMPLIED_ROLES_CLOSURE_ATTR_]
_IMPLIED_ROLES_ = [entity._UUID_]
_IMPLIED_ROLES_CLOSURE_ = _IMPLIED_ROLES_ + entity._IMPLIED_ROLES_CLOSURE_





################################################################################
# classes
################################################################################
class Role(entity.Role):
    """
    Role Role
    """
    
    # only an aggregate of the class not the instance
    # cuz otherwise it will create a chicken and egg problem
    __IMPLIED_ROLES_ = (entity.Role,)
    __IMPLIED_ROLES_CLOSURE_ = __IMPLIED_ROLES_ + entity.Role.__IMPLIED_ROLES_CLOSURE_
    __UUID_ = _UUID_
    __ATTRIBUTES_ = _ATTRIBUTES_
        

class UForm(entity.UForm):
    """
    Role UForm
    """
    
    __ROLES_ = (Role, )
    

