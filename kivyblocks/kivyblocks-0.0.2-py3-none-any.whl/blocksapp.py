
import os
import sys

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

from kivy.config import Config
from kivy.metrics import sp,dp
from kivy.core.window import WindowBase

import kivy
from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(__file__),'./ttf'))
Config.set('kivy', 'default_font', [
    'msgothic',
    'DroidSansFallback.ttf'])

from kivy.app import App
# from .baseWidget import baseWidgets
# from .widgetExt import Messager
# from .externalwidgetmanager import ExternalWidgetManager
from .threadcall import HttpClient,Workers
from .derivedWidget import buildWidget, loadUserDefinedWidget

class BlocksApp(App):
	myFontSizes = {
		"small":12,
		"normal":16,
		"large":20,
		"huge":24,
	}
	separatorsize = 2
	def build(self):
		config = getConfig()
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		self.workers.start()
		self.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
			
		if config.font_sizes:
			self.myFontSizes = config.font_sizes

		self.font_size = self.getFontSize(config.font_name)
		x = None
		loadUserDefinedWidget()
		if config.root:
			x = buildWidget(config.root)
			self.rootWidget = x
			return x
		raise Exception('please define root widget')
			
	def getFontSize(self,fontsizename):
		x = self.myFontSizes.get(fontsizename,None)
		if x == None:
			x = self.myFontSizes.get('normal')
		return x

	def textsize(self,x,y=None):
		if y is None:
			return sp(x * self.font_size)
		return (sp(int(x * self.font_size)), sp(int(y * self.font_size)))

	def buttonsize(self,x):
		m = int(0.6 * self.font_size)
		return (sp(int(self.font_size * x + m),
					sp(self.font_size + m )))
	def __del__(self):
		self.workers.running = False		
