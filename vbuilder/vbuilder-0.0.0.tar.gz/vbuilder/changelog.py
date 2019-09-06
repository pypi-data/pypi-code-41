import subprocess
import re


class Changelog(object):

	def __init__(self, path):

		self.path = path

	def list_version(self):

		hasil = []

		with open(self.path, 'r') as out:
			for line in out:
				if line[:8] == 'Version:':
					text = re.sub('[^0-9\\.]', '', line)
					hasil.append(text)

		return hasil


class Version(object):

	def __init__(self):
		pass

	def get_branch(self):
		hasil = subprocess.check_output(["git", "branch"])

	def count_commit(self):

		pass






if __name__ == '__main__':
	
	change = Changelog('changelog.txt.example')
	change.list_version()






