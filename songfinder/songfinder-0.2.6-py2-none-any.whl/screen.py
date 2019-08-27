# -*- coding: utf-8 -*-
from __future__ import division

import warnings
import sys
try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk
try:
	import screeninfo
except ImportError:
	pass

from songfinder import commandLine
from songfinder import exception
from songfinder import globalvar

class Screen(object):
	def __init__(self, width=720, height=480, xposition=0, yposition=0, stringScreen=None):
		if not stringScreen:
			try:
				self._width = int(width)
				self._height = int(height)
				self._xposition = int(xposition)
				self._yposition = int(yposition)
				self._isOK = True
			except ValueError:
				warnings.warn("Erreur de lecture des donnees de l'ecran")
				self._isOK = False
		else:
			self._setScreen(stringScreen)
		self._areUsableSet = False

	def _setScreen(self, stringScreen):
		sizeList = stringScreen.split('x')
		if len(sizeList) != 2:
			warnings.warn('Erreur de lecture de la resolution de l''ecran, '
					'le format des donnees n''est pas valide : "%s". '
					'Le format valide est : "wxh+pw+ph'%stringScreen)
			self._isOK = False
		else:
			positionList = sizeList[1].split('+')
			if len(positionList) != 3:
				warnings.warn('Erreur de lecture de la position de l''ecran, '
										'le format des donnees n''est pas valide : "%s". '
										'Le format valide est : "wxh+pw+ph'%stringScreen)
				self._isOK = False
			else:
				try:
					self._width = int(float(sizeList[0]))
					self._height = int(float(positionList[0]))
					self._xposition = int(float(positionList[1]))
					self._yposition = int(float(positionList[2]))
					self._isOK = True
				except ValueError:
					warnings.warn("Erreur de lecture des donnees de l'ecran")
					self._isOK = False

	def __bool_(self):
		return self._isOK

	@property
	def xposition(self):
		return self._xposition

	@property
	def yposition(self):
		return self._yposition

	@property
	def width(self):
		return self._width

	@property
	def height(self):
		return self._height

	@property
	def usableXposition(self):
		self._getUsableScreen()
		return self._usableXposition

	@property
	def usableYposition(self):
		self._getUsableScreen()
		return self._usableYposition

	@property
	def usableWidth(self):
		self._getUsableScreen()
		return self._usableWidth

	@property
	def usableHeight(self):
		self._getUsableScreen()
		return self._usableHeight

	@property
	def ratio(self):
		if self._height != 0:
			ratio = self._width/self._height
		else:
			ratio = 1
		return ratio

	def _getUsableScreen(self):
		if not self._areUsableSet:
			try:
				frame = tk.Toplevel()
				frame.wm_attributes('-alpha', 0)
				frame.withdraw()
				frame.geometry('+%d+%d'%(self.xposition, self.yposition))
				frame.update()
				frame.state('zoomed')
				frame.withdraw()
			except tk.TclError:
				self._usableWidth = int(self.width*0.9)
				self._usableHeight = int(self.height*0.9)
				self._usableXposition = int(self.xposition*0.9)
				self._usableYposition = int(self.yposition*0.9)
			else:
				frame.update()
				self._usableWidth = frame.winfo_width()
				self._usableHeight = frame.winfo_height()
				self._usableXposition = frame.winfo_rootx()
				self._usableYposition = frame.winfo_rooty()
				frame.destroy()
			self._areUsableSet = True

	def __str__(self):
		out = ''.join([str(self._width), 'x', str(self._height), '+', \
						str(self._xposition), '+', str(self._yposition)])
		return out

	@property
	def usable(self):
		self._getUsableScreen()
		out = ''.join([str(self._usableWidth), 'x', str(self._usableHeight), '+', \
						str(self._usableXposition), '+', str(self._usableYposition)])
		return out

	def isWidgetInScreen(self, widget):
		widget.update()
		xposition = widget.winfo_rootx() - self.xposition
		yposition = widget.winfo_rooty() - self.yposition
		return xposition  >= 0 \
		and xposition < self.width \
		and yposition >= 0 \
		and yposition < self.height

	def centerFrame(self, frame):
		newx = (self.usableWidth-frame.winfo_reqwidth())//2 + self.usableXposition
		newy = (self.usableHeight-frame.winfo_reqheight())//2 + self.usableYposition
		frame.geometry('+%d+%d'%(newx, newy))

	def resizeFrame(self, frame, width, height):
		newWidth = min(self.usableWidth, width)
		newHeight = min(self.usableHeight, height)
		clipx = self.usableWidth-newWidth+self.usableXposition
		clipy = self.usableHeight-newHeight+self.usableYposition
		newx = max(min(frame.winfo_x(), clipx), self.usableXposition)-1
		newy = max(min(frame.winfo_y(), clipy), self.usableYposition)-1
		frame.geometry('%dx%d+%d+%d'%(newWidth, newHeight, newx, newy))

	def chooseOrientation(self, ratio, decal_w, decal_h):
		use_w = self.usableWidth-decal_w
		use_h = self.usableHeight-decal_h
		use_ratio = use_w/use_h
		if use_ratio < ratio:
			return tk.TOP
		else:
			return tk.LEFT

	def fullScreen(self, frame):
		frame.geometry(str(self))
		if globalvar.myOs == 'ubuntu':
			frame.attributes("-fullscreen", True)
		if globalvar.myOs == 'darwin':
			frame.tk.call("::tk::unsupported::MacWindowStyle", "style", frame._w, "plain", "none")
			frame.update_idletasks()
			frame.wm_attributes("-fullscreen", True)
		else:
			frame.overrideredirect(1)
		print('Fullscreen on: %s'%str(self))

	def __repr__(self):
		return repr(str(self))

class Screens(object):
	def __init__(self):
		self._screens = []
		self._maxScreens = sys.maxsize

	def centerFrame(self, frame):
		if hasattr(frame, 'master') and frame.master:
			for screen in self._screens:
				if screen.isWidgetInScreen(frame.master):
					screen.centerFrame(frame)
					break
		else:
			self._screens[0].centerFrame(frame)

	def resizeFrame(self, frame, width, height):
		for screen in self._screens:
			if screen.isWidgetInScreen(frame):
				screen.resizeFrame(frame, width, height)
				break

	def fullScreen(self, frame):
		self[-1].fullScreen(frame)

	def __getitem__(self, index):
		if index > len(self):
			raise IndexError
		return self._screens[(index%len(self))%self._maxScreens]

	def __len__(self):
		if len(self._screens) == 0:
			self.update()
		return len(self._screens)

	@property
	def maxScreens(self):
		return self._maxScreens

	@maxScreens.setter
	def maxScreens(self, value):
		self._maxScreens = int(value)

	def update(self, referenceWidget=None, verbose=True):
		del self._screens[:]
		try:
			monitors = screeninfo.get_monitors()
		except (NotImplementedError, NameError):
			monitors = []
		if len(monitors) > 0:
			for monitor in monitors:
				self._screens.append(Screen(monitor.width, \
									monitor.height, \
									monitor.x, monitor.y))
		else:
			warnings.warn('Screeninfo did not output any screen infos')
			if globalvar.myOs == 'windows':
				self._getWindowsScreens()
			elif globalvar.myOs == 'ubuntu':
				self._getLinuxScreens()
			elif globalvar.myOs == 'darwin':
				self._getMacOsScreens()
			else:
				warnings.warn("No screen found, OS is not supported.")
				self._getLinuxScreens()

		self._screens = [screen for screen in self._screens if screen]

		if referenceWidget:
			self._reorder(referenceWidget)
		if verbose:
			print("Using %d screens: "%len(self._screens))
			for screen in self._screens:
				print('	Full: %s, Usable: %s'%(str(screen), screen.usable))

	def _reorder(self, referenceWidget):
		for i,screen in enumerate(self._screens):
			if screen.isWidgetInScreen(referenceWidget):
				self._screens[0], self._screens[i] = self._screens[i], self._screens[0]
				break

	def _getLinuxScreens(self):
		if not self._getXrandrScreen():
			if not self._getByTopLevelScreens():
				self._getDefaultScreen()

	def _getWindowsScreens(self):
		if not self._getWindowsTopLevelScreens():
			self._getDefaultScreen()

	def _getMacOsScreens(self):
		if not self._getXrandrScreen():
			if not self._getWindowServerScreens():
				if not self._getSystemProfilerScreens():
					if not self._getByTopLevelScreens():
						self._getDefaultScreen()

	def _getDefaultScreen(self):
		self._screens.append(Screen(width=720, height=480))

	def _getXrandrScreen(self):
		xrandr = commandLine.MyCommand('xrandr')
		try:
			xrandr.checkCommand()
		except exception.CommandLineError:
			return False
		else:
			code, out, err = xrandr.run(['|', 'grep \\*', '|', "cut -d' ' -f4"])
			if code != 0:
				warnings.warn("Erreur de detection des ecrans\nError %s\n%s"%(str(code), err))
				return False
			liste_res = out.strip('\n').splitlines()
			if '' in liste_res:
				liste_res.remove('')
			if not liste_res:
				liste_res = []
				code, out, err = xrandr.run(['|', 'grep connected'])
				if code != 0:
					warnings.warn("Erreur de detection des ecrans\nError %s\n%s"%(str(code), err))
					return False
				line_res = out.replace('\n', '')
				deb = line_res.find('connected')
				fin = line_res.find('+', deb+1)
				deb = line_res.rfind(' ', 0, fin)
				liste_res.append(line_res[deb+1: fin])

			code, out, err = xrandr.run()
			if code != 0:
				warnings.warn("Erreur de detection des ecrans: Error %s"%str(code) + "\n" + err)
				return False
			deb = 0
			liste_respos = []
			for res in liste_res:
				deb = out.find(res + '+', deb)
				fin = out.find(' ', deb)
				self._screens.append(Screen(stringScreen=out[deb:fin]))
				deb = fin + 1
		return True

	def _getWindowsTopLevelScreens(self):
		try:
			test = tk.Toplevel()
		except tk.TclError:
			return False
		else:
			test.wm_attributes('-alpha', 0)
			test.withdraw()
			test.update_idletasks()
			test.overrideredirect(1)
			test.state('zoomed')
			test.withdraw()
			w1 = test.winfo_width()
			h1 = test.winfo_height()
			posw1 = test.winfo_x()
			posh1 = test.winfo_y()
			test.state('normal')
			test.withdraw()
			self._screens.append(Screen(w1, h1, posw1, posh1))
			# Scan for second screen
			test.overrideredirect(1)
			for decal in [[w, h] for w in [w1, w1//2, -w1//8] for h in [h1//2, h1, -h1//8]]:
				test.geometry("%dx%d+%d+%d"%(w1//8, h1//8, decal[0], decal[1]))
				test.update_idletasks()
				test.state('zoomed')
				test.withdraw()
				if test.winfo_x() != posw1 or test.winfo_y() != posh1:
					newW = test.winfo_width()
					newH = test.winfo_height()
					newPosW = test.winfo_x()
					newPosH = test.winfo_y()
					self._screens.append(Screen(width=newW, height=newH, \
								xposition=newPosW, yposition=newPosH))
				test.state('normal')
				test.withdraw()
			test.destroy()
			return True

	def _getWindowServerScreens(self):
		read = commandLine.MyCommand('defaults read')
		try:
			read.checkCommand()
		except exception.CommandLineError:
			return False
		code, out, err = read.run(['/Library/Preferences/com.apple.windowserver.plist'])
		if code != 0:
			warnings.warn("Erreur de detection des ecrans\nError %s\n%s"%(str(code), err))
			return False
		return False

	def _getSystemProfilerScreens(self):
		systemProfiler = commandLine.MyCommand('system_profiler')
		try:
			systemProfiler.checkCommand()
		except exception.CommandLineError:
			return False
		keyWord = 'Resolution:'
		code, out, err = systemProfiler.run(['SPDisplaysDataType', '|', 'grep', keyWord])
		if code != 0:
			warnings.warn("Erreur de detection des ecrans\nError %s\n%s"%(str(code), err))
			return False
		widthOffset = 0
		heightOffset = 0
		for line in [line for line in out.split('\n') if line]:
			deb = line.find(keyWord) + len(keyWord)
			end = line.find('x', deb)
			width = line[deb:end].strip(' ')
			height = line[end+1:line.find(' ', end+2)].strip(' ')
			self._screens.append(Screen(width=width, height=height, \
							xposition=widthOffset, yposition=heightOffset))
			widthOffset = width
		return True

	def _getByTopLevelScreens(self):
		try:
			test = tk.Toplevel()
		except tk.TclError:
			return False
		else:
			test.wm_attributes('-alpha', 0)
			test.withdraw()
			test.update_idletasks()

			posw1 = test.winfo_x()
			posh1 = test.winfo_y()
			scrW = test.winfo_screenwidth()
			scrH = test.winfo_screenheight()
			test.destroy()
			if scrW > 31*scrH//9:
				scrW = scrW//2
			elif scrW < 5*scrH//4:
				scrH = scrH//2
			self._screens.append(Screen(width=scrW, height=scrH))
			return True

def getRatio(ratio, default=None):
	try:
		a, b = ratio.split('/')
		value = round(int(a)/int(b), 3)
	except (ValueError, AttributeError):
		if default:
			value = default
		else:
			value = 16/9
	return value
