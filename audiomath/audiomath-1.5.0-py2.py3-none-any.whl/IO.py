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

__all__ = [
	
]

import os
import sys
import time
import wave
import struct
import ctypes, ctypes.util
import platform

from . import Base;  from .Base import Sound, Silence, ACROSS_SAMPLES
from . import Meta; from .Meta import FindFile

def EndianSwap( s, nbytes ):
	if   nbytes == 1 or sys.byteorder == 'little': return s
	elif nbytes == 2: fmt = 'H'
	elif nbytes == 4: fmt = 'L'
	else: raise ValueError( "failed to swap endianness for %d-byte values" % nbytes )
	fmt = str( int( len(s) / nbytes ) ) + fmt
	return struct.pack( '<' + fmt, *struct.unpack( '>' + fmt, s ) )

def Read_Wav(self, filename):
	wf = wave.open( filename, 'rb' )
	nbytes = wf.getsampwidth()
	nchan = wf.getnchannels()
	nsamp = wf.getnframes()
	fs = wf.getframerate()
	comptype = ( wf.getcomptype(), wf.getcompname() )
	strdat = wf.readframes( nsamp )
	wf.close()
	strdat = EndianSwap( strdat, nbytes )
	self.bits = nbytes * 8
	self.fs = fs
	self.filename = os.path.realpath( filename )
	self.compression = comptype
	self.y = self.str2dat( strdat, nsamp, nchan )
	if strdat != self.dat2str():
		print( "warning: data mismatch in %r" % self )
	return self

def Write_Wav( self, filename=None ):
	"""
	Write the sound waveform in uncompressed `'.wav'`
	format, to the specified `filename`.  If `filename`
	is unspecified, `self.filename` is used, if present.
	"""
	if filename is None: filename = self.filename
	if filename is None: raise TypeError( 'no filename supplied' )
	wf = wave.open( filename, 'wb' )
	wf.setsampwidth( self.nbytes )
	wf.setnchannels( self.NumberOfChannels() )
	wf.setnframes( self.NumberOfSamples() )
	wf.setframerate( self.fs )
	wf.setcomptype( *self.compression )
	s = self.dat2str()
	s = EndianSwap( s, self.nbytes )
	wf.writeframes( s )
	wf.close()
	self.filename = os.path.realpath( filename )
	return self


avbin = None
def Load_AVBin( tolerateFailure=False ):
	global avbin
	if avbin: return avbin
		
	from . import _wrap_avbin as avbin
	if avbin: return avbin
		
	if 'pyglet' not in sys.modules: os.environ[ 'PYGLET_SHADOW_WINDOW' ] = '0'

	try: import pyglet.media.sources.avbin as avbin
	except: pass
	if avbin: return avbin

	try: import pyglet.media.avbin as avbin
	except: pass
	if avbin: return avbin
		
	if avbin is None and not tolerateFailure: raise ImportError( 'failed to import avbin (is pyglet installed?)' )
	return avbin
	
def Read_AVBin( self, filename, duration=None, verbose=False ):
	if not avbin: Load_AVBin()
	sourceHandle = avbin.AVbinSource( filename )
	self.bits = sourceHandle.audio_format.sample_size
	self.fs = int( sourceHandle.audio_format.sample_rate )
	numberOfChannels = int( sourceHandle.audio_format.channels )
	bytesPerSample = int( sourceHandle.audio_format.bytes_per_sample )
	if duration is None: duration = sourceHandle.duration
	else: duration = min( duration, sourceHandle.duration )
	totalNumberOfSamples = int( round( duration * self.fs ) )
	cumulativeNumberOfSamples = 0
	self.filename = os.path.realpath( filename )
	subsDst = [ slice( None ), slice( None ) ]
	subsSrc = [ slice( None ), slice( None ) ]
	if verbose: print( 'reserving space for %g sec: %d channels, %d samples @ %g Hz = %g MB' % ( duration, numberOfChannels, totalNumberOfSamples, self.fs, totalNumberOfSamples * numberOfChannels * 4 / 1024 ** 2.0 ) )
	y = Silence( totalNumberOfSamples, numberOfChannels, 'float32' )
	t0 = 0.0
	while cumulativeNumberOfSamples < totalNumberOfSamples:
		if verbose:
			t = time.time()
			if not t0 or t > t0 + 0.5: t0 = t; print( '    read %.1f%%' % ( 100.0 * cumulativeNumberOfSamples / float( totalNumberOfSamples ) ) )
		dataPacket = sourceHandle.get_audio_data( 4096 )
		if dataPacket is None: break
		numberOfSamplesThisPacket = int( dataPacket.length / bytesPerSample )
		subsDst[ ACROSS_SAMPLES ] = slice( cumulativeNumberOfSamples, cumulativeNumberOfSamples + numberOfSamplesThisPacket )
		subsSrc[ ACROSS_SAMPLES ] = slice( 0, min( numberOfSamplesThisPacket,  totalNumberOfSamples - cumulativeNumberOfSamples ) )
		cumulativeNumberOfSamples += numberOfSamplesThisPacket
		data = self.str2dat( dataPacket.data, numberOfSamplesThisPacket, numberOfChannels )
		y[ tuple( subsDst ) ] = data[ tuple( subsSrc ) ]
	self.y = y
	return self
		
def Read( self, source, raw_dtype=None ):
	"""
	Args:
		source:
			A filename, or a byte string containing raw audio data.
			With filenames, files are decoded according to their file extension,
			unless the `raw_dtype` argument is explicitly specified, in which case files
			are assumed to contain raw data without header, regardless of extension.
			
		raw_dtype (str):
			If supplied, `source` is interpreted either as raw audio data, or
			as the name of a file *containing* raw audio data without a header.
			If `source` is a byte string containing raw audio data, and `raw_dtype` is
			unspecified, `raw_dtype` will default to `self.dtype_encoded`.
			Examples might be `float32` or even `float32*2`---the latter explicitly
			overrides the current value of `self.NumberOfChannels()` and interprets the
			raw data as 2-channel.
			
	"""
	isFileName = False
	for i in range( 32 ):
		try: nonprint = chr( i ) in source
		except: break
		if nonprint: break
	else:
		isFileName = True
	if isFileName:
		resolvedFileName = FindFile( source )
		source = resolvedFileName if resolvedFileName else os.path.realpath( source )
	isExistingFile = isFileName and os.path.isfile( source )
	if isFileName and not isExistingFile: raise IOError( 'could not find file %s' % source )
	
	if not isExistingFile or raw_dtype:
		if isExistingFile:
			self.filename = os.path.realpath( source )
			source = open( source, 'rb' )
		else:
			self.filename = ''
		if hasattr( source, 'read' ): source = source.read()
		nchan = None # default is self.NumberOfChannels()
		if not isinstance( raw_dtype, str ):
			raw_dtype = None  # default will be self.dtype_encoded
		elif '*' in raw_dtype:
			raw_dtype, count = raw_dtype.split( '*', 1 )
			if count: nchan = int( count )
		self.y = self.str2dat( source, nsamp=None, nchan=nchan, dtype=raw_dtype )
		return self
	
	if source.lower().endswith( '.wav' ): return Read_Wav( self, source )
	
	return Read_AVBin( self, source )
Sound.Read  = Read
Sound.Write = Write_Wav
