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
python loops with filter,map, etc... for speed

"""

import MAYA.uform
import MAYA.uuid
import MAYA.repos
from MAYA.role import entity

__uuid_class  = MAYA.uuid.UUID
__uform_class = MAYA.uform.UForm
__repos_class = MAYA.repos.Repository

__role_role_uuid = MAYA.uuid.fromString("~fd000a0251-0b-fd1d650a97")
__entity_role_uuid = entity.uuid
uuid = __role_role_uuid


################################################################################
#
# to create a uuid out of stuff if possible
#
################################################################################
def _UUIDfyOrCreate(uu, create = 1):
    
    if uu == None and create:
        
        return MAYA.uuid.UUID()
    elif isinstance(uu,__uuid_class):
        
        return uu
    elif isinstance(uu,__uform_class):
        
        return uu.uuid
    elif type(uu) == type(""):
        
        return MAYA.uuid.fromString(uu)
    else:
        
        raise TypeError,"Parameter passed in could not be UUIDfied"

# backward compatibility
__UUIDfyOrCreate = _UUIDfyOrCreate


################################################################################
#
# to create a uform out of stuff if possible
#
################################################################################
def _UFormifyOrCreate(uu, create = 1):
    
    try:
        if not isinstance(uu,__uform_class):
            uu = __UUIDfyOrCreate(uu,create)
            
            return MAYA.uform.UForm(uu)
        else:
            
            return uu
    except TypeError:
        
        raise TypeError,"Parameter passed in could not be Uformified"
        
# backward compatibility
__UFormifyOrCreate = _UFormifyOrCreate

###############################################################################
#
# to connect to a repository (pegasus) or wrap a repository interface 
# to the socket connection
#
###############################################################################
def __RepositoryfyOrConnect(repos, connect = 1):
    
    import socket
    
    if repos == None and connect == 1:
        
        return MAYA.repos.Repository("www.maya.com:6201")
    elif isinstance(repos,MAYA.repos.Repository):
        
        return repos
    elif type(repos) == type(""):

        return MAYA.repos.Repository(repos)
    elif hasattr(repos,"_sock"): # hack .. should i do
                                 # type(sock.sock(sock.AF_INET,sock.SOCK_STREAM)
                                 
        return MAYA.repos.Repository(connection = repos)
    else:
        
        raise TypeError,"Paramester passed in could not be Repositoryfied"
    


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


    uf = __UFormifyOrCreate(uu)
    repos = __RepositoryfyOrConnect(repos)
    
    # create a uform that is an instance of the role uform
    uf = createUFormOfRole(uf,(__role_role_uuid,),repos)
    
    # it'll at least imply entity
    if not implied_roles:
        implied_roles = (__entity_role_uuid,)


    # You need to pass in a sequence as the value of the
    # implied_roles parameter 
    assert(type(implied_roles) in (type(()),
                                   type([])))
                    
    # make sure the items in the list are uuids
    implied_roles = list(implied_roles)
    for i in range(len(implied_roles)):
        implied_roles[i] = __UUIDfyOrCreate(implied_roles[i],0)
        
    uf["implied_roles"] = implied_roles
   
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
    
    all_implied_roles = list(implied_roles)
    
    # we only need to check one-level deep
    # per the roles implied_roles closure
    # spec
    def add_if_not_already_there(uu,
                                 all_implied_roles = all_implied_roles,
                                 repos = repos):
        
        uf_closure = repos.getUForm(uu).get("implied_roles_closure",[])
        # now only add the uu in to our closures list if it's not
        # there already
        for uf_closure_uu in uf_closure:    
            if uf_closure_uu not in all_implied_roles:
                all_implied_roles.extend(uf_closure)
                #print "now all implied roles is %s"%(repr(all_implied_roles))

            
    map(add_if_not_already_there,all_implied_roles) 

    #print "\ncomplete list of implied roles: %s"%(repr(all_implied_roles))

    uf["implied_roles_closure"] = all_implied_roles

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
        uf["label"] = string.replace(label," ","_")
        uf["name"] = "%s Role"%(label)

        
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
                      roles             = (__entity_role_uuid,),
                      repos             = None,
                      create_attributes = 1):
    
    uf = __UFormifyOrCreate(uu)
    repos = __RepositoryfyOrConnect(repos)
    
    attributes       = []
    traversed_roles  = []
    roles_collection = []

    # the roles argument must be a sequence
    assert( (type(roles) == type(())) or (type(roles) == type([])) )

    # traverse the roles list depth-first    
    for role in roles:
        # make sure it's a UUID
        role = __UUIDfyOrCreate(role,0)
            
        if role not in traversed_roles:
            roles_collection.append(role)
            role_uf=repos.getUForm(role)
            # gather the values of the "attributes" attribute of the role uform
            # also gather the uuid of the roles that have been
            # directly/indirectly traversed so that we don't duplicate efforts
            
            more_attributes,traversed_roles = __getRoleAttrs(role_uf,
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
    
    uf["roles"] = roles_collection

    return uf


###############################################################################
#
# checks whether role uform uu2 is implied by uform uu1
# by inspecting the roles and the implied roles attribute
#
#
# return value: 1 or 0
###############################################################################
def impliesRole(uu1, uu2, repos = None):
    
    uu1   = __UUIDfyOrCreate(uu1)
    uu2   = __UUIDfyOrCreate(uu2)
    
    repos = __RepositoryfyOrConnect(repos)
    roles = repos.getAttr(uu1, "roles")

    if not roles:
    
        return 0
    elif type(roles) != type([]):
        roles = [roles]
        
    # find out if any one of the roles
    # in the roles list happens to include
    # the role in its implied_roles_closure
    def __checkImplication(item, U = uu2, r = repos):
        # maybe we don't even need to check the closure
        # this role just may well be
        
        # this should really do a recursive search, especially
        # if there is no impiled_roles_closure attribute,
        # but I've got bigger fish to fry right now -- Jer
        
        if U == item:
            
            return 1
        
        i_roles = r.getAttr(item, "implied_roles_closure")
        if i_roles:
            if U in i_roles:

                return 1

        return 0
    
    # but, filter checks all... would it
    # be faster in common case to just
    # stop checking once it finds a match???
    if filter(__checkImplication , roles):

        return 1
    else:

        return 0


###############################################################################
#                            helper functions
###############################################################################

def __getRoleAttrs(role_uf, roles_not_to_look_at, repos):
    
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
        if role_uf.has_key("implied_roles_closure"):
            for role_uu in role_uf["implied_roles_closure"]:
                implied_role_uf = repos.getUForm(role_uu)
                more_attrs,roles_not_to_look_at = __getRoleAttrs(implied_role_uf,
                                                            roles_not_to_look_at,
                                                            repos)
                attrs = attrs + more_attrs
    else:
        #print "skipping role %s inside __getRoleAttrs"%(role_uf.uuid)
        pass
    
    return (attrs,roles_not_to_look_at)





