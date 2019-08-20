#!/usr/bin/python
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

import sys, cgi, time, os, urllib, sha
import CONFIG
image_path = CONFIG.image_path


import sys, cgi, time, os, urllib
import MAYA.VIA
import MAYA.utils
from MAYA.VIA import uuid,vsmf,repos,uform
vsmf.WARN_UTF8=0

param = cgi.SvFormContentDict()
form = cgi.FieldStorage()
def getp(n,d=None):
  if param.has_key(n):
    return param[n]
  if form.has_key(n):
    return form[n].value
  return d

def hstr(s,nonpre=1):
  s = s.replace('&','&amp;')
  s = s.replace(' ','&nbsp;')
  s = s.replace('<','&lt;')
  s = s.replace('>','&gt;')
  if nonpre:
    s = s.replace('\r\n','<BR>')
    s = s.replace('\n','<BR>')
    s = s.replace('\r','<BR>')        
  return s

def uneditit(x): 
  if isinstance(x,MAYA.VIA.vsmf.Date):
     return repr(x).replace("MAYA.VIA.vsmf.Date._","DATE")
  if isinstance(x,MAYA.VIA.vsmf.uuid.UUID):
     return 'UUID('+repr(x.toString())+')'
  if isinstance(x,MAYA.VIA.vsmf.Binary):
     return 'BINARY('+repr(str(x))+')'
  if isinstance(x,MAYA.VIA.vsmf.MimeVal):
     return 'MIME('+repr(str(x.getType()))+','+repr(str(x.getBuf()))+')'
  if isinstance(x,MAYA.VIA.vsmf.EForm) or isinstance(x,dict):
     ret = []
     itms = x.items()
     itms.sort()
     for a,v in itms:
       ret.append(repr(a)+":"+uneditit(v)) 
     return '{\n' + ',\n'.join(ret) + '\n}'
  if isinstance(x,list):
    return "[ " + ', '.join(map(uneditit,x)) + " ]"
  return repr(x)

def eval_it(x):
  what = {
    'DATE':MAYA.utils.date._,
    'UUID':MAYA.VIA.vsmf.uuid.UUID,
    'BINARY':MAYA.VIA.vsmf.Binary,
    'MIME':MAYA.VIA.vsmf.MimeVal,
  }
  # safety
  x = x.replace("\r",'')
  exec "MYVAL="+x in what
  return what['MYVAL']

uu = getp('uuid')
attr = getp('attr')
val = getp('val','fake')
err = getp('err','')
radr=getp('radr','')
if val != 'fake':
  if attr != None and len(attr) >  0:
    attr = attr.lower()
  if attr != None and len(attr) >  0 and not attr.startswith("shepherd_")  :
    # do write here
    href="editattr.py?uuid=%s&attr=%s&radr=%s" %(uu,attr,radr)
    s = 0
    try:
      v = eval_it(val)
    except:
      raise
      s = -98
    if s == 0:
      if radr == None or radr == '':
        xx = CONFIG.repos_addr
      else: 
        xx = radr
      rps = repos.Repository(xx)
      auf = uform.UForm()
      auf['client_type'] = ["authenticated", 1]
      rps.authenticate(auf)
      s = rps.setAttr(uuid._(uu),attr,v)
  else: 
    s = -99
  if s != 0: href = href + "&err=Error During Write "+str(s) 
  print 'Content-Type: text/html\nLocation: %s\n\n<HTML><BODY style="font-size:10px;"><a href="%s">Click here to redirect</a></BODY></HTML>' % (href,href)
  sys.exit(0)

href="uf.py?uuid=%s&radr=%s&ss=0&sn=0&mx=50&sr=0&edit=y" %(uu,radr)
print '''Content-Type: text/html; charset=UTF-8\n\n

<HTML><HEAD><TITLE>%s:%s</TITLE></HEAD><BODY><a href="%s"><H1>%s:%s</H1></a><p>''' % (uu,hstr(attr),href,uu,hstr(attr),)
body_started = 1
try:
  import CONFIG

  if err != '':
    print '<h2><font color="red">'+err+'</font></h2>'
    
  t0 = t1 = 0
  if radr == None or radr == '':
    xx = CONFIG.repos_addr
  else:
    xx = radr
  rps = repos.Repository(xx)
  auf = uform.UForm()
  auf['client_type'] = ["authenticated", 1]
  rps.authenticate(auf)

  x = rps.getAttr(uuid._(uu),attr)
  print '<form method="post" action="editattr.py">%s:<p><textarea name="val" rows=20 cols=80>%s</textarea><br><input type="submit"><input type="hidden" name="uuid" value="%s" ><input type="hidden" name="attr" value="%s" ><input type="hidden" name="radr" value="%s" ></form>' %("EDIT "+hstr(attr),uneditit(x),uu,attr,radr)

except:
  if not body_started:
     print '<BODY>'
  print '<br><font color="red">Server error encountered</font><br>'
  import traceback,StringIO
  x = StringIO.StringIO()
  traceback.print_exc(100,x)
  print '<PRE>'
  print x.getvalue()
  print '</PRE>'

print '</BODY></HTML>'
  
  

