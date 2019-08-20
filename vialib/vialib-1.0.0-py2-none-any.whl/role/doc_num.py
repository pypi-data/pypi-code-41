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
Document Top Level Role

UUID:   ~01BD00FEF9-E45F-4f4b-9ED5-5FC478847C1C


Implied Roles:

-=-=-=-
Entity
-=-=-=-
Name            String
Label           String
Description     String


The real deal:

revisions
"""



import MAYA.uuid

UUID       = MAYA.uuid.fromString("~01BD00FEF9-E45F-4f4b-9ED5-5FC478847C1C")

attributes = ["revisions"]

name = "Document Top Level"




###############################################################################
#
###############################################################################
def isImpliedBy(uu_or_uf, repos = None):
    """
    checks if the passed in uform implies the Extranet client role
    """
    
    if repos == None:
        assert(MAYA.uform.isa(uu_or_uf))
        if not uu_or_uf.has_key("implied_roles_closure"):
            uu_or_uf["implied_roles_closure"] = []
         
        if not uu_or_uf.has_key("roles"):
            uu_or_uf["roles"] = []
            
        assert(len(uu_or_uf["implied_roles_closure"]) > 0 or \
               len(uu_or_uf["roles"]) >0)
        
        return (UUID in uu_or_uf["implied_roles_closure"] or\
                UUID in uu_or_uf["roles"])
    
        
    else:
        assert(MAYA.uuid.isa(uu_or_uf))
    
        return MAYA.role.impliesRole(uu_or_uf, UUID, repos)
