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
import sys,string,xmllib
from MAYA.VIA import repos,uuid,uform

class UFormSoap(xmllib.XMLParser):
    def __init__(self, **kw):
        self.state = 0
        self.data = ""
        self.vstack = []
        self.cval = None

        apply(xmllib.XMLParser.__init__, (self,), kw)

    def handle_data(self, data):
        self.data = self.data + data
    # Example -- handle cdata, could be overridden
    def handle_cdata(self, data):
        raise "no cdata expected"

    def start_uform(self,attrs):
        print "hi there"
        self.vstack.append(uform.UForm()) # placeholder
    def end_uform(self,attrs):
        self.cval = self.vstack.pop()

    def start_eform(self,attrs):
        self.vstack.append({})
    def end_eform(self):
        self.cval = self.vstack.pop()
        if len(self.vstack) > 0:
            building = self.vstack[-1]
            if uform.isa(building):
                building.eform = self.cval
        
    def start_uuid(self,attrs):
        self.data = ''
    def end_uuid(self):
        self.cval = uuid.fromString(string.replace(self.data,'\n',''))
        if len(self.vstack) > 0:
            building = self.vstack[-1]
            if uform.isa(building):
                building.uuid = self.cval
                
    def start_avpair(self,attrs):
        pass
    def end_avpair(self):
        pass
    def start_attribute(self,attrs):
        self.data = ''
    def end_attribute(self):
        # this isn't going to work on nested eforms
        self.attribute = self.data
    def start_value(self,attrs):
        if hasattr(self, "cval"):
            self.vstack.append(self.cval)
        self.cval = None
        self.data = ''
        
    def end_value(self):
        if len(self.vstack) > 0:
            building = self.vstack[-1]
            if type(building) == type([]):
                building.append(self.cval)
            elif type(building) == type({}):
                building[self.attribute] = self.cval
            self.cval = building

    def start_string(self,attrs):
        pass
    def end_string(self):
        self.cval = self.data
        
    def start_integer(self,attrs):
        pass
    def end_integer(self):
        self.cval = int(string.replace(self.data,'\n',''))
        
    def start_float(self,attrs):
        pass
    def end_float(self,attrs):
        self.cval = int(string.replace(self.data,'\n',''))
        
    def start_array(self,attrs):
        self.vstack.append([])
    def end_array(self,attrs):
        self.cval = self.vstack.pop()

    def unknown_starttag(self, tag, attrs):
        print "unknown tag " + tag
    def unknown_endtag(self, tag):
        pass

"""
    def start_k(self,attrs):
        self.data = ''        
    def end_k(self):
        self.key = string.replace(self.data,'\n','')

    def start_v(self,attrs):
        t = attrs['http://www.w3.org/2001/XMLSchema-instance/ type']
        if hasattr(self,'cval'):
            self.vstack.append(self.cval)
        self.cval = None
        self.data = ''
        self.finish_value = None
        if t == 'may:uform':
            self.cval = uform.UForm('')
        elif t == 'may:eform':
            self.cval = {}
        elif t == 'may:uuid':
            self.finish_value = self.finish_uuid
        elif t == 'xsd:string':
            self.finish_value = self.finish_string
        elif t == 'xsd:int':
            self.finish_value = self.finish_int
        elif t == 'xsd:ur-type[]':
            self.cval = []

    def finish_uuid(self):
        self.cval = uuid.fromString(string.replace(self.data,'\n',''))
    def finish_int(self):
        self.cval = int(string.replace(self.data,'\n','')) 
    def finish_string(self):
        self.cval = self.data
        
    def end_v(self):
        if self.finish_value:
          self.finish_value()
        self.finish_value = None
        self.result = self.cval
        if len(self.vstack) > 0:
          v = self.vstack.pop()            
          if type(v) == type({}) or uform.isa(v):
              v[self.key] = self.result
          elif type(v) == type([]):
              v.append(self.result)
          self.cval = v
"""
        
def xml_to_uform(x):
  p = UFormSoap()
  p.feed(x)
  return p.cval


envelope_body = """<env:Envelope xmlns:env='http://schemas.xmlsoap.org/soap/envelope/' xmlns:enc='http://schemas.xmlsoap.org/soap/encoding/' xmlns:lab='http://www.pythonware.com/soap/' xmlns:xsd='http://www.w3.org/1999/XMLSchema/' xmlns:xsi='http://www.w3.org/1999/XMLSchema/instance/' xmlns:may='http://www.maya.com/xmlns/soap/' env:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'>
<env:Body>
<v xsi:type='may:uform'>
"""
end_body = """</v>
</env:Body>
</env:Envelope>"""
uuid_tag = "<uuid xsi:type='may:uuid'>\n%s\n</uuid>\n"
attr_tag = "<k xsi:type='xsd:string'>%s</k>\n"
eform_tag = "<eform xsi:type='may:eform'>\n"
eform_etag = "</eform>\n"

safechars = (('&','&amp;'),
             ('<','&lt;'),
             ('>','&gt;'))

import sys,string
from MAYA import repos,uuid

#make the string clean for XML parsing
def clean_string(s):
    for k,v in safechars:
        s = string.replace(s,k,v)
    return s

def write_value(x,v):
    if type(v) == type(''):
        x.write("<v xsi:type='xsd:string'>")
        x.write(clean_string(v))
        x.write("</v>\n")
    elif uuid.isa(v):
        x.write("<v xsi:type='may:uuid'>")
        x.write(clean_string(v.toString()))
        x.write("</v>\n")
    elif type(v) == type(1):
        x.write("<v xsi:type='xsd:int'>")
        x.write(clean_string(str(v)))
        x.write("</v>\n")
    elif type(v) == type([]) or type(v) == type(()):
        x.write("<v xsi:type='xsd:ur-type[]'>\n")
        for a in v:
            write_value(x,a)
        x.write("</v>\n")
    else:
        print "unknown type",type(v)

def uform_to_xml(x, uf):
    x.write(envelope_body)
    x.write(uuid_tag % uf.uuid.toString())
    x.write(eform_tag)    
    for k in uf.keys():
      v = uf[k]
      x.write(attr_tag % k)
      write_value(x,v)
    x.write(eform_etag)
    x.write(end_body)


def test():
    if sys.argv[1] == "download":
      r = repos.Repository("pegasus.maya.com:6200")
      uu = uuid.fromString(sys.argv[2])
      uf = r.getUForm(uu)
      x = open(sys.argv[3],"w")
      uform_to_xml(x,uf)
      x.close()
    elif sys.argv[1] == "upload":
      r = repos.Repository("pegasus.maya.com:6200")
      uf = xml_to_uform(open(sys.argv[2],"r").read())
      r.setUForm(uf)
    elif sys.argv[1] == "parse":
      print repr(xml_to_uform(open(sys.argv[2],"r").read()))

if __name__ == '__main__':
    test()

