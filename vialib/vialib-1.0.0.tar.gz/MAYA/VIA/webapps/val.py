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
try:
 import CONFIG
 rpsaddr = CONFIG.repos_addr
 import sys,os
 pi = os.environ.get('PATH_INFO','').split('/')
 uu = pi[1]
 at = pi[2]
 from MAYA.VIA import uuid,repos,vsmf,uform
 rps = repos.Repository(rpsaddr)
 uf = uform.UForm()
 uf['client_type'] = ['authenticated',1]
 rps.authenticate(uf)
 uu = uuid._(uu)
 vv = rps.getAttr(uu,at)
 tv = type(vv)
 if vv == None:
   print "Content-Type: text/plain\n\n"
 elif isinstance(vv,vsmf.mimeVal) or isinstance(vv,vsmf.MimeVal):
   print "Content-Type: %s\n" % vv.getType()
   print vv.getBuf()
 elif tv == type('') or tv == type(u''):
   print "Content-Type: text/plain\n"
   print vv
 else:
   print "Content-Type: text/plain\n"
   print repr(vv)

except:
  print "Content-Type: text/plain\n"
  import traceback,StringIO
  x = StringIO.StringIO()
  traceback.print_exc(100,x)
  print x.getvalue()
  



