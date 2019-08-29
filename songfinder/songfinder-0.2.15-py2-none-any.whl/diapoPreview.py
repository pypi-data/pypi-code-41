# ~ # -*- coding: utf-8 -*-
# ~ from __future__ import division

# ~ import tkFont
# ~ import Tkinter as tk
# ~ import math
# ~ import warnings
# ~ import time
# ~ import traceback
# ~ import gc

# ~ import src.elements.elements as elements
# ~ import src.screen as screen
# ~ import globalvar as globalvar
# ~ import src.diapo as classDiapo
# ~ import src.themes as themes
# ~ import src.simpleProgress as simpleProgress
# ~ import src.diapoListGui as diapoListGui


# ~ class Presentation(object):
	# ~ def __init__(self, frame, **kwargs):
		# ~ tmpsTotal=time.time()
		# ~ Frame.__init__(self, fenetre, **kwargs)
		# ~ self._parent = parent

		# ~ self.fen_player = None
		# ~ self.videopanel = None
		# ~ self.player = None
		# ~ self.sub = globalvar.genSettings.get('Parameters', 'size_of_previews')

		# ~ self._diapoList = diapoList

		# ~ # Fenetre de presentation
		# ~ self.fen_pres = Toplevel(self)
		# ~ self.fen_pres.withdraw()
		# ~ self.fen_pres.title("Presentation")
		# ~ if globalvar.myOs == 'ubuntu':
			# ~ self.fen_pres.attributes("-fullscreen", True)
		# ~ else:
			# ~ self.fen_pres.overrideredirect(1)
		# ~ self.fen_pres.protocol("WM_DELETE_WINDOW", self.quit)
		# ~ self.nb_screen, self.screen1, self.screen2, self.screen1use = screen.number_screen() ## very Slow

		# ~ ratio_impose = screen.getRatio(globalvar.genSettings.get('Parameters', 'ratio'), self.screen2.ratio)
		# ~ self.fen_pres.geometry(self.screen2.full)
		# ~ if ratio_impose != 0:
			# ~ self.screen2.set_w( int(math.floor(min(ratio_impose*self.screen2.h, self.screen2.w))) )
			# ~ self.screen2.set_h( int(math.floor(min(self.screen2.w//ratio_impose, self.screen2.h))) )

		# ~ self._themePres = themes.Theme(self.fen_pres, width=self.screen2.w, height=self.screen2.h, bg='black')
		# ~ self._themePres.pack(side=TOP, fill=BOTH, expand=1)
		# ~ listToPrefetch = [self._themePres]

		# ~ print("Nombre d'ecrans: %d -- Resolutions: %s (%s)- %s"\
				# ~ %(self.nb_screen, self.screen1, self.screen1use, self.screen2))

		# ~ # Gestion liste
		# ~ if self.nb_screen > 1:
			# ~ self.fen_gestion = Toplevel(self)
			# ~ self.fen_gestion.withdraw()
			# ~ self.fen_gestion.title("Gestion diapositives")
			# ~ self.fen_gestion.resizable(True,True)
			# ~ self.fen_gestion.update_idletasks()
			# ~ self.fen_gestion.protocol("WM_DELETE_WINDOW", self.quit)
			# ~ listSubFrame = Frame(self.fen_gestion)
			# ~ previewSubFrame = Frame(self.fen_gestion)

		# ~ ########
			# ~ self._themePrev1 = themes.Theme(previewSubFrame)
			# ~ self._themePrev1.pack(side=TOP)
			# ~ self._themePrev2 = themes.Theme(previewSubFrame)
			# ~ self._themePrev2.pack(side=TOP)
			# ~ listToPrefetch.append(self._themePrev1)
			# ~ listToPrefetch.append(self._themePrev2)
		# ~ ########

			# ~ self._listGui = diapoListGui.DiapoListGui(listSubFrame, self._diapoList, \
												# ~ callback=self.printer, args=[])
			# ~ listSubFrame.pack(side=LEFT, fill=BOTH, expand=1)

			# ~ self.slider = Scale(self.fen_gestion, from_=0.3, to=3, resolution=0.1, length=300, orient=VERTICAL)
			# ~ self.slider.pack(side=LEFT)
			# ~ self.slider.set(globalvar.genSettings.get('Parameters', 'size_of_previews'))

			# ~ previewSubFrame.pack(side=LEFT, fill=BOTH, expand=1)

			# ~ self.fen_gestion.update()
			# ~ self.widthOffset = 	self._listGui.width() + \
								# ~ self.slider.winfo_reqwidth()
			# ~ self.previewWidth = min((self.screen1use.w-self.widthOffset), self.screen1use.h*self.screen2.ratio)
			# ~ self.previewHeight = self.previewWidth/self.screen2.ratio

			# ~ self.orient = screen.choose_orient(self.screen1use, self.screen2.ratio, \
												# ~ self.widthOffset, 0)

			# ~ self.w_g = self.fen_gestion.winfo_reqwidth()
			# ~ self.h_g = self.fen_gestion.winfo_reqheight()
			# ~ self.fen_gestion.geometry(screen.Screen(self.w_g, self.h_g).full)
			# ~ self.fen_gestion.update()

			# ~ self.slider.bind("<ButtonRelease-1>", self._place_preview)

		# ~ globalBindings = {"<Left>":self._previousSlide, \
						# ~ "<Right>":self._nextSlide, \
						# ~ "<Prior>":self._previousSlide, \
						# ~ "<Next>":self._nextSlide, \
						# ~ "<Escape>":self.quit}
		# ~ self.bindingsObjects = {key:self.bind_all(key, value) for key,value in globalBindings.items()}
		# ~ self.fen_pres.bind("<Up>", self._previousSlide)
		# ~ self.fen_pres.bind("<Down>", self._nextSlide)
		# ~ self.fen_pres.bind("<Button-1>", self._nextSlide)
		# ~ self.fen_pres.bind("<Button-3>", self._previousSlide)

		# ~ if vlc and self.fen_player:
			# ~ self.fen_player.bind("<Up>", self._previousSlide)
			# ~ self.fen_player.bind("<Down>", self._nextSlide)
			# ~ self.fen_player.bind("<Button-1>", self._nextSlide)
			# ~ self.fen_player.bind("<Button-3>", self._previousSlide)

		# ~ elif self.nb_screen == 1:
			# ~ self._themePres.focus_set()

		# ~ ### Setting up diapo list
		# ~ progressBar = simpleProgress.SimpleProgress(self, "Création du cache des images", screen=self.screen1)
		# ~ progressBar.start(len(self._diapoList))
		# ~ self._diapoList.prefetch(listToPrefetch, progressBar.update)
		# ~ progressBar.stop()
		# ~ self._diapoList.getList(debut)
		# ~ ###

		# ~ if self.nb_screen > 1:
			# ~ self._place_preview()
			# ~ self.printer()
			# ~ listSubFrame.focus_set()
			# ~ self._listGui.write()
			# ~ self.fen_gestion.deiconify()
		# ~ self.fen_pres.deiconify()
		# ~ print("Temps creation presentation " + str(time.time()-tmpsTotal))


	# ~ def _previousSlide(self, event):
		# ~ self._diapoList.decremente()
		# ~ self.printer()

	# ~ def _nextSlide(self, event):
		# ~ self._diapoList.incremente()
		# ~ self.printer()

	# ~ def printer(self, event=None):
		# ~ self._quit_media()
		# ~ if self.nb_screen > 1:
			# ~ self._listGui.select()
		# ~ self._printer()
		# ~ self._prefetcher()

	# ~ def _printer(self):
		# ~ diapo = self._diapoList.current
		# ~ if self._themePres.name != diapo.themeName:
			# ~ self._themePres.destroy()
			# ~ self._themePres = themes.Theme(self.fen_pres, diapo.etype, width=self.screen2.w, height=self.screen2.h)
			# ~ self._themePres.pack(side=TOP, fill=BOTH, expand=1)
		# ~ diapo.printDiapo(self._themePres)

		# ~ if self.nb_screen > 1:
			# ~ if self._themePrev1.name != diapo.themeName:
				# ~ self._themePrev1.destroy()
				# ~ self._themePrev1 = themes.Theme(self.fen_gestion, diapo.etype)
				# ~ self._themePrev1.pack(side=self.orient)
			# ~ diapo.printDiapo(self._themePrev1)

			# ~ diapo = self._diapoList.next
			# ~ if self._themePrev2.name != diapo.themeName:
				# ~ self._themePrev2.destroy()
				# ~ self._themePrev2 = themes.Theme(self.fen_gestion, diapo.etype)
				# ~ self._themePrev2.pack(side=self.orient)
			# ~ diapo.printDiapo(self._themePrev2)

	# ~ def _prefetcher(self):
		# ~ themes = []
		# ~ if self.nb_screen > 1:
			# ~ themes.append(self._themePrev1)
		# ~ themes.append(self._themePres)
		# ~ self._diapoList.previous.prefetch(themes)
		# ~ if self.nb_screen > 1:
			# ~ self._diapoList.previous.prefetch([self._themePrev2])
		# ~ self._diapoList.next.prefetch(themes)
		# ~ if self.nb_screen > 1:
			# ~ self._diapoList.nextnext.prefetch([self._themePrev2])

	# ~ def _place_preview(self, event=None):
		# ~ try:
			# ~ self.sub = float(self.slider.get())
		# ~ except ValueError:
			# ~ warnings.warn('ValueError in place preview')
			# ~ self.sub = globalvar.genSettings.get('Parameters', 'size_of_previews')

		# ~ width = self.previewWidth/(1+self.sub)
		# ~ height = self.previewHeight/(1+self.sub)

		# ~ self._themePrev1.resize(width*self.sub, height*self.sub)
		# ~ self._themePrev2.resize(width, height)

		# ~ self._themePrev1.pack_forget()
		# ~ self._themePrev2.pack_forget()

		# ~ self._themePrev1.pack(side=self.orient)
		# ~ self._themePrev2.pack(side=self.orient)

		# ~ self.printer()
		# ~ self._resizeGestion()

	# ~ def _resizeGestion(self):
		# ~ try:
			# ~ self.fen_gestion.update_idletasks() # Seems to be necessary ?
			# ~ prev1Width = self._themePrev1.winfo_reqwidth()
			# ~ prev2Width = self._themePrev2.winfo_reqwidth()
			# ~ prev1Height = self._themePrev1.winfo_reqheight()
			# ~ prev2Height = self._themePrev2.winfo_reqheight()
			# ~ if self.orient == TOP:
				# ~ longueur = self.widthOffset + max(prev1Width, prev2Width)
				# ~ hauteur = prev1Height + prev2Height
			# ~ else:
				# ~ longueur = self.widthOffset + prev1Width + prev2Width
				# ~ hauteur = max(prev1Height, prev2Height)

			# ~ # On windows winfo_x and winfo_y are offset by -8 ?
			# ~ longueur = min(longueur, self.screen1use.w - self.fen_gestion.winfo_x()-9)
			# ~ hauteur = min(hauteur, self.screen1use.h - self.fen_gestion.winfo_y()-9)
			# ~ self.fen_gestion.geometry("%dx%d"%(longueur, hauteur))
		# ~ except:
			# ~ warnings.warn('Update_fen failed: %s'%traceback.format_exc())

	# ~ def _quit_media(self):
		# ~ if self.videopanel:
			# ~ self.videopanel.destroy()
			# ~ self.videopanel = None
		# ~ if self.player:
			# ~ self.player.timer.stop()
			# ~ self.player.OnStop()
			# ~ self.player.ctrlpanel.pack_forget()
			# ~ self.player.ctrlpanel2.pack_forget()
		# ~ if self.fen_player:
			# ~ self.fen_player.destroy()
			# ~ self.fen_player = None

	# ~ def quit(self, event=None):
		# ~ self._quit_media()
		# ~ for key,value in self.bindingsObjects.items():
			# ~ self.unbind(key, value)
		# ~ self._diapoList = None
		# ~ if self.nb_screen > 1:
			# ~ self.fen_gestion.destroy()
			# ~ self.fen_gestion = None
			# ~ globalvar.genSettings.set('Parameters', 'size_of_previews', str(self.sub))
		# ~ self.fen_pres.destroy()
		# ~ self.fen_pres = None
		# ~ self.destroy()
		# ~ self._parent.closePresentWindow()
		# ~ print('GC collected objects : %d' % gc.collect())

# -*- coding: utf-8 -*-
from __future__ import division

try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk

from songfinder import screen
from songfinder import themes
from songfinder import classSettings as settings


class Preview(object):
	def __init__(self, frame, diapoList, screens=None,\
					startingElement=0, **kwargs):

		self._frame = frame
		self._diapoList = diapoList

		if screens[0].width < 2000:
			self._previewSize = 300
		else:
			self._previewSize = 400

		self._previews = []

		self._frame.bind("<Button-1>", self._nextSlide)
		self._frame.bind("<Button-3>", self._previousSlide)
		self._frame.bind("<Configure>", self.updatePreviews)

		self.printer()

	def _previousSlide(self, event):
		self._diapoList.decremente()

	def _nextSlide(self, event):
		self._diapoList.incremente()

	def updatePreviews(self, event=None):
		ratio = screen.getRatio(settings.GENSETTINGS.get('Parameters', 'ratio'))
		previewCount = max(int(self._frame.winfo_height()//(self._previewSize/ratio)), 1)
		if len(self._previews) != previewCount:
			for theme in self._previews:
				theme.pack_forget()
			del self._previews[:]
			for _ in range(previewCount):
				theme = themes.Theme(self._frame, width=self._previewSize, height=self._previewSize/ratio)
				self._previews.append(theme)
				theme.pack(side=tk.TOP)
		self.printer()

	def printer(self):
		ratio = screen.getRatio(settings.GENSETTINGS.get('Parameters', 'ratio'))
		for i,theme in enumerate(self._previews):
			diapo = self._diapoList[i]
			if theme.name != diapo.themeName:
				theme.destroy()
				theme = themes.Theme(self._frame, diapo.etype, width=self._previewSize, height=self._previewSize/ratio)
				self._previews[i] = theme
				theme.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
			diapo.printDiapo(theme)
		self._prefetcher()

	def _prefetcher(self):
		self._diapoList[-1].prefetch(self._previews)
		self._diapoList[1].prefetch(self._previews)
