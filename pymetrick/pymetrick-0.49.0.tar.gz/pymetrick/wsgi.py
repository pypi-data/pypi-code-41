#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Pymetrick.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Modulo para gestionar WSGI"""

from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2014-05-21'
__credits__ = ''
__text__ = 'Gestion de funciones para WSGI'
__file__ = 'wsgi.py'

#--- CHANGES ------------------------------------------------------------------
# 2012-09-21 v0.01 PL: - First version
# 2017-10-02 v0.43 PL: - Migrar a PYTHON 3.6

import sys
import os
import re
import base64
import logging
import logging.handlers
import collections
try:
  import simplejson as json
except:
  import json

from io import BytesIO, TextIOWrapper, BufferedReader

from pymetrick.helpers import *
from pymetrick.session import *


long = int

# Check development code
DEBUG = True


CONTENT_TYPE = {"7z":"application/x-7z-compressed",
                "aac":"audio/aac",
                "abw":"application/x-abiword",
                "arc":"application/octet-stream",
                "avi":"video/x-msvideo",
                "azw":"application/vnd.amazon.ebook",
                "bin":"application/octet-stream",
                "bmp":"image/bmp",
                "bz":"application/x-bzip",
                "bz2":"application/x-bzip2",
                "csh":"application/x-csh",
                "css":"text/css",
                "csv":"text/csv",
                "doc":"application/msword",
                "epub":"application/epub+zip",
                "gif":"image/gif",
                "htm":"text/html",
                "html":"text/html",
                "ico":"image/x-icon",
                "ics":"text/calendar",
                "jar":"application/java-archive",
                "jpeg":"image/jpeg",
                "jpg":"image/jpeg",
                "js":"application/javascript",
                "ical":"text/calendar",
                "ics":"text/calendar",
                "ifb":"text/calendar",
                "icalendar":"text/calendar",
                "json":"application/json",
                "mid":"audio/midi",
                "midi":"audio/midi",
                "mp4":"video/mp4",
                "mpeg":"video/mpeg",
                "mpkg":"application/vnd.apple.installer+xml",
                "odp":"application/vnd.oasis.opendocument.presentation",
                "ods":"application/vnd.oasis.opendocument.spreadsheet",
                "odt":"application/vnd.oasis.opendocument.text",
                "oga":"audio/ogg",
                "ogg":"audio/ogg",
                "ogv":"video/ogg",
                "ogx":"application/ogg",
                "pdf":"application/pdf",
                "png":"image/png",
                "ppt":"application/vnd.ms-powerpoint",
                "rar":"application/x-rar-compressed",
                "rtf":"application/rtf",
                "sh":"application/x-sh",
                "svg":"image/svg+xml",
                "swf":"application/x-shockwave-flash",
                "tar":"application/x-tar",
                "tif":"image/tiff",
                "tiff":"image/tiff",
                "ttf":"font/ttf",
                "txt":"text/plain",
                "vsd":"application/vnd.visio",
                "wav":"audio/x-wav",
                "weba":"audio/webm",
                "webm":"video/webm",
                "webp":"image/webp",
                "woff":"font/woff",
                "woff2":"font/woff2",
                "xhtml":"application/xhtml+xml",
                "xls":"application/vnd.ms-excel",
                "xml":"application/xml",
                "xul":"application/vnd.mozilla.xul+xml",
                "zip":"application/zip"}


STATUS_CODE = {
    "100": {
        "text": "Continue",
        "description": "\"indicates that the initial part of a request has been received and has not yet been rejected by the server.\"",
    },
    "101" : {
        "text": "Switching Protocols",
        "description": "\"indicates that the server understands and is willing to comply with the client's request, via the Upgrade header field, for a change in the application protocol being used on this connection.\"",
    },
    "102" : {
        "text": "Processing",
        "description": "\"is an interim response used to inform the client that the server has accepted the complete request, but has not yet completed it.\"",
    },
    "200" : {
        "text": "OK",
        "description": "\"indicates that the request has succeeded.\"",
    },
    "201" : {
        "text": "Created",
        "description": "\"indicates that the request has been fulfilled and has resulted in one or more new resources being created.\"",
    },
    "202" : {
        "text": "Accepted",
        "description": "\"indicates that the request has been accepted for processing, but the processing has not been completed.\"",
    },
    "203" : {
        "text": "Non-Authoritative Information",
        "description": "\"indicates that the request was successful but the enclosed payload has been modified from that of the origin server's 200 (OK) response by a transforming proxy.\"",
    },
    "204" : {
        "text": "No Content",
        "description": "\"indicates that the server has successfully fulfilled the request and that there is no additional content to send in the response payload body.\"",
    },
    "205" : {
        "text": "Reset Content",
        "description": "\"indicates that the server has fulfilled the request and desires that the user agent reset the \"document view\", which caused the request to be sent, to its original state as received from the origin server.\"",
    },
    "206" : {
        "text": "Partial Content",
        "description": "\"indicates that the server is successfully fulfilling a range request for the target resource by transferring one or more parts of the selected representation that correspond to the satisfiable ranges found in the requests's range header field.\"",
    },
    "207" : {
        "text": "Multi-Status",
        "description": "\"provides status for multiple independent operations.\"",
    },
    "226" : {
        "text": "IM Used",
        "description": "\"The server has fulfilled a GET request for the resource, and the response is a representation of the result of one or more instance-manipulations applied to the current instance.\"",
    },
    "300" : {
        "text": "Multiple Choices",
        "description": "\"indicates that the target resource has more than one representation, each with its own more specific identifier, and information about the alternatives is being provided so that the user (or user agent) can select a preferred representation by redirecting its request to one or more of those identifiers.\"",
    },
    "301" : {
        "text": "Moved Permanently",
        "description": "\"indicates that the target resource has been assigned a new permanent URI and any future references to this resource ought to use one of the enclosed URIs.\"",
    },
    "302" : {
        "text": "Found",
        "description": "\"indicates that the target resource resides temporarily under a different URI.\"",
    },
    "303" : {
        "text": "See Other",
        "description": "\"indicates that the server is redirecting the user agent to a different resource, as indicated by a URI in the Location header field, that is intended to provide an indirect response to the original request.\"",
    },
    "304" : {
        "text": "Not Modified",
        "description": "\"indicates that a conditional GET request has been received and would have resulted in a 200 (OK) response if it were not for the fact that the condition has evaluated to false.\"",
    },
    "305" : {
        "text": "Use Proxy",
        "description": "*deprecated*",
    },
    "307" : {
        "text": "Temporary Redirect",
        "description": "\"indicates that the target resource resides temporarily under a different URI and the user agent MUST NOT change the request method if it performs an automatic redirection to that URI.\"",
    },
    "308" : {
        "text": "Permanent Redirect",
        "description": "\"The target resource has been assigned a new permanent URI and any future references to this resource outght to use one of the enclosed URIs. [...] This status code is similar to 301 Moved Permanently (Section 7.3.2 of rfc7231), except that it does not allow rewriting the request method from POST to GET.\"",
    },
    "400" : {
        "text": "Bad Request",
        "description": "\"indicates that the server cannot or will not process the request because the received syntax is invalid, nonsensical, or exceeds some limitation on what the server is willing to process.\"",
    },
    "401" : {
        "text": "Unauthorized",
        "description": "\"indicates that the request has not been applied because it lacks valid authentication credentials for the target resource.\"",
    },
    "402" : {
        "text": "Payment Required",
        "description": "*reserved*",
    },
    "403" : {
        "text": "Forbidden",
        "description": "\"indicates that the server understood the request but refuses to authorize it.\"",
    },
    "404" : {
        "text": "Not Found",
        "description": "\"indicates that the origin server did not find a current representation for the target resource or is not willing to disclose that one exists.\"",
    },
    "405" : {
        "text": "Method Not Allowed",
        "description": "\"indicates that the method specified in the request-line is known by the origin server but not supported by the target resource.\"",
    },
    "406" : {
        "text": "Not Acceptable",
        "description": "\"indicates that the target resource does not have a current representation that would be acceptable to the user agent, according to the proactive negotiation header fields received in the request, and the server is unwilling to supply a default representation.\"",
    },
    "407" : {
        "text": "Proxy Authentication Required",
        "description": "\"is similar to 401 (Unauthorized), but indicates that the client needs to authenticate itself in order to use a proxy.\"",
    },
    "408" : {
        "text": "Request Timeout",
        "description": "\"indicates that the server did not receive a complete request message within the time that it was prepared to wait.\"",
    },
    "409" : {
        "text": "Conflict",
        "description": "\"indicates that the request could not be completed due to a conflict with the current state of the resource.\"",
    },
    "410" : {
        "text": "Gone",
        "description": "\"indicates that access to the target resource is no longer available at the origin server and that this condition is likely to be permanent.\"",
    },
    "411" : {
        "text": "Length Required",
        "description": "\"indicates that the server refuses to accept the request without a defined Content-Length.\"",
    },
    "412" : {
        "text": "Precondition Failed",
        "description": "\"indicates that one or more preconditions given in the request header fields evaluated to false when tested on the server.\"",
    },
    "413" : {
        "text": "Payload Too Large",
        "description": "\"indicates that the server is refusing to process a request because the request payload is larger than the server is willing or able to process.\"",
    },
    "414" : {
        "text": "URI Too Long",
        "description": "\"indicates that the server is refusing to service the request because the request-target is longer than the server is willing to interpret.\"",
    },
    "415" : {
        "text": "Unsupported Media Type",
        "description": "\"indicates that the origin server is refusing to service the request because the payload is in a format not supported by the target resource for this method.\"",
    },
    "416" : {
        "text": "Range Not Satisfiable",
        "description": "\"indicates that none of the ranges in the request's range header field overlap the current extent of the selected resource or that the set of ranges requested has been rejected due to invalid ranges or an excessive request of small or overlapping ranges.\"",
    },
    "417" : {
        "text": "Expectation Failed",
        "description": "\"indicates that the expectation given in the request's Expect header field could not be met by at least one of the inbound servers.\"",
    },
    "418" : {
        "text": "I'm a teapot",
        "description": "\"Any attempt to brew coffee with a teapot should result in the error code 418 I'm a teapot.\"",
    },
    "426" : {
        "text": "Upgrade Required",
        "description": "\"indicates that the server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol.\"",
    },
    "422" : {
        "text": "Unprocessable Entity",
        "description": "\"means the server understands the content type of the request entity (hence a 415(Unsupported Media Type) status code is inappropriate), and the syntax of the request entity is correct (thus a 400 (Bad Request) status code is inappropriate) but was unable to process the contained instructions.\"",
    },
    "423" : {
        "text": "Locked",
        "description": "\"means the source or destination resource of a method is locked.\"",
    },
    "424" : {
        "text": "Failed Dependency",
        "description": "\"means that the method could not be performed on the resource because the requested action depended on another action and that action failed.\"",
    },
    "428" : {
        "text": "Precondition Required",
        "description": "\"indicates that the origin server requires the request to be conditional.\"",
    },
    "429" : {
        "text": "Too Many Requests",
        "description": "\"indicates that the user has sent too many requests in a given amount of time (\"rate limiting\").\"",
    },
    "431" : {
        "text": "Request Header Fields Too Large",
        "description": "\"indicates that the server is unwilling to process the request because its header fields are too large.\"",
    },
    "451" : {
        "text": "Unavailable For Legal Reasons",
        "description": "\"This status code indicates that the server is denying access to the resource in response to a legal demand.\"",
    },
    "500" : {
        "text": "Internal Server Error",
        "description": "\"indicates that the server encountered an unexpected condition that prevented it from fulfilling the request.\"",
    },
    "501" : {
        "text": "Not Implemented",
        "description": "\"indicates that the server does not support the functionality required to fulfill the request.\"",
    },
    "502" : {
        "text": "Bad Gateway",
        "description": "\"indicates that the server, while acting as a gateway or proxy, received an invalid response from an inbound server it accessed while attempting to fulfill the request.\"",
    },
    "503" : {
        "text": "Service Unavailable",
        "description": "\"indicates that the server is currently unable to handle the request due to a temporary overload or scheduled maintenance, which will likely be alleviated after some delay.\"",
    },
    "504" : {
        "text": "Gateway Time-out",
        "description": "\"indicates that the server, while acting as a gateway or proxy, did not receive a timely response from an upstream server it needed to access in order to complete the request.\"",
    },
    "505" : {
        "text": "HTTP Version Not Supported",
        "description": "\"indicates that the server does not support, or refuses to support, the protocol version that was used in the request message.\"",
    },
    "506" : {
        "text": "Variant Also Negotiates",
        "description": "\"indicates that the server has an internal configuration error: the chosen variant resource is configured to engage in transparent content negotiation itself, and is therefore not a proper end point in the negotiation process.\"",
    },
    "507" : {
        "text": "Insufficient Storage",
        "description": "\"means the method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request.\"",
    },
    "511" : {
        "text": "Network Authentication Required",
        "description": "\"indicates that the client needs to authenticate to gain network access.\"",
    }
}

'''
DEBUG - debug message
INFO - info message
WARNING - warn message
ERROR - error message
CRITICAL - critical message
'''
LOG_FILENAME = '-'.join([os.path.abspath(__file__).split(os.sep)[len(os.path.abspath(__file__).split(os.sep))-1],])[:-3]
LOG = logging.getLogger(LOG_FILENAME)

if 'LD_LIBRARY_PATH' in list(os.environ.keys()):
    # CGI environment
    sys.stdout = sys.stderr
    if DEBUG:
        logging.basicConfig(stream = sys.stderr, level=logging.DEBUG, format='%(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(stream = sys.stderr, level=logging.WARNING, format='%(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
else:
    # not CGI environment
    logging.basicConfig(stream=sys.stderr)
    hdlr = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME+'.log',mode='a', encoding='utf-8', maxBytes=1048576, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    LOG.addHandler(hdlr)
    if DEBUG:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.WARNING)

bytes_types = (bytes, bytearray)

class wsgateway:
    '''Gestion de entorno Web Server Gateway Interface'''

    def __init__(self, environment, start_response, settings = None):

        try:
            self._p = None
            self._q = None
            self.status = '200'
            self.header = dict()
            self.parametros = None
            self.environ = environment
            self.settings = settings if settings is not None else {};
            self.response = start_response
            if DEBUG:
                '''mostrar entorno en caso de DEBUG
                   con claves ordenadas
                '''
                keys = sorted(list(self.environ.keys()))
                for key in keys:
                    LOG.debug("%s: %s" % (key, self.environ[key]))

            # check xmlhttprequest
            self.ajax_request = self.is_xmlhttprequest()
            # check REQUEST_METHOD
            if self.is_allowed_request_method():
                '''La variable de environ CONTENT_LENGTH puede ser 0 o estar ausente en las variables de environ
                   esta relacionada con el contenido de wsgi.input
                '''
                if int(self.environ.get('CONTENT_LENGTH','0'))>0 and self.environ.get('wsgi.input',None):
                    self._p = self.environ['wsgi.input'].read(int(self.environ['CONTENT_LENGTH']))
                else:
                    '''QUERY_STRING puede no tener contenido o estar ausente en las variables de environ'''
                    try:
                        if self.environ.get('QUERY_STRING',None):
                            '''QUERY_STRING The portion of the request URL that follows the "?" , if any. May be empty or absent.'''
                            self._p = self.environ.get('QUERY_STRING','')
                    except Exception as e:
                        pass

                self.parametros = None
                if self._p is not None:
                    self.request()
                else:
                    if self._p is not None and DEBUG:
                        LOG.debug("self.parametros %s" % (self._p,))
                    self.parametros = None

        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error("Error en metodo '__init__' <%s> en linea %s !!!\n" % (repr(e),tb.tb_lineno))

    def is_xmlhttprequest(self):
        '''Check xmlhttprequest'''
        if self.environ.get('HTTP_X_REQUESTED_WITH','').lower() == 'xmlhttprequest' or self.environ.get('X_REQUESTED_WITH','').lower() == 'xmlhttprequest':
            return True
        return False

    def is_allowed_request_method(self):
        '''Check REQUEST_METHOD'''
        if self.environ.get('REQUEST_METHOD','').upper() in ['GET','POST','PUT','DELETE','HEADER']:
            return True
        return False

    def get_key(self, key):
        return self.environment.get(key)

    def get_request(self):
        return self.parametros

    def set_status(self,status):
        self.status = status

    def set_header(self,header):
        if isinstance(header,(list,tuple)):
            for n in header:
                if isinstance(n,(list,tuple)):
                    if len(n)==2:
                        self.header[n[0]] = n[1]
                elif len(header)==2:
                    self.header[header[0]] = header[1]
                    break

    def status_response(self,output,jwt):
        try:
            self.header_list = []
            LOG.debug('self.status {0}'.format(self.status))
            LOG.debug('self.status type {0}'.format(type(self.status).__name__))
            if self.header.get('content-type',None):
                LOG.debug('header[content-type] {0}'.format(self.header['content-type']))
                LOG.debug('header[content-type] type {0}'.format(type(self.header['content-type']).__name__))
            if str(self.status) in STATUS_CODE:
                self.status = getStatus(self.status)
                self.header['X-Authorization'] = jwt.get_token()
                self.header['Set-Cookie'] = jwt.get_cookie()
                if self.header.get('content-type',None):
                    if self.header['content-type'] == 'application/octet-stream' or self.header['content-type'] == 'application/force-download':
                        # corregir content-type
                        if output[output.find('.')+1:].replace('_','') in CONTENT_TYPE.keys():
                            self.header['content-type'] = CONTENT_TYPE[output[output.find('.')+1:].replace('_','')]
                        self.header['content-transfer-encoding'] = 'binary'
                        self.header['content-disposition'] =  'attachment; filename={0};'.format(output)
                        file_path = os.path.join(self.settings.get('download',''), bytes2str(output))
                        self.header['X-Sendfile'] = file_path
                        for key,value in self.header.items():
                            self.header_list.append((key,value,))
                        self.response(self.status,self.header_list)
                        return [b'']
                else:
                    self.header['content-type'] = 'text/html; charset=UTF-8'
                self.header['content-length'] = str(len(str2bytes(output)))
                self.header['Cache-Control'] = 'no-store'
                for key,value in self.header.items():
                    self.header_list.append((key,value,))
                self.response(self.status,self.header_list)
                if self.environ.get('REQUEST_METHOD','').upper() == 'HEADER':
                    return [b'']
                else:
                    return str2bytes([output])
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error("Error en metodo 'status_response' <%s> en linea %s !!!\n" % (repr(e),tb.tb_lineno))


    def request(self):
        ''' Process all parameters except content-type <multipart/form-data>'''
        try:
            # self.environ.get('CONTENT_TYPE','').split(';')[0] in ('multipart/form-data',) &&
            if self.environ['REQUEST_METHOD'] == 'POST' and self.environ.get('CONTENT_TYPE','').split(';')[0] in ('multipart/form-data',):
                # request for file upload
                # get first 'boundary' code
                _q_list = self._p.split(b"\r",1)
                json_q = dict()
                # split by 'boundary'
                _q_list = self._p.split(_q_list[0])

                _pp = dict()
                for n in range(len(_q_list)):
                    json_q[n] = _q_list[n].split(b"\r\n")
                    if len(json_q[n])>3:
                        # json_q[n][1]  Content-Disposition: form-data; name="file"; filename="example.jpg"
                        # json_q[n])>2  Content-Type: image/jpeg if a file or None
                        # json_q[n][3]  Value
                        if json_q[n][2].lower().startswith(b'content-type'):
                            content_disposition_name = None             # id field
                            content_disposition_filename = None         # file name
                            # join list like file
                            json_q[n][4] += b"\r\n"
                            for m in range(5,len(json_q[n])):
                                json_q[n][4] += b''.join([json_q[n][m],b"\r\n"])
                            # id field
                            content_disposition_name = json_q[n][1].split(b':')[1].split(b';')[1].split(b'=')[1].replace(b'"', b'')
                            # file name
                            content_disposition_filename = json_q[n][1].split(b':')[1].split(b';')[2].split(b'=')[1].replace(b'"', b'')
                            if content_disposition_name is not None and content_disposition_filename is not None:
                                # if form is multi files, file name save like list
                                if _pp.get(content_disposition_name,None):
                                    _pp[content_disposition_name].append(content_disposition_filename)
                                else:
                                    _pp[content_disposition_name]= [content_disposition_filename]
                            # save file on self.settings['upload']
                            if len(json_q[n][4])>0:
                                file_path = os.path.join(self.settings.get('upload',''), bytes2str(content_disposition_filename))
                                counter = 0
                                with open(file_path, 'wb') as output_file:
                                    output_file.write(json_q[n][4])
                                output_file.closed
                        else:
                            # is a value
                            content_disposition_name = None
                            content_type = None
                            for m in range(len(json_q[n])):
                                if json_q[n][m].lower().startswith(b'content-disposition'):
                                    # id field
                                    content_disposition_name = json_q[n][1].split(b':')[1].split(b';')[1].split(b'=')[1].replace(b'"', b'')
                                elif len(json_q[n][m])>0:
                                    # value
                                    content_type = json_q[n][3].strip()
                            if content_disposition_name is not None and content_type is not None:
                                _pp[content_disposition_name]=content_type
                # set clear memory
                _q_list = None
                json_q = None
            else:
                # request for json or scheme key=value&
                try:
                    LOG.debug('self._p %s' % self._p)
                    for n in self.environ.keys():
                        LOG.debug("key %s  value %s" % (n,self.environ[n]))
                    if isinstance(self._p, (str,)) and (re.search('^\{.*}$', self._p ) or re.search('^\[{.*}]$', self._p )):
                        # check if parameters like str received with format JSON (dict, array)
                        LOG.debug("json str")
                        json_q = json.loads(self._p)
                        LOG.debug("json str json_q %s" % (json.dumps(json_q),))
                    elif isinstance(self._p, (bytes,bytearray)) and (re.search(b'^\{.*}$', self._p ) or re.search(b'^\[{.*}]$', self._p )):
                        # check if parameters like bytes received with format JSON (dict, array)
                        LOG.debug("json bytes")
                        json_q = json.loads(self._p)
                        LOG.debug("json bytes json_q %s" % (json.dumps(json_q),))
                    else:
                        # parameters received like scheme key=value
                        LOG.debug("other")
                        json_q = parse_qs(self._p)
                        LOG.debug("other json_q %s" % (json.dumps(json_q),))
                except Exception as e:
                    LOG.error("parameters error %s" % (self._p,))
                    json_q = parse_qs(self._p)
                # check if parameters value coded on base64 y decode them
                json_q = obj_b64decode(json_q)
                # Change from bytes to str
                json_q = bytes2str(json_q)

                self.parametros = json.dumps(json_q, default=to_json)
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error("metodo 'request' <%s> en linea %s !!!\n" % (repr(e),tb.tb_lineno))

    def request_multipart(self):
        ''' Process parameters content-type <multipart/form-data>'''
        try:
            if self.environ['REQUEST_METHOD'] == 'POST':
                # get first 'boundary' code
                _q_list = self._p.split(b"\r",1)
                json_q = dict()
                # split by 'boundary'
                _q_list = self._p.split(_q_list[0])

                _pp = dict()
                for n in range(len(_q_list)):
                    json_q[n] = _q_list[n].split(b"\r\n")
                    if len(json_q[n])>3:
                        # json_q[n][1]  Content-Disposition: form-data; name="file"; filename="example.jpg"
                        # json_q[n])>2  Content-Type: image/jpeg if a file or None
                        # json_q[n][3]  Value
                        if json_q[n][2].lower().startswith(b'content-type'):
                            content_disposition_name = None             # id field
                            content_disposition_filename = None         # file name
                            # join list like file
                            json_q[n][4] += b"\r\n"
                            for m in range(5,len(json_q[n])):
                                json_q[n][4] += b''.join([json_q[n][m],b"\r\n"])
                            # id field
                            content_disposition_name = json_q[n][1].split(b':')[1].split(b';')[1].split(b'=')[1].replace(b'"', b'')
                            # file name
                            content_disposition_filename = json_q[n][1].split(b':')[1].split(b';')[2].split(b'=')[1].replace(b'"', b'')
                            if content_disposition_name is not None and content_disposition_filename is not None:
                                # if form is multi files, file name save like list
                                if _pp.get(content_disposition_name,None):
                                    _pp[content_disposition_name].append(content_disposition_filename)
                                else:
                                    _pp[content_disposition_name]= [content_disposition_filename]
                            # save file on self.settings['upload']
                            if len(json_q[n][4])>0:
                                file_path = os.path.join(self.settings.get('upload',''), bytes2str(content_disposition_filename))
                                counter = 0
                                with open(file_path, 'wb') as output_file:
                                    output_file.write(json_q[n][4])
                                output_file.closed
                        else:
                            # is a value
                            content_disposition_name = None
                            content_type = None
                            for m in range(len(json_q[n])):
                                if json_q[n][m].lower().startswith(b'content-disposition'):
                                    # id field
                                    content_disposition_name = json_q[n][1].split(b':')[1].split(b';')[1].split(b'=')[1].replace(b'"', b'')
                                elif len(json_q[n][m])>0:
                                    # value
                                    content_type = json_q[n][3].strip()
                            if content_disposition_name is not None and content_type is not None:
                                _pp[content_disposition_name]=content_type
                # set clear memory
                _q_list = None
                json_q = None
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error("metodo 'request_multipart' <%s> en linea %s !!!\n" % (repr(e),tb.tb_lineno))

def getStatus(status_id):
    '''Process LOT errors'''
    try:
        if isinstance(status_id,(int,)):
            status_id = str(status_id)
        if STATUS_CODE.get(status_id,None):
            return "{0} {1}".format(status_id,STATUS_CODE[status_id]['text'])
        else:
            status_id = "200"
            return "{0} {1}".format(status_id,STATUS_CODE[status_id]['text'])
    except Exception as e:
        tb = sys.exc_info()[2]
        LOG.debug("Error <%s> en linea %s !!!\n" % (repr(e),tb.tb_lineno))

_implicit_encoding = 'ascii'
_implicit_errors = 'strict'

def _noop(obj):
    return obj

def _encode_result(obj, encoding=_implicit_encoding,
                        errors=_implicit_errors):
    return obj.encode(encoding, errors)

def _decode_args(args, encoding=_implicit_encoding,
                       errors=_implicit_errors):
    return tuple(x.decode(encoding, errors) if x else '' for x in args)

def _coerce_args(*args):
    # Invokes decode if necessary to create str args
    # and returns the coerced inputs along with
    # an appropriate result coercion function
    #   - noop for str inputs
    #   - encoding function otherwise
    str_input = isinstance(args[0], str)
    for arg in args[1:]:
        # We special-case the empty string to support the
        # "scheme=''" default argument to some functions
        if arg and isinstance(arg, str) != str_input:
            raise TypeError("Cannot mix str and non-str arguments")
    if str_input:
        return args + (_noop,)
    return _decode_args(args) + (_encode_result,)

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

def unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded as UTF-8. This is only an issue if it contains
    # unescaped non-ASCII characters, which URIs should not.
    if not string:
        # Is it a string-like object?
        string.split
        return b''
    if isinstance(string, str):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    if len(bits) == 1:
        return string
    res = [bits[0]]
    append = res.append
    # Delay the initialization of the table to not waste memory
    # if the function is never called
    global _hextobyte
    if _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes.fromhex(a + b)
                      for a in _hexdig for b in _hexdig}
    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    return b''.join(res)

_asciire = re.compile('([\x00-\x7f]+)')

def unquote(string, encoding='utf-8', errors='replace'):
    """Replace %xx escapes by their single-character equivalent. The optional
    encoding and errors parameters specify how to decode percent-encoded
    sequences into Unicode characters, as accepted by the bytes.decode()
    method.
    By default, percent-encoded sequences are decoded with UTF-8, and invalid
    sequences are replaced by a placeholder character.
    unquote('abc%20def') -> 'abc def'.
    """
    if '%' not in string:
        string.split
        return string
    if encoding is None:
        encoding = 'utf-8'
    if errors is None:
        errors = 'replace'
    bits = _asciire.split(string)
    res = [bits[0]]
    append = res.append
    for i in range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    return ''.join(res)

def parse_qs(qs, keep_blank_values=False, strict_parsing=False,encoding='utf-8', errors='replace'):
    """Parse a query given as a string argument.
        Arguments:
        qs: percent-encoded query string to be parsed
        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as if they were
            not included.
        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.
        encoding and errors: specify how to decode percent-encoded sequences
            into Unicode characters, as accepted by the bytes.decode() method.
        Returns a dictionary of list - Modify to return a dictionary of values
    """
    parsed_result = {}
    pairs = parse_qsl(qs, keep_blank_values, strict_parsing, encoding=encoding, errors=errors)
    for name, value in pairs:
        if name in parsed_result:
            # if more than 1 value
            if isinstance(parsed_result[name],(str,bytes,bytearray)):
                parsed_tmp = parsed_result[name]
                parsed_result[name] = [parsed_tmp]
            if isinstance(parsed_result[name],(list,tuple)):
                parsed_result[name].append(value)
        else:
            # if only 1 value
            parsed_result[name] = value
    return parsed_result

def parse_qsl(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace'):
    """Parse a query given as a string argument.
        Arguments:
        qs: percent-encoded query string to be parsed
        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as blank
            strings.  The default false value indicates that blank values
            are to be ignored and treated as if they were  not included.
        strict_parsing: flag indicating what to do with parsing errors. If
            false (the default), errors are silently ignored. If true,
            errors raise a ValueError exception.
        encoding and errors: specify how to decode percent-encoded sequences
            into Unicode characters, as accepted by the bytes.decode() method.
        Returns a list, as G-d intended.
    """
    qs, _coerce_result = _coerce_args(qs)
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = nv[0].replace('+', ' ')
            name = unquote(name, encoding=encoding, errors=errors)
            name = _coerce_result(name)
            value = nv[1].replace('+', ' ')
            value = unquote(value, encoding=encoding, errors=errors)
            value = _coerce_result(value)
            r.append((name, value))
    return r

def unquote_plus(string, encoding='utf-8', errors='replace'):
    """Like unquote(), but also replace plus signs by spaces, as required for
    unquoting HTML form values.
    unquote_plus('%7e/abc+def') -> '~/abc def'
    """
    string = string.replace('+', ' ')
    return unquote(string, encoding, errors)

_ALWAYS_SAFE = frozenset(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         b'abcdefghijklmnopqrstuvwxyz'
                         b'0123456789'
                         b'_.-~')
_ALWAYS_SAFE_BYTES = bytes(_ALWAYS_SAFE)
_safe_quoters = {}

class Quoter(collections.defaultdict):
    """A mapping from bytes (in range(0,256)) to strings.
    String values are percent-encoded byte values, unless the key < 128, and
    in the "safe" set (either the specified safe set, or default set).
    """
    # Keeps a cache internally, using defaultdict, for efficiency (lookups
    # of cached keys don't call Python code at all).
    def __init__(self, safe):
        """safe: bytes object."""
        self.safe = _ALWAYS_SAFE.union(safe)

    def __repr__(self):
        # Without this, will just display as a defaultdict
        return "<%s %r>" % (self.__class__.__name__, dict(self))

    def __missing__(self, b):
        # Handle a cache miss. Store quoted string in cache and return.
        res = chr(b) if b in self.safe else '%{:02X}'.format(b)
        self[b] = res
        return res

def quote(string, safe='/', encoding=None, errors=None):
    """quote('abc def') -> 'abc%20def'
    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.
    RFC 3986 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.
    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | "," | "~"
    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.
    Python 3.7 updates from using RFC 2396 to RFC 3986 to quote URL strings.
    Now, "~" is included in the set of reserved characters.
    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.
    string and safe may be either str or bytes objects. encoding and errors
    must not be specified if string is a bytes object.
    The optional encoding and errors parameters specify how to deal with
    non-ASCII characters, as accepted by the str.encode method.
    By default, encoding='utf-8' (characters are encoded with UTF-8), and
    errors='strict' (unsupported characters raise a UnicodeEncodeError).
    """
    if isinstance(string, str):
        if not string:
            return string
        if encoding is None:
            encoding = 'utf-8'
        if errors is None:
            errors = 'strict'
        string = string.encode(encoding, errors)
    else:
        if encoding is not None:
            raise TypeError("quote() doesn't support 'encoding' for bytes")
        if errors is not None:
            raise TypeError("quote() doesn't support 'errors' for bytes")
    return quote_from_bytes(string, safe)

def quote_plus(string, safe='', encoding=None, errors=None):
    """Like quote(), but also replace ' ' with '+', as required for quoting
    HTML form values. Plus signs in the original string are escaped unless
    they are included in safe. It also does not have safe default to '/'.
    """
    # Check if ' ' in string, where string may either be a str or bytes.  If
    # there are no spaces, the regular quote will produce the right answer.
    if ((isinstance(string, str) and ' ' not in string) or
        (isinstance(string, bytes) and b' ' not in string)):
        return quote(string, safe, encoding, errors)
    if isinstance(safe, str):
        space = ' '
    else:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    return string.replace(' ', '+')

def quote_from_bytes(bs, safe='/'):
    """Like quote(), but accepts a bytes object rather than a str, and does
    not perform string-to-bytes encoding.  It always returns an ASCII string.
    quote_from_bytes(b'abc def\x3f') -> 'abc%20def%3f'
    """
    if not isinstance(bs, bytes_types):
        raise TypeError("quote_from_bytes() expected bytes")
    if not bs:
        return ''
    if isinstance(safe, str):
        # Normalize 'safe' by converting to bytes and removing non-ASCII chars
        safe = safe.encode('ascii', 'ignore')
    else:
        safe = bytes([c for c in safe if c < 128])
    if not bs.rstrip(_ALWAYS_SAFE_BYTES + safe):
        return bs.decode()
    try:
        quoter = _safe_quoters[safe]
    except KeyError:
        _safe_quoters[safe] = quoter = Quoter(safe).__getitem__
    return ''.join([quoter(char) for char in bs])

if __name__  == "__main__":
    print ('''copyright {0}'''.format( __copyright__))
    print ('''license {0}'''.format( __license__))
    print ('''version {0}'''.format( __version__))
    if len(sys.argv) < 2:
        sys.stderr.write("for help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''
        Tratamiento de WSGI\n\n''')







