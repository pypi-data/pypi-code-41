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
"""

###############################################################################
#
###############################################################################
import re
from MAYA.VIA import uuid, uform






###############################################################################
#
###############################################################################





###############################################################################
#
###############################################################################
class HcollectionReader:
    def __init__(self, repos, root_uuid):
        assert(uuid.isa(root_uuid))
        self._repos = repos
        self._root_uuid = root_uuid

    def findMember(self, path=(), dimension="members", not_found_callback=None):
        uu = self._root_uuid        

        for i in range(len(path)):
            members = self._repos.getAttr(uu, dimension)

            if type(members) != type([]):
                self._repos.setAttr(uu, dimension, [])
                members = []
                
            self._repos.setBatchMode(1)
            
            try:
                # names = []

                for j in range(len(members)):
                    self._repos.getAttr(members[j], "name")
                    
                names = self._repos.commit(retain_order=1)
            finally:
                self._repos.setBatchMode(0)

            names = [ name and name.lower() or repr(name) for name in names ]
 
            try:
                index = names.index(path[i] and path[i].lower() or repr(path[i]))
            except ValueError:
                # no such sub collection
                if not_found_callback:
                    assert(callable(not_found_callback))
                    uu = not_found_callback(uu, path[i])
                else:
                    
                    raise ValueError, "%s not found under %s"%(str(path[:i]), self._root_uuid)
            else:
                uu = members[index]

        return uu

    
    def getMembers(self, path=(), dimension="members"):
        try:
            uu = self.findMember(path, dimension)
        except ValueError:

            return []
        else:
                
            return self._repos.getAttr(uu, dimension)


class HcollectionWriter(HcollectionReader):
    COLLECTION_ROLE = uuid.fromString("~fd000a02510bfd17204424")
    ROLES = [COLLECTION_ROLE]
    
    APOS_REGEX = re.compile("(\w)'[sS](\s*)")
    
    def __init__(self, repos, root_uuid):
        HcollectionReader.__init__(self, repos, root_uuid)
        self._repos.setAttr(root_uuid, "roles", HcollectionWriter.ROLES)

        
    def _makeTitle(self, s):
        def f(match):
            return "%s's%s"%(match.group(1), match.group(2))
        
        return HcollectionWriter.APOS_REGEX.sub(f, (s.title()))

    
    def addMember(self, path, member, dimension="members"):
        def cb(uu, name):
            # no such sub collection, so create one
            uf = uform.UForm()
            uf["roles"] = HcollectionWriter.ROLES
            uf["members"] = []
            uf["name"] = self._makeTitle(name)
            uf["parent"] = uu
            
            # append it to the parent collection
            if self._repos.setAttr(uf) == 0:
                if self._repos.chunkInsertAfter(uu, dimension,[[-1,-1,'',16]], uf.uuid) == 0:
                    
                    return uf.uuid
                else:
                    
                    raise RuntimeError, "Unable to write to repository"
            else:
                
                raise RuntimeError, "Unable to write to repository"
        
        uu = self.findMember(path, dimension, cb)

        # add member
        
        if self._repos.chunkInsertAfter(uu, dimension,[[-1,-1,'',16]], member) == 0:           
            
            return uu
        else:
            
            raise RuntimeError, "Unable to write to repository"
        


    def removeMember(self, path, member, dimension="members", remove_dups=False):
        try:
            uu = self.findMember(path, dimension)
        except ValueError, why:

            raise ValueError, why
        else:
            members = self._repos.getAttr(uu, dimension)

            try:
                if remove_dups:
                    how_many = members.count(member)
                    
                    if how_many > 0:
                        for i in range(how_many):
                            members.remove(member)
                    else:
                        raise ValueError, "%s not found in %s under %s"%(member, path, self._root_uuid)
                else:
                    members.remove(member)
            except ValueError:

                raise
            else:
                if self._repos.setAttr(uu, dimension, members) != 0:
                    
                    raise RuntimeError, "Unable to write to the repository"
        
                return uu
