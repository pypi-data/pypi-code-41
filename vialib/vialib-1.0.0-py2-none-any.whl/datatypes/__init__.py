#######################################################################
#
#       COPYRIGHT 2008 RHIZA LABS, LLC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY RHIZA OR
# MAYA DESIGN
#
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY
# RHIZA OR MAYA AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR
# CONSENT OF THE OWNER.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH
# THE TERMS  OF THE APPLICABLE LICENSE AGREEMENT FROM RHIZA. THIS LEGEND MAY
# NOT BE REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY RHIZA LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################
"""
"""
###############################################################################
#  this module is now obsolete.  Use MAYA.VIA.vsmf instead
##########################`%#####################################################

from MAYA.VIA.vsmf import native_bool,Binary,MimeVal,True,False,Null,Date
from MAYA.utils import date

# this is a hack to handle deprecated uses of Boolean class; will break if used
class Boolean(object):
    pass
