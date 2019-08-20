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

UUID: ~fd000a0251-0b-fd0a96b73e
Design Note: http://intra.maya.com/design/visage/visage_des/visnote/99024/99024v1-2.htm

Label        String
Name         String
Description  String

NOTE:
 unofficially, the attribute 'id' used to be used to store something like
 the current label.

Seung Chan Lim

"""

###############################################################################
#
###############################################################################
import MAYA.VIA.uuid
import MAYA.VIA.uform



###############################################################################
#
###############################################################################
_LABEL_ATTR_       = "label"
_NAME_ATTR_        = "name"
_DESCRIPTION_ATTR_ = "description"

_UUID_ = MAYA.VIA.uuid.fromString("~fd000a0251-0b-fd0a96b73e")
_ATTRIBUTES_ = [_LABEL_ATTR_,
		_NAME_ATTR_,
		_DESCRIPTION_ATTR_]
_IMPLIED_ROLES_ = []
_IMPLIED_ROLES_CLOSURE_ = []

uuid = _UUID_
UUID = uuid
attributes = _ATTRIBUTES_




###############################################################################
#
###############################################################################
def getName(uu, r):
	
	return (r.getAttr(uu, _NAME_ATTR_) or \
		r.getAttr(uu, _LABEL_ATTR_) or \
		r.getAttr(uu, 'id') or \
		uu.toString())



###############################################################################
# classes
###############################################################################
class Role(MAYA.VIA.uform.UForm):
	"""
	Entity Role
	"""
	
	import MAYA.VIA.roles
	import MAYA.VIA.uform
	
	__IMPLIED_ROLES_ = ()
	__IMPLIED_ROLES_CLOSURE_ = ()
	__UUID_ = _UUID_
	__ATTRIBUTES_ = _ATTRIBUTES_
	
	def __init__(self, retain_object_relation=0):
		
		implied_roles_list = []
		map(lambda i, r=implied_roles_list: r.append(i()), self.__IMPLIED_ROLES_)

		assert(not filter(lambda i, M=MAYA.VIA.uform: not M.isa(i), implied_roles_list))
		
		uf = MAYA.VIA.roles.createRoleUForm(self.__UUID_,
					       self.__module__,
					       implied_roles_list,
					       self.__ATTRIBUTES_)
		if retain_object_relation:
			# this basically puts back the UForm objects in the relations
			# instead of keeping just the UUIDs
			implied_roles_closure_list = []
			map(lambda i, r=implied_roles_closure_list: r.append(i()), self.__IMPLIED_ROLES_CLOSURE_)
		
			assert(not filter(lambda i, M=MAYA.VIA.uform: not M.isa(i), implied_roles_list))
			
			uf.eform[MAYA.VIA.roles._IMPLIED_ROLES_ATTR_] = implied_roles_list		
			uf.eform[MAYA.VIA.roles._IMPLIED_ROLES_CLOSURE_ATTR_] = implied_roles_closure_list
			
		MAYA.VIA.uform.UForm.__init__(self,
					  uf.uuid,
					  uf.eform)
		
	
class UForm(MAYA.VIA.uform.UForm):
	"""
	Entitiy UForm
	"""
	
	import MAYA.VIA.roles
	import MAYA.VIA.uform

	# only an aggregate of the class not the instance
	# cuz otherwise it will create a chicken and egg problem
	__ROLES_ = (Role, )
    
	def __init__(self, uu=None, eform=None, create_attributes=1, repos=None):
		assert(uu == None or MAYA.VIA.uuid.isa(uu))
		assert(eform == None or type(eform) == type({}))

		roles_list = []
		map(lambda i, r=roles_list: r.append(i(retain_object_relation=1)), self.__ROLES_)
		
		assert(not filter(lambda i, M=MAYA.VIA.uform: not M.isa(i), roles_list))

		uf = MAYA.VIA.roles.createUFormOfRole(uu,
						 roles=roles_list,
						 repos=repos,
						 create_attributes=create_attributes)

		MAYA.VIA.uform.UForm.__init__(self,
					  uf.uuid,
					  uf.eform)
		if eform:
			self.eform.update(eform)
