#!/usr/bin/env python
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
from MAYA.VIA import repos,uform,uuid,vsmf
import time
import sha

def renderRole(repos, role_uuid):
    role = Role(role_uuid)
    role.load(repos)
    return role.toHTML()


class Role:
    def __init__(self, role_uuid):
        if type(role_uuid) == type(''):
            self.uuid = uuid.fromString(role_uuid)
        elif type(role_uuid) == type(uuid.UUID()):
            self.uuid = role_uuid
        else:
            self.uuid = uuid.UUID()
        self.notes = ''
        self.roles = []
        self.rolenames = []
        self.implied_roles = []
        self.impliednames = []
        self.implied_attr = []
        self.attribute_prefixes = None
        self.name = ''
        self.label = ''
        self.description = ''
        self.attributes = []
        self.example = None
        self.sample_rendering = ''
            
    def getNames(self, repos, coll):
        results = []
        for obj in coll:
            results.append([repos.getAttr(obj, 'name'), obj])
        return results
            
    def load(self, repos):
        uf = repos.getUForm(self.uuid)
        if uf.has_key('text_content'):
            self.notes = uf['text_content']
        if uf.has_key('roles'):
            self.roles = uf['roles']
            self.rolenames = self.getNames(repos, self.roles)            
        if uf.has_key('name'):
            self.name = uf['name']
        if uf.has_key('label'):
            self.label = uf['label']
        self.adescrip = uf.get('attribute_descriptors',None)
        if uf.has_key('implied_roles'):
            self.implied_roles = uf['implied_roles']
            self.impliednames = self.getNames(repos, self.implied_roles)
            for role in self.implied_roles:
                attr = repos.getAttr(role, 'attributes') or []
                dict = {}
                for a in attr:
                    dict[a.lower()] = 1
                self.implied_attr.append(dict)
        if uf.has_key('attribute_prefixes'):
            self.attribute_prefixes = uf['attribute_prefixes']
        if uf.has_key('description'):
            self.description = uf['description']
        if uf.has_key('attributes'):
            atr = uf.get('attributes') or []
            req = uf.get('requireds') or ([vsmf.False] * len(atr))
            typ = uf.get('types') or ([None] * len(atr))
            rng = uf.get('ranges') or ([None] * len(atr))
            sem = uf.get('semantics') or ([None] * len(atr))
            for i in range(len(atr)):
                self.attributes.append([atr[i], req[i], typ[i], rng[i], sem[i]])
        if uf.has_key('example'):
            self.example = uf['example']
        if uf.has_key('sample_rendering'):
            self.sample_rendering = uf['sample_rendering']
            
    def save(self, repos):
        repos.setAttr(self.uuid, 'text_content', self.notes)
        repos.setAttr(self.uuid, 'roles', self.roles)
        repos.setAttr(self.uuid, 'label', self.label)
        repos.setAttr(self.uuid, 'name', self.name)
        repos.setAttr(self.uuid, 'implied_roles', self.implied_roles)
        repos.setAttr(self.uuid, 'attribute_prefixes', self.attribute_prefixes)
        repos.setAttr(self.uuid, 'description', self.description)
        atr = []
        req = []
        typ = []
        rng = []
        sem = []
        for a in self.attributes:
            atr.append(a[0])
            req.append(vsmf.boolean(a[1]))
            typ.append(a[2])
            rng.append(a[3])
            sem.append(a[4])
        repos.setAttr(self.uuid, 'attributes', atr)
        repos.setAttr(self.uuid, 'requireds', req)
        repos.setAttr(self.uuid, 'types', typ)
        repos.setAttr(self.uuid, 'ranges', rng)
        repos.setAttr(self.uuid, 'semantics', sem)
        if self.sample_rendering:
            repos.setAttr(self.uuid, 'sample_rendering', self.sample_rendering)
        if self.example:
            repos.setAttr(self.uuid, 'example', self.example)
    
    def HTMLTableHeader(self):
        return """
            <tr>
                <th align="left" width="20%">attribute</th>
                <th align="left" width="40%">type</th>
                <th align="left" width="30%">range</th>
                <th align="left" width="10%">required</th>
            </tr>
            """
            
    def toHTML(self):
        st = []
        st.append('<h3>%s</h3>' % self.name)
        st.append('<strong>UUID: </strong>%s<br />' % self.uuid.toString())
        st.append('<strong>label: </strong>%s<br />' % self.label)
        st.append('<strong>name: </strong>%s<br />' % self.name)
        st.append('<strong>description: </strong>%s<br />' % self.description)
        if self.example:
            st.append('<strong>example: </strong>%s<br />' % self.example.toString())
        if self.sample_rendering:
            st.append('<strong>sample rendering: </strong><a href="%s">%s</a><br />' % (self.sample_rendering, self.sample_rendering))
        bits = []
        for nm in self.rolenames:
            bits.append('<a href="uf.py?uuid=%s">%s</a>' % (nm[1].toString(), nm[0]))
        st.append('<strong>roles: </strong>[%s]<br />' % ', '.join(bits))
        bits = []
        for nm in self.impliednames:
            bits.append('<a href="uf.py?uuid=%s">%s</a>' % (nm[1].toString(), nm[0]))
        st.append('<strong>implied_roles: </strong>[%s]<br />' % ', '.join(bits))
        if self.attribute_prefixes != None:
          st.append('<strong>attribute_prefixes: </strong>%s<br />' % self.attribute_prefixes)
        if self.adescrip:
            st.append('<strong>attribute_descriptors: </strong>[%s]<br /><br />' % ', '.join(self.adescrip))
        if self.attributes:
            st.append('<table border="1" cellpadding="4" cellspacing="0" width="600">')
            st.append(self.HTMLTableHeader())
            for attr in self.attributes:
                bits = []
                idx = 0
                for implied in self.implied_attr:
                    if implied.has_key(attr[0].lower()):
                        nm = self.impliednames[idx]
                        bits.append('<a href="uf.py?uuid=%s">%s</a>' % (nm[1].toString(), nm[0]))

                    idx = idx + 1
                st.append('<tr>')
                seealso = ''
                attrname = attr[0]
                if bits:
                    seealso = '<br><font color="#999999">(see also: ' + ', '.join(bits) + ')</font>'
                else:
                    attrname = '<b>' + attrname + '</b>'
                st.append('<td rowspan="2" valign="top">%s</td>' % (attrname))
                st.append('<td valign="top">%s</td>' % attr[2])
                st.append('<td valign="top">%s</td>' % attr[3])
                if attr[1]:
                    req = 'Yes'
                else:
                    req = 'No'
                st.append('<td valign="top">%s</td>' % req)
                st.append('</tr><tr>')
                desc = (attr[4] or '') + seealso
                if (not desc) or (len(desc) <= 1):
                    desc = '<font color="#c0c0c0">(no semantics provided)</font>'
                st.append('<td colspan="3" valign="top">%s</td>' % desc)
                st.append('</tr>')
            st.append('</table><br />')
        if self.notes:
            st.append('<strong>notes: </strong>%s<br />' % self.notes)
        return '\n'.join(st)
        
        
        
        
    
