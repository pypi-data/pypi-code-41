#!/usr/bin/env python
import sys,os,re
from  collections import defaultdict
##########
cluster_file=sys.argv[1]
outdir=sys.argv[2]
Output_dir=sys.argv[3]
tpd=sys.argv[4]
if not os.path.exists(outdir):
	os.makedirs(outdir)
####
sys.stderr.write('Reading Cluster file...\n')
cluster=open(cluster_file,'r')
mapdict=defaultdict(dict)
for line in cluster:
	line=line.strip('\n')
	name=line.split()[0]
	mapdict[name][line]=1
sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
##########
oFile = open(outdir+'/nat.txt', 'w'); ## alt-3 SS output file
oFileHeader = "ID\t";
oFile.write(oFileHeader+'\n');
###################################
barcount=-1
sys.stderr.write('complute nat ...\n')
natcount=-1
for i in mapdict:
	gene=i.split('.')[0]
	strand=list(set([x.split()[4] for x in mapdict[i]]))
	if len(strand)!=2:
		continue
	natcount+=1
	oFile.write("%s\n"%(i));
oFile.close()
print "there is %d nat pairs"%(natcount)
