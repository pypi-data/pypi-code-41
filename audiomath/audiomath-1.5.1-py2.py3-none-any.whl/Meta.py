# $BEGIN_AUDIOMATH_LICENSE$
# 
# This file is part of the audiomath project, a Python package for
# recording, manipulating and playing sound files.
# 
# Copyright (c) 2008-2019 Jeremy Hill
# 
# audiomath is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# The audiomath distribution includes binaries from the third-party
# AVbin and PortAudio projects, released under their own licenses.
# See the respective copyright, licensing and disclaimer information
# for these projects in the subdirectories `audiomath/_wrap_avbin`
# and `audiomath/_wrap_portaudio` .
# 
# $END_AUDIOMATH_LICENSE$
"""
Package introspection tools.
"""
__all__ = [
	'__meta__',
	'__version__',
	'WhereAmI',
	'PACKAGE_LOCATION',
	'PackagePath',
	'FindFile',
	'ComputerName',
	'GetRevision',
]

import os
import sys
import ast
import shlex
import socket
import inspect
import subprocess

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x

def WhereAmI( nFileSystemLevelsUp=1, nStackLevelsBack=0 ):
	"""
	`WhereAmI( 0 )` is equivalent to `__file__`
	
	`WhereAmI()` or `WhereAmI(1)` gives you the current source file's
	parent directory.
	"""
	try:
		frame = inspect.currentframe()
		for i in range( abs( nStackLevelsBack ) + 1 ):
			frame = frame.f_back
		file = inspect.getfile( frame )
	finally:
		del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	return os.path.realpath( os.path.join( file, *[ '..' ] * abs( nFileSystemLevelsUp ) ) )

def Bang( cmd, shell=False ):
	windows = sys.platform.lower().startswith('win')
	# If shell is False, we have to split cmd into a list---otherwise the entirety of the string
	# will be assumed to be the name of the binary. By contrast, if shell is True, we HAVE to pass it
	# as all one string---in a massive violation of the principle of least surprise, subsequent list
	# items would be passed as flags to the shell executable, not to the targeted executable.
	# Note: Windows seems to need shell=True otherwise it doesn't find even basic things like ``dir``
	# On other platforms it might be best to pass shell=False due to security issues, but note that
	# you lose things like ~ and * expansion
	if isinstance( cmd, str ) and not shell:
		if windows: cmd = cmd.replace( '\\', '\\\\' ) # otherwise shlex.split will decode/eat backslashes that might be important as file separators
		cmd = shlex.split( cmd ) # shlex.split copes with quoted substrings that may contain whitespace
	elif isinstance( cmd, ( tuple, list ) ) and shell:
		quote = '"' if windows else "'"
		cmd = ' '.join( ( quote + item + quote if ' ' in item else item ) for item in cmd )
	try: sp = subprocess.Popen( cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	except OSError as err: return err, '', ''
	output, error = [ IfStringThenNormalString( x ).strip() for x in sp.communicate() ]
	return sp.returncode, output, error
	

	
PACKAGE_LOCATION = WhereAmI()

def PackagePath( *pieces ):
	"""
	Return a resolved absolute filesystem path based on the
	`pieces` that are expressed relative to the location
	of this package. Useful for finding resources within a
	package.
	"""
	return os.path.realpath( os.path.join( PACKAGE_LOCATION, *pieces ) )

def FindFile( filename ):
	"""
	Look for a file based on `filename`.  Return the full path
	to it if it can be found, or `None` if not.
	
	If the `filename` does not include a file extension, try a
	number of different common extensions. 
	
	If the `filename` does not specify a parent directory, look
	in the current working directory *and* in the `example_media`
	directory that is bundled with this package.
	"""
	if not isinstance( filename, str ): return
	variants = []
	parent, basename = os.path.split( filename )
	stem, extension = os.path.splitext( basename )
	basenames = [ basename ]
	if not extension: basenames.extend( basename + extensionVariant for extension in '.wav .mp3 .ogg .aac .m4a'.split() for extensionVariant in [ extension, extension.upper() ] )
	if parent: parents = [ os.path.realpath( parent ) ]
	else: parents = [ os.getcwd(), PackagePath( 'example_media' ) ]
	for parent in parents:
		for basename in basenames:
			variant = os.path.join( parent, basename )
			if os.path.isfile( variant ): return variant
		
def ComputerName():
	"""
	Return the name of the computer.
	"""
	return os.path.splitext( socket.gethostname() )[ 0 ].lower()

def GetRevision():
	"""
	If this package is installed as an "editable" copy, running
	out of a location that is under version control by mercurial
	(which is the way it is developed), then return information
	about the current mercurial revision.
	"""
	hgrev = '@HGREV@'
	if hgrev.startswith( '@' ):
		hgrev = 'unknown revision'
		possibleRepo = PackagePath( '..', '..' )
		repoSubdirectories = [ entry for entry in os.listdir( possibleRepo ) if os.path.isdir( os.path.join( possibleRepo, entry ) ) ]
		if all( x in repoSubdirectories for x in [ '.hg', 'python' ] ): # then we're probably in the right place
			errorCode, stdout, stderr = Bang( 'hg id -intb -R "%s"' % possibleRepo )
			if not errorCode: hgrev = stdout
	return hgrev
	

__meta__ = ast.literal_eval( open( PackagePath( 'MASTER_META' ), 'rt' ).read() )
__version__ = __meta__[ 'version' ]
