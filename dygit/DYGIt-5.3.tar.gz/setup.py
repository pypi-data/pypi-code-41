from distutils.core import setup
import os 
import pip
import subprocess
import shutil
try:
	__import__('curses')
except ImportError:
	if os.name == 'nt':
		subprocess.check_call(["python", '-m', 'pip', 'install', 'windows-curses'])
	else:
		pass
from os.path import expanduser
home = expanduser("~/")
with open("README.txt") as f:
	desc = f.read()
setup(
	name="DYGIt",
	version="5.3",
	packages=['DYGI',],
	scripts=['DYGI/DYGIt.py'],
	author='Mason Lapine',
    author_email='masonlapine@gmail.com',
    license='MIT',
    description='A text based email client for those of us without a UI.',
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/myson1515/DYGI',
	install_requires=[
		'npyscreen',
		'httplib2',
		'wheel',
	]
	)
truepath = os.path.join(home, ".DYGIdep/")
#print truepath
basedir = os.path.dirname(truepath)
#print str(basedir)
if os.name == 'nt':
	print "Creating email files..."
	if os.path.exists(basedir):
		shutil.rmtree(basedir)
	os.makedirs(basedir)
	os.system("pip install windows-curses")
	os.system("cd " + basedir + " && copy NUL results.txt folders.txt ID.txt emails.txt DEBUG.txt email.txt currentFolder.txt log.txt")
	os.system("cd " + basedir + " && copy NUL color.txt")
	os.system("cd " + basedir + " && copy NUL Date.txt")
	os.system("cd " + basedir + " && copy NUL emailNum.txt")
	with open(home + "/.DYGIdep/color.txt", "w") as f:
		f.write("DEFAULT")
	#os.system("cd C:/Python/Lib/site-packages/windows-curses && build-wheels.bat 2.7")
	print "Done."

	
else: 
	if os.path.exists(basedir):
		shutil.rmtree(basedir)
	print "Creating email files..."
	os.makedirs(basedir)
	os.system("touch ~/.DYGIdep/color.txt ~/.DYGIdep/results.txt ~/.DYGIdep/emailNum.txt ~/.DYGIdep/Date.txt ~/.DYGIdep/folders.txt ~/.DYGIdep/log.txt ~/.DYGIdep/ID.txt ~/.DYGIdep/emails.txt ~/.DYGIdep/DEBUG.txt ~/.DYGIdep/currentFolder.txt ~/.DYGIdep/email.txt")
	with open(home + "/.DYGIdep/color.txt", "w") as f:
		f.write("DEFAULT")
	print "Done."
		

	
