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

#!/usr/bin/python

"""

Role utils

Seung Chan Lim (limsc@maya.com)

I'm gonna scan the source again sometime
to find out places where I can susbtitute
python loops with filter,map, etc... for speed.
It also still uses the string module... are we
moving on to 2.x???

The functions have been carefully coded so that
you can use it to either dynamically retreive
role information via a repository interface or
pass in a pre-cached uform to carry out the
function in a repository-less manner.


"""


################################################################################
# imports
################################################################################
import MAYA.VIA.uform
import MAYA.VIA.uuid
import MAYA.VIA.repos

from MAYA.VIA.roles import entity
from MAYA.VIA.roles import role




################################################################################
# globals
################################################################################
__uuid_class  = MAYA.VIA.uuid.UUID
__uform_class = MAYA.VIA.uform.UForm
__repos_class = MAYA.VIA.repos.Repository

__role_role_uuid = role._UUID_
__entity_role_uuid = entity.uuid

__entity_role_uf = MAYA.VIA.uform.UForm(entity._UUID_,
                                    {"attributes" : entity._ATTRIBUTES_,
                                     "implied_roles" : [],
                                     "implied_roles_closure" : [],
                                     "roles" : [__role_role_uuid]})

__role_role_uf = MAYA.VIA.uform.UForm(__role_role_uuid,
                                  {"attributes" : role._ATTRIBUTES_,
                                   "implied_roles" : [__entity_role_uf],
                                   "implied_roles_closure" : [__entity_role_uf],
                                   "roles" : [__role_role_uuid]})
__role_role_uf["roles"] = [__role_role_uf]


_IMPLIED_ROLES_CLOSURE_ATTR_ = role._IMPLIED_ROLES_CLOSURE_ATTR_
_IMPLIED_ROLES_ATTR_ = role._IMPLIED_ROLES_ATTR_
_ROLES_ATTR_ = "roles"




################################################################################
# functions
################################################################################




###############################################################################
# creates a new role uform with optional implied roles
# role uform will have the role uform as a member of its roles collection
# and a list of implied roles in its implied_roles and implied_roles_closure
# collections
# 
# parameter(s)   : uu            - uuid or a uform or a string representation
#                                  of a uuid
#                  label         - label intended to fill the label attribute.
#                                  The name attribute will be automatically filled
#                                  in by appending the word "Role" to this value
#                  implied_roles - tuple of uuid of role uforms that this role
#                                  implies
#                  attrs         - tuple of attribute names that this role has
#                                  unique from the implied roles
#                  repos         - repository object or a socket connection to the
#                                  repository
#                  
# return value   : a role uform
###############################################################################
def createRoleUForm(uu            = None,
                    label         = None,
                    implied_roles = None,
                    attrs         = (),
                    repos         = None):

    uf = __UFormifyOrCreate(uu, create=1)
    
    # create a uform that is an instance of the role uform
    uf = createUFormOfRole(uf, (__role_role_uf,), repos, create_attributes=1)
    
    # it'll at least imply entity
    if not implied_roles:
        if uu == __entity_role_uuid:
            implied_roles = ()
        else:
            implied_roles = (__entity_role_uf,)


    # You need to pass in a sequence as the value of the
    # implied_roles parameter 
    assert(type(implied_roles) in (type(()),
                                   type([])))
    
    # make sure we're dealing with a list here
    # as a side effect we're also making a copy
    # just in case we were passed in a list
    # cuz we don't want the passed in parameter
    # do change when we return
    implied_roles = list(implied_roles)
    
    # Make sure you don't pass in duplicate roles
    assert(not filter(lambda i, r=implied_roles: r.count(i) > 1, implied_roles))

    # make sure the items in the list are uuids/uforms
    assert(not filter(lambda i, M1=MAYA.VIA.uform, M2=MAYA.VIA.uuid:
                      not M1.isa(i) and not M2.isa(i),
                      implied_roles))
        
   
    # now traverse the implied_roles_closure list
    # of all the roles in the implied_roles passed in
    # by default, you'll at least have the entity role
    # as part of your implied_roles even if you didn't pass
    # it in
    
    # NOTE:
    #    should I check for __entity_role_uuid
    #    when something IS passed in ?
    #    is that redundant since all roles will
    #    imply entity ?
    
    all_implied_roles = []
    
    # we only need to check one-level deep
    # per the roles implied_roles closure
    # spec
    def add_if_not_already_there(uu,
                                 all_implied_roles=all_implied_roles,
                                 repos = repos):
        if MAYA.VIA.uuid.isa(uu):
            try:
                uf_closure = repos.getAttr(uu, _IMPLIED_ROLES_CLOSURE_ATTR_) or []
            except AttributeError:

                raise TypeError, "Invalid repository interface"
            else:
                # we add the uuid that came in into the closure list as well
                uf_closure.append(uu)
        else:
            assert(MAYA.VIA.uform.isa(uu))
            uf_closure = uu.get(_IMPLIED_ROLES_CLOSURE_ATTR_, [])
            
            # we add the uuid that came in into the closure list as well
            uf_closure.append(uu)
            
        # given the closure list of this particular role
        # traverse and add the ones in it that we don't already have
        for uf_closure_uu in uf_closure:
            uf_closure_uu = __UUIDfyOrCreate(uf_closure_uu)

            if not filter(lambda i, u=uf_closure_uu: hasattr(i, "uuid") and i.uuid == u or i == u, all_implied_roles):
                all_implied_roles.append(uf_closure_uu)
        
                #print "now all implied roles is %s"%(repr(all_implied_roles))

    # for each of the implied roles we know of recurse one level
    # to grab their closures lists
    map(add_if_not_already_there, implied_roles)
    
    # make sure all are UUIDs
    for i in range(len(implied_roles)):
        implied_roles[i] = __UUIDfyOrCreate(implied_roles[i], 0)
        
    # all_implied_roles should now ONLY have the roles found in the
    # closure lists, so we need to add the original implied roles
    # list
    #all_implied_roles.extend(list(implied_roles))
    
    #print "\ncomplete list of implied roles: %s"%(repr(all_implied_roles))

    uf[_IMPLIED_ROLES_ATTR_] = implied_roles
    uf[_IMPLIED_ROLES_CLOSURE_ATTR_] = all_implied_roles

    # now add the extra attributes specific to this role
    if attrs:
        # You need to pass in a sequence as the value of
        # the attrs parameter
        assert( (type(attrs) == type(())) or (type(attrs) == type([])) )

        uf["attributes"] = list(attrs)

    # if we have a label for this, then set that as well
    if label:
        import string
        
        label = string.strip(label)
        uf["label"] = string.replace(label, " ", "_")
        
        uf["name"] = "%s%sRole"%(label,
                                 (label) and " " or "")
    else:
        uf["label"] = "Role_UForm"
        uf["name"] = "Role UForm"
        
        
    return uf


###############################################################################
#
# createUFormOfRole
# 
# creates a uform that is an instance of one or more roles
# 
# parameter(s) : uu                - uuid of the new uform
#                roles             - tuple of roles that this uform should be
#                                    an instance of
#                repos             - repository connection
#                create_attributes - if set to 0 no attributes will be created 
#                                    for the uform
#                
# return value : uform
###############################################################################
def createUFormOfRole(uu                = None,
                      roles             = (__entity_role_uf,),
                      repos             = None,
                      create_attributes = 1):
    
    uf = __UFormifyOrCreate(uu, create=1)
    
    attributes       = []
    traversed_roles  = []
    roles_collection = []

    # the roles argument must be a sequence
    assert( (type(roles) == type(())) or (type(roles) == type([])) )

    # traverse the roles list depth-first    
    for role in roles:
        # get its UUID
        role_uu = __UUIDfyOrCreate(role,0)
            
        if role_uu not in traversed_roles:
            roles_collection.append(role_uu)
            
            if MAYA.VIA.uuid.isa(role):
                try:
                    role_uf=repos.getAttr(MAYA.VIA.uform.UForm(role_uu,
                                                           {"attributes" : [],
                                                            _IMPLIED_ROLES_CLOSURE_ATTR_ : [],
                                                            _IMPLIED_ROLES_ATTR_: []}))
                except AttributeError:
                    
                    raise TypeError, "Invalid repository interface"
            else:
                assert(MAYA.VIA.uform.isa(role))
                
                role_uf = role
                
            if not role_uf["attributes"]:
                role_uf["attributes"] = []
                
            if not role_uf[_IMPLIED_ROLES_ATTR_]:
                role_uf[_IMPLIED_ROLES_ATTR_] = []
                
            if not role_uf[_IMPLIED_ROLES_CLOSURE_ATTR_]:
                if role_uf[_IMPLIED_ROLES_ATTR_]:
                    # if we don't have any closure info, but have some directly
                    # implied roles, we'll settle for those
                    role_uf[_IMPLIED_ROLES_CLOSURE_ATTR_] = role_uf[_IMPLIED_ROLES_ATTR_]
                else:
                    role_uf[_IMPLIED_ROLES_CLOSURE_ATTR_] = []


                    
            # gather the values of the "attributes" attribute of the role uform
            # also gather the uuid of the roles that have been
            # directly/indirectly traversed so that we don't duplicate efforts
            
            (more_attributes,
             traversed_roles) = __getRoleAttrs(role_uf,
                                               traversed_roles,
                                               repos)
            attributes = attributes + more_attributes
        else:
            #print "role %s skipped in createUFormOfRole"%(role.toString())
            pass
        
    #print "attributes required are %s"%(repr(attributes))
    #print "roles inherited from are %s"%(repr(traversed_roles))
    #print "roles directly inherited from are %s"%(repr(roles_collection))
    
    # add the attributes - since this is not type-enhanced
    # so we'll just set it to None
    if create_attributes:
        map(lambda k,u = uf:u.__setitem__(k,None),attributes)
    
    #print "now the uform has the following attributes: %s"%(uf.keys())
    
    uf[_ROLES_ATTR_] = roles_collection

    return uf

createUformOfRole = createUFormOfRole



def roleImpliesRole(role1, role2, repos=None):
    """
    Checks if ROLE uform role1 inherits ROLE uform role2
    by checking if the two uuid are the same or
    if the implied_roles_closure attribute of role1 contains
    role2

    return: 1 or 0
    """
    
    assert(MAYA.VIA.uuid.isa(role1) or MAYA.VIA.uform.isa(role1))
    assert(MAYA.VIA.uuid.isa(role2) or MAYA.VIA.uform.isa(role2))
    
    # make sure we have the UUID of role2 and role1
    uu1 = __UUIDfyOrCreate(role1)
    uu2 = __UUIDfyOrCreate(role2)
    
    try:
        # get the closure of role1
        closure1 =  __getClosure(role1, repos)
        
        # make sure the closure contains only UUIDs
        for i in range(len(closure1)):
            if MAYA.VIA.uform.isa(closure1[i]):
                closure1[i] = closure1[i].uuid

    except TypeError:
        
        raise TypeError, "Repository parameter is missing or invalid"
    else:
        assert(len(closure1) >= 0)
        
        return ((uu1 == uu2) or (uu2 in closure1))
            
    
def uFormImpliesRole(uf, role, repos=None):
    """
    Checks if any of the roles that uf plays implies
    the specified role

    return: 1 or 0
    """

    assert(MAYA.VIA.uuid.isa(role) or MAYA.VIA.uform.isa(role))
    
    try:
        roles = __getRoles(uf, repos)
    except TypeError:
        
        raise TypeError, "Repository parameter is missing or invalid"
        # ---------------------------------------------------------------------
    else:
        assert(len(roles) >= 0)

        if filter(lambda i, ru=role, f=roleImpliesRole, r=repos:
                  f(i, ru, r),
                  roles):

            return 1
            # -----------------------------------------------------------------
        else:
            
            return 0

uformImpliesRole = uFormImpliesRole



###############################################################################
# internal helper functions
###############################################################################
def __getClosure(uu_or_uf, repos=None):
    """
    given a ROLE uuid or a uform it returns the value of the
    /implied_roles_closure/ attribute

    return: list
    """

    roles = (__getAttr(uu_or_uf, _IMPLIED_ROLES_CLOSURE_ATTR_, repos) or [])

    if not roles:
        # hmmm... fishy
        roles = __getAttr(uu_or_uf, _ROLES_ATTR_, repos) or []
        roles.extend(__getAttr(uu_or_uf, _IMPLIED_ROLES_ATTR_, repos) or [])

    return roles


def __getRoles(uu_or_uf, repos=None):
    """
    given a uuid or a uform it returns the value of the
    /roles/ attribute

    return: list
    """
    
    return (__getAttr(uu_or_uf, _ROLES_ATTR_, repos) or [])


def __getAttr(uu_or_uf, attr, repos=None):
    """
    given a uuid or a uform it returns the specified attribute
    """
    
    if MAYA.VIA.uuid.isa(uu_or_uf):
        try:
            
            return (repos.getAttr(uu_or_uf, attr) or None)
            # -----------------------------------------------------------------
        except AttributeError:
            
            raise TypeError, "Invalid Repository Interface"
            # -----------------------------------------------------------------
    else:
        assert(MAYA.VIA.uform.isa(uu_or_uf) or \
               (type(uu_or_uf) == type({})))
        
        return (uu_or_uf.get(attr, None))
        # ---------------------------------------------------------------------

        
def __getRoleAttrs(role_uf, roles_not_to_look_at, repos):
    """
    gets an aggregate list of attribute names found in the /role_uf/'s
    "attributes" attribute. It then traverses and recurses into each
    of the the uuids/uforms found inside its "implied_roles_closure"
    attribute for a complete attributes list
    """
    
    #print "traversing down to role %s"%(role_uf.uuid)
    attrs = []
    
    if role_uf.uuid  not in roles_not_to_look_at:
        # grab the attributes attribute
        if role_uf["attributes"]:
            attrs = attrs + role_uf["attributes"]

        # add the uuid of this role to the roles_not_to_look_at since it's be
        # traversed
        roles_not_to_look_at.append(role_uf.uuid)
        
        # recurse into each role specified in the "implied_roles_clossure"
        closure = role_uf.get(_IMPLIED_ROLES_CLOSURE_ATTR_, [])

        for role_uu in role_uf[_IMPLIED_ROLES_CLOSURE_ATTR_]:

            if MAYA.VIA.uuid.isa(role_uu):
                try:
                    implied_role_uf = repos.getAttr(MAYA.VIA.uform.UForm(role_uu,
                                                                     {"attributes" : [],
                                                                      _IMPLIED_ROLES_CLOSURE_ATTR_ : []}))
                except AttributeError:

                    raise TypeError, "Invalid repository interface"
            else:
                assert(MAYA.VIA.uform.isa(role_uu))

                implied_role_uf = role_uu
                
                if not implied_role_uf["attributes"]:
                    implied_role_uf["attributes"] = []

                if not implied_role_uf[_IMPLIED_ROLES_CLOSURE_ATTR_]:
                    implied_role_uf[_IMPLIED_ROLES_CLOSURE_ATTR_] = []
                
            (more_attrs,
             roles_not_to_look_at) = __getRoleAttrs(implied_role_uf,
                                                    roles_not_to_look_at,
                                                    repos)
            attrs = attrs + more_attrs
    else:
        #print "skipping role %s inside __getRoleAttrs"%(role_uf.uuid)
        pass
    
    return (attrs,roles_not_to_look_at)


def __UUIDfyOrCreate(uu, create=0):
    """
    to create a uuid out of stuff if possible
    """
    
    if uu == None and create:
        
        return MAYA.VIA.uuid.UUID()
    elif isinstance(uu,__uuid_class):
        
        return uu
    elif isinstance(uu,__uform_class):
        
        return uu.uuid
    elif type(uu) == type(""):
        
        return MAYA.VIA.uuid.fromString(uu)
    else:
        
        raise TypeError,"Parameter passed in [%s] could not be UUIDfied"%(repr(uu))



def __UFormifyOrCreate(uu, create=0):
    """
    Creates and returns a uform given a uuid. It will return /uu/
    back if it happens to already be a uform.
    """
    
    try:
        if not isinstance(uu,__uform_class):
            uu = __UUIDfyOrCreate(uu, create)
            
            return MAYA.VIA.uform.UForm(uu)
        else:
            
            return uu
    except TypeError:
        
        raise TypeError,"Parameter passed in could not be Uformified"
        
