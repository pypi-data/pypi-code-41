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
def ATI(clu,strand):
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
				polyamap.append(int(info[2]))
			if strand == '-':
				polyamap.append(int(info[3]))
		if not polyamap:
			break
		#print polyamap
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
			return position
		position=",".join(sorted(position.split(","), key=lambda d:(int(d)),reverse=False))
		if strand=="-":
			position=",".join(map(str,[int(x)-1 for x in position.split(",")]))
		return position
##################################
cluster_file=sys.argv[1]
outdir=sys.argv[2]
Output_dir=sys.argv[3]
tpd=sys.argv[4]
width_of_peaks,MinDist,MinSupport=sys.argv[5:8]
##################################
if not os.path.exists(outdir):
	os.makedirs(outdir)
####
sys.stderr.write('Reading Cluster file...\n')
cluster=open("%s/merge.format.none.cluster"%(Output_dir),'r')
mapdict=defaultdict(dict)
trimid=sys.argv[8]
trimdict=[]
for i in open(trimid,"r"):
	i=i.rstrip()
	i=i.upper()
	trimdict.append(i)
###
for line in cluster:
	line=line.strip('\n')
	name=line.split()[0]
	if name in trimdict:
		continue
	mapdict[name][line]=1
sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
###################################
oFile = open(outdir+'/ati.txt', 'w'); ## alt-3 SS output file
oFileHeader = "ID\tStrand\tNum_of_Reads\tReads\tPos";
oFile.write(oFileHeader+'\n');
###################################
sys.stderr.write('complute ATI ...\n')
aticount=0
for i in mapdict:
	gene=i.split('.')[0]
	strand=list(set([x.split()[4] for x in mapdict[i]]))
	if len(strand)==2:
		continue
	strand=strand[0]
	position=ATI(i,strand)
	if position!="NULL":
		if len(position.split(","))==1:
			pass
		else:
			aticount+=1
		trans=";".join([x.split()[5] for x in mapdict[i]])
		num=len(mapdict[i])
		oFile.write("%s\t%s\t%d\t%s\t%s\n"%(i,strand[0],num,trans,position))
oFile.close()
print "there is %d ati "%(aticount)
