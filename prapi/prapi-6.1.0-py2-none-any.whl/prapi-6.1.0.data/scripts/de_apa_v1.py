#!python
from __future__ import division
import numpy as np
import sys,os,re,commands
import numpy
from fisher import pvalue
from  collections import defaultdict
from itertools import combinations
import ConfigParser
global cf
cf = ConfigParser.ConfigParser()
cf.read(sys.argv[-1])
def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, show=False, ax=None):
    """Detect peaks in data based on their amplitude and other features.
    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.

    Notes
    -----
    The detection of valleys instead of peaks is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`
    
    The function can handle NaN's 

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb

    Examples
    --------
    >>> from detect_peaks import detect_peaks
    >>> x = np.random.randn(100)
    >>> x[60:81] = np.nan
    >>> # detect all peaks and plot data
    >>> ind = detect_peaks(x, show=True)
    >>> print(ind)

    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
    >>> # set minimum peak height = 0 and minimum peak distance = 20
    >>> detect_peaks(x, mph=0, mpd=20, show=True)

    >>> x = [0, 1, 0, 2, 0, 3, 0, 2, 0, 1, 0]
    >>> # set minimum peak distance = 2
    >>> detect_peaks(x, mpd=2, show=True)

    >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
    >>> # detection of valleys instead of peaks
    >>> detect_peaks(x, mph=0, mpd=20, valley=True, show=True)

    >>> x = [0, 1, 1, 0, 1, 1, 0]
    >>> # detect both edges
    >>> detect_peaks(x, edge='both', show=True)

    >>> x = [-2, 1, -2, 2, 1, 1, 3, 0]
    >>> # set threshold = 2
    >>> detect_peaks(x, threshold = 2, show=True)
    """

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indexes of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                    & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indexes by their occurrence
        ind = np.sort(ind[~idel])

    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)
    return ind
def Wig_count_no_normaltion(bamfile,Gene_coordinate,strand):
	wig=dict()
	typpd=dict()
	reads=commands.getoutput("samtools view %s %s"%(bamfile,Gene_coordinate))
	##############
	#strand
	#print bamfile,Gene_coordinate
	for i in reads.split('\n'):
		dd=i.split()
		if not dd:
			continue
		if i.startswith("[main_samview]") or i.startswith("Warning"):
			continue
		#print "samtools view %s %s"%(bamfile,Gene_coordinate)
		(flag,pos,cigar,seq)=(int(dd[1]),int(dd[3]),dd[5],dd[9])
		if True:
			if (flag&16)==0 and strand=='-':
				continue
			if (flag&16)==16 and strand=='+':
				continue
	#################
		#Mapping position
		if 'D' in cigar or 'I' in cigar:
			continue
		if 'N' in cigar:
			ele=[int(x) for y,x in enumerate(re.split('M|N',cigar)) if int(y)!=(len(re.split('M|N',cigar))-1)]
			for j in range(0,len(ele),2):
				if j==0:
					for k in range(0,ele[0]):
						if k+pos not in wig:
							wig[k+pos]=1
						else:
							wig[k+pos]+=1
						#print k+pos,
				else:
					for k in range(sum(x-1 for x in ele[:j]),sum(x-1 for x in ele[:j+1])+1):
						if k+pos not in wig:
							wig[k+pos]=1
						else:
							wig[k+pos]+=1
			continue
		##Mapping position 
		#########################
		#All position
		for j in range(len(seq)):
			if j+pos not in wig:
				wig[j+pos]=1
			else:
				wig[j+pos]+=1
	##############
	sortwig=sorted(wig.iteritems(), key=lambda d:d[0])
	return wig
def difference_expression_peaks(clu,cluster,apapos,strand,Gene_coordinate):
	lib=cf.get("DE APA option","DElib")
	outputdir=cf.get("outputdir","Output_dir")
	p_value_set=float(cf.get("DE APA option","p_value_set"))
	#two_fisher_length=int(cf.get("DE APA option","two_fisher_length"))
	Scan_length=int(cf.get("DE APA option","Scan_length"))
	libs=list(x for x in lib.split())
	comlibs=list(combinations(libs,2))
	#####
	# find the bigger two apa sites
	#####
	allsitedict=[]
	(tpp,filee,rgb)=conf[libs[0].lower()].strip('\n').split()
	wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
	######
	indexes=detect_peaks(wig.values(),mph=10,mpd=2*Scan_length,show=False)
	peaks=dict()
	for i in indexes:
		peaks[wig.keys()[i]]=wig[wig.keys()[i]]
	high2=dict()
	for i in apapos.split(","):
		i=int(i)
		minpos=dict()
		for j in peaks:
			minpos[abs(j-i)]=j
		if not minpos:
			continue
		closest=minpos[sorted(minpos,key=lambda d:(d),reverse = False)[0]]
		high2[closest]=peaks[closest]
	if not high2:
		return "NULL"
	if len(high2)<2:
		return "NULL"
	pos1,pos2=sorted(high2,key=lambda d:high2[d],reverse=True)[:2]
	apapos="%d,%d"%(pos1,pos2)
	#####
	returndict=[]
	for i,j in comlibs:
		#out=open("%s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename),"w")
		#out.write("%s\n"%("\t".join(apapos.split(","))))
		##################
		(tppi,filee,rgb)=conf[i.lower()].strip('\n').split()
		#out.write("%s\t"%(tpp))
		pinput=[]
		for k in (pos1,pos2):
			#Gene_coordinate="%s:%s-%s"%(clu.split(".")[0],k,k)
			k=int(k)
			wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
			try: 
				maxx=wig[k]
			except:
				maxx=0
			#try:
			#	maxx=max(wig[x] for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			#except:
			#	maxx=0
			#print k,maxx,i,k-Scan_length,k+Scan_length,list("%d-%d"%(x,wig[x]) for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			pinput.append(maxx)
			#out.write("%d\t"%(maxx))
		#out.write("\n")
		##################
		(tppj,filee,rgb)=conf[j.lower()].strip('\n').split()
		#out.write("%s\t"%(tpp))
		for k in (pos1,pos2):
			k=int(k)
			wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
			try: 
				maxx=wig[k]
			except:
				maxx=0
			#try:
			#	maxx=max(wig[x] for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			#except:
			#	maxx=0
			#print k,maxx,j,k-Scan_length,k+Scan_length,list("%d-%d"%(x,wig[x]) for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			#out.write("%d\t"%(maxx))
			pinput.append(maxx)
		a,b,c,d=(x for x in pinput)
		p_value=pvalue(a,b,c,d).two_tail
		#cmd="Rscript scripts/fisher.R %s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename)
		#result=commands.getoutput(cmd)
		#p_value=result.split()[-1]
		#if p_value=="in":
		#	p_value="NULL"
		#out=open("%s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename),"a")
		#out.write("%s\n"%(p_value))
		#out.close()
		print p_value
		if p_value=="NULL":
			return "NULL"
		try:
			if float(p_value)<=p_value_set:
				returndict.append((tppi,tppj,apapos,str(p_value)))
		except:
			continue
	if returndict:
		return returndict
	else:
		return "NULL"
##################################
cluster_file=sys.argv[1]
outdir=sys.argv[2]
Output_dir=sys.argv[3]
tpd=sys.argv[4]
Multile_processing=sys.argv[5]
#########
global conf
conf=dict()
for x in cf.items("Wig option"):
	if x[0].startswith("lib"):
		conf[x[0]]=x[1]
#########
sys.stderr.write('Reading Cluster file...\n')
cluster=open("%s/merge.format.none.cluster"%(Output_dir),'r')
mapdict=defaultdict(dict)
for line in cluster:
	line=line.strip('\n')
	name=line.split()[0]
	mapdict[name][line]=1
sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
###################################
oFile = open(outdir+'/de_apa.txt', 'w'); ## alt-3 SS output file
oFileHeader = "ID\tChromosome\tLib\tPos\tPvalue";
oFile.write(oFileHeader+'\n');
###################################
apadict=dict()
for i in open("%s/apa.txt"%(outdir),"r"):
	if i.startswith("ID"):
		continue
	ele=i.rstrip().split()
	apadict[ele[0]]=ele[-1]
###################################
############
barcount=-1
sys.stderr.write('complute de apa ...\n')
deapacount=0
for i in mapdict:
	# We restore the cursor to saved position before writing
	gene=i.split(';')[0]
	#
	strand=list(set([x.split()[4] for x in mapdict[i]]))
	if len(strand)==2 or len(apadict[i].split(","))<2:
		continue
	strand=strand[0]
	########################
	minpos  = min(int(x.split()[2]) for x in mapdict[i])
	maxpos  = max(int(x.split()[3]) for x in mapdict[i])
	minpos=int(minpos)
	maxpos=int(maxpos)
	Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
	########################
	difflib=difference_expression_peaks(i,mapdict[i],apadict[i],strand,Gene_coordinate)
	if difflib=="NULL":
		continue
	else:
		deapacount+=1
		for x in difflib:
			oFile.write("%s\t%s\t%s_VS_%s\t%s\t%s\n"%(i,gene,x[0],x[1],x[2],x[3]))
oFile.close()
print "there is %d de apa "%(deapacount)
