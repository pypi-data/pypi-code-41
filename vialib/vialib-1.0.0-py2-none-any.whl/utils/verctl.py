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

# $Id: verctl.py 9726 2005-04-08 20:35:34Z widdows $

## verctl.py
##
## This provides an implementation of a version control facility for uforms.
## It is somewhat based on the version control design note, though currently
## there is no vault, no sandbox uforms, and the attributes have been
## renamed.  Also, it creates the UUIDs for the historical versions by
## right-extending the original uform with the ISO-8601 date of the checkin;
## combined with the stemming functionality in the repository, this allows for
## the recovery of historical versions even if the current version is
## corrupted or missing entirely.

from MAYA.VIA import uuid
from MAYA.VIA import uform
from MAYA.utils import date
from MAYA.utils.shepherding import waitForPresence
from MAYA.utils import conflicts
import time, string

VCU_ROLE = uuid.fromString('~01ac7bd7061bc711d988462a8370461b09')
VCU_HISTORY_ROLE = uuid.fromString('~01dd130c161c7811d9b37123d449f929f4')

class VersionControlException(Exception):
    pass

def currentDate():
    return date.fromUnix(time.time())

def checkin(r, uu, author = None, comment = '', timestamp = None):
    if conflicts.is_conflicted(r, uu):
        raise VersionControlException('uform %s is conflicted' % uu.toString())
	
    if not timestamp:
        timestamp = currentDate()
    
	tsuu = uuid.fromString(timestamp.toString(0))
	historicalUU = tsuu.leftExtend(uu)    
    
    waitForPresence(r, uu)    

    uf = uform.UForm(uu, ['roles', 'vcs_current', 'vcs_ancestor'])
    uf = r.getAttr(uf)
    
    if uf['vcs_current'] and (uf['vcs_current'] != uu):
        raise VersionControlException("can't check in historical uform")
    
    roles = uf['roles'] or []
    if not (VCU_ROLE in roles):
        roles.append(VCU_ROLE)
    uf['roles'] = roles
    uf['vcs_current'] = uu
    r.setAttr(uf)
    
    uf = r.getUForm(uu)
    uf.uuid = historicalUU
    if not (VCU_HISTORY_ROLE in uf['roles']):
        uf['roles'].append(VCU_HISTORY_ROLE)
    uf['vcs_author'] = author
    uf['vcs_comment'] = comment
    uf['vcs_date'] = timestamp
    r.setAttr(uf)
    
    r.setAttr(uu, 'vcs_ancestor', historicalUU)  
    
def getVersions(r, uu):
    verD = {}
    curr = uu
    while curr:
        verD[curr] = 1
        waitForPresence(r, curr)
        curr = r.getAttr(curr, 'vcs_ancestor') or None
    
    uubuf = uu.getBuf()
    curr = uu
    while curr:
        buf = curr.getBuf()
        if (string.find(buf, uubuf) == 0):
            verD[curr] = 1
        else:
            break
        curr = r.nextUForm(curr)
        
    del verD[uu]
    results = verD.keys()
    results.sort()
    results.reverse()
    return results
   