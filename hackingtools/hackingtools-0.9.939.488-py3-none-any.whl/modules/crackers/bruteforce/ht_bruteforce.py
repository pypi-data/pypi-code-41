from hackingtools.core import Logger, Utils, Config
import hackingtools as ht
import os

import progressbar

config = Config.getConfig(parentKey='modules', key='ht_bruteforce')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

	def __init__(self):
		Utils.emptyDirectory(output_dir)
		pass

	def help(self):
		Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_bruteforce'))

	def crackZip(self, zipPathName, alphabet='lalpha', consecutive=True, log=False):
		word_length = 4
		unzipper = ht.getModule('ht_unzip')
		tested = []
		if log:
			Logger.setDebugCore(True)
		texts = Utils.getDict(length=word_length, alphabet=alphabet, consecutive=consecutive)
		password = None
		while not password:
			for text in texts:
				if not text in tested:
					tested.append(text)
					if os.path.isfile(zipPathName):
						password = unzipper.extractFile(zipPathName, text, posible_combinations=len(texts))
					else:
						print('File doesnt exists {a}'.format(a=zipPathName))
						break
					if password:
						break
			Logger.setDebugCore(True)
			return password
		Logger.setDebugCore(True)
		return password