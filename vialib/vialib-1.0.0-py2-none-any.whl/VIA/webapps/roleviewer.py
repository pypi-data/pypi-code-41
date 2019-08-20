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
from MAYA.VIA import uuid
def load_n_go(m, r,uu):
    import imp
    x = imp.load_source('render',m,open(m,'r'))
    return x.render(r,uu)
    
def check(roles):
  for k in viewers:
    if k in roles: return lambda b,c: load_n_go(viewers[k],b,c)
  return None

viewers = {}
def VIEWER(a,b): viewers[uuid._(a)] = b

# VIEWER('~01539e9d1cfb4811d785253c3f510d30fc','role_ffp_evidence.py')


    



    
    
    
