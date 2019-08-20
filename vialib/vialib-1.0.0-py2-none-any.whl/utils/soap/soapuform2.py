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
# Routines to convert uforms to and from XML, according to the schema
# at http://www.maya.com/local/higgins/mayaschema6.xsd
#
# We don't really handle fully qualified namespaces.  I'm not sure
# how those work in this version of the XML utilities.
#
# This will generate Python objects with Unicode strings in them.
# Hope you can deal with that.
#
# 2001-06-03 higgins

# Added routines to serialize to and from Response and Request objects
#
# 2001-07-12 higgins

# Added trivial SOAP wrapper support
# 2001-07-25 higgins

# Added support VSMF date
# 2003-08-26 slim


# The two big missing things are to implement the issue() method of
# the Request class, so that Repository is actually called, and to
# implement a server using this.

import sys, string, StringIO
import time
from xml.sax import saxutils, make_parser
from xml.sax import handler
from MAYA.VIA import repos, uuid, uform
from types import *

import sys

# XXX okay, the namespace handling is pretty hacky.  SOAP wants you to
# qualify the topmost element, but none of the others.  I can't figure
# out how to get the parser to do this work for me.  Therefore there's a
# bunch of grotty exception handling to try to figure out if we're using
# this namespace anywhere.
maya = 'http://www.maya.com/local/higgins/mayaschema6.xsd '
rschema = 'http://www.maya.com/local/higgins/repos_schema3.xsd '
soap = 'http://schemas.xmlsoap.org/soap/envelope/ '
soapenc = 'http://schemas.xmlsoap.org/soap/encoding/ ' # XXX this is not handled

# Repository opcodes by command
opcodes = {}
opcodes['AUTHENTICATE'] = 1
opcodes['GETUFORM'] = 3
opcodes['GETATTR'] = 8
opcodes['LISTATTR'] = 6
opcodes['UFORMKNOWN'] = 301
opcodes['GETNEXT'] = 31
opcodes['SETUFORM'] = 4
opcodes['SETATTR'] = 9
opcodes['FORGETUFORM'] = 5
opcodes['REMOVEATTR'] = 110
opcodes['REGISTERNOTIFY'] = 21
opcodes['CANCELNOTIFY'] = 22
opcodes['NOTIFY_AND_GETUFORM'] = 121
opcodes['NOTIFY_AND_GETATTR'] = 122
opcodes['NOTIFY'] = 23
opcodes['LOCKUFORM'] = 2001
opcodes['UNLOCKUFORM'] = 2002
opcodes['CHUNKATTR_SELECT'] = 10
opcodes['CHUNKATTR_DELETE'] = 11
opcodes['CHUNKATTR_REPLACE'] = 12
opcodes['CHUNKATTR_INSERTAFTER'] = 13
opcodes['CHUNKATTR_INSERTBEFORE'] = 14
opcodes['CHUNKATTR_SPLIT'] = 15
opcodes['CHUNKATTR_COUNT'] = 16
opcodes['CHUNKATTR_LOC'] = 17
opcodes['CHUNKATTR_LENGTH'] = 18

# Repository commands by opcode
# remember to run str() on an int before indexing
commands = {}
commands['1'] = 'AUTHENTICATE'
commands['3'] = 'GETUFORM'
commands['8'] = 'GETATTR'
commands['6'] = 'LISTATTR'
commands['301'] = 'UFORMKNOWN'
commands['31'] = 'GETNEXT'
commands['4'] = 'SETUFORM'
commands['9'] = 'SETATTR'
commands['5'] = 'FORGETUFORM'
commands['110'] = 'REMOVEATTR'
commands['21'] = 'REGISTERNOTIFY'
commands['22'] = 'CANCELNOTIFY'
commands['121'] = 'NOTIFY_AND_GETUFORM'
commands['122'] = 'NOTIFY_AND_GETATTR'
commands['23'] = 'NOTIFY'
commands['2001'] = 'LOCKUFORM'
commands['2002'] = 'UNLOCKUFORM'
commands['10'] = 'CHUNKATTR_SELECT'
commands['11'] = 'CHUNKATTR_DELETE'
commands['12'] = 'CHUNKATTR_REPLACE'
commands['13'] = 'CHUNKATTR_INSERTAFTER'
commands['14'] = 'CHUNKATTR_INSERTBEFORE'
commands['15'] = 'CHUNKATTR_SPLIT'
commands['16'] = 'CHUNKATTR_COUNT'
commands['17'] = 'CHUNKATTR_LOC'
commands['18'] = 'CHUNKATTR_LENGTH'

# just a container struct
class avpair:
    def __init__(self):
        self.attribute = ''
        self.value = None

# quick typecheck functions
def isavpair(obj):
    if type(obj) is InstanceType:
        return isinstance(obj, avpair)
    return 0

def isRequest(obj):
    if type(obj) is InstanceType:
        return isinstance(obj, Request)
    return 0

def isResponse(obj):
    if type(obj) is InstanceType:
        return isinstance(obj, Response)
    return 0

def isSOAP(obj):
    if type(obj) is InstanceType:
        return isinstance(obj, SOAP)

# Handler class for the XML Sax parser to use in deserializing
# uforms and such from XML
class Deserialize(handler.ContentHandler):
#class Deserialize(saxutils.DefaultHandler):

    # jumptables to make processing a tad more efficient
    start_handlers = {}
    end_handlers = {}

    def __init__(self):
        self.data = ''
        self.vstack = []
        self.cval = None
        self.ns = {}
        
    # XXX I believe this is too naive, in general.  But I'm not sure I
    # totally understand how whitespace works in XML.  I haven't done
    # anything for CDATA yet.  What happens to entity references?  I
    # *think* the parser is cleaning that up for me.
    def _normalize_whitespace(self, s):
        return string.join(string.split(s), ' ')

    def characters(self, ch):
        self.data = self.data + ch

    def start_uform(self, name, attrs):
        self.vstack.append(uform.UForm()) # placeholder typed value
    start_handlers[maya + 'uform'] = start_uform
    start_handlers['uform'] = start_uform
    
    def start_eform(self, name, attrs):
        self.vstack.append({})
    start_handlers[maya + 'eform'] = start_eform
    start_handlers['eform'] = start_eform

    def start_uuid(self, name, attrs):
        self.data = ''
    start_handlers[maya + 'uuid'] = start_uuid
    start_handlers['uuid'] = start_uuid    

    def start_avpair(self, name, attrs):
        self.vstack.append(avpair())
    start_handlers[maya + 'avpair'] = start_avpair
    start_handlers['avpair'] = start_avpair    

    def start_attribute(self, name, attrs):
        self.data = ''
    start_handlers[maya + 'attribute'] = start_attribute
    start_handlers['attribute'] = start_attribute    

    def start_value(self, name, attrs):
        pass
    start_handlers[maya + 'value'] = start_value
    start_handlers['value'] = start_value    

    def start_date(self, name, attrs):
        self.data = ''
    start_handlers[maya + 'date'] = start_date
    start_handlers['date'] = start_date
    
    def start_string(self, name, attrs):
        self.data = ''
    start_handlers[maya + 'string'] = start_string
    start_handlers['string'] = start_string    

    def start_integer(self, name, attrs):
        self.data = ''
    start_handlers[maya + 'integer'] = start_integer
    start_handlers['integer'] = start_integer    

    def start_float(self, name, attrs):
        self.data = ''
    start_handlers[maya + 'float'] = start_float
    start_handlers['float'] = start_float    

    def start_array(self, name, attrs):
        self.vstack.append([])
    start_handlers[maya + 'array'] = start_array
    start_handlers['array'] = start_array    

    def start_request(self, name, attrs):
        self.vstack.append(Request())
    start_handlers[rschema + 'request'] = start_request
    start_handlers['request'] = start_request

    def start_response(self, name, attrs):
        self.vstack.append(Response())
    start_handlers[rschema + 'response'] = start_response
    start_handlers['response'] = start_response        

    def start_id(self, name, attrs):
        self.data = ''
    start_handlers[rschema + 'id'] = start_id
    start_handlers['id'] = start_id

    def start_priority(self, name, attrs):
        self.data = ''
    start_handlers[rschema + 'priority'] = start_priority
    start_handlers['priority'] = start_priority

    def start_opcode(self, name, attrs):
        self.data = ''
    start_handlers[rschema + 'opcode'] = start_opcode
    start_handlers['opcode'] = start_opcode

    def start_status(self, name, attrs):
        self.data = ''
    start_handlers[rschema + 'status'] = start_status
    start_handlers['status'] = start_status

    def start_envelope(self, name, attrs):
        pass
    start_handlers[soap + 'Envelope'] = start_envelope
    start_handlers['Envelope'] = start_envelope

    def start_body(self, name, attrs):
        pass
    start_handlers[soap + 'Body'] = start_body
    start_handlers['Body'] = start_body    
        
    def startElement(self, name, attrs):
        try:
            self.start_handlers[name](self, name, attrs)
        except KeyError:
            # XXX is there a more efficient way to process namespaces?
            if ':' in name:
                ns, tag = string.split(name, ':')
                if self.ns.has_key(ns):
                    tag = self.ns[ns] + tag
                else:
                    # look for a namespace declaration
                    for k, v in attrs.items():
                        if k[:6] == "xmlns:":
                            self.ns[k[6:]] = v + ' '
                    tag = self.ns[ns] + tag
                # now try with the qualified tag name
                if self.start_handlers.has_key(tag):
                    self.start_handlers[tag](self, tag, attrs)
                else:
                    sys.stderr.write( "Unrecognized namespace/tag at start " + tag)
            else:
                sys.stderr.write( "Unknown start tag " + name)

    def end_uform(self, name):
        self.cval = self.vstack.pop()
        if len(self.vstack) > 0 and (isRequest(self.vstack[-1]) or
                                     isResponse(self.vstack[-1])):
            self.vstack[-1].uf = self.cval
            
    end_handlers[maya + 'uform'] = end_uform
    end_handlers['uform'] = end_uform    

    def end_eform(self, name):
        self.cval = self.vstack.pop()
        if len(self.vstack) > 0:
            building = self.vstack[-1]
            if uform.isa(building):
                building.eform = self.cval                    
    end_handlers[maya + 'eform'] = end_eform
    end_handlers['eform'] = end_eform        

    def end_uuid(self, name):
        self.cval = uuid.fromString(self._normalize_whitespace(self.data))
        if len(self.vstack) > 0:
            building = self.vstack[-1]
            if uform.isa(building):
                building.uuid = self.cval        
    end_handlers[maya + 'uuid'] = end_uuid
    end_handlers['uuid'] = end_uuid    

    def end_avpair(self, name):
        avp = self.vstack.pop()
        self.vstack[-1][avp.attribute] = avp.value
    end_handlers[maya + 'avpair'] = end_avpair
    end_handlers['avpair'] = end_avpair    

    def end_attribute(self, name):
        self.vstack[-1].attribute = self._normalize_whitespace(self.data)
    end_handlers[maya + 'attribute'] = end_attribute
    end_handlers['attribute'] = end_attribute    

    def end_value(self, name):
        if len(self.vstack) > 0:
            building = self.vstack[-1]
            if type(building) == type([]):
                building.append(self.cval)
            elif isavpair(building):
                building.value = self.cval
    end_handlers[maya + 'value'] = end_value
    end_handlers['value'] = end_value    

    def end_string(self, name):
        self.cval = self._normalize_whitespace(self.data)        
    end_handlers[maya + 'string'] = end_string
    end_handlers['string'] = end_string    

    def end_date(self, name):
        self.cval = self._normalize_whitespace(self.data)        
    end_handlers[maya + 'date'] = end_date
    end_handlers['date'] = end_date    

    def end_integer(self, name):
        self.cval = int(self._normalize_whitespace(self.data))
    end_handlers[maya + 'integer'] = end_integer
    end_handlers['integer'] = end_integer    

    def end_float(self, name):
        self.cval = float(self._normalize_whitespace(self.data))
    end_handlers[maya + 'float'] = end_float
    end_handlers['float'] = end_float    

    def end_array(self, name):
        self.cval = self.vstack.pop()
    end_handlers[maya + 'array'] = end_array
    end_handlers['array'] = end_array    

    def end_request(self, name):
        self.cval = self.vstack.pop()    
    end_handlers[rschema + 'request'] = end_request
    end_handlers['request'] = end_request

    def end_response(self, name):
        self.cval = self.vstack.pop()    
    end_handlers[rschema + 'response'] = end_response
    end_handlers['response'] = end_response    

    def end_id(self, name):
        self.vstack[-1].id = int(self._normalize_whitespace(self.data))
    end_handlers[rschema + 'id'] = end_id
    end_handlers['id'] = end_id

    def end_priority(self, name):
        self.vstack[-1].priority = int(self._normalize_whitespace(self.data))
    end_handlers[rschema + 'priority'] = end_priority
    end_handlers['priority'] = end_priority    
        
    def end_opcode(self, name):
        self.vstack[-1].opcode = opcodes[self._normalize_whitespace(self.data)]
    end_handlers[rschema + 'opcode'] = end_opcode
    end_handlers['opcode'] = end_opcode

    def end_status(self, name):
        self.vstack[-1].status = int(self._normalize_whitespace(self.data))
    end_handlers[rschema + 'status'] = end_status
    end_handlers['status'] = end_status    

    def end_envelope(self, name):
        self.cval = SOAP(self.cval)
    end_handlers[soap + 'Envelope'] = end_envelope
    end_handlers['Envelope'] = end_envelope

    def end_body(self, name):
        pass
    end_handlers[soap + 'Body'] = end_body
    end_handlers['Body'] = end_body

    def endElement(self, name):
        try:
            self.end_handlers[name](self, name)
        except KeyError:
            # XXX is there a more efficient way to process namespaces?
            if ':' in name:
                ns, tag = string.split(name, ':')
                if self.ns.has_key(ns):
                    tag = self.ns[ns] + tag
                # now try with the qualified tag name
                if self.end_handlers.has_key(tag):
                    self.end_handlers[tag](self, tag)
                else:
                    sys.stderr.write( "Unrecognized namespace/tag at end " + tag)
            else:
                sys.stderr.write( "Unknown end tag " + name)

# Serialize and Deserialize uforms and other VSMF Python objects
# according to the schemas at
# http://www.maya.com/local/higgins/mayaschema6.xsd and
# http://www.maya.com/local/higgins/repos_schema3.xsd
class MAYASchema:

    # it's important that '&' is always first
    safechars = (('&', '&amp;'),
                 ('<', '&lt;'),
                 ('>', '&gt;'),
                 ("'", '&apos;'),
                 ('"', '&quot;'),
                 )

    
    # XXX replace funny characters with entity refs.  I don't think
    # this is complete
    def _clean_string(self, s):

        for k,v in self.safechars:
            try:
                s = string.replace(s,k,v)
            except Exception, err:
                raise "Problem working with string %s %s: %s"%(repr(s), type(s), err)
        return s

    def _writeOpenTag(self, x, name, toplevelqual='', namespacespec=''):
        if not namespacespec == '':
            x.write("<" + toplevelqual + name + " " + namespacespec + ">")
        else:
            x.write("<" + toplevelqual + name + ">")

    def _writeCloseTag(self, x, name, toplevelqual=''):
        x.write("</" + toplevelqual + name + ">")        

    # the serialization function
    def _write_value(self, x, v, toplevelqual='', namespacespec=''):
        if type(v) is StringType:
            self._writeOpenTag(x, "string", toplevelqual, namespacespec)
            x.write(self._clean_string(v))
            self._writeCloseTag(x, "string", toplevelqual)
        elif type(v) is UnicodeType:
            self._writeOpenTag(x, "string", toplevelqual, namespacespec)
            x.write(self._clean_string(v))
            self._writeCloseTag(x, "string", toplevelqual)
        elif type(v) is IntType:
            self._writeOpenTag(x, "integer", toplevelqual, namespacespec)
            x.write(self._clean_string(str(v)))
            self._writeCloseTag(x, "integer", toplevelqual)
        elif type(v) is FloatType:
            self._writeOpenTag(x, "float", toplevelqual, namespacespec)
            x.write(self._clean_string(str(v)))
            self._writeCloseTag(x, "float", toplevelqual)
        elif type(v) is ListType:
            self._writeOpenTag(x, "array", toplevelqual, namespacespec)
            for a in v:
                self._writeOpenTag(x, "value")
                self._write_value(x, a)
                self._writeCloseTag(x, "value")
            self._writeCloseTag(x, "array", toplevelqual)
        elif hasattr(v, "_implements_date"):
            self._writeOpenTag(x, "date", toplevelqual, namespacespec)
            x.write(v.toString()) # iso 8601 time in utc
            self._writeCloseTag(x, "date", toplevelqual)
        elif uuid.isa(v):
            self._writeOpenTag(x, "uuid", toplevelqual, namespacespec)
            x.write(self._clean_string(v.toString()))
            self._writeCloseTag(x, "uuid", toplevelqual)
        elif uform.isa(v):
            toplevelqual = "maya:"
            namespacespec = 'xmlns:maya="http://www.maya.com/local/higgins/mayaschema6.xsd"'            
            self._writeOpenTag(x, "uform", toplevelqual, namespacespec)
            self._write_value(x, v.eform)
            self._write_value(x, v.uuid)
            self._writeCloseTag(x, "uform", toplevelqual)
        elif isRequest(v):
            toplevelqual = "repos:"
            namespacespec = 'xmlns:repos="http://www.maya.com/local/higgins/repos_schema3.xsd"'            
            self._writeOpenTag(x, "request", toplevelqual, namespacespec)
            if v.id:
                x.write("<id>" + str(v.id) + "</id>")
            if v.priority:
                x.write("<priority>" + str(v.priority) + "</priority>")
            x.write("<opcode>" + commands[str(v.opcode)] + "</opcode>")
            self._write_value(x, v.uf)
            self._writeCloseTag(x, "request", toplevelqual)
        elif isResponse(v):
            toplevelqual = "repos:"
            namespacespec = 'xmlns:repos="http://www.maya.com/local/higgins/repos_schema3.xsd"'            
            self._writeOpenTag(x, "response", toplevelqual, namespacespec)
            if v.id:
                x.write("<id>" + str(v.id) + "</id>")
            x.write("<opcode>" + commands[str(v.opcode)] + "</opcode>")
            self._write_value(x, v.uf)
            x.write("<status>" + str(v.status) + "</status>")            
            self._writeCloseTag(x, "response", toplevelqual)
        elif isSOAP(v):
            startsoap = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body>
            """
            endsoap = """</SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
            """
            x.write(startsoap)
            self._write_value(x, v.ob)
            x.write(endsoap)
        elif type(v) == DictionaryType:
            self._writeOpenTag(x, "eform", toplevelqual, namespacespec)
            for k in v.keys():
                self._writeOpenTag(x, "avpair")
                self._writeOpenTag(x, "attribute")
                x.write(self._clean_string(k))
                self._writeCloseTag(x, "attribute")
                self._writeOpenTag(x, "value")
                self._write_value(x, v[k])
                self._writeCloseTag(x, "value")
                self._writeCloseTag(x, "avpair")
            self._writeCloseTag(x, "eform", toplevelqual)
        else:
            sys.stderr.write( "Serializing unknown type " + str(type(v)))

    # needs a Python object representation of a VSMF value
    def toXML(self, value, nonamespace=0):
        sio = StringIO.StringIO()
        if isRequest(value) or isResponse(value):
            self._write_value(sio, value, "repos:",
                              'xmlns:repos="http://www.maya.com/local/higgins/repos_schema3.xsd"')
        else:
            if nonamespace == 1:
                self._write_value(sio, value)
            else:
                self._write_value(sio, value, "maya:",
                                  'xmlns:maya="http://www.maya.com/local/higgins/mayaschema6.xsd"')
        s = sio.getvalue()
        sio.close()
        return s

    # needs an XML string of the mayaschema6.xsd schema or
    # the repos_schema3.xsd schema or a SOAP wrapper containing those
    def fromXML(self, s):
        parser = make_parser()
        dh = Deserialize()
        parser.setContentHandler(dh)
        parser.feed(s)
        parser.close()
        return dh.cval

# just a type wrapper
class SOAP:

    def __init__(self, ob):
        self.ob = ob

# Repository request class
class Request:

    def __init__(self, id=None, priority=None, opcode=None, uf=None):
        self.priority = priority
        self.opcode = opcode # the integer representation
        self.id = id
        self.uf = uf

    # stubbed out; this should let you issue the request
    def issue(self):
        pass

# Repository response class
class Response:

    def __init__(self, id=None, opcode=None, uf=None, status=None):
        self.id = id
        self.opcode = opcode # the integer representation
        self.status = status
        self.uf = uf

# TEST requires a soap_request.xml and soap_response.xml file to exist
# these can be found at http://www.maya.com/local/higgins/soap_request.xml
# and http://www.maya.com/local/higgins/soap_response.xml
if __name__ == '__main__':
    # open some XML files
    fd = open('soap_request.xml', 'r')
    request_str = fd.read()
    fd.close()
    fd = open('soap_response.xml', 'r')
    response_str = fd.read()
    fd.close()

    # create a schema object to run our parsers
    ms = MAYASchema()

    # create two SOAP objects
    req = ms.fromXML(request_str)
    resp = ms.fromXML(response_str)

    # round-trip through the parser
    req_str = ms.toXML(req)
    req = ms.fromXML(req_str)
    req_str = ms.toXML(req)
    print req_str

    resp_str = ms.toXML(resp)
    resp = ms.fromXML(resp_str)
    resp_str = ms.toXML(resp)
    print resp_str
    
