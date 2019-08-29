# -*- coding: utf-8 -*-
from __future__ import division

import time

from songfinder.elements import elements
from songfinder import classDiapo
from songfinder import exception
from songfinder import classSettings as settings

class DiapoList(object):
	def __init__(self, elementList=(), guiUpdate=None, loadCallbacks=(), isLoadAlowed=lambda:True):
		self._elementList = elementList
		self._emptyDiapo = classDiapo.Diapo(elements.Element(), 0, settings.GENSETTINGS.get('Syntax', 'newslide')[0], 90)
		self._diapos = []
		self._element2diapo = []
		self._diapo2element = []
		self._diapoNum = 0
		self._upToDate = False

		self._guiUpdate = guiUpdate
		self._loadCallbacks = list(loadCallbacks)
		self._isLoadAlowed = isLoadAlowed

	@property
	def list(self):
		self._constructLists()
		return self._diapos

	def _constructLists(self):
		if not self._upToDate and self._elementList:
			del self._diapos[:]
			del self._element2diapo[:]
			del self._diapo2element[:]
			self._element2diapo.append(0)
			previous = 'empty'
			for i, element in enumerate(self._elementList):
				if element.etype != 'image' or previous != 'image':
					self._diapos += [self._emptyDiapo]
					self._diapo2element += [i]
				self._diapos += element.diapos
				self._element2diapo.append(len(self._diapos))
				self._diapo2element += [i]*len(element.diapos)
				previous = element.etype
			self._diapo2element.append(len(self._elementList)-1)
			self._diapos += [self._emptyDiapo]
		self._upToDate = True
		return self._diapos

	def __len__(self):
		return len(self.list)

	def prefetch(self, themes, callback=None, args=()):
		tmp = time.time()
		self._constructLists()
		for diapo in reversed(self._diapos):
			diapo.prefetch(themes, text=False)
			if callback:
				callback(*args)
		print('Image prefetching time: %f'%(time.time()-tmp))

	def incremente(self, event=None):
		self._diapoNum = min(self._diapoNum+1, len(self)-1)
		if self._guiUpdate:
			self._guiUpdate()

	def decremente(self, event=None):
		self._diapoNum = max(self._diapoNum-1, 0)
		if self._guiUpdate:
			self._guiUpdate()

	@property
	def diapoNumber(self):
		return self._diapoNum

	@diapoNumber.setter
	def diapoNumber(self, num):
		if num >= len(self) and num < 0:
			raise exception.DiapoError(num)
		self._diapoNum = num

	@property
	def elementNumber(self):
		self._constructLists()
		return self._diapo2element[self._diapoNum]

	@elementNumber.setter
	def elementNumber(self, value):
		self._constructLists()
		self.diapoNumber = self._element2diapo[value]

	def bindGuiUpdate(self, function):
		self._guiUpdate = function

	def bindloadCallback(self, function):
		self._loadCallbacks.append(function)

	def bindIsLoadAlowed(self, function):
		self._isLoadAlowed = function

	def load(self, elementList):
		if self._isLoadAlowed():
			newElementList = [element for element in elementList if element]
			oldNames = set([element.nom for element in self._elementList])
			newNames = set([element.nom for element in newElementList])
			if len(oldNames & newNames)/len(oldNames | newNames) > 0.5:
				currentElem = self.elementNumber
				currentElemDiapo = self.diapoNumber - self._element2diapo[currentElem]
				currentElemName = self._elementList[currentElem].nom
				self._elementList = newElementList
				self._upToDate = False
				self._constructLists()
				for i,element in enumerate(self._elementList):
					if element.nom == currentElemName:
						if self._element2diapo[i+1] - self._element2diapo[i] > currentElemDiapo:
							self.diapoNumber = self._element2diapo[i] + currentElemDiapo
							break
			else:
				self._elementList = newElementList
				self._upToDate = False
				self.diapoNumber = 0
			for callback in  self._loadCallbacks:
				callback()

	def resetText(self):
		for element in self._elementList:
			element.resetText()
		self._upToDate = False

	def __getitem__(self, key):
		self._constructLists()
		num = self._diapoNum+key
		if num < len(self) and num >= 0:
			output = self._diapos[num]
		else:
			output = self._emptyDiapo
		return output

	def bindFrameEvent(self, frame):
		globalBindings = {"<Left>":self.decremente, \
						"<Right>":self.incremente, \
						"<Prior>":self.decremente, \
						"<Next>":self.incremente}
		bindingsObjects = {key:frame.bind_all(key, value) for key,value in globalBindings.items()}
