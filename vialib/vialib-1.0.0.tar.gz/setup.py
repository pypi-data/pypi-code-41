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

# Setup script for the MAYA library
#
# Targets: build test install help

import sys, os

try:
  from setuptools import setup
  print "Using setuptools since I found it"
except:
  from distutils.core import setup

# ooo : feb 25 2007
# whenever you are tagging, be sure to comment out the following two lines, commit to svn, make the tag
# then uncomment these two lines and commit

#print """
#This setup.py is now deprecated; to make a distribution of the
#repository APIs, please descend into the (most recent) tagged version
#of the tree and run the setup utility there. At the time of writing,
#this is MAYA-0.2-prerelease.
#"""
#sys.exit(0)

# note that this setup does not build the _mpicrypt module --
# though you may descend into that directory and use the build script there
# to do so
skip = ('MAYA.utils._mpicrypt',)

# collect all the packages below MAYA (assume we want them all)
def get_rec(d):
  def is_pdir(r,d):
    if d.startswith(".") or d == "CVS" : return 0
    return os.path.isdir(r+os.sep+d)
  ret = []
  for k in filter(lambda a: is_pdir(d,a),os.listdir(d)):
    f = (d+os.sep+k).replace(os.sep,".")
    if f not in skip:
      ret.append(f)
      ret.extend(get_rec(d+os.sep+k))
  return ret
    
pkgs = ["MAYA"] + get_rec("MAYA")

setup (name="vialib",
       version="1.0.0",
       description="MAYA VIA Python Libraries",
       author="MAYA Design",
       author_email="jeffsenn@gmail.com",
       packages=pkgs,
       package_data={'MAYA.utils.charting': ['fonts/*.TTF', 'fonts/courB08.*']},)

