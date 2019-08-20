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

#!/usr/bin/env python

from MAYA.utils.shepherding import waitForPresence
from MAYA.VIA import uform

# $Id: conflicts.py 9726 2005-04-08 20:35:34Z widdows $
#
# This file offers some simple capabilities for dealing with conflicted uforms

CURR_VENUE = 'shepherd_conflict_current_venue'
MEMBERS = 'shepherd_conflict_members'
VENUES = 'shepherd_conflict_venues'
SIGNATURE = 'shepherd_conflict_signature'

# returns a list of the attributes in "uu" which are actually conflicted
def get_attrs(r, uu):
    waitForPresence(r, uu)	
    members = r.getAttr(uu, 'shepherd_conflict_members') or []
    members.append(uu)
    infos = []
    conflicted = {}
    attrs = {}
    for mem in members:
        waitForPresence(r, mem)
        info = r.listAttrInfo(mem)
        for attr in info.keys():
            attrs[attr] = 1
        infos.append(info)
    for attr in attrs.keys():
        curr = None
        for info in infos:
            if info.has_key(attr):
                if (curr != None) and (curr != info[attr]):
                    conflicted[attr] = 1
                else:
                    curr = info[attr]
    return conflicted.keys()

# "resolves" a conflict by removing the conflict attributes
# this means that the version in the venue specified by "r" will win out
def force_resolve(r, uu):
    waitForPresence(r, uu)
    uf = uform.UForm(uu, [CURR_VENUE, MEMBERS, VENUES, SIGNATURE])
    uf = r.getAttr(uf)
    uf[CURR_VENUE] = None
    uf[MEMBERS] = None
    uf[VENUES] = None
    uf[SIGNATURE] = None
    r.setAttr(uf)
    
def force_resolve_batch(r, uuid_list):
    for uu in uuid_list:
        if is_conflicted(r, uu):
            force_resolve(r, uu)

def is_conflicted(r, uu):
	waitForPresence(r, uu)
	attrs = r.listAttr(uu)
	return ((CURR_VENUE in attrs) or (MEMBERS in attrs) or (VENUES in attrs) or (SIGNATURE in attrs))
