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
try: import roleviewer
except: pass
from MAYA.VIA import uuid,vsmf,repos,uform
from MAYA.utils import shepherding
vsmf.WARN_UTF8=0
param = cgi.SvFormContentDict()
form = cgi.FieldStorage()
def getp(n,d=None):
  if param.has_key(n):
    return param[n]
  if form.has_key(n):
    return form[n].value
  return d
unames = {}
do_wait_for_presence = True
def ulink(uu,spec=None,nm=None):
 global show_names,show_roles,maxelem,do_wait_for_presence
 if spec == None:
   spec = "sn=%d&sr=%d&mx=%d&radr=%s&pubidx=%s"%(show_names,show_roles,maxelem,radr,pubidx)
 if nm == None:
  if show_names:
    nm = unames.get(uu)
    if nm == None:
      if do_wait_for_presence:
        try:
          shepherding.waitForPresence(rps, uuid._(uu), timeoutSecs=3)
        except shepherding.TimeoutError:
          pass
        except AttributeError:
          pass
      nm = rps.getAttr(uuid._(uu),'name')
      if nm == None or nm == '': nm = rps.getAttr(uuid._(uu),'label')
      if nm == None or nm == '': nm = uu
      unames[uu] = nm
  else:
    nm = uu
 try:
   enam = nm.encode('utf8')
 except:
   enam = str(nm)
 return '<a href="uf.py?uuid=%s&%s">%s&nbsp;</a>' % (urllib.quote(uu),spec,enam)

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

def verify_sig(uu,a,v):
  if type(v) == type(()) or type(v) == type([]):
    owner = 0
    if a == 'acu_owner_signature':
      try:
        c,s = v[1]
        owner = 1
      except:
        return '<font color="orange">(bad format)</font>'
    else:
      try:
        ck,prot,sig = v
        c,s = sig
      except:
        return '<font color="orange">(bad format)</font>'
    try:
      e,pub = rps.getAttr(c,'rsa-publickey')
    except:
      return '<font color="orange">(no credential)</font>'
    from MAYA.utils import crypto
    if not owner:
      x = rps.getAttr(uu,'shepherd_versions')
      if x[0] != uu: x.insert(0,uu)
      csv = x[2:]
      csv.sort()
      csv.insert(0,x[1])
      csv.insert(0,x[0])
      csv = vsmf.serialize(csv)
    l = rps.listAttrInfo(uu)
    ks = map(lambda a: a.lower().encode('utf8'), l.keys())
    ks.sort()
    digest = ''
    digest2 = ''
    for k in ks:
      if k.startswith('shepherd_') and k != 'shepherd_versions': continue
      if owner:
        if k in ('acu_list', 'acu_perm_owners', 'acu_owners'):
          digest += k + l[k.decode('utf8')][0].getBuf()
      else:
        if k == 'shepherd_versions':
          digest += k + l[k.decode('utf8')][0].getBuf()
          digest2 += k + sha.new(csv).digest()
        else:
          digest += k + l[k.decode('utf8')][0].getBuf()
          digest2 += k + l[k.decode('utf8')][0].getBuf()
    if crypto.rsa_verify(digest,s,pub,e):
       return '<font color="green">{VERIFIED}</font>'    
    elif crypto.rsa_verify(digest2,s,pub,e):
       return '<font color="green">{VERIFIED-CANON}</font>'      
    else:
       return '<font color="red">{BAD SIGNATURE}</font>'    
  return ''          

def format_value(v,top=0,attr=''):
  global maxelem
  t = type(v)
  if t == type([]) or t == type(()):
    if len(v) > maxelem:
      return '[' + ','.join(map(format_value,v[:maxelem])) + '<font color="red"> <br>...INCOMPLETE VALUE SHOWN...(%d of %d)</font> <a href="%s">MORE</a> ]' % (maxelem,len(v),more)      
    else:  
      return '[' + ','.join(map(format_value,v)) + ']'
  elif uuid.isa(v):
    return ulink(v.toString())
  elif (attr == 'uri') and (t == type('')):
    return '<a href="' + v + '">' + v + '</a>'
  elif t == type({}):
    xas = v.keys()
    xas.sort()
    return '<TABLE CELLSPACING=1>'+''.join(map(lambda x: '<TR><TD class="brborder" VALIGN="top">' + hstr(x.encode('utf8')) + '</TD><TD class="bborder">' + format_value(v[x]) + "</TD></TR>", xas)) + '</TABLE>'
  elif isinstance(v,vsmf.MimeVal): #or isinstance(v,vsmf.mimeVal):
    mt = v.getType()
    if mt.split("/")[0].lower() == 'image':
      return '<img src="val.py/%s/%s">' % (uu,attr,)
    else:
      return '<a href="val.py/%s/%s">MIME:%s</a>' % (uu,attr,hstr(mt),)
  elif t == type('') or t == type(u''):
    try:
      v = v.encode('utf8')
    except: pass
    if len(v) > 2000:
      v = v[:2000] + '... (%d characters total)' % len(v)
    if top:
      n = v.find('\n')
      r = v.find('\r')
      #if the first line is long then not python
      if (n >= 0 and n < 72) or (r >= 0 and r < 72):
        return '<PRE>%s</PRE>' % hstr(v,nonpre=0)
    return hstr(v)
  elif v == None:
    return '<font color="orange">Empty</font>'
  return repr(v)

rimpls = {}
def app_notin(l,x):
  try:
    i = l.index(x)
    return 0
  except:
    l.append(x)
    return 1
def role_implies(uus):
  global rimpls
  r = rimpls.get(uus)
  if r == None:
    r = []
    rs = rps.getAttr(uuid._(uus),'implied_roles')
    if type(rs) == type([]):
     for rr in rs:
      if app_notin(r,rr):
        im = role_implies(rr.toString())
        for x in im:
          app_notin(r,x)
    rimpls[uus] = r
  return r
def roleclosure(l):
  r = []
  try:
   for x in l:
    app_notin(r,x)
    im = role_implies(x.toString())
    for xx in im:
      app_notin(r,xx)
  except: pass
  return r

if os.environ.get("HTTP_USER_AGENT") == 'Java1.3.1':
  broken_browse = 1
else:
  broken_browse = 0  
uu = getp('uuid')
show_names = getp('sn',0)
if show_names == '1': show_names = 1
else: show_names = 0
show_roles = getp('sr','1')
if show_roles == '0':
  show_roles = 0
else:
  show_names = 1
  show_roles = 1
radr=getp('radr','')
pubidx=getp('pubidx','')
editflag=getp('edit','')
maxelem = int(getp('mx','50'))
if maxelem < 1: maxelem = 50
show_search = getp('ss','0')
if show_search == '1': show_search = 1
else: show_search = 0
more = 'uf.py?uuid=%s&sn=%d&sr=%d&mx=%d&ss=%d&radr=%s&pubidx=%s&' % (uu,show_names,show_roles,maxelem*2,show_search,radr,pubidx)
print '''Content-Type: text/html; charset=UTF-8\n\n

<HTML><HEAD>'''
if not broken_browse:
  print '''
<link rel="stylesheet" type="text/css" href="%suf.css">
'''%(image_path)
body_started = 0

def options(ss=show_search, sr=show_roles, sn=show_names, mx=maxelem, ra=radr, pi=pubidx):
  return "&newframe=no&sr=%d&sn=%d&ss=%d&mx=%d&radr=%s&pubidx=%s"%(sr,sn,ss,mx,ra,pi)
  
try:
  import CONFIG
    
  t0 = t1 = 0
  if radr == None or radr == '':
    xx = CONFIG.repos_addr
  else:
    xx = radr
  rps = repos.Repository(xx)
  auf = uform.UForm()
  auf['client_type'] = ["authenticated", 1]
  rps.authenticate(auf)
  def WAITFOR(x):
    try:
      shepherding.waitForPresence(rps, uuid._(x), timeoutSecs=3)
    except shepherding.TimeoutError:
      pass
    except AttributeError:
      pass
  WAITFOR(uu)
  overwrites = None
  pubcontent = None
  foo = []
  if pubidx != '': # lookup publisher content here
    pubidxu = uuid._(pubidx)
    WAITFOR(pubidxu)
    btree = rps.getAttr(pubidxu,'btree_root')
    foo.append(btree)
    if btree is not None:
      target = uu
      while btree != None:
        WAITFOR(btree)
        ch = rps.getAttr(btree,'children')
        if ch is None or len(ch) < 1: break
        if target < ch[0][0]: break
        for i in xrange(0,len(ch)-1):
          if i == len(ch)-1 or target < ch[i+1][0]: # descend i-1
            if len(ch[i]) == 2: # non-leaf
              btree = ch[i][1] # descend
              break
            elif ch[i][0] == target: #found
              pubcontent = ch[i][1][0]
              btree = None
              break
            else: # leaf but wrong one -- nothing found
                btree = None                
                break
    #
    if pubcontent is not None: 
      overwrites = rps.getAttr(pubcontent,'overwrites')
  if overwrites is None: overwrites = {}

  if show_names:
    nm = rps.getAttr(uuid._(uu),'name')
    if nm == None: nm = rps.getAttr(uuid._(uu),'label')
    if nm != None:
     nm1 = format_value(nm)
    else:
     nm1 = ''
    nm2 = 'UUID: '+uu 
  else:
    nm1 = 'UUID: '+uu
    nm2 = ''

  print '<TITLE>%s %s</TITLE>' % (nm1,nm2)
  print '<BODY>'
  body_started = 1

  bs = 'uf.py?uuid='+uu
  b1 = '0'
  if show_names and not show_roles: b1 = '1'
  b2 = '1'
  if show_names or show_roles: b2 = '0'
  b3 = '0'
  if show_roles: b3 = '1'
  if show_search:
    src = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/joshua/repos.html">New Search</a> | <a href="/">Home</a>&nbsp;<br>'
  else: src = ''
  print '<TABLE cellspacing=0 cellpadding=0 width="100%%"><TR><TD class="bborder" width=60%%><font size="+2">%s</font><BR><font size="-1">%s</font></TD><TD class="gborder"><font size="-2">%s<a href="%s"><img border=0 src="%sbut%s.gif"></a> Raw u-form display<!-- <br><a href="%s"><img border=0 src="%sbut%s.gif"></a> Lookup name attributes of UUIDs --> <br><a href="%s"><img border=0 src="%sbut%s.gif"></a> Use roles to format display</font> </TD><TD class="bborder">&nbsp;&nbsp;&nbsp;</TD></TR><TR><TD></TD><TD class="g2border"><font size="-2"><form action="uf.py" method="post">Show up to <input type="text" style="font-size:80%%" size=4 value="%s" name="mx"/> elements <input type="hidden" value="%s" name="uuid"/><input type="hidden" value="%s" name="sn"/><input type="hidden" value="%s" name="sr"/><input type="hidden" value="%s" name="ss"/><br>Publisher Index: <input type="text" style="font-size:80%%" size-=40 value="%s" name="pubidx"/> <input type="image" onclick="this.form.submit();" src="%sbut.gif"/></form></font></TD><TD></TD></TABLE><BR>' % (nm1,nm2, src, bs+options(sr=0,sn=0),image_path,b2, bs+options(sn=1,sr=0),image_path,b1,bs+options(sr=1),image_path,b3,maxelem,uu,show_names,show_roles,show_search,pubidx,image_path)

  t0 = time.time()
  uf = rps.getUForm(uuid._(uu))
  if len(overwrites):
    for k in overwrites:
      if k.lower() == 'roles': # roles special (for now)
        uf[k] = uf[k] + overwrites[k]
      elif overwrites[k] is None:
        uf.pop(k)
      else:
        uf[k] = overwrites[k]

  xas = uf.keys()
  xas.sort()
  t1 = time.time()
  role_viewer = None
  probably_a_role = 0
  try:
    if uuid._('~fd000a02510bfd1d650a97') in uf['roles'] or uf.get('implied_roles') != None or uuid._('~fd000a02510bfd57e6f173') in uf['roles']:
      probably_a_role = 1
  except: pass
  try: role_viewer = roleviewer.check(uf['roles'])
  except: pass    
  try:
    i = xas.index('roles')
    del xas[i]
    xas.insert(0,'roles')
    #if probably_a_role:
    #  print '<br> -- <a href="roleview.py?uuid=%s">View using Role Viewer</a> -- <br>' % uu
  except:
    pass
  if len(xas) < 1:
    print "<br><br>U-form has no attributes."
  if show_roles:
    
   rls = uf.get('roles')
   rls_errs = []

   if role_viewer:
     x = role_viewer(rps,uf.uuid)
     try:
       x = x.encode('utf8')       
     except:
       print "WARNING: Role Viewer encode error"
     print x
     xas = [] # clr attr left list
   elif probably_a_role:
     import rolelib
     import os
     if os.environ.get('REMOTE_ADDR').startswith('10.20.32.40'):
       #jeff machine hack... could let everyone have this feature someday...
       print '<B><A href="roleedit.py?uuid=%s&server=%s">EDIT</A></B><br>' % (uf.uuid.toString(),CONFIG.repos_addr)
     x = rolelib.renderRole(rps, uf.uuid)
     try:
       x = x.encode('utf8')       
     except:
       print "WARNING: Rolelib encode error"
     print x
     xas = []
   elif rls != None:
     try:
       rls = list(rls) #don't muck it up
     except: pass
     rls_c = roleclosure(rls)
     print '<TABLE cellpadding=1 cellspacing=0><TR><TD VALIGN="top"><B>roles:&nbsp;</B></TD><TD>%s</TD></TR></TABLE>' % format_value(rls,top=1)
     xas.remove('roles')  
     for r in rls_c:
       try:
         rls.remove(r)
         implied = ''
       except:
         implied = '(implied)'
       ras = None
       if uuid.isa(r):
         ras = rps.getAttr(r,'attributes')
         rqs = rps.getAttr(r,'requireds')       
         rnm = rps.getAttr(r,'name')
         prf = rps.getAttr(r,'attribute_prefixes')
       if ras == None:
         try:
           rls_errs.append(r.toString())
         except:
           pass
       else:
         print '<BR><BR><TABLE CELLSPACING=0 CELLPADDING=0 width="100%%" BGCOLOR="#F0F0F0"><TR><TD class="tborder">Attributes in %s role: <b>' % (implied,) , ulink(r.toString(),None,rnm),'</b></TD></TR></TABLE>'
         print '<TABLE cellspacing=1>'
         for i in range(len(ras)):
           a = ras[i].lower()
           req = 0
           if type(rqs) == type([]) and len(rqs)>i: req = rqs[i]
           try:
             xas.remove(a)
           except: pass
           v = uf.get(a)
           if v != None or req:
             lk1 = lk2 = ''
             if editflag == 'y': 
               lk2 = '</a>'
               lk1 = '<a href="editattr.py?uuid=%s&attr=%s&radr=%s">' %(uf.uuid.toString(),hstr(a),radr)
             print '<TR><TD class="brborder" VALIGN="top">%s<B>%s</B>%s'% (lk1,hstr(a),lk2,)
             if v == None and req: print '<font color="red"> (required)</font>'
             if overwrites.has_key(a): print '<font color="orange"> (publisher)</font>'
             if a == 'shepherd_signature' or a == 'acu_owner_signature':
               print verify_sig(uf.uuid,a,v)
             print '</TD>'
             if a == 'shepherd_versions':
               do_wait_for_presence = False
             else:
               do_wait_for_presence = True
             v = format_value(v,top=1,attr=a)
             print '<TD  class="bborder">%s</TD></TR>' % (v,)
         if prf != None:
           for aprf in prf:
             try: a = aprf.lower()
             except: continue
             # FIXED; hope it behaves as expected -higgins 2003-07-10
             for aa in xas[:]:
               if aa.startswith(aprf):
                 xas.remove(aa)
                 v = uf.get(aa)
                 if v != None:                 
                   print '<TR><TD class="brborder" VALIGN="top"><B>%s</B> (prefixed)</TD>'% (hstr(aa),)
                 v = format_value(v,top=1,attr=aa)
                 print '<TD  class="bborder">%s</TD></TR>' % (v,)
         print '</TABLE>'

   if len(rls_errs):
     print '<BR><HR color="green"><font color="red">These roles had no attributes and may be malformed or missing:</font><BR>'
     print '<BR>'.join(map(lambda x: ulink(x),rls_errs))

   if len(xas) > 0: print '<BR><BR><TABLE CELLSPACING=0 CELLPADDING=0 width="100%%" BGCOLOR="#F0F0F0"><TR><TD class="tborder">Attributes not found in any role:</TD></TR></TABLE>'

  # show rest
  if len(xas) > 0:
   print '<TABLE style="border-bottom-width:1px;" cellpadding=1 cellspacing=0>'
   for a in xas:
    print '<TR>'
    lk1 = lk2 = ''
    if editflag == 'y': 
      lk2 = '</a>'
      lk1 = '<a href="editattr.py?uuid=%s&attr=%s&radr=%s">' %(uf.uuid.toString(),hstr(a),radr)
    print '<TD class="brborder" VALIGN="top">%s<B>%s</B>%s</TD>' % (lk1,hstr(a),lk2)
    print '<TD class="bborder">%s</TD>' % format_value(uf[a],top=1,attr=a)
    print "</TR>"          
   print '</TABLE>'

  if pubcontent is not None:  
     print '<BR><BR><TABLE CELLSPACING=0 CELLPADDING=0 width="100%%" BGCOLOR="#F0F0F0"><TR><TD class="tborder">Additional content in Publisher Index: '+ulink(pubidxu.toString())+' </TD></TR></TABLE>' 
     cps = rps.getAttr(pubcontent,'child_properties')
     if cps is not None:
       print '<TABLE style="border-bottom-width:1px;" cellpadding=1 cellspacing=0>'
       for mem,eform in cps:
         print '<TR>'
         print '<TD class="brborder" VALIGN="top"><B>%s</B></TD>' % format_value(eform,top=1,attr='')
         print '<TD class="bborder">%s</TD>' % ulink(mem.toString())
         print "</TR>"          
       print '</TABLE>'
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
print '<HR><font size="-2">Took %s seconds of initial fetch, %s seconds of formatting and additional attribute fetch.' % (round((t1-t0)*100)/100,round((time.time()-t1)*100)/100,)
print '</BODY></HTML>'
  
  

