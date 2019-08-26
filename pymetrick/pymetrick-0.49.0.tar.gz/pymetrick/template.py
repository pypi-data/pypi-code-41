#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Pymetrick.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Modulo para generar paginas html5"""

from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2012-09-21'
__credits__ = ''
__text__ = 'Generador de codigo HTML5 a partir de ficheros'
__file__ = 'template.py'

#--- CHANGES ------------------------------------------------------------------
# 2012-09-21 v0.01 PL: - First version
# 2017-10-02 v0.43 PL: - Migrar a PYTHON 3.6

import sys
import os
import string
import pdb
import re
import logging
import logging.handlers
try:
    import simplejson as json
except ImportError:
    import json
from pymetrick.common import _weekdayname,_monthname

long = int

# Comprimir HTML
HTML_COMPRESS = False

# Check development code
DEBUG = False

acceptable_head_elements = ['head','title','base','link','meta','style','script']

acceptable_head_attributes = ['name','content','type','size','href']

acceptable_body_elements = ['a', 'abbr', 'acronym', 'address', 'area',
        'article', 'aside', 'audio', 'b', 'big', 'blockquote', 'br', 'button',
        'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup',
        'command', 'datagrid', 'datalist', 'dd', 'del', 'details', 'dfn',
        'dialog', 'dir', 'div', 'dl', 'dt', 'em', 'event-source', 'fieldset',
        'figcaption', 'figure', 'footer', 'font', 'form', 'header', 'hgroup', 'h1',
        'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input', 'ins',
        'keygen', 'kbd', 'label', 'legend', 'li', 'm', 'map', 'mark', 'menu', 'meter',
        'multicol', 'nav', 'nextid', 'ol', 'output', 'optgroup', 'option',
        'p', 'pre', 'progress', 'q', 's', 'samp', 'section', 'select',
        'small', 'sound', 'source', 'spacer', 'span', 'strike', 'strong',
        'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'time', 'tfoot',
        'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var', 'video']

self_closing_tag = ['base','br','col','hr','img','input','link','meta','param']

acceptable_attributes = ['abbr', 'accept', 'accept-charset', 'accesskey',
        'action', 'align', 'alt', 'autocomplete', 'autofocus', 'axis',
        'background', 'balance', 'bgcolor', 'bgproperties', 'border',
        'bordercolor', 'bordercolordark', 'bordercolorlight', 'bottompadding',
        'cellpadding', 'cellspacing', 'ch', 'challenge', 'char', 'charoff',
        'choff', 'charset', 'checked', 'cite', 'class', 'clear', 'color',
        'cols', 'colspan', 'compact', 'contenteditable', 'controls', 'coords',
        'data', 'datafld', 'datapagesize', 'datasrc', 'datetime', 'default',
        'delay', 'dir', 'disabled', 'draggable', 'dynsrc', 'enctype', 'end',
        'face', 'for', 'form', 'frame', 'galleryimg', 'gutter', 'headers',
        'height', 'hidefocus', 'hidden', 'high', 'href', 'hreflang', 'hspace',
        'icon', 'id', 'inputmode', 'ismap', 'keytype', 'label', 'leftspacing',
        'lang', 'list', 'longdesc', 'loop', 'loopcount', 'loopend',
        'loopstart', 'low', 'lowsrc', 'max', 'maxlength', 'media', 'method',
        'min', 'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'open',
        'optimum', 'pattern', 'ping', 'point-size', 'prompt', 'pqg',
        'radiogroup', 'readonly', 'rel', 'repeat-max', 'repeat-min',
        'replace', 'required', 'rev', 'rightspacing', 'rows', 'rowspan',
        'rules', 'scope', 'selected', 'shape', 'size', 'span', 'src', 'start',
        'step', 'style', 'summary', 'suppress', 'tabindex', 'target',
        'template', 'title', 'toppadding', 'type', 'unselectable', 'usemap',
        'urn', 'valign', 'value', 'variable', 'volume', 'vspace', 'vrml',
        'width', 'wrap', 'xml:lang']

acceptable_css_properties = ['azimuth', 'background-color',
        'border-bottom-color', 'border-collapse', 'border-color',
        'border-left-color', 'border-right-color', 'border-top-color', 'clear',
        'color', 'cursor', 'direction', 'display', 'elevation', 'float', 'font',
        'font-family', 'font-size', 'font-style', 'font-variant', 'font-weight',
        'height', 'letter-spacing', 'line-height', 'overflow', 'pause',
        'pause-after', 'pause-before', 'pitch', 'pitch-range', 'richness',
        'speak', 'speak-header', 'speak-numeral', 'speak-punctuation',
        'speech-rate', 'stress', 'text-align', 'text-decoration', 'text-indent',
        'unicode-bidi', 'vertical-align', 'voice-family', 'volume',
        'white-space', 'width']

acceptable_css_keywords = ['auto', 'aqua', 'black', 'block', 'blue',
        'bold', 'both', 'bottom', 'brown', 'center', 'collapse', 'dashed',
        'dotted', 'fuchsia', 'gray', 'green', '!important', 'italic', 'left',
        'lime', 'maroon', 'medium', 'none', 'navy', 'normal', 'nowrap', 'olive',
        'pointer', 'purple', 'red', 'right', 'solid', 'silver', 'teal', 'top',
        'transparent', 'underline', 'white', 'yellow']



def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (_weekdayname[wd], day, _monthname[month], year, hh, mm, ss)

def char2Html(_value = None):
    """Realiza el cambio en un texto, de todos los caracteres especiales en UTF-8 y ASCII a su correspondencia en HTML"""
    char2 = {r'\xe1': "&aacute;", \
                  r'\xc1': "&Aacute;", \
                  r'\xe9': "&eacute;", \
                  r'\xc9': "&Eacute;", \
                  r'\xed': "&iacute;", \
                  r'\xcd': "&Iacute;", \
                  r'\xf3': "&oacute;", \
                  r'\xd3': "&Oacute;", \
                  r'\xfa': "&uacute;", \
                  r'\xda': "&Uacute;", \
                  r'\xf1': "&ntilde;", \
                  r'\xd1': "&Ntilde;", \
                  r'\xfc': "&uuml;", \
                  r'\xdc': "&Uuml;", \
                  r'\x7e': "&tilde;", \
                  r'\x3c': "&lt;", \
                  r'\x3e': "&gt;", \
                  r'\xa3': "&pound;", \
                  r'\x80': "&euro;", \
                  r'\x24': "$", \
                  r'\xa5': "&yen;", \
                  'á': "&aacute;", \
                  'Á': "&Aacute;", \
                  'é': "&eacute;", \
                  'É': "&Eacute;", \
                  'í': "&iacute;", \
                  'Í': "&Iacute;", \
                  'ó': "&oacute;", \
                  'Ó': "&Oacute;", \
                  'ú': "&uacute;", \
                  'Ú': "&Uacute;", \
                  'ü': "&uuml;", \
                  'Ü': "&Uuml;", \
                  'ñ': "&ntilde;", \
                  'Ñ': "&Ntilde;", \
                  'ç': "&ccedil;", \
                  'Ç': "&Ccedil;", \
                  '~': "&tilde;", \
                  '<': "&lt;", \
                  '>': "&gt;", \
                  '£': "&pound;", \
                  '€': "&euro;", \
                  ' EURO ': " &euro; ", \
                  ' euro ': " &euro; ", \
                  ' EUROS ': " &euro; ", \
                  ' euros ': " &euro; ", \
                  '¥': "&yen;", \
                  '&': "&amp;", \
                  '"': "&quot;", \
                  "'": "&apos;" \
                  }
    for n in list(char2.keys()):
        _value = re.sub(n,char2[n],_value)
    return _value

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

#=== CLASS HTML5 ===============================================================

class Html5(object):
    """Realiza objetos HTML5 con una estructura completa HTML,HEAD,BODY,FOOTER """

    def __init__( self ):
        """Inicializa la clase Html5"""

        self._text = ''
        self.treeHtml = []
        self.treeHead = []
        self.treeBody = []


    def tagHtml(self, content='lang="es"'):

        self._text = content.strip()
        tokenHtml = {"doctype":"<!DOCTYPE html>",
                          "html":"<html [[content]]>"}
        self.treeHtml.append(tokenHtml["doctype"])
        self.treeHtml.append(tokenHtml["html"].replace('[[content]]',self._text))
        self._text = ''

    def tagHead(self):

        tokenHead = {"head":"<head>"}
        self.treeHead.append(tokenHead['head'])


    def addHead( self, *args, **kwargs):
        '''
           tag, content, size, type_content
           Para etiqueta stylesheet
           type_content  all, aural, braille, embossed, handheld, print, projection, screen, tty, tv

           Para etiqueta script
           type text/javascript

           Para etiqueta apple-touch-icon-precomposed
           size
                 144x144 , 114x114, 72x72

           type_content
                 Formato png: image/png
                 Formato gif: image/gif
                 Formato jpeg (extension jpg o jpeg): image/jpeg
                 Formato ico  image/x-icon

           Ejemplos meta :
           <meta name="HandheldFriendly" content="True">
           <meta name="MobileOptimized" content="320">
           <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">

           <base href="http://www.w3schools.com/images/" target="_blank">
        '''
        """global treeHead"""

        _metaTags = {'tag':'','content':'','size':'','type_content':''}
        _metaList = ['tag','content','size','type_content']
        if args:
            for n in range(len(args)):
                _metaTags[_metaList[n]] = args[n]
        if kwargs:
            for n,m in list(kwargs.items()):
                _metaTags[n]=m

        nodeTag = {"title":'<title>[[content]]</title>',
                   "DC.title":'<meta name="DC.title" content="[[content]]">',
                   "description":'<meta name="description" content="[[content]]">',
                   "keywords":'<meta name="keywords" content="[[content]]">',
                   "author":'<meta name="author" content="[[content]]">',
                   "generator":'<meta name="generator" content="[[content]]">',
                   "application-name":'<meta name="application-name" content="[[content]]">',
                   "content-type":'<meta http-equiv="content-type" content="[[content]]">',
                   "default-style":'<meta http-equiv="default-style" content="[[content]]">',
                   "language":'<meta http-equiv="content-language" content="[[content]]">',
                   "refresh":'<meta http-equiv="refresh" content="[[content]]">',
                   "cleartype":'<meta http-equiv="cleartype" content="[[content]]">',
                   "cache-control":'<meta http-equiv="Cache-control" content="[[content]]">',
                   "handheldfriendly":'<meta name="HandheldFriendly" content="[[content]]">',
                   "mobileoptimized":'<meta name="MobileOptimized" content="[[content]]">',
                   "viewport":'<meta name="viewport" content="[[content]]">',
                   "robots":'<meta name="robots" content="[[content]]">',
                   "ICBM":'<meta name="ICBM" content="[[content]]">',
                   "geo.position":'<meta name="geo.position" content="[[content]]">',
                   "geo.placename":'<meta name="geo.placename" content="[[content]]">',
                   "geo.region":'<meta name="geo.region" content="[[content]]">',
                   "google-site-verification":'<meta name="google-site-verification" content="[[content]]">',
                   "bing-site-verification":'<meta name="msvalidate.01" content="[[content]]">',
                   "yandex-site-verification":'<meta name="yandex-verification" content="[[content]]">',
                   "authenticity-token":'<meta name="authenticity-token" content="[[content]]">',
                   "charset":'<meta charset="[[content]]">',
                   "format-detection":'<meta name="format-detection" content="[[content]]">',
                   "stylesheet":'<link rel="stylesheet" type="text/css" href="[[content]]" media="[[type]]"/>',
                   "style":'<style type="text/css">[[content]]</style>',
                   "script":'<script src="[[content]]" type="[[type]]" ></script>',
                   "apple-touch-icon-precomposed":'<link rel="apple-touch-icon-precomposed" sizes="[[size]]" href="[[content]]">',
                   "apple-touch-icon":'<link rel="apple-touch-icon" href="[[content]]">',
                   "apple-touch-icon_size":'<link rel="apple-touch-icon" sizes="[[size]]" href="[[content]]">',
                   "shortcut_icon":'<link rel="shortcut icon" href="[[content]]">',
                   "shortcut_icon_type":'<link rel="shortcut icon" href="[[content]]" type="[[type]]">',
                   "apple-touch-startup-image":'<link rel="apple-touch-startup-image" href="[[content]]">',
                   "code":'[[content]]'
                   }

        if _metaTags['tag'] in nodeTag:
            self.treeHead.append(nodeTag[_metaTags['tag']].replace('[[content]]',_metaTags['content']).replace('[[size]]',_metaTags['size']).replace('[[type]]',_metaTags['type_content']))
        else:
            '''No existen ningun nodo que identifique su proceso'''
            self.treeHead.append(_metaTags)


    def gettreeHead(self):
        """Devuelve el dict que contiene los datos de Head"""
        return self.treeHead

    def tagBody(self,content=''):
        """Introduce en el objeto HTML5 la etiqueta <BODY> e inicializa su estructura"""

        self._text = content.strip()
        tokenBody = {}
        tokenBody = {"body":"<body [[content]]>"}
        self.treeBody.append(tokenBody["body"].replace('[[content]]',self._text))
        self._text = ''

    def addBody(self,*args,**kwargs):
        """Incorpora elementos a la estructura de <BODY> del objeto HTML5"""

        tokenBody = {}
        if args:
            for n in args:
                self.treeBody.append(n)
        if kwargs:
            for n,m in list(kwargs.items()):
                '''pendiente de gestionar'''

    def gettreeBody(self):
        """Devuelve el dict que contiene los datos de Body"""

        return self.treeBody

    def getHtml(self):
        """Recupera la información del objeto HTML5 en formato HTML"""

        try:
            self._text = ''
            for x in self.treeHtml:
                self._text += "%s\r" % x
            if len(self.treeHead)>0:
                for x in self.treeHead:
                    self._text += "%s\r" % x.replace('&#61;','=')
                if re.search(r'<head',self._text.replace(' ','')):
                    self._text += '</head>\r'
            if len(self.treeBody)>0:
                for x in self.treeBody:
                    self._text += "%s\r" % x
                if re.search(r'<body',self._text.replace(' ','')):
                    self._text += '</body>\r'
            if re.search(r'<html',self._text.replace(' ','')):
                    self._text += '</html>\r'
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en Html5.getHtml <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            if not self._text:
                self._text = "<!DOCTYPE HTML><html><body><div>NO EXISTE INFORMACION</div></body></html>"
            return self._text

    def gettreeHtml(self):
        """Devuelve el dict que contiene los datos de Html"""

        return self.treeHtml

    def escapeRegexp(string):
        '''Escape special characters'''

        specialCharacters = (".", "^", "$", "*", "+", "?", "{", "}",
                          "[", "]", "|", "(", ")", "-")
        for char in specialCharacters:
            string = string.replace(char, "\\" + char)
        return string

    def hexToInt(hex_str):
        '''Transforma en hexadecimal'''
        return int(hex_str, 16)

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("Html5.del ha eliminado el objeto")
        else:
            pass

#=== CLASS TABLE ===============================================================

TABLE_STYLE_THINBORDER = "border: 1px solid #000000; border-collapse: collapse;"

class Table (object):
    """Table crea tablas HTML5 (TABLE tag)

    Atributos:
    - rows: list, tuple or any iterable, containing one iterable or TableRow
            object for each row
    - header_row: list, tuple or any iterable, containing the header row (optional)
    - foot_row: list, tuple or any iterable, containing the header row (optional)
    - border: str or int, border width
    - caption: str, table title
    - style: str, table style in CSS syntax (thin black borders by default)
    - attribs: dict, additional attributes for the TABLE tag
    - col_styles: list or tuple of HTML styles for each column
    """

    #Tratamiento de errores en LOG

    def __init__(self, rows=None, border='1', caption=None, style=None, attribs=None, header_row=None, footer_row=None, col_styles=None):
        """TableCol constructor"""
        self.border = border
        self.caption = caption
        self.style = style
        # style for thin borders by default
        if style == None: self.style = TABLE_STYLE_THINBORDER
        self.header_row  = header_row
        if not header_row:self.header_row = []
        self.rows        = rows
        if not rows: self.rows = []
        self.attribs     = attribs
        if not attribs: self.attribs = {}
        self.col_styles  = col_styles
        self.footer_row  = footer_row
        if not footer_row: self.footer_row = []

    def __str__(self):
        """return the HTML code for the table as a string"""
        attribs_str = ""
        if self.border: self.attribs['border'] = self.border
        if self.style:  self.attribs['style'] = self.style
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = '<table%s>\n' % attribs_str
        if self.caption:
            result +='<caption>%s</caption>' % self.caption
        # insert column tags and attributes if specified:
        # First insert a header row if specified:
        if self.header_row:
            result +='<thead>'
            if not isinstance(self.header_row, TableRow):
                result += str(TableRow(self.header_row, header=True))
            else:
                result += str(self.header_row)
            result +='</thead>'
        # Then all data rows:
        if self.rows:
            result +='<tbody>'
            for row in self.rows:
                if not isinstance(row, TableRow):
                    row = TableRow(row)
                # apply column alignments  and styles to each row if specified:
                if self.col_styles and not row.col_styles:
                    row.col_styles = self.col_styles
                result += str(row)
            result +='</tbody>'
        # Last insert a footer row if specified:
        if self.footer_row:
            result +='<tfoot>'
            if not isinstance(self.footer_row, TableRow):
                result += str(TableRow(self.footer_row, footer=True))
            else:
                result += str(self.footer_row)
            result +='</tfoot>'
        result += '</table>'
        return result

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("Table.del ha eliminado el objeto")
        else:
            pass


class TableCol (object):
    """TableCol crea celdas en una tabla HTML (TD o TH)

    Atributos:
    - text: text in the cell (may contain HTML tags). May be any object which
            can be converted to a string using str().
    - header: bool, false for a normal data cell (TD), true for a header cell (TH)
    - style: str, CSS style
    - attribs: dict, additional attributes for the TD/TH tag
    """

    #Tratamiento de errores en LOG

    def __init__(self, text="", header=False, style=None, attribs=None):
        """TableCell constructor"""
        self.text    = text
        self.header  = header
        self.style   = style
        self.attribs = attribs
        if attribs==None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table cell as a string"""
        attribs_str = ""
        if self.style:   self.attribs['style']   = self.style
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.text:
            text = str(self.text)
        else:
            # An empty cell should at least contain a non-breaking space
            text = '&nbsp;'
        if self.header:
            return '  <TH%s>%s</TH>\n' % (attribs_str, text)
        else:
            return '  <TD%s>%s</TD>\n' % (attribs_str, text)

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("TableCol.del ha eliminado el objeto")
        else:
            pass

class TableRow (object):
    """TableRow crea filas en tablas HTML (TR tag)

    Atributos:
    - cells: list, tuple or any iterable, containing one string or TableCell
             object for each cell
    - header: bool, true for a header row (TH), false for a normal data row (TD)
    - footer: bool, true for a footer row (TH), false for a normal data row (TD)
    - attribs: dict, additional attributes for the TR tag
    - col_styles: dict, additional attributes for the TR tag
    """


    def __init__(self, cells=None, header=False, footer=False, attribs=None, col_styles=None):
        """TableCol constructor"""
        self.cells       = cells
        self.header      = header
        self.footer      = footer
        self.col_styles  = col_styles
        self.attribs     = attribs
        if attribs==None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table row as a string"""
        attribs_str = ""
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = ' <TR%s>\n' % attribs_str
        for cell in self.cells:
            col = self.cells.index(cell)    # cell column index
            if not isinstance(cell, TableCol):
                cell = TableCol(cell, header=self.header)
            # apply column style if specified:
            if self.col_styles and cell.style==None:
                cell.style = self.col_styles[col]
            result += str(cell)
        result += ' </TR>\n'
        return result

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("TableRow.del ha eliminado el objeto")
        else:
            pass

#=== CLASS LIST  ===============================================================

class List (object):
    """List crea listas ordenadas o no ordeandas en HTML5 (UL/OL tag)

    Atributos:
    - lines: list, tuple or any iterable, containing one string for each line
    - ordered: bool, choice between an ordered (OL) or unordered list (UL)
    - attribs: dict, additional attributes for the OL/UL tag
    """

    def __init__(self, lines=None, ordered=False, start=None, attribs=None):
        """List constructor"""
        if lines:
            self.lines = lines
        else:
            self.lines = []
        self.ordered = ordered
        self.start = start
        if attribs:
            self.attribs = attribs
        else:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the list as a string"""
        attribs_str = ""
        if self.start:  self.attribs['start'] = self.start
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.ordered: tag = 'OL'
        else:            tag = 'UL'
        result = '<%s%s>\n' % (tag, attribs_str)
        for line in self.lines:
            result += ' <LI>%s\n' % str(line)
        result += '</%s>\n' % tag
        return result

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("List.del ha eliminado el objeto")
        else:
            pass

#=== CLASS FORM  ===============================================================

class Form(object):
    """Form crea un formulario en HTML5

    Atributos:
    - legend : titulo del formulario
    - id : identifica el formulario (id, name)
    - method : tipo de envio de datos (get, post)
    - action : direccion de envio de los datos
    - events : dict, eventos
    - attribs: dict, atributos adicionales
    - inputs: list of dicts, etiquetas de entrada de datos
    Ejemplo:
       <form method="post" name=f enctype="multipart/form-data onsubmit="return check(); "
       action="http://www.cs.tut.fi/cgi-bin/run/~jkorpela/echo.cgi">
       Eventos posibles	onReset(), onSubmit()
       inputs = ({'type':'text','id':'nombre'},{'type':'number','id':'edad'})
    """

    def __init__(self, legend=None, id=None, method='get', action=None, events=None, attribs=None, inputs=None):
        """Form constructor"""
        try:
            self.legend = legend
            self.id    = id
            self.method  = method
            self.action   = action
            self.events = events
            if not events: self.events = {}
            self.attribs     = attribs
            if not attribs: self.attribs = {}
            self.inputs     = inputs
            if not inputs: self.inputs = list()
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en Form.__init__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))

    def __str__(self):
        """Vincula objetos INPUT a un objeto FORM"""
        try:
            attribs_str = ""
            if self.id: self.attribs['id'] = self.id
            if self.id: self.attribs['name'] = self.id
            if self.method:  self.attribs['method'] = self.method
            if self.action:  self.attribs['action'] = self.action
            for event in self.events:
                attribs_str += ' %s="%s"' % (event, self.events[event])
            for attr in self.attribs:
                attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
            result = '<form %s>\n' % attribs_str
            if self.legend:
                # Enmarca el formulario con un titulo
                result += '<fieldset><legend>%s</legend>' % self.legend
            if self.inputs:
                # Obtiene la estructura de inputs a incluir en el form
                result += str(Input(self.inputs))
            if self.legend:
                # cierra el marco del formulario
                result += '</fieldset>'

        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en Form.__str__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            result += '</form>'
            return result

    def getForm(self):
        """Recupera la información del objeto FORM en formato HTML"""
        try:
            while self._stack:
                self._text += self._stack.pop()
            return self._text
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en Form.getForm <%s> in line %s !!!' % (repr(e),tb.tb_lineno))

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("Form.del ha eliminado el objeto")
        else:
            pass


'''pattern
   Ipv4              type="text" pattern="\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
   precio con punto  type="text" pattern="\d+(\.\d{2})?"
   precio con coma   type="text" pattern="\d+(\,\d{2})?"
   latitud/longitud  type="text" pattern="-?\d{1,3}\.\d+"
   alfanumerico      type="text" pattern="[a-zA-Z0-9]+"
   username 2-20 car type="text" pattern="^[a-zA-Z][a-zA-Z0-9-_\]{1.20}$"
   password alfanum. type="text" pattern="^(?=.*\d)(?=.*[a-Z])(?=.*[A-Z])(?!.*\s).*$"
   spanish postal-code  type="text" pattern="((0[1-9]|5[0-2])|[1-4][0-9])[0-9]{3}
   01xxx a 50xxx
   entero con o sin decimales
                     type="text" pattern="\-?\d+(\.\d{0,})?"
'''

#=== CLASS INPUT  ===============================================================

def input(*args,**kw_args):
    """Crea objetos INPUT que pueden incorporarse a objetos FORM y a objetos HTML"""

    """
       @parameters
       @ css       incorpora caracteristicas de Hojas de Estilo en Cascada como class='etiqueta',id='mini',...etc. Se incluye informacion de forma literal
       @ type      text, number, date, time, email, tel, url, range, datalist, search, password, checkbox, radio, file, submit, reset, image, hidden, textarea
       @ label     incorpora el titulo o etiqueta visible del input
       @ id        denominacion e identificacion del input, los datos se podran direccionar desde javascript
       @ name      tiene el mismo tratamiento que id, aunque se emplea por compatibilidad con navegadores que no soporten 'id'
       @ autofocus por defecto a 'False', permite dirigir el cursor al input que sea 'True'
       @ autocomplete = Off
       @ required = False valor booleano que nos indica que es una informacion obligatoria
       @ placeholder texto que sirve de informacion o guia al usuario y desaparece al pulsar dentro del campo
       @ size      cuantos caracteres se veran
       @ maxlength cuantos caracteres admite el campo
       @ min       min="0"   min="2011-01-01"
       @ max       max="1"   max="2015-12-31"
       @ cols      cols"0"   atributo de textarea
       @ rows      rows="1"  atributo de textarea
       @ value     valor del campo
       @ checked   permitido en inputs tipo checkbox y radio, por defecto su valor es 'False' sin marcar y 'True' marcado
       @ step      solo hh:mm, step="10" hh:mm:ss, y con step="any" hh:mm:ss.sss
       @ align     alineacion del contenido TOP, MIDDLE, BOTTOM, RIGHT, LEFT, TEXTTOP, BASELINE, ABSMIDDLE, ABSBOTTOM
       @ tabindex  orden de campos que seguira el cursor al pulsar tecla TAB
       @ pattern   expresion regular que se puede incorporar para validar entradas de datos

       @return
       string


    """
    try:
        acceptable_form_elements= {"text":None,"textarea":None,"number":None,"date":None,"time":None,"email":None,"tel":None,"url":None,"range":None,"datalist":None,"search":None,"password":None,"select":None,"datalist":None,"checkbox":None,"radio":None,"file":None,"submit":None,"reset":None,"button":None,"image":None,"hidden":None}
        """cargar plantilla de cada elemento"""
        #acceptable_form_elements["number"] = "\-?\d+(\,\d{0,})?"
        acceptable_form_elements["number"] = "\-?[0-9]+([\.|,][0-9]+)?"
        """DD/MM/YYYY"""
        acceptable_form_elements["date"] = "(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d"
        acceptable_form_elements["email"] = "[*@-.-|*@*]"
        acceptable_form_elements["tel"] = "[0-9]{9}"
        acceptable_form_elements["url"] = "https?://.+"
        acceptable_form_elements["password"] = "^(?=.*\d)(?=.*[a-Z])(?=.*[A-Z])(?!.*).*$"
        """          """
        if len(args)>0:
            inputs = args
        elif len(kw_args)>0:
            inputs = kw_args
        else:
            inputs = list()

        input_str=""

        # buscamos en el contenido de cada diccionario
        if isinstance(inputs,(dict,)):
            if inputs.get('type',None):
                # preparar id y name
                if inputs.get('id',None):
                    inputs['name'] = inputs['id'] if inputs.get('id',None) else None;
                elif inputs.get('name',None):
                    inputs['id'] = inputs['name'] if inputs.get('name',None) else None;

                if inputs.get("type").lower()!="checkbox" and inputs.get("type").lower()!="radio":
                    if inputs.get('label',None) and inputs.get('id',None):
                        # comprobar atributos de label
                        attribs = ''
                        if inputs.get('attribs_label',None):
                            for n in list(inputs['attribs_label'].keys()):
                                attribs += ' %s="%s" ' % (n,inputs['attribs_label'][n])
                        # label asociada a un input
                        input_str += ('<label for=%s %s >%s</label>' % (inputs["id"],attribs, inputs["label"]))
                if inputs.get("type").lower()!='textarea' and inputs.get("type").lower()!='select' and inputs.get("type").lower()!='datalist':
                    if inputs.get('id',None):
                        input_str += ('<input type="%s" id="%s" name="%s" ' % (inputs.get("type"),inputs.get("id"),inputs.get("id")))
                else:
                    input_str += ('<%s ' % inputs.get("type"))

                if inputs.get("css",None):
                    input_str += inputs['css']
                # comprobar atributos de input
                if inputs.get('attribs_input',None):
                    attribs = ''
                    for n in list(inputs['attribs_input'].keys()):
                        attribs += ' %s="%s" ' % (n,inputs['attribs_input'][n])
                    input_str += (' %s' % attribs)
                if inputs.get('autofocus',None):
                    input_str += (' %s' % "autofocus")
                if inputs.get('autocomplete',None):
                    input_str += (' autocomplete="%s" ' % (inputs["autocomplete"]))
                if inputs.get('required',None):
                    input_str += (' %s' % "required")
                if inputs.get('placeholder',None):
                    input_str += (' placeholder="%s" ' % (inputs["placeholder"]))
                if inputs.get('size',None):
                    input_str += (' size=%s ' % (inputs["size"]))
                if inputs.get('maxlength',None):
                    input_str += (' maxlength="%s" ' % (inputs["maxlength"]))
                if inputs.get('align',None):
                    """align=left|right|middle|top|bottom"""
                    input_str += (' align="%s" ' % (inputs["align"]))
                elif inputs.get('type').lower() == 'number':
                    # alinear a la derecha para numeros
                    input_str += (' style="text-align: right;" ')
                if inputs.get('tabindex',None):
                    input_str += (' tabindex="%s" ' % (inputs["tabindex"]))
                if inputs.get('list',None):
                    input_str += (' list="%s" ' % (inputs["list"]))
                if inputs.get('disabled',None):
                    input_str += (' %s' % 'disabled')
                if inputs.get('multiple',None):
                    # Se podran seleccionar o incorporar varios datos SELECT, FILE, EMAIL, IMAGE
                    input_str += (' %s ' % 'multiple')
                if inputs.get('readonly',None):
                    input_str += (' %s' % 'readonly')
                if inputs.get('formnovalidate',None):
                    input_str += (' %s' % 'formnovalidate')


                if inputs.get("type",None).lower() == "number" or inputs.get("type",None).lower() == "date" or inputs.get("type",None).lower() == "range":
                    """ number, date y range """
                    if inputs.get('value',None):
                        input_str += (' value="%s"' % (inputs["value"]))
                    if inputs.get('min',None):
                        input_str += (' min="%s"' % (inputs["min"]))
                    if inputs.get('max',None):
                        input_str += (' max="%s"' % (inputs["max"]))
                    if inputs.get('step',None):
                        input_str += (' step="%s"' % (inputs["step"]))
                    elif inputs.get('type',None).lower() == 'number':
                        input_str += (' step="any"')

                elif inputs.get("type",None).lower() == "checkbox" or inputs.get("type",None).lower() == "radio":
                    """ chekbox y radio """
                    if inputs.get('checked',None):
                        input_str += (' checked="%s"' % "checked")
                    if inputs.get('value',None):
                        input_str += (' value="%s"' % (inputs["value"]))

                elif inputs.get("type",None).lower() == "file":
                    """ file """
                    if inputs.get('accept',None):
                        input_str += (' accept="%s" ' % (inputs["accept"]))
                    if inputs.get('value',None):
                        input_str += (' value="%s"' % (inputs["value"]))

                elif inputs.get("type",None).lower() == "image":
                    """ imagen """
                    if inputs.get('src',None):
                        input_str += (' src="%s" ' % (inputs["src"]))
                    if inputs.get('width',None):
                        input_str += (' width="%s" ' % (inputs["width"]))
                    if inputs.get('height',None):
                        input_str += (' height="%s" ' % (inputs["height"]))
                    if inputs.get('alt',None):
                        input_str += (' alt="%s" ' % (inputs["alt"]))

                elif inputs.get("type",None).lower() == "textarea":
                    """ textarea """
                    if inputs.get('value',None):
                        input_str += (' value="%s"' % (inputs["value"]))
                    if inputs.get('rows',None):
                        input_str += (' rows=%s ' % (inputs["rows"]))
                    if inputs.get('cols',None):
                        input_str += (' cols=%s ' % (inputs["cols"]))

                elif inputs.get("type",None).lower() == "select":
                    """ select

                        @parameters
                        name, id, size, multiple, css, option

                        option <dict> donde los valores del <dict> pueden ser string
                            option {'option_label...': 'value|selected',
                        resultando:
                            <option value="...">...</option>

                        si usa un select con agrupaciones por titulo <optgroup> el <dict> inicial se compone de <dict>
                            option {'optgroup_label...':{'option_label...':'value|selected' o 'value'},
                        resultando:
                        <optiongroup label="...">
                            <option value="...">...</option>
                    """
                    if inputs.get('option',None):
                        # Cerrar etiqueta select
                        input_str += ">"
                        # incorporar opciones seleccionables ordenadas por clave
                        k = list(inputs['option'].keys())
                        k.sort()
                        for n in k:
                            if isinstance(inputs['option'][n],(str,)):
                                if re.search(r'\|selected',inputs['option'][n]):
                                    # Si es la opcion seleccionada por defecto
                                    input_str += ('<option value="%s" selected >%s</option>' % (n,inputs['option'][n].replace('|selected','')))
                                else:
                                    input_str += ('<option value="%s">%s</option>' % (n,inputs['option'][n]))
                            elif isinstance(inputs['option'][n],(dict,)):
                                input_str += '<optgroup label="%s">' % n
                                kk = list(inputs['option'][n].keys())
                                kk.sort()
                                for m in kk:
                                    if isinstance(inputs['option'][n][m],(str,)):
                                        if re.search(r'\|selected',inputs['option'][n][m]):
                                            # Si es la opcion seleccionada por defecto
                                            input_str += ('<option value="%s" selected >%s</option>' % (m,inputs['option'][n][m].replace('|selected','')))
                                        else:
                                            input_str += ('<option value="%s">%s</option>' % (m,inputs['option'][n][m]))
                                input_str += '</optgroup>'
                    """ atributos exclusivo para select """
                elif inputs.get("type",None).lower() == "datalist":
                    if inputs.get('value',None):
                        input_str += (' value="%s"' % (inputs["value"]))
                    if inputs.get('size',None):
                        # Elementos de la lista que se podran ver
                        input_str += (' size=%s ' % (inputs["size"]))
                    if inputs.get('option',None):
                        # Cerrar etiqueta datalist
                        input_str += ">"
                        for n in list(inputs['option'].keys()):
                            # incorporar opciones seleccionables
                            input_str += ('<option value="%s" label="%s">' % (n,inputs['option'][n]))
                    """ atributos exclusivo para submit """
                elif inputs.get("type",None).lower() == "submit":
                    if inputs.get('formaction',None):
                        input_str += (' formaction="%s"' % (inputs["formaction"]))
                    if inputs.get('formenctype',None):
                        # Elementos de la lista que se podran ver
                        input_str += (' formenctype="%s" ' % (inputs["formenctype"]))
                    if inputs.get('formmethod',None):
                        input_str += (' formmethod="%s" ' % (inputs["formmethod"]))
                    """ atributos para el resto """
                else:
                    if inputs.get('value',None):
                        input_str += (' value="%s"' % (inputs["value"]))
                """                        """
                if inputs.get('pattern',None):
                    input_str += (' pattern="%s" ' % (inputs["pattern"]))
                elif acceptable_form_elements[inputs["type"]] is not None:
                    input_str += (' pattern="%s" ' % acceptable_form_elements[inputs["type"]])



                if inputs.get("type",None).lower() == "textarea":
                    # final de etiqueta textarea
                    input_str += ('></textarea>')

                elif inputs.get("type",None).lower() == "select":
                    # final de etiqueta select
                    input_str += ('</select>')

                elif inputs.get("type",None).lower() == "datalist":
                    # final de etiqueta datalist
                    input_str += ('</datalist>')
                else:
                    # final para las restantes etiquetas
                    input_str += ('/>')

                if inputs.get("type",None).lower() == "checkbox" or inputs.get("type",None).lower() == "radio":
                    if inputs.get('label',None) and (inputs.get('id',None) or inputs.get('name',None)):
                        input_str += ('<label for=%s>%s</label>' % (inputs["id"],inputs["label"]))
            else:
                # comprobar atributos de label
                attribs = ''
                if inputs.get('attribs_label',None):
                    for n in list(inputs['attribs_label'].keys()):
                        attribs += ' %s="%s" ' % (n,inputs['attribs_label'][n])
                # label independiente
                input_str += ('<label %s >%s</label>' % (attribs,inputs["label"]))
            if inputs.get('br',None):
                input_str += ('%s' % '<br>\r')
        return input_str
    except Exception as e:
        tb = sys.exc_info()[2]
        LOG.error('Error en Input.__str__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))

"""

Ejemplos :
    <input name="lat" type="number" min="-90.000000" max="90.000000" step="0.000001">
    <input name="lon" type="number" min="-180.000000" max="180.000000" step="0.000001">

"""


class formData(object):
    '''Tratamiento de valores de un Form como un diccionario'''

    _formData = {}

    def __init__(self, stringForm):
        '''dataForm recibe un parametro cadena como test1=cualquier
        +dato&test2=otro+dato+mas y debe separarlo, asignando valores a datos'''
        listForm = ''
        if len(stringForm) > 0:
            listForm = stringForm.split('&')   # separar los datos por &
            for x in listForm:
                y = x.split('=')               # separar los datos por =
                # datos:valor en diccionario  dataForm['text1]='cualquier dato'
                # Cambiar caracteres especiales por reales
                self._formData[y[0]]=y[1].replace("+"," ")  # eliminar caracter +
            self.sanitize_value()  # eliminar caracteres no permitidos

    def sanitize_value(self):
        '''sanitize_value eliminara todos los caracteres no permitidos y que podrian
	    causar algun error en la evaluacion de cadenas'''
        valid_chars = "?!-_.,()" % (string.ascii_letters, string.digits, string.whitespace)
        special_chars = ''
        for dato,valor in list(self._formData.items()):
            if len(valor)>0:
                self._formData[dato]="".join([x for x in valor if x in valid_chars])
            else:
                pass


    def get(self):
        '''get devuelve el diccionario con tuplas dato:valor tratados'''
        return self._formData

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("formData.del ha eliminado el objeto")
        else:
            pass

#=== CLASS HTML TEMPLATE========================================================

class htmlTemplate(object):
    """Tratamiento de templates para generar paginas html"""

    """
    Convenciones para ficheros con extension .tpl
    Los comandos de control que se indican a continuacion deben comenzar in lines separadas.
    Comentarios       <!-- Esto es un comentario --> los comentarios no se insertan en el fichero resultado
    Iniciar un bloque {%block body%}  cerrar un bloque  {%endblock body%}
    Bloques posibles                  html,head,body,footer,article,section,aside,form,header,hgroup,table,nav
    Iniciar y cerrar funciones {%for i in ies%}  {%if i%} {%else%} {%endif%} {%endfor%}
    Variables o funciones  {{fecha_del_dia}} o {{dia_semana()}}  sin espacios
    Insertar informacion de forma exacta   {%literal%}  {%endliteral%}
    Incluir una plantilla externa {%include fichero_template.tpl%}   Se procesa sobrecargando la clase
    Incluir datos de un fichero externo de forma literal {%merge fichero_externo.txt%} los datos se importan
    tal cual, igual que si la informacion fuera insertada entre las etiquetas {%literal%}...{%endliteral%}
    Todo dato que se introduzca entre < y > se comprobara como elemento HTML valido y se insertara en el codigo
    Condiciones posibles
         {% if condicion %}
          ...
         {% else %}
          ...
         {% endif %}


         {% if not condicion %}
         ...
         {% endif %}

     Bucles posibles
          {% for valor in lista_valores %}
          ...
          {% endfor %}

    Como insertar valores en el fichero resultado :
    **kwargs es un parametro opcional, que puede contener un diccionario, con una estructura clave:valor, la clave
    se buscara dentro del codigo como una variable {{variable}} y ser sustituida por el valor.
    """

    #Declaracion de variables universales de clase
    UNJOIN = '|'
    _stack = []
    _tpl = None
    _deep = 0

    def __init__(self,template_file):
        # Es posible que la clase deba interpretar diversas plantillas de forma recursiva a partir de la plantilla principal,
        # la profundidad de plantillas llamadas desde la plantilla principal se mide con _deep
        # Si _deep=1 el proceso estará interpretando la plantilla principal.
        htmlTemplate._deep += 1
        # comprobacion de profundidad recursiva
        if DEBUG:
            LOG.debug('__init__ _deep <%s> !!!' % (str(htmlTemplate._deep)))
        #
        self._tpl_form = ''
        self._tpl_html = ''
        self.parseHtml(template_file)

    def parseHtml(self,template_file):
        # Interpreta el fichero .tpl

        _file = ''
        linea = ''
        f1 = ''
        _elements = list()
        try:

            _file = self.__system__(template_file).lower()


            if _file and _file[-3:]=='tpl' and os.path.isfile(_file):
                with open(_file, mode='r', encoding='utf-8') as f1:
                # Inicializar objeto html5

                    while True:
                        #Procesar plantilla
                        #Eliminar lineas de comentario <!-- ... -->
                        _ll = f1.readline()
                        while re.search(r'<!--.*?-->\n',_ll):
                            _ll = re.sub(r'<!--.*?-->\n','',_ll)
                            if not _ll or len(_ll)==0:
                                _ll = f1.readline()
                        linea += ' '+_ll
                        #linea += ' '+f1.readline()
                        #Pueden aparecer en la línea Byte Order Mark o marca en little-endian \xEF\xBB\xBF que debemos eliminar
                        linea = linea.replace('\xef\xbb\xbf','')
                        linea = linea.strip()
                        if not linea:
                            #No existen datos y finaliza el proceso
                            break


                        if not re.search(r'^{%literal%}',linea.replace(' ','')):
                            #Buscar etiqueta html
                            if re.search(r'^{%blockhtml',linea.replace(' ','')):
                                htmlTemplate._tpl = Html5()
                                if linea.find(self.UNJOIN)>-1:
                                    linea = linea[linea.find(self.UNJOIN)+1:].replace('{%','').replace('%}','')
                                    htmlTemplate._tpl.tagHtml(linea)
                                else:
                                    htmlTemplate._tpl.tagHtml()
                                linea = ''
                                htmlTemplate._stack.append('html')

                                #Buscar comentarios  <!-- ... -->
                            elif re.search('^<!--',linea) and re.search('-->$',linea.replace(' ','')):
                                #Se eliminan los comentarios para producir un codigo más compacto
                                linea = ''
                                linea += ' '+f1.readline()
                                linea = linea.strip()
                                if linea.__len__()==0:
                                    break

                                """Buscar bloques {%block ....%} y cierre de bloques  {%endblock ...%}
                                los bloques posibles son html, head, body, footer, article, section,
                                aside, form, header, hgroup, table, nav """
                            elif re.search(r'^{%block',linea.replace(' ','')):
                                #Extrae la informacion de bloque
                                self.__block__(linea)
                                linea = ''

                            elif re.search(r'^{%endblock',linea.replace(' ','')):
                                #Extrae la informacion de fin de bloque
                                self.__block__(linea)
                                linea = ''

                            elif re.search(r'^{%if',linea.replace(' ','')) or re.search(r'^{%else',linea.replace(' ','')) or re.search('^{%for',linea.replace(' ','')):
                                #Comprobar comandos if, else y for
                                self.__loop__(linea)
                                linea = ''

                            elif re.search(r'^{%endif',linea.replace(' ','')) or re.search(r'^{%endfor',linea.replace(' ','')):
                                #Comprobar comandos endif y endfor
                                self.__loop__(linea)
                                linea = ''

                                #Buscar importacion de plantillas externas {%include fichero_template.tpl%}
                            elif re.search(r'^{%include',linea.replace(' ','')) and re.search(r'%}$',linea.replace(' ','')):
                                linea = self.__include__(linea)

                                #Buscar importar fichero externo {%merge fichero_externo.txt%} literalmente
                            elif re.search(r'^{%merge',linea.replace(' ','')) and re.search(r'%}$',linea.replace(' ','')):
                                linea = self.__merge__(linea)

                                #Buscar comandos <% .... %>
                            elif re.search(r'^<%',linea.replace(' ','')) and re.search(r'%>$',linea.replace(' ','')):
                                self.__command__(linea)
                                linea = ''

                                #Buscar etiquetas html < >...</ >
                                """ La primera línea que solo contenga etiquetas html debe comenzar con < y la ultima linea debe finalizar con </
                                Las restantes lineas contenidas pueden contener etiquetas html o no.
                                Las etiquetas html con autocierre no se consideran para el proceso """
                            elif re.search(r'^<\w+',linea.replace(' ','')) or re.search(r'^</\w+',linea.replace(' ','')) or re.search(r'</\w+>$',linea.replace(' ','')) or len(_elements)>0:
                                l = re.findall(r'(<\w+|<\w+\s|</\w+)',linea)
                                for i in l:
                                    i= re.sub(r'^<', r'', i)
                                    if i in acceptable_body_elements and i not in self_closing_tag:
                                        #Si es una etiqueta html de apertura, se guardara hasta comprobar la etiqueta html de cierre
                                        _elements.append(i)
                                    else:
                                        i= re.sub(r'^/',r'',i)
                                        if i in acceptable_body_elements and i not in self_closing_tag and len(_elements)>0:
                                            if i == _elements[len(_elements)-1]:
                                                #Se comprueba etiqueta html de cierre y se elimina de la pila, la etiqueta html de apertura
                                                _elements.pop()
                                        else:
                                            if i in self_closing_tag:
                                                #Es una etiqueta html de autocierre y no se considera para su tratamiento
                                                pass
                                linea = '{%literal%}'+linea+'{%endliteral%}'

                        #Buscar informacion literal {%literal%} ... {%endliteral%}
                        if (re.search(r'^{%literal%}',linea.replace(' ','')) and re.search(r'{%endliteral%}$',linea.replace(' ',''))):
                            self.__literal__(linea)
                            linea = ''
                f1.close()
            else:
                #No existe fichero de plantilla
                htmlTemplate._tpl = Html5()
                htmlTemplate._tpl.tagHtml()
                self.__block__('{%block html|lang="es"%}')
                self.__block__('{%block head%}')
                self.__block__('{%block body%}')
                if _file:
                    linea = 'NO EXISTE %s' % _file
                else:
                    linea = 'NO EXISTEN DATOS'
                self.__literal__('{%literal%}<div>'+linea+'</div>{%endliteral%}')
                self.__block__('{%block footer%}')
                self.__block__('{%endblock footer%}')
                self.__block__('{%endblock body%}')
                self.__block__(linea)

        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.parseHtml <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            if _file and os.path.isfile(_file):
                f1.close()


    def get(self):

        _vars_ = []
        _tpl_html_copy_ = ''
        try:
            if not self._tpl_html:
                self._tpl_html = htmlTemplate._tpl.getHtml()
                _tpl_html_copy_ = self._tpl_html
            else:
                _tpl_html_copy_ = self._tpl_html
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Template -> Error en htmlTemplate.get <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            #Solo finaliza de procesar el codigo html si _deep<=1 o procesando la plantilla principal
            if htmlTemplate._deep<=1:
                htmlTemplate._stack = []
                htmlTemplate._tpl = ''
                htmlTemplate._deep = 0
                # _tpl_html_copy_ += '</html>'
            return _tpl_html_copy_

    def __block__(self, linea):

        _text = ''
        _tag = ''
        try:
            if re.search('^{%block',linea.replace(' ','')):
                if re.search('^{%blockhead%}',linea.replace(' ','')):
                    htmlTemplate._tpl.tagHead()
                    htmlTemplate._stack.append('head')
                elif re.search('^{%blockbody',linea.replace(' ','')):
                    if linea.find(self.UNJOIN)>-1:
                        htmlTemplate._tpl.tagBody(linea[linea.find(self.UNJOIN)+1:].replace('{%','').replace('%}',''))
                    else:
                        htmlTemplate._tpl.tagBody()
                    htmlTemplate._stack.append('body')
                else:
                    _tag = linea[7:linea.find('%}')].strip()
                    if linea.find(self.UNJOIN)>-1:
                        _tag = _tag[:_tag.find(self.UNJOIN)].replace(' ','')
                        _text = linea[linea.find(self.UNJOIN)+1:].replace('{%','').replace('%}','')
                        # incorpora a etiquetas block distintas de html, head, body y form, los atributos recibidos
                        _tag = ' '.join((_tag,_text))
                    else:
                        _text = ''
                    _tag = _tag.lower()
                    _text_list = []
                    _text_dict = {}
                    if len(htmlTemplate._stack)>0:
                        if htmlTemplate._stack[-1]=='body':
                            htmlTemplate._stack.append(_tag)
                            if htmlTemplate._stack[-1]=='form':
                                self._tpl_form = Form(_text)
                            else:
                                #Apertura de etiquetas block diferentes a html,head,body y form
                                _text_list.append('<%s>' % _tag)
                                htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
            if re.search('^{%endblock',linea.replace(' ','')):
                if re.search('{%endblockhead%}$',linea.replace(' ','')):
                    if len(htmlTemplate._stack)>0:
                        if htmlTemplate._stack[-1] == 'head':
                            htmlTemplate._stack.pop()
                elif re.search('{%endblockbody%}$',linea.replace(' ','')):
                    if len(htmlTemplate._stack)>0:
                        if htmlTemplate._stack[-1] == 'body':
                            htmlTemplate._stack.pop()
                else:
                    if len(htmlTemplate._stack)>0:
                        _text_list = []
                        _text_dict = {}
                        if htmlTemplate._stack[-1] == linea.replace(' ','')[10:linea.replace(' ','').find('%}')]:
                            _tag = linea.replace(' ','')[10:linea.replace(' ','').find('%}')].lower()
                            if htmlTemplate._stack[-1]=='form' and _tag=='form':
                                #Crear lista de valores para incluir en Form
                                _text_list = []
                                _text_list.append(self._tpl_form.getForm())
                                htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
                            else:
                                _text_list.append('</%s>' % _tag)
                                htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
                            htmlTemplate._stack.pop()
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__block__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            pass

    def __loop__(self, linea):

        _tag = None
        _rslt = None
        try:
            if re.search('^{%if',linea.replace(' ','')):
                _text = u(linea.replace('{%','').replace('%}',':\n\r').strip())
                _text_tab += 4
            elif re.search('^{%for',linea.replace(' ','')):
                _text = u(linea.replace('{%','').replace('%}',':\n\r').strip())
                _text_tab += 4
            elif re.search('^{%else',linea.replace(' ','')):
                _text +='else:\n'
            elif re.search('^{%endif',linea.replace(' ','')):
                _text_tab -= 4
                if len(_text)>0:
                    _tag = compile(_text,'','exec')
                    exec(_tag)
                    htmlTemplate._tpl = _rslt
                    _text = None
                    _text_tab = 0
            elif re.search('^{%endfor',linea.replace(' ','')):
                _text_tab -= 4
                if len(_text)>0:
                    _tag = compile(_text,'','exec')
                    exec(_tag)
                    htmlTemplate._tpl = _rslt
                    _text = None
                    _text_tab = 0
            else:
                _text += '_rslt += "'+' '*_text_tab+linea.strip()+'\n"'

        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__loop__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            pass


    def __merge__(self,linea):

        _text = '{%literal%}'
        _file = ''
        try:
            if re.search('^{%merge',linea.replace(' ','')):
                #Carga fichero sin tratar contenido, como literal
                _file = self.__system__(linea.replace(' ','')[7:linea.find('%}')-1].strip())
                if os.path.isfile(_file):
                    with open(_file,mode="r", encoding='utf-8') as f2:
                        _linea2 = f2.readline()
                        _text += _linea2
                        while True:
                            _linea2 = f2.readline()
                            _text += _linea2
                            if _linea2 == "":
                                break
                        f2.close()
                        _linea2 = ''
                    f2.close()
                else:
                    _text += '<div>NO EXISTE %s</div>' % _file

        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__merge__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            _text += '{%endliteral%}'
            return _text


    def __include__(self,linea):

        _tpl_include = ''
        _file = ''
        _text = ''
        try:
            if re.search('^{%include',linea.replace(' ','')):
                _file = self.__system__(linea.replace(' ','')[9:linea.find('%}')-1].strip())
                if DEBUG:
                    LOG.debug('__include__ _file <%s> !!!' % (_file,))

                if _file and _file[-3:].lower()=='tpl':
                    if os.path.isfile(_file):
                        _tpl_include = htmlTemplate(_file)
                        '''_text = _tpl_include.get()'''
                        htmlTemplate._deep -= 1
                    else:
                        #No encuentra el fichero de carga
                        _text += '<div>NO EXISTE %s</div>' % _file
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__include__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            if len(_text)>0:
                return ''.join(['{%literal%}', _text,'{%endliteral%}'])
            else:
                return ''

    def __literal__(self,linea):

        _text = ''
        try:
            _text += linea
            _text = _text.replace('{%literal%}','').replace('{%endliteral%}','')
            _text_dict = {}
            _text_list = []
            if len(htmlTemplate._stack)>0:
                if htmlTemplate._stack[-1] == 'head':
                    #Crear lista de valores, precedidos por 'code' para Head
                    _text_list.append('code')
                    _text_list.append(_text)
                    htmlTemplate._tpl.addHead(*_text_list,**_text_dict)
                elif htmlTemplate._stack[-1] == 'form':
                    #Crear lista de valores para Form
                    htmlTemplate._tpl.addForm(*_text_list,**_text_dict)
                else:
                    #Crear lista de valores para Body, por defecto
                    _text_list.append(_text)
                    htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
            else:
                #Por defecto, crea lista de valores para Body
                _text_list.append(_text)
                #Si no es una plantilla completa html, se inicializa el objeto HTML5
                if type(htmlTemplate._tpl).__name__ != "Html5":
                    htmlTemplate._tpl = Html5()
                htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
                _text = ''
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__literal__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            pass


    def __command__(self, linea):

        _text = ''
        try:
            #Cargar contenido tratado con parametros
            _text = linea
            _text_split = _text.replace('<%','').replace('%>','').split(self.UNJOIN)
            _text_dict = {}
            _text_list = []
            for n in _text_split:
                n = n.strip()
                pos_x = n.find('=')
                if pos_x > -1:
                    #Crear un diccionario con valores con clave
                    _text_dict[n[0:pos_x]]=n[pos_x+1:].replace('"','')
                else:
                    #Crear una lista con valores sin clave
                    _text_list.append(n)
            if len(htmlTemplate._stack)>0:
                if htmlTemplate._stack[-1] == 'head':
                    htmlTemplate._tpl.addHead(*_text_list,**_text_dict)
                elif htmlTemplate._stack[-1] == 'form':
                    self._tpl_form.addForm(*_text_list,**_text_dict)
                else:
                    htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
            else:
                #Por defecto, crea lista de valores para Body
                _text_list.append(_text)
                htmlTemplate._tpl.addBody(*_text_list,**_text_dict)
                _text = ''
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__command__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))

    def setData(self,data=None):
        '''A partir de un diccionario, sustituira las claves por valores
        las claves a sustituir se encuentran entre {{ y }}. La modificacion
        se produce en una copia de la plantilla, por tanto, la plantilla no
        se ve afectada por los cambios.
        Las claves no sustituidas se modificaran a un espacio
        '''

        try:
            __strLeft = "{{"
            __strRight = "}}"
            __strClear = ""
            tplData = self.get()
            if type(data).__name__!='dict':
                data = dict()
            for n in list(data.keys()):
                data[n] = data[n]
                if DEBUG:
                    LOG.debug('data %s %s' % (data[n],type(data[n])))
                tplData = tplData.replace('%s%s%s' % (__strLeft,n,__strRight),"%s" % data[n])
            tplData = re.sub("\{{2}[\w]+\}{2}",__strClear,tplData)
            # compresor de todo el contenido HTML
            '''
            tplData = re.sub('<!--(.*?)-->','',tplData)                 # eliminar comentarios html <!--
            tplData = re.sub('\/\*(.*?)\*\/','',tplData)                # eliminar comentarios javascript multilinea /*
            '''
            if HTML_COMPRESS:
                tplData = re.sub('>\s<','><',re.sub('\s\s+','\s',tplData))   # varios espacios o espacios entre > <
                tplData = re.sub('"\s+/>','"/>',tplData)                     # espacios entre " />
                no_space = [['\n',''],['\r',''],['=\s','='],['\s=','='],[':\s',':'],['\s:',':'],[';\s',';'],['\s;',';'],['/\*(.*?)\*/',''],['"\s>','">'],["'\s<","'<"],['\s/>','/>']]
                # ['/\*(.*?)\*/',''],['\)[\s]{','){']
                for n in no_space:
                    tplData = re.sub(n[0],n[1],tplData)
                # reemplazar \s{ {\s \s} }\s  \s(  (\s  \s) )\s
                no_space = [[' {','{'],['{ ','{'],[' }','}'],['} ','}'],[' (','('],['( ','('],[' )',')'],[') ',')']]
                for n in no_space:
                    tplData = tplData.replace(n[0],n[1])
            # finaliza compresor de todo el codigo HTML
            if DEBUG:
                with open('htmlTemp.txt',mode='w', encoding="utf-8") as file_t:
                    file_t.write(tplData)
                LOG.debug('TIPO DE DATOS %s' % (self.errorTags(tplData),))
            return tplData
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.setData <%s> in line %s !!!' % (repr(e),tb.tb_lineno))

    def errorTags(self,text):
        '''Comprobar etiquetas correctas'''
        try:
            d_none = dict()
            i = re.findall(r"<[^\/][a-zA-Z0-9]*?[\s,>]",text,re.M)
            d_init = dict()
            for n in i:
                if n.strip() not in list(d_init.keys()):
                    d_init[n.strip()] = 1
                else:
                    d_init[n.strip()] += 1
            e = re.findall(r"<\/[a-zA-Z0-9]*?>",text,re.M)
            d_end = dict()
            for n in e:
                if n.strip() not in list(d_end.keys()):
                    d_end[n.strip()] = 1
                else:
                    d_end[n.strip()] += 1
            # eliminar claves apertura con >
            for n in list(d_init.keys()):
                if len(n) != len(n.replace('>','')):
                    value = d_init[n]
                    if n.replace('>','') in list(d_init.keys()):
                        d_init[n.replace('>','')] = d_init[n.replace('>','')] + value
                    else:
                        d_init[n.replace('>','')] = value
                    del d_init[n]
            # comparar apertura y terminacion
            for n in list(d_end.keys()):
                m = n.replace('/','').replace('>','')
                if m in list(d_init.keys()):
                    # acumula las diferencias
                    if d_init[m] != d_end[n]:
                        d_none[m] = [d_init[m],d_end[n]]
                        # comprueba errores
                        for match in re.finditer(r""+m+"\s", text):
                            s = match.start()
                            e = match.end()
                        for match in re.finditer(r""+n+"\s", text):
                            s = match.start()
                            e = match.end()
                    # eliminar key apertura
                    del d_init[m]
                else:
                    # terminacion no tiene inicio
                    d_none[m] = [0,d_end[n]]
            if len(d_init)>0:
                for m in list(d_init.keys()):
                    # apertura sin terminacion
                    d_none[m] = [d_init[m],0]
            return d_none
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.setData <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
            return {}


    def __system__(self,linea):

        __path__ = ''
        __os__ = ''
        try:
            if linea:

                __os__ = os.name
                if __os__ == 'posix':
                    __path__ = linea.replace("\\",os.sep)
                elif __os__ == 'nt':
                    __path__ = linea.replace("\\",os.sep)
                else:
                    #Sistema operativo desconocido
                    __path__ = linea.strip()
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error('Error en htmlTemplate.__system__ <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        finally:
            return __path__

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        if DEBUG:
            LOG.debug("Template.del ha eliminado el objeto")
        else:
            pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("for help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''version {0}'''.format( __version__))
        print ('''
        Puede cargar una plantilla que siempre debe tener una extensión .tpl :
        página = htmlTemplate('e:/mipymetrick/index.tpl')
        posteriormente recuperará los datos html creados con :
        pagina.get()
        ''')
    '''
    p = input(label='vinos',type='radio',css='class="form_control"',name='vinos',br='True')
    print p
    p = input(label='nacimiento',type='date',css='class="form_control"',name='fecha',br='True')
    print p
    p = input(type='text',css='class="form_control"',name='varios',br='True')
    print p

    p = input(type='number',css='class="form_control"',id='numero',formnovalidate=True,br='True')
    print p
    p = input(type='select',css='class="form_control"',id='country', multiple="multiple", option={'':'SELECCIONE UNA OPCION','28':'Madrid','08':'Barcelona','41':'Sevilla','01':'Alava','pruebame':{'07':'nose','11':'tampoco'}},br='True')
    print p
    p = input(type='hidden',css='class="form_control"',id='id',formnovalidate=True)
    print p
    '''
