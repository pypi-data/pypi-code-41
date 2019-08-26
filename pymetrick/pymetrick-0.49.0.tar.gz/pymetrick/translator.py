#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2012-09-21'
__credits__ = ''
__text__ = 'Tratamiento de traducciones a traves de Google Trnaslate'
__file__ = 'translator.py'

#--- CHANGES ------------------------------------------------------------------
# 2012-09-21 v0.01 PL: - First version

import os
import sys

try:
     import urllib.request                # python 3
except:
     import urllib2                       # python 2

# Version PY
PY2 = True if sys.version[:1] == '2' else False;
PY3 = True if sys.version[:1] == '3' else False;

def translate(to_translate, to_langage="auto", langage="auto"):
     '''Return the translation using google translate
     you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
     if you don't define anything it will detect it or use english by default
     Example:
     print(translate("salut tu vas bien?", "en"))
     hello you alright?'''
     agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
     before_trans = 'class="t0">'
     link = ("http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+")))
     if PY2:
          request = urllib2.Request(link, headers=agents)
          page = urllib2.urlopen(request).read()
     elif PY3:
          request = urllib.request.Request(link, headers=agents)
          page = urllib.request.urlopen(request).read()

     result = page[page.find(before_trans)+len(before_trans):]
     result = result.split("<")[0]
     return result

if __name__ == '__main__':
    print ('''copyright {0}'''.format( __copyright__))
    print ('''license {0}'''.format( __license__))
    print ('''version {0}'''.format( __version__))
    if len(sys.argv) < 2:
        sys.stderr.write("for help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''
        Tratamiento de traducciones :\n\n''')
    '''
    to_translate = 'Hola como estas?'
    print("%s >> %s" % (to_translate, translate(to_translate)))
    print("%s >> %s" % (to_translate, translate(to_translate, 'pt')))
    print("%s >> %s" % (to_translate, translate(to_translate, 'ca')))
    #should print Hola como estas >> Hello how are you
    #and Hola como estas? >> Bonjour comment allez-vous?
    '''