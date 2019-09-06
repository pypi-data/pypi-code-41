#!python
import sys,os,re
import numpy
from  collections import defaultdict
def getPeaks(depths):
    """
    Get polyA peaks for given set of depths
    """
    #width_of_peaks=cf.get("Polya option","width_of_peaks")
    #MinDist=cf.get("Polya option","MinDist")
    #MinSupport=cf.get("Polya option","MinSupport")
    w = int(width_of_peaks)
    minDist =int(MinDist)
    N = len(depths)
    keepGoing = True
    peaks = []
    counts = [ ]
    while True:
        currPeaks = numpy.zeros(len(depths))
        for i in xrange(N):
            for c in peaks:
                if i <= c and c - i + 1 < minDist or \
                   i >= c and i - c + 1 < minDist:
                    break
            else:
                if numpy.sum(depths[ max(0, i-w-1):min(N,i+w)]) >= int(MinSupport):
                    currPeaks[i] = depths[i]*2+numpy.median(depths[ max(0, i-w-1):min(N,i+w)])
        if numpy.max(currPeaks) ==0:
            break
        cp = numpy.argmax(currPeaks)
        if cp not in peaks:
            peaks.append(cp)
            counts.append(currPeaks[cp])
    return peaks, counts
def APA(clu,strand):
	#print mapdict[clu]
	###############################
	for clu in [clu]:
		polyamap=[]
		scafo=clu.split('.')[0]
		for iso in mapdict[clu]:
			info=iso.split()
			if info[5].startswith("cufflinks") or info[4]!=strand:
				continue
			strand=info[4]
			if strand == '+':
				polyamap.append(int(info[3]))
			if strand == '-':
				polyamap.append(int(info[2]))
		if not polyamap:
			break
		minpos=min(polyamap)
		maxpos=max(polyamap)
		depth = numpy.zeros( maxpos-minpos+1, int)
		offset = min(polyamap)
		for loc in polyamap:
			depth[loc-offset] += 1
		peaks,counts = getPeaks(depth)
		position=','.join([str(x+offset) for x in peaks])
		if position=="":
			position="NULL"
		else:
			position=",".join(sorted(position.split(","), key=lambda d:(int(d)),reverse=False))
			if strand=="-":
				position=",".join(map(str,[int(x) for x in position.split(",")]))
		return position
##################################
cluster_file=sys.argv[1]
outdir=sys.argv[2]
Output_dir=sys.argv[3]
tpd=sys.argv[4]
width_of_peaks,MinDist,MinSupport=sys.argv[5:8]
trimid=sys.argv[8]
if not os.path.exists(outdir):
	os.makedirs(outdir)
####
trimdict=[]
for i in open(trimid,"r"):
	i=i.rstrip()
	i=i.upper()
	#+".PATH1"
	trimdict.append(i)
######### 
sys.stderr.write('Reading Cluster file...\n')
cluster=open(cluster_file,'r')
mapdict=defaultdict(dict)
for line in cluster:
	line=line.strip('\n')
	name=line.split()[0]
	names=line.split()[5]
	if names in trimdict:
		print line.split()[5]
		continue
	mapdict[name][line]=1
sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
###################################
oFile = open(outdir+'/apa.txt', 'w'); ## alt-3 SS output file
oFileHeader = "ID\tReads\tPos";
oFile.write(oFileHeader+'\n');
###################################
sys.stderr.write('complute APA ...\n')
apacount=0
for i in mapdict:
	# We restore the cursor to saved position before writing
	gene=i.split('.')[0]
	strand=list(set([x.split()[4] for x in mapdict[i]]))
	if len(strand)==2:
		continue
	strand=strand[0]
	################################
	position=APA(i,strand)
	if position!="NULL":
		if len(position.split(","))==1:
			pass
		else:
			apacount+=1
		trans=";".join([x.split()[5] for x in mapdict[i]])
		oFile.write("%s\t%s\t%s\n"%(i,trans,position))
oFile.close()
print "there is %d APA "%(apacount)
