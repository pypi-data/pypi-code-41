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

	def crackZip(self, zipPathName, alphabet='lalpha', password_length=4, consecutive=True, log=False):
		unzipper = ht.getModule('ht_unzip')
		tested = []
		if log:
			Logger.setDebugCore(True)
		texts = Utils.getDict(length=int(password_length), alphabet=alphabet, consecutive=consecutive)
		passwords = []
		count = 0
		while count <= len(texts):
			for text in texts:
				if not text in tested:
					tested.append(text)
					if os.path.isfile(zipPathName):
						password = unzipper.extractFile(zipPathName, text, posible_combinations=len(texts))
					else:
						print('File doesnt exists {a}'.format(a=zipPathName))
						break
					if password:
						passwords.append(password)
						count += 1
			Logger.setDebugCore(True)
			return passwords
		Logger.setDebugCore(True)
		return passwords