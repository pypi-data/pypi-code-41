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
Design Note

URL:    http://intra.maya.com/design/visage/visage_des/visnote/00012/visnote_00012.html
Number: VISNOTE-00012 
UUID:   ~fd000a0251-0b-fd0668dd9c 

Implied Roles:

-=-=-=-
Entity
-=-=-=-
Name            String
Label           String
Description     String

-=-=-=-
Collection
-=-=-=-
Members         Array

-=-=-=-
Text_Scrap
-=-=-=-
Text_Content    String

-=-=-=-
The real deal
-=-=-=-

ID              String  
Ref_RefBy       UUID    
Ref_Address     String  
Ref_Author      String  
Ref_Booktitle   String  
Ref_Chapter     String  
Ref_Edition     String  
Ref_Editor      String  
Ref_Journal     String  
Ref_Meeting     String  
Ref_Date        String  
Ref_Month       String  
Ref_Year        String  
Ref_Volume      String  
Ref_Number      String  
Ref_OrganizationString  
Ref_Pages       String  
Ref_Publisher   String  
Ref_Series      String  
Ref_Type                
                        
"""
import MAYA.uuid
import MAYA.role

UUID=MAYA.uuid.fromString("~fd000a0251-0b-fd0668dd9c")
attributes=['ref_refby', 'ref_address', 'ref_author', 'ref_booktitle', 'ref_chapter', 'ref_edition', 'ref_editor', 'ref_journal', 'ref_meeting', 'ref_date', 'ref_month', 'ref_year', 'ref_volume', 'ref_number', 'ref_organization', 'ref_pages', 'ref_publisher', 'ref_series', 'ref_type']

###############################################################################
"""
checks if the passed in uform implies the bibliographic entry role
"""
###############################################################################
def isImpliedBy(uu):
    
    uu=MAYA.role.__UFormifyOrCreate(uu)
    if uu.has_key("role"):
        return (UUID in uu["implied_roles_closure"])
    else:
        return 0
    
