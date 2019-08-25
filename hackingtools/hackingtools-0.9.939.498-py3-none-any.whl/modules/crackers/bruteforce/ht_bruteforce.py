from hackingtools.core import Logger, Utils, Config
import hackingtools as ht
import os

import time
import progressbar
import numpy

config = Config.getConfig(parentKey='modules', key='ht_bruteforce')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

	def __init__(self):
		Utils.emptyDirectory(output_dir)
		pass

	def help(self):
		Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_bruteforce'))

	def crackZip(self, zipPathName, unzipper=None, alphabet='lalpha', password_length=4, consecutive=True, log=False):
		if not unzipper:
			unzipper = ht.getModule('ht_unzip')
		if log:
			Logger.setDebugCore(True)
		texts = Utils.getDict(length=int(password_length), alphabet=alphabet, consecutive=consecutive)
		passwords = []
		texts_list = numpy.array_split(texts,10000)
		for index_t_list, t_list in enumerate(texts_list):
			Logger.printMessage(message='crackZip', description='Chunk {n}'.format(n=index_t_list))
			for text in t_list:
				if os.path.isfile(zipPathName):
					password = unzipper.extractFile(zipPathName, text, posible_combinations=len(texts))
				else:
					Logger.printMessage(message='crackZip', description='File doesnt exists {a}'.format(a=zipPathName), is_error=True)
					break
				if password:
					passwords.append(password)
		Logger.setDebugCore(False)
		return passwords