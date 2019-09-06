#!python
# -*- coding utf-8 -*-

"""
m6A.py 0.1 -- pacbio Iso-Seq rna base modifications.

Usage: m6A.py [options]


Options:
    --version                   Show version.
    -h --help                   Show this screen.
    -f FOFN --fofn=FOFN         FOFN file contines bax.h5 files,: split libs.
    -a FASTA --fasta=FASTA      Genome files.
    -t THREAD --thread=THREAD   Thread use to align.
    -o OUT --output=OUT     outputs dirs,default output.
"""
__author__ = 'gyb'
__version__ = '0.1'
#from __future__ import division
import sys,os,re,cairo,time
from docopt import docopt
#####
def mk(fl):
	if not os.path.exists(fl):
		sys.stderr.write("Making %s\n"%(fl))
		os.makedirs(fl)
def exe(cmd):
	time_now = int(time.time())
	time_local = time.localtime(time_now)
	dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
	sys.stderr.write("%s\tExecute CMD\t%s\n"%(dt,cmd))
	try:
		os.system(cmd)
	except:
		sys.stderr.write("%s\tError while Execute%s!!!\n"%(dt,cmd))
if __name__=='__main__':
	if len(sys.argv)<4:
		sys.exit(__doc__)
	options = docopt(__doc__, version=__version__)
	######
	#	step1 align
	mk("%s/temp/"%(options['--output']))
	cmd="blasr %s  %s -sam -clipping soft -out %s/temp/align.sam -nproc 30"%(options['--fofn'],options['--fasta'],options['--output'],options['--thread'])
	exe(cmd)
	#	step2 samtoh5
	cmd="samtoh5  %s/temp/align.sam %s %s/temp/align.cmp.h5"%(options['--output'],options['--fasta'],options['--output'])
	exe(cmd)
	#	step3 add pusle
	cmd="loadPulses  %s %s/temp/align.cmp.h5"%(options['--fofn'],options['--output'])
	exe(cmd)
	# 	step4 run idp
	cmd="ipdSummary %s/temp/align.cmp.h5 --reference %s --identify m6A --methylFraction --gff %s/m6A.gff --csv %s/sam/m6A.csv"%(options['--output'],options['--fasta'],options['--output'],options['--output'])
	exe(cmd)
