import sys,os,re
sys.stderr.write('Starting setup pacbio scripts...\n')
if os.uname()[0]!="Linux":
	sys.stderr.write('unspporting system exit...\n')
########################
try:
	import SpliceGrapher
except:
	sys.stderr.write('installing SpliceGrapher...\n')
	os.chdir("scripts/SpliceGrapher-0.2.5")
	cmd="python setup.py install"
	os.system(cmd)
	os.chdir("../../")
#############
try:
	import numpy
except:
	sys.stderr.write('installing numpy...\n')
	cmd="conda install numpy"
	os.system(cmd)
##############
##############
try:
	import cairo
except:
	sys.stderr.write('installing cairo...\n')
	cmd="conda install cairo"
	os.system(cmd)
##############
sys.stderr.write('Please type where you want to install the Pacbio tools ...\n')
path= raw_input("Path: ")
##############
if not os.path.exists(path):
	os.makedirs(path)
sys.stderr.write('Do you want to write in the .bashrc ...\n')
###############
choice= raw_input("Your choice(Y/N): ")
if choice=="N":
	sys.exit()
home=os.environ['HOME']
out=open("%s/.bashrc"%(home),"a")
out.write("\n#added by pacbio soft\nexport PATH=$PATH:%s\n"%(path))
out.close()
###############
cmd="cp * %s"%(path)
os.system(cmd)
###############
sys.stderr.write('Installing complete...\n')
################
