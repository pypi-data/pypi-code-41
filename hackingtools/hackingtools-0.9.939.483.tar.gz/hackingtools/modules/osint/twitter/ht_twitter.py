from hackingtools.core import Logger, Utils, Config
global ht
import os

config = Config.getConfig(parentKey='modules', key='ht_twitter')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

	def __init__(self):
		pass

	def help(self):
		Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_twitter'))
