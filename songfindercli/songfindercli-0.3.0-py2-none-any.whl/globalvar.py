# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import errno
import sys
import platform
import warnings

appName = 'songfinder'

def getOs():
	if platform.system() == 'Linux':
		if platform.dist()[0] == 'Ubuntu':
			outOs = 'ubuntu'
		else:
			outOs = 'linux'
	elif platform.system() == 'Windows':
		outOs = 'windows'
	elif platform.system() == 'Darwin':
		outOs = 'darwin'
	else:
		outOs = 'notSupported'
		warnings.warn(
			'Your `%s` isn\'t a supported operatin system`.' % platform.system())
	return outOs

myOs = getOs()

# Define root diretcory
chemin_root = os.getcwd()

# Define data directory
dataPath = os.path.join(os.path.split(__file__)[0], 'data')

# Define settings directory
portable = os.path.isfile( os.path.join(chemin_root, 'PORTABLE') )

# Set if installation is portable
try:
	f = open( os.path.join(chemin_root, 'test.test') ,"w")
	f.close()
	os.remove( os.path.join(chemin_root, 'test.test') )
except (OSError, IOError) as error:
	if error.errno == errno.EACCES:
		portable = False
	else:
		raise

# Define Settings directory
if portable:
	print('Portable version')
	settingsPath = os.path.join(chemin_root, '.' + appName, '')
else:
	print('Installed version')
	settingsPath = os.path.join(os.path.expanduser("~"), '.' + appName, '')

if sys.maxsize == 9223372036854775807:
	arch = 'x64'
else:
	arch = 'x86'
dependances = 'deps-%s'%arch
unittest = False
