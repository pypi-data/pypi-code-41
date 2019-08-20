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
Document Number role

UUID:   ~019602D126-00BE-4481-9229-2E79B02134A6

Implied Roles:

-=-=-=-
Entity
-=-=-=-
Name            String
Label           String
Description     String


The real deal:

owner            UUID
issue date       Date
client           UUID
project          UUID
content approval UUID
copy approval    UUID
document         MIME
file name        String
revisions        UUID
"""

###############################################################################
#
###############################################################################
import MAYA.uuid
import sys
import string
import types


###############################################################################
#
###############################################################################
UUID       = MAYA.uuid.fromString("~019602D126-00BE-4481-9229-2E79B02134A6")

attributes = ["owner", "issue date", "client", "project",
              "content approval", "copy approval", "document", "file name",
              "revisions"]

name = "Document Number"



###############################################################################
#
###############################################################################
MAX_FILENAME_LEN = 31



###############################################################################
#
###############################################################################
def generateFileName(label, file_ext, description = ""):
    """
    /label/       the document number i.e. MAYA-01004
    /file_ext/    the extension of this file without any "."'s
    /description/ whatever additional info
    
    returns a good filename for this document that's less or equal to %s chars
    including the extension
    """%(MAX_FILENAME_LEN)
    
    
    label_len = len(label)
    ext_len   = len(file_ext)
    len_avail = MAX_FILENAME_LEN - label_len - ext_len - 2

    description = description or ""

    assert(type(description) in types.StringTypes)
    
    if label:
        label = "%s_"%(label)
        
    if label_len < MAX_FILENAME_LEN:
        filename = "%s%s.%s"%(label,
                             description[:len_avail],
                             file_ext)
        #sys.stderr.write("%s - %d"%(filename , len(filename)))

    else:
        filename = "%s.%s"%(label_len[:(MAX_FILENAME_LEN - ext_len - 2)],
                            file_ext)

    assert(len(filename) <= MAX_FILENAME_LEN)
    
    filename = string.lower(filename)
    
    final_filename = []
    
    # convert special characters to plain ol' underscores
    for s in filename:
        if s in (" ", "\\", "/", ":", "*", "?", '"', "<", ">", "|", "-", "#"):
            s = "_"
        final_filename.append(s)
        
    return string.join(final_filename, "")

