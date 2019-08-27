# -*- coding: utf-8 -*-

__version__ = "0.2.14"
__author__ = "danbei"
__appName_ = "songfinder"


try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk
import os
import warnings
import traceback

from songfinder import screen
from songfinder import splash
from songfinder import globalvar

def _gui(fenetre, fileIn=None):
	# Creat main window and splash icon
	from songfinder import guiHelper
	screens = screen.Screens()
	with guiHelper.SmoothWindowCreation(fenetre, screens):
		screens.update(referenceWidget=fenetre)

		with splash.Splash(fenetre, os.path.join(globalvar.dataPath, 'icon.png'), 0, screens):
			# Compile cython file and cmodules
			if not globalvar.portable:
				try:
					import subprocess
					import distutils.spawn
					python = distutils.spawn.find_executable('python')
					if python:
						command = python + ' setup_cython.py build_ext --inplace'
						proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
						out, err = proc.communicate()
						if out:
							print(out)
							print(err)
				except Exception: # pylint: disable=broad-except
					warnings.warn(traceback.format_exc())

			from PIL import ImageTk
			from songfinder import interface

			# Set bar icon
			try:
				if os.name == 'posix':
					img = ImageTk.PhotoImage(file = os.path.join(globalvar.dataPath, 'icon.png') )
					fenetre.tk.call('wm', 'iconphoto', fenetre._w, img)
				else:
					fenetre.iconbitmap( os.path.join(globalvar.dataPath, 'icon.ico'))
			except Exception: # pylint: disable=broad-except
				warnings.warn(traceback.format_exc())
			if fileIn :
				fileIn = fileIn[0]
			songFinder = interface.Interface(fenetre, screens=screens, fileIn=fileIn)
			fenetre.title('SongFinder')
			fenetre.protocol("WM_DELETE_WINDOW", songFinder.quit)

	songFinder.__syncPath__() # TODO This is a hack
	fenetre.mainloop()

def _webServer():
	from songfinder import webServer
	server = webServer.FlaskServer()
	server.run()

def _song2markdown(fileIn, fileOut):
	from songfinder import fileConverter
	converter = fileConverter.Converter()
	converter.makeSubDirOn()
	converter.markdown(fileIn, fileOut)

def _song2html(fileIn, fileOut):
	from songfinder import fileConverter
	converter = fileConverter.Converter()
	converter.makeSubDirOn()
	converter.html(fileIn, fileOut)

def _parseArgs():
	import argparse
	arg_parser = argparse.ArgumentParser()
	arg_parser = argparse.ArgumentParser(description="%s v%s"% (globalvar.appName, __version__),
									formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	arg_parser.add_argument("-f", "--file",
						nargs=1,
						metavar=('inputFile',),
						help="Song file or set file to open")

	arg_parser.add_argument("-m", "--songtomarkdown",
						nargs=2,
						metavar=('song[File/Dir]', 'markdown[File/Dir]'),
						help="Convert song file (xml or chordpro) files to markdown file")

	arg_parser.add_argument("-t", "--songtohtml",
						nargs=2,
						metavar=('song[File/Dir]', 'html[File/Dir]'),
						help="Convert song file (xml or chordpro) files to html file")

	arg_parser.add_argument("-w", "--webserver",
						action="store_true",
						default=False,
						help="Launch songfinder webserver")

	arg_parser.add_argument("--version",
						action="store_true",
						default=False,
						help="Print songfinder version")

	arg_parser.add_argument("-v", "--verbosity",
						type=int, choices=[0, 1, 2],
						help="Increase output verbosity")

	return arg_parser.parse_args()

def songFinderMain():
	args = _parseArgs()
	if args.webserver:
		_webServer()
	elif args.songtomarkdown:
		_song2markdown(*args.songtomarkdown)
	elif args.songtohtml:
		_song2html(*args.songtohtml)
	elif args.version:
		print('%s v.%s by %s'%(__appName_, __version__, __author__))
	else:
		fenetre = tk.Tk()
		try:
			_gui(fenetre, fileIn=args.file)
		except SystemExit:
			raise
		except:
			import sys
			if not getattr(sys, "frozen", False):
				from songfinder import messages as tkMessageBox
				tkMessageBox.showerror('Erreur', traceback.format_exc())
			raise

if __name__ == '__main__':
	songFinderMain()
