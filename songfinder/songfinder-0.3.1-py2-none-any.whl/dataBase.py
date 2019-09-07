# -*- coding: utf-8 -*-
#cython: language_level=2
from __future__ import unicode_literals
from __future__ import division

import os
import importlib

from songfinder import globalvar

try:
	fileName = os.path.splitext( os.path.split(__file__)[1] )[0]
	module = importlib.import_module('%s.lib.%s_%s'%(globalvar.appName, fileName, globalvar.arch))
	print("Using compiled version %s module"%fileName)
	globals().update(
		{n: getattr(module, n) for n in module.__all__} if hasattr(module, '__all__')
		else
		{k: v for (k, v) in module.__dict__.items() if not k.startswith('_')
	})
except (ImportError, NameError):
	# print(traceback.format_exc())

	import warnings
	import time
	try:
		import cython
	except ImportError:
		pass

	from songfinder.elements import elements
	from songfinder import classPaths
	from songfinder import fonctions as fonc
	from songfinder import gestchant
	from songfinder import classSettings as settings

	class DataBase(object):
		def __init__(self, songPath=None, **kwargs):
			self._sizeMax = 3
			if songPath:
				self._songPath = songPath
			else:
				self._songPath = classPaths.PATHS.songs
			self._mergedDataBases = []
			self._maxCustomNumber = 0
			self.update()

		def __contains__(self, value):
			return value in self._dicoLyrics.keys()

		def __getitem__(self, key):
			return self._dicoLyrics[key]

		def keys(self):
			return self._dicoLyrics.keys()

		def __iter__(self):
			return iter(self._dicoLyrics)

		def remove(self, song):
			del self._dicoLyrics[song]
			del self._dicoTitles[song]
			for num in song.nums.values():
				if num:
					self._dicoNums[num].remove(song)

		def add(self, song):
			self._dicoLyrics[song] = self._getStrings('%s %s'%(song.title, song.text))
			self._dicoTitles[song] = self._getStrings(song.title)
			self.addDictNums(song)
			if song.songBook == 'SUP' \
				and song.customNumber > self._maxCustomNumber:
				self._maxCustomNumber = song.customNumber

		def addDictNums(self, song):
			for num in [num for num in song.nums.values() if num]:
				try:
					self._dicoNums[num].add(song)
				except KeyError:
					self._dicoNums[num] = set([song])

		def getDico(self, whichOne):
			if whichOne == 'lyrics':
				return self._dicoLyrics
			elif whichOne == 'titles':
				return self._dicoTitles
			elif whichOne == 'nums':
				return self._dicoNums
			else:
				warnings.warn('Don\'t know which dico to return.'
							'You asked for %s, possible values '
							'are "lyrics" and "titles".'%whichOne )
				return  dict()

		def update(self, callback=None, args=()):
			tmpsRef = time.time()
			self._dicoLyrics = dict()
			self._dicoTitles = dict()
			self._dicoNums = dict()
			self._findSongs(callback, args)
			print('Updated dataBase in %fs, %d songs'%(time.time()-tmpsRef, len(self)))
			self._merge(update=True)

		def _findSongs(self, callback, args):
			extChant = settings.GENSETTINGS.get('Extentions', 'chant') \
						+ settings.GENSETTINGS.get('Extentions', 'chordpro')
			exclude = ['LSG', 'DAR', 'SEM', 'KJV', ]
			counter = 0
			if self._songPath:
				for root, _, files in os.walk(self._songPath):
					for fichier in files:
						path = os.path.join(root, fichier)
						if (path).find(os.sep + '.') == -1 \
								and fonc.get_ext(fichier) in extChant \
								and fichier not in exclude:
							newChant = elements.Chant( os.path.join(root, fichier)) # About 2/3 of the time
							# ~ newChant._replaceInText('raDieux', 'radieux')
							if newChant.exist(): # About 1/3 of the time
								self.add(newChant)
								self.addDictNums(newChant)
							if callback:
								callback(*args)
							counter += 1

		def _getStrings(self, paroles):
			try:
				i = cython.declare(cython.int)
				size = cython.declare(cython.int)
				nb_mots = cython.declare(cython.int)
			except NameError:
				pass

			paroles = gestchant.netoyage_paroles(paroles) # Half the time

			list_mots = paroles.split()
			nb_mots = len(list_mots)-1

			outPut = [paroles.replace(' ', ';')] # First word list can be done faster with replace
			for size in range(1, self._sizeMax): # Half the time
				addList = [ ' '.join(list_mots[i:i+size+1]) for i in range(max(nb_mots-size, 0)) ]
				addList.append( ' '.join(list_mots[-size-1:]) )
				outPut.append(';'.join(addList))
			return outPut

		def __len__(self):
			return len(self._dicoLyrics)

		@property
		def maxCustomNumber(self):
			return self._maxCustomNumber

		def merge(self, others):
			self._mergedDataBases += others
			self._merge()

		def _merge(self, update=False):
			if self._mergedDataBases:
				tmpsRef = time.time()
				for dataBase in self._mergedDataBases:
					if update:
						dataBase.update()
					tmp = list(self.keys())
					for song in dataBase:
						if not song in tmp:
							self.add(song)
						else:
							tmp.remove(song)
				print('Merged %d dataBase in %fs, %d songs'%(len(self._mergedDataBases)+1, time.time()-tmpsRef, len(self)))

		def removeExtraDatabases(self, update=False):
			del self._mergedDataBases[:]
			if update:
				self.update()
