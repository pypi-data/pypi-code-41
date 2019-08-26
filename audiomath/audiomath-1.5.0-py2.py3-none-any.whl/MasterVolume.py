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

# adapted from a mail.python.org post by Ray Schumacher

__all__ = [
	'GetMasterVolume',
	'SetMasterVolume',
]

GetMasterVolume = None
SetMasterVolume = None

import platform
if platform.system().lower() == 'windows': 
	import ctypes
	
	mixerSetControlDetails = ctypes.windll.winmm.mixerSetControlDetails
	mixerGetControlDetails = ctypes.windll.winmm.mixerGetControlDetailsA
	
	# Some constants
	MIXER_OBJECTF_MIXER = 0   # mmsystem.h
	VOLUME_CONTROL_ID = 0     # Device ID: same on all machines?
	
	SPEAKER_LINE_FADER_ID = 0 # control ID: clearly varies between XP and Vista/7, and also between machines: see #***
	
	MINIMUM_VOLUME = 0        # fader control (MSDN Library)
	MAXIMUM_VOLUME = 65535    # fader control (MSDN Library)
	
	DWORD = ctypes.c_uint32
	
	class MIXERCONTROLDETAILS(ctypes.Structure):
		_pack_ = 1
		_fields_ = [
			('cbStruct',       DWORD),
			('dwControlID',    DWORD),
			('cChannels',      DWORD),
			('cMultipleItems', DWORD),
			('cbDetails',      DWORD),
			('paDetails',      ctypes.POINTER(ctypes.c_uint32)),
		]
	
	def SetMasterVolume(volume, channel=None):
		if channel is None: channel = SPEAKER_LINE_FADER_ID
		volume = min(1.0, max(0.0, volume))
		volume = int( 0.5 + MINIMUM_VOLUME + (MAXIMUM_VOLUME - MINIMUM_VOLUME) * volume )
		
		s = MIXERCONTROLDETAILS(
			ctypes.sizeof(MIXERCONTROLDETAILS),
			channel,
			1, 0,
			ctypes.sizeof(ctypes.c_uint32),
			ctypes.pointer(ctypes.c_uint32(volume)),
		)
		ret = mixerSetControlDetails(
			VOLUME_CONTROL_ID,
			ctypes.byref(s),
			MIXER_OBJECTF_MIXER,
		)
		if ret != 0: raise WindowsError( "Error %d while setting master volume" % ret )
			
	def GetMasterVolume(channel=None):
		if channel is None: channel = SPEAKER_LINE_FADER_ID
		s = MIXERCONTROLDETAILS(
			ctypes.sizeof(MIXERCONTROLDETAILS),
			channel,
			1, 0,
			ctypes.sizeof(ctypes.c_uint32),
			ctypes.pointer(ctypes.c_uint32(0)),
		)
		ret = mixerGetControlDetails(
			VOLUME_CONTROL_ID,
			ctypes.byref(s),
			MIXER_OBJECTF_MIXER,
		)
		if ret != 0: raise WindowsError( "Error %d while getting mixer control details" % ret )
		volume = s.paDetails.contents.value
		return (float(volume) - MINIMUM_VOLUME) / (MAXIMUM_VOLUME - MINIMUM_VOLUME)

	#*** extreme empirical adhockery ahead: if anyone knows how to navigate the rocks of the windows API to do this properly, please tell me!
	if platform.win32_ver()[0].lower().startswith('xp'):
		try: GetMasterVolume()  #  control ID=0 is correct on some XP machines but fails with an exception on others
		except: SPEAKER_LINE_FADER_ID = 1  #  control ID=1 is correct on some XP machines
	else: SPEAKER_LINE_FADER_ID = 2  # control ID=2 seems to be correct on some Vista/Win7 machines (whereas 0 throws an error and 1 is, extremely inconveniently, the mute control)
	
if SetMasterVolume is None:
	print( '%s module could not find an implementation for SetMasterVolume---only supported for Win32 at the moment' % __name__ )
