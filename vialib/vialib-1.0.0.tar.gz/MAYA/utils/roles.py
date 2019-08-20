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

# $Id: roles.py 33189 2008-07-16 13:48:55Z vanstone $

# A bunch of common roles, and some common role manipulations.

from MAYA.VIA import uuid, uform
from MAYA.utils import buckets
from MAYA.utils.shepherding import waitForPresence

# common roles; feel free to add more
entity_role = uuid._('~fd000a02510bfd0a96b73e')
shepherable_role = uuid._('~fd000a02510bfd5c14cb15')
index_root_role = uuid._('~010a685574d02011d89f8179ba7fb44707')
publisher_spatial_index_role = uuid._('~01e8855ff0b0c511d8ab5051d332a474d1')
scalable_collection_head_role = uuid._('~01b8b8d720d01e11d8a50d487872f16706')
scalable_collection_segment_role = uuid._('~01d2021300d01d11d8932f026153455feb')
collection_role = uuid._('~fd000a02510bfd17204424')
annotated_collection_role = uuid._('~fd000a02510bfdad92deec')
path_role = uuid._('~01e7225c0a1ed811d8a9335c3a4539639d')
image_role = uuid._('~fd000a02510bfd8c2411dc')
temporal_reference_role = uuid._('~fd000a02510bfdb8057f01')
geo_ref_global_coordinate_system_role = uuid._('~fd000a02510bfd7b6cab54')
location_reference_role = uuid._('~0142fbc37cef2611d88bb7026b4b4a3086')
member_of_dataset_role = uuid._('~fd000a02510bfd85df4b69')
channel_role = uuid._('~01e60a713488bb11d88a1936f55b8528c2')
outbox_role = uuid._('~0145eb163488bd11d8936b43b045af7460')
cred_role = uuid._('~fd000a02510bfd6ab544cc')
person_role = uuid._('~fd000a02510bfd0cada40f')
secret_role = uuid._('~01d206946c92eb11d8bc9b0d8259cc676a')
rtree_role = uuid._ ( '~01d37ae72c119311d99a7239eb19bd68fc' )
trie_role = uuid._('~01a306a77c1ef711d9ace12f8a2ae45168')
civ_content_role = uuid.fromString('~fd000a02510bfda74e1879')
infoline_la_taxonomy_element_role = uuid._('~019f9d781023aa11d99ead5983685e1d86')
dhs_facility_role = uuid._('~013aeb775a074911d9be646e6f5ea75580')
facility_role = uuid._('~fd000a02510bfd9051eb7e')
address_role = uuid._('~fd000a02510bfd59fdde44')
telephone_role = uuid._('~fd000a02510b2e1c711f')
legislator_role = uuid._('~01135d98802f8f11d98651601342094f36')
textscrap_role = uuid._('~fd000a02510bfd0451f0cb')
activist_issue_role = uuid._('~01e70e8fe8305411d9a2444a4b0e2e6fab')
java_renex_atomic_bp_role = uuid._('~01a469b60a4fc011d98d3200b458227ee3')
dataset_role = uuid._('~fd000a02510bfdafa9cbbd')
attribution_role = uuid._('~fd000a02510bfd81b171c7')
uri_ref_role = uuid._('~0114f7aa626ec111d88b023b633ac819b5')
rtree_head_role = uuid._('~0189112434c7c911d98e2c34db737a4e2a')
rtree_node_role = uuid._('~01d37ae72c119311d99a7239eb19bd68fc')
access_controlled_role = uuid._('~fd000a02510bfd4301b149')
event_schedule_role = uuid._('~013be71d209fc011d98d6f1f5a685c0301')
event_role = uuid._('~01e0e9f72463ee11d9aa5f52ef1ed14fb3')
augmented_entity_role = uuid._('~fd000a02510bfdb1c0b88e')
nsc_role = uuid._('~0165594120056b100c9bf802e15c6e69fe')
org_role = uuid._('~fd000b70d45d06')
service_offering_role = uuid._('~01008d6010cb23100aba7d6d9a044703b5')

class RoleImplication(object):

    def __init__(self):
        self.role_implications = {}
        
    def implies(self, r, role_a, role_b):
        """ True if role_a implies role_b """

        if role_a not in self.role_implications:
            closure = {role_a: 1}
            while expand_role_closure(r, closure):
                pass
            self.role_implications[role_a] = closure
        return role_b in self.role_implications[role_a]

    def plays_role(self, r, uid, role_a):
        waitForPresence(r, uid)
        roles = r.getAttr(uid, 'roles') or []
        if role_a in roles:
            return True
        for rl in roles:
            if self.implies(r, rl, role_a):
                return True
        return False

role_implication = RoleImplication()

# return 1 if all the given roles are found in the roles of uid
# "role" can be either a uuid or a list of uuids
def has_role(r, uid, role):
    waitForPresence(r, uid)
    roles = r.getAttr(uid, 'roles') or []
    t = type(role)
    if t is type([]) or t is type(()):
        for r in role:
            if not (r in roles):
                return 0
        return 1
    return role in roles

# return 1 if more roles are added, 0 otherwise
def expand_role_closure(r, role_closure):
    n = len(role_closure)
    roles = role_closure.keys()
    for role in roles:
        waitForPresence(r, role)
        implied_roles = r.getAttr(role, 'implied_roles') or []
        for rl in implied_roles:
            role_closure[rl] = 1
    return len(role_closure) > n

# return True if the given role is implied by any of the uid's roles
def plays_role(r, uid, role):
    return role_implication.plays_role(r, uid, role)

def old_plays_role(r, uid, role):
    waitForPresence(r, uid)
    roles = r.getAttr(uid, 'roles') or []
    if role in roles: return True
    role_closure = {}
    for rl in roles:
        role_closure[rl] = True
    while expand_role_closure(r, role_closure):
        if role in role_closure.keys():
            return True
    return False
    
# make sure uid plays the given role
def ensure_role(r, uid, role):
    if not plays_role(r, uid, role):
        roles = r.getAttr(uid, 'roles') or []
        roles.append(role)
        r.setAttr(uid, 'roles', roles)
    return

# remove a role from a uform if present    
def remove_role(r, concept, role):
    waitForPresence(r, concept)
    roles = r.getAttr(concept, "roles") or []
    try:
        del roles[roles.index(role)]
        r.setAttr(concept, 'roles', roles)
    except:
        pass

class RoleTree:

    def __init__(self, r, starting_roles):
        self.r = r
        self.role_list = []
        self.expand(starting_roles)
        self.build_attr_map()

    def get_all_roles(self):
        return self.role_list

    def get_all_attributes(self):
        return self.attr_map.keys()

    def is_in_list(self, role):
        for r in self.role_list:
            if role == r.uuid:
                return 1
        return 0

    def expand(self, roles):
        if not roles: return
        fringe = []
        for role in roles:
            if self.is_in_list(role): continue
            if uuid.isa(role):
                waitForPresence(self.r, role)
		attrs = self.r.listAttr(role)
                uf = self.r.getAttr(uform.UForm(role, list(attrs)))
            else:
                uf = role
            self.role_list.append(uf)
            fringe.extend(uf.get('implied_roles') or [])
        self.expand(fringe)
        return

    def build_attr_map(self):
        attr_map = buckets.Buckets()
        for uf in self.role_list:
            for attr in uf.get('attributes', []):
                attr_map[attr] = uf
        self.attr_map = attr_map
        return

    def getRolesByAttr(self, attr):
        return self.attr_map[attr]

def describe(uu,r=None):
	# added by DH 03-Aug-2006
	from MAYA.VIA import repos
	if r is None: r = repos.Repository('localhost:6200')
	i_care_about = ['name', 'description']
	return dict( [ (x,r.getAttr(uu,x)) for x in i_care_about ] )

def test():
    # add the path role to Trinidad
    from MAYA.VIA import repos
    r = repos.Repository('joshua3.prv.maya.com:8888')
    trinidad = uuid._('~01b39c4c3cdceb11d8a6d37ee938d3240a')
    ensure_role(r, trinidad, path_role)
    return

def test_roletree():
    from MAYA.VIA import repos
    r = repos.Repository('joshua3.prv.maya.com:8888')
    rt = RoleTree(r, [path_role])
    ufs = rt.getRolesByAttr('path_bounds')
    for uf in ufs:
        print uf['name']

if __name__ == '__main__':
    test_roletree()
