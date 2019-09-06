#!python
from __future__ import division
import sys,re,os,shutil,copy
import collections,commands,numpy
from bx.intervals.cluster import ClusterTree
from SpliceGrapher.formats.FastaLoader import FastaLoader
from  collections import defaultdict
from itertools import combinations
from pyper import *
from numpy import NaN, Inf, arange, isscalar, asarray, array
sys.path.append("scripts")
#import detect_peaks
import pysam
def de_nat_edger(genename,fpkmcal,cf,conf):
	pass
	outputdir=cf.get("outputdir","Output_dir")
	libgroup=cf.get('DE NAT option','delib')
	#myr = R()
	libs=list(x for x in libgroup.split())
	comlibs=list(combinations(libs,2))
	p_value=float(cf.get("DE option","p_value"))
        fdr=float(cf.get("DE option","fdr"))
	fcup=float(cf.get("DE option","fc"))
        fcdown=fcup/2
        #comlibs=list(combinations(libs, len(libs)-1))
	returndict=[]
        #print comlibs
	for i,j in comlibs:
		lib1=conf[i.split("_")[0].lower()].strip('\n').split()[0]
		lib11=re.sub("\d+","",lib1)
		lib2=conf[j.split("_")[0].lower()].strip('\n').split()[0]
		lib22=re.sub("\d+","",lib2)
		out=open("%s/temp/%s_%s_%s.R"%(outputdir,genename,lib11,lib22),"w")
		ii=i.split("_")
		jj=j.split("_")
		#####
		#print fpkmcal,ii
		#print fpkmcal[ii[0]]["+_f"]
		#print fpkmcal[ii[1]]["+_f"]
		#print fpkmcal[ii[2]]["+_f"]
		out.write("Symbol\tA\tA\tA\tB\tB\tB\n")	
		out.write("%s_%s_%s_+\t%d\t%d\t%d\t"%(genename,lib11,lib22,fpkmcal[ii[0].lower()]["+_f"],fpkmcal[ii[1].lower()]["+_f"],fpkmcal[ii[2].lower()]["+_f"]))
		out.write("%d\t%d\t%d\n"%(fpkmcal[jj[0].lower()]["+_f"],fpkmcal[jj[1].lower()]["+_f"],fpkmcal[jj[2].lower()]["+_f"]))
		#####
		out.write("%s_%s_%s_-\t%d\t%d\t%d\t"%(genename,lib11,lib22,fpkmcal[ii[0].lower()]["-_r"],fpkmcal[ii[1].lower()]["-_r"],fpkmcal[ii[2].lower()]["-_r"]))
                out.write("%d\t%d\t%d\n"%(fpkmcal[jj[0].lower()]["-_r"],fpkmcal[jj[1].lower()]["-_r"],fpkmcal[jj[2].lower()]["-_r"]))
		out.close()
		#####
		clu=genename
		cmd="/home/pub/tool/r/bin/Rscript scripts/edge.R %s/temp/%s_%s_%s.R %s/temp/%s_%s_%s.out 1>/dev/null 2>/dev/null"%(outputdir,genename,lib11,lib22,outputdir,genename,lib11,lib22)
		os.system(cmd)
        	if not os.path.exists("%s/temp/%s_%s_%s.out"%(outputdir,genename,lib11,lib22)):
                	print "None"
			return 0
		else:
			print "%s\thave results"%(genename)
        	for line in open("%s/temp/%s_%s_%s.out"%(outputdir,genename,lib11,lib22),"r"):
                	if line.startswith("logFC"):
                        	continue
                	line=line.rstrip()
                	ele=line.split()
                	logFC,logCPM,PValue,FDR=(float(x) for x in ele[1:])
                	FC=pow(2,abs(logFC))
                	#print genename,FC,fcup,fcdown
                	if PValue<p_value and FDR <fdr:
                        	if FC>fcup or FC<fcdown:
                                	print ele[1:],FC,PValue,FDR,fcup,fcdown
                                	returndict.append([ele[0],""])
        #print astype,returnstring
	return returndict
def de_nat(genename,fpkmcal,cf,conf):
	pass
	outputdir=cf.get("outputdir","Output_dir")
	myr = R()
	libs=list(x for x in fpkmcal)
	comlibs=list(combinations(libs,2))
	#comlibs=list(combinations(libs, len(libs)-1))
	returndict=[]
	print genename
	#print comlibs
	for i,j in comlibs:
		#if not 0.1<(fpkmcal[i]["+"]+1)/(fpkmcal[i]["-"]+1)<1:
		#	continue
		cmd="fisher.test(matrix(c(%d,%d,%d,%d),nrow=2,byrow=TRUE))$p.value"%(fpkmcal[i]["+"],fpkmcal[i]["-"],fpkmcal[j]["+"],fpkmcal[j]["-"])
		pvalue=myr[cmd]
		if pvalue<0.1:
			lib1=conf[i.lower()].strip('\n').split()[0]
			lib2=conf[j.lower()].strip('\n').split()[0]
			out=open("%s/temp/%s.natde"%(outputdir,genename),"w")
			out.write("%s\t%s+:%f\t%s-:%f\t%s+:%f\t%s-:%f\t%f\n"%(genename,lib1,fpkmcal[i]["+"],lib1,fpkmcal[i]["-"],lib2,fpkmcal[j]["+"],lib2,fpkmcal[j]["-"],pvalue))
			out.close()
			returndict.append([i,j])
	return returndict
def fpkm(bamfile,chro,strand,s,e,uniqexonlength,num):
	samfile = pysam.AlignmentFile(bamfile, "rb")
	filterdict=[]
	if s>e:
		s,e=e,s
	for read in samfile.fetch(chro,s, e):
		#if not is_unique(read): ## not unique, go to the next one
		#	continue; ## process next read
		mc=read.pos
		if mc>e+read.qlen or mc<s-read.qlen:
			continue
		d=int(read.flag)&16
		if (d==0 and strand=='-') or(d==16 and strand=='+'):
			continue
		filterdict.append(read.qname)
	seread=len(filterdict)
	pereaddict=defaultdict(dict)
	for i in filterdict:
		uniqname=":".join(i.split(":")[:-1])
		pereaddict[uniqname][i]=1
	peread=len([x for x in pereaddict if len(pereaddict[x])==2])
	##########
	perKBperMillion=1E9
	fpkm=(perKBperMillion*peread*2)/(num*uniqexonlength)
	return  fpkm,peread
def get_junction_pickle():
	samIndex=0;
	for s1 in samFiles: ## for each samFiles
		if len(s1.strip())<1: ## incorrect split. a user might accidently put comma at the end of input sam file list
			continue; ### just skip this entry, probably the last one though
		print("processing %s" % s1.strip());
		sFile = pysam.Samfile(s1.strip(),'rb'); ## open bam file
		for read in sFile.fetch():
			#if not is_unique(read): ## not unique, go to the next one
			#continue; ## process next read
			chr = sFile.getrname(read.tid);
			mc = read.pos+1;
			mString = read.cigarstring; ## mapping string, 50M or aMbNcMdNeMfNgM format, CIGAR string
			group = mc/chunk; ## group does not change, it's okay to check only one group for a junction read
			if 'D' in mString or 'I' in mString or 'S' in mString or 'H' in mString or 'P' in mString or 'X' in mString or '=' in mString: ## skip
				continue; ## go to next line
			### check to see if the line is either exonic read or junction read
			split_mString = mString.split('M');
			tor = 0; ## type of read, 0 nothing, 1 exonic read, 2 junction read
			if len(split_mString)==2:
			#tor = 1; ## exonic read ##
				continue; ## go to next line
			elif len(split_mString)>=3:    ###### junction read ###########
			#tor = 2; ## junction read
				jS=mc; jE=mc-1; 
			for ec in range(0,len(split_mString)-2): ## for each coordinate
				secondNumber = int(split_mString[ec].split('N')[-1]); 
				jS = jE+secondNumber; ## 1-base
				jE = jS+int(split_mString[ec+1].split('N')[0]); ## 0-base
				key = chr+'_'+str(jS)+'_'+str(jE);
				jGrp=range(jS/chunk, jE/chunk+1);
				jGrp=list(set(jGrp));  ## remove duplicate group
				for grp in jGrp: ## for each possible group
					if grp in tJunctions:
						if key in tJunctions[grp]:
							tJunctions[grp][key] += 1;
						else:
							tJunctions[grp][key]=1;
					else:
						tJunctions[grp]={};
						tJunctions[grp][key]=1;
				if grp in junctions:
					if samIndex in junctions[grp]:
						if key in junctions[grp][samIndex]:
							junctions[grp][samIndex][key]+=1;
						else:
							junctions[grp][samIndex][key]=1;
					else: 
						junctions[grp][samIndex]={};
						junctions[grp][samIndex][key]=1;
				else:
					junctions[grp]={};
					junctions[grp][samIndex]={};
					junctions[grp][samIndex][key]=1;
		samIndex+=1; ## for the junctions dictionary index
def mats_count(i):
	pass
def difference_expression_as(clu,cluster,ir,es,altd,alta,altp,cf,conf,strand,Gene_coordinate,genename):
	p_value_set=float(cf.get("DE AS option","p_value_set"))
	lib=cf.get("DE AS option","DElib")
	outputdir=cf.get("outputdir","Output_dir")
	libs=list(x for x in lib.split())
	comlibs=list(combinations(libs, len(libs)-1))
	asdict=["ir","es","altd","alta","altp"]
	asdict=["es"]
	for seq in asdict:
		if eval(seq)=="NULL":
			status="NULL"
		status=if_differencial(eval(seq),seq,comlibs,genename,conf,clu,outputdir,p_value_set)
		print status,seq,eval(seq)
		#if status=="NULL":
		#	exec("seq=\"NULL\"")
		#	print eval(seq)
	return status
def if_differencial(seq,types,comlibs,genename,conf,clu,outputdir,p_value_set):
	returnseq=[]
	if seq=="NULL":
		return "NULL"
	else:
		for i in seq.split(","):
			s,e=[int(x) for x in i.split(":")]
			for j,k in comlibs:
				(tpp,filee,rgb)=conf[j.lower()].strip('\n').split()
				if types=="es":
					irpair1,irpair2=junction_num_es(clu,filee,s,e)
				elif types=="ir":
					irpair1,irpair2=junction_num_ir(clu,filee,s,e)
				(tpp,filee,rgb)=conf[k.lower()].strip('\n').split()
				if types=="es":
					irpair1,irpair2=junction_num_es(clu,filee,s,e)
				elif types=="ir":
					irpair1,irpair2=junction_num_ir(clu,filee,s,e)
				if irpair1!=0 and irpair2!=0 and irpair3!=0 and irpair4!=0:
					out=open("%s/temp/%s_%s_%s.plot"%(outputdir,j,k,genename),"w")
					out.write("%d\t%d\n%s\t%d\t%d\n%s\t%d\t%d\n"%(s,e,j,irpair1,irpair3,k,irpair2,irpair4))
					out.close()
					cmd="Rscript scripts/fisher.R %s/temp/%s_%s_%s.plot"%(outputdir,j,k,genename)
					result=commands.getoutput(cmd)
					print result
					p_value=result.split()[-1]
					if float(p_value)<=p_value_set:
						returnseq.append("%s:%s:%s:%s"%(j,k,s,e))
	if returnseq:
		return returnseq
	else:
		return "NULL"
def junction_num_es(clu,bamfile,s,e):
	irpair1=0
	irpair2=0
	samfile = pysam.AlignmentFile(bamfile, "rb")
	for read in samfile.fetch(clu.split(".")[0],s, e):
		#if not is_unique(read): ## not unique, go to the next one
		#	continue; ## process next read
		mc=read.pos
		mString=read.cigarstring
		if 'D' in mString or 'I' in mString or 'S' in mString or 'H' in mString or 'P' in mString or 'X' in mString or '=' in mString: ## skip
			continue; ## go to next line
		 ### check to see if the line is either exonic read or junction read
		split_mString = mString.split('M');
		#tor = 0; ## type of read, 0 nothing, 1 exonic read, 2 junction read
		if len(split_mString)==2:
			continue
			#tor = 1; ## exonic read ##
		elif len(split_mString)>=3:    ###### junction read ###########
			#tor = 2; ## junction read
			jS=mc; jE=mc-1;
			for ec in range(0,len(split_mString)-2): ## for each coordinate
				secondNumber = int(split_mString[ec].split('N')[-1]); 
				jS = jE+secondNumber; ## 1-base
				jE = jS+int(split_mString[ec+1].split('N')[0]); ## 0-base
				if (jE-jS)!=(e-s):
					continue
				print mString,jS,jE,s,e
	return  irpair1,irpair2
def junction_num_ir(clu,bamfile,s,e):
	irpair1=0
	irpair2=0
	samfile = pysam.AlignmentFile(bamfile, "rb")
	for read in samfile.fetch(clu.split(".")[0],s, e):
		if not is_unique(read): ## not unique, go to the next one
			continue; ## process next read
		mc=read.pos
		mString=read.cigarstring
		if 'D' in mString or 'I' in mString or 'S' in mString or 'H' in mString or 'P' in mString or 'X' in mString or '=' in mString: ## skip
			continue; ## go to next line
		 ### check to see if the line is either exonic read or junction read
		split_mString = mString.split('M');
		#tor = 0; ## type of read, 0 nothing, 1 exonic read, 2 junction read
		if len(split_mString)==2:
			if mc<=(s-1) and (e-2)<=(mc+len(read.seq)-1):
				irpair1+=1
			#tor = 1; ## exonic read ##
		elif len(split_mString)>=3:    ###### junction read ###########
			#tor = 2; ## junction read
			jS=mc; jE=mc-1;
			for ec in range(0,len(split_mString)-2): ## for each coordinate
				secondNumber = int(split_mString[ec].split('N')[-1]); 
				jS = jE+secondNumber; ## 1-base
				jE = jS+int(split_mString[ec+1].split('N')[0]); ## 0-base
				if jS==s-1 and jE==e-2:
					irpair2+=1
	return  irpair1,irpair2
def is_unique(r):
  # check if read is uniquely mapped
  for tag in r.tags:
    if tag[0]=='NH': # NH is tag for number of hits
      if int(tag[1])==1: # uniquely mapped if NH=1
        if True: ## single end, sufficient
          return True;
        elif r.is_proper_pair:
          return True; 
  return False
def convert_gff_gff3_gtf(cf):
	Genome_Annotion=cf.get("input file","genome_annotion")
	#if open(Genome_Annotion,"r").readline().rstrip()=="##gff-version 3":
def Wig_count_no_normaltion(bamfile,Gene_coordinate,strand):
	wig=dict()
	typpd=dict()
	reads=commands.getoutput("samtools view %s %s"%(bamfile,Gene_coordinate))
	##############
	#strand
	for i in reads.split('\n'):
		dd=i.split()
		if not dd:
			continue
		if i.startswith("[main_samview]") or i.startswith("Warning"):
			continue
		#print "samtools view %s %s"%(bamfile,Gene_coordinate)
		#print dd
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
def difference_expression_peaks(clu,cluster,apapos,cf,conf,strand,Gene_coordinate,genename):
	print apapos
	if len(apapos.split(","))==1:
		return "NULL"
	lib=cf.get("DE APA option","DElib")
	outputdir=cf.get("outputdir","Output_dir")
	p_value_set=float(cf.get("DE APA option","p_value_set"))
	two_fisher_length=int(cf.get("DE APA option","two_fisher_length"))
	Scan_length=int(cf.get("DE APA option","Scan_length"))
	libs=list(x for x in lib.split())
	comlibs=list(combinations(libs, len(libs)-1))
	#####
	# find the bigger two apa sites 
	#####
	allsitedict=[]
	(tpp,filee,rgb)=conf[libs[0].lower()].strip('\n').split()
	wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
	######
	indexes = detect_peaks.detect_peaks(wig.values(),mph=10,mpd=40,show=False)
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
	#print genename,high2,apapos
	if not high2:
		return "NULL"
	if len(high2)<2:
		return "NULL"
	pos1,pos2=sorted(high2,key=lambda d:high2[d],reverse=True)[:2]
	print pos1,pos2
	apapos="%d,%d"%(pos1,pos2)
	#####
	returndict=[]
	for i,j in comlibs:
		out=open("%s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename),"w")
		out.write("%s\n"%("\t".join(apapos.split(","))))
		##################
		(tpp,filee,rgb)=conf[i.lower()].strip('\n').split()
		out.write("%s\t"%(tpp))
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
			out.write("%d\t"%(maxx))
		out.write("\n")
		##################
		(tpp,filee,rgb)=conf[j.lower()].strip('\n').split()
		out.write("%s\t"%(tpp))
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
			out.write("%d\t"%(maxx))
		out.write("\n")
		out.close()
		cmd="Rscript scripts/fisher.R %s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename)
		result=commands.getoutput(cmd)
		p_value=result.split()[-1]
		if p_value=="in":
			p_value="NULL"
		out=open("%s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename),"a")
		out.write("%s\n"%(p_value))
		out.close()
		print p_value
		if p_value=="NULL":
			return "NULL"
		try:
			if float(p_value)<=p_value_set:
				returndict.append((i,j,apapos))
		except:
			continue
	if returndict:
		return returndict
	else:
		return "NULL"
		###################
def difference_expression(clu,cluster,apapos,cf,conf,strand,Gene_coordinate,genename):
	if len(apapos.split(","))==1:
		return "NULL"
	#print apapos
	#apamin,apamax= (int(x) for x in  apapos.split(","))
	#if abs(apamin-apamax)<=50:
	#	return "NULL"
	lib=cf.get("DE APA option","DElib")
	outputdir=cf.get("outputdir","Output_dir")
	p_value_set=float(cf.get("DE APA option","p_value_set"))
	two_fisher_length=int(cf.get("DE APA option","two_fisher_length"))
	Scan_length=int(cf.get("DE APA option","Scan_length"))
	libs=list(x for x in lib.split())
	comlibs=list(combinations(libs, len(libs)-1))
	###
	# find the bigger two apa sites 
	#####
	#####
	allsitedict=[]
	(tpp,filee,rgb)=conf[libs[0].lower()].strip('\n').split()
	for k in apapos.split(","):
		k=int(k)
		wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
		#print wig
		try:
			maxx=max(wig[x] for x in wig if (k-Scan_length)<=x<(k+Scan_length))
		except:
			maxx=0
		allsitedict.append("%s %s"%(k,maxx))
	#####
	allsitedictsort=sorted(allsitedict, key=lambda d:(int(d.split()[-1])), reverse = True)
	breakkey=0
	for i in  allsitedictsort[1:]:
		pos,num=(int(x) for x in i.split())
		if (pos-int(allsitedictsort[0].split()[0]))>=two_fisher_length:
			breakkey=pos
			break
	#####
	if breakkey==0:
		return "NULL"
	else:
		apapos="%s,%s"%(allsitedictsort[0].split()[0],breakkey)
	#####
	#####
	out=open("%s/temp/%s.plot"%(outputdir,clu),"w")
	returndict=[]
	for i,j in comlibs:
		out=open("%s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename),"w")
		out.write("%s\n"%("\t".join(apapos.split(","))))
		##################
		(tpp,filee,rgb)=conf[i.lower()].strip('\n').split()
		out.write("%s\t"%(tpp))
		for k in apapos.split(","):
			#Gene_coordinate="%s:%s-%s"%(clu.split(".")[0],k,k)
			k=int(k)
			wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
			try:
				maxx=max(wig[x] for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			except:
				maxx=0
			#print k,maxx,i,k-Scan_length,k+Scan_length,list("%d-%d"%(x,wig[x]) for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			out.write("%d\t"%(maxx))
		out.write("\n")
		##################
		##################
		(tpp,filee,rgb)=conf[j.lower()].strip('\n').split()
		out.write("%s\t"%(tpp))
		for k in apapos.split(","):
			k=int(k)
			wig=Wig_count_no_normaltion(filee,Gene_coordinate,strand)
			try:
				maxx=max(wig[x] for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			except:
				maxx=0
			#print k,maxx,j,k-Scan_length,k+Scan_length,list("%d-%d"%(x,wig[x]) for x in wig if (k-Scan_length)<=x<(k+Scan_length))
			out.write("%d\t"%(maxx))
		out.write("\n")
		out.close()
		cmd="Rscript scripts/fisher.R %s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename)
		result=commands.getoutput(cmd)
		p_value=result.split()[-1]
		if p_value=="in":
			p_value="NULL"
		out=open("%s/temp/%s_%s_%s.plot"%(outputdir,i,j,genename),"a")
		out.write("%s\n"%(p_value))
		out.close()
		print p_value
		if p_value=="NULL":
			return "NULL"
		try:
			if float(p_value)<=p_value_set:
				returndict.append((i,j,apapos))
		except:
			continue
	if returndict:
		return returndict
	else:
		return "NULL"
		###################
def countgene_num(genomecorrdinate,bamfile,libtype,Strand_Specificity,s,e,strand):
	reads=commands.getoutput("samtools view %s %s"%(bamfile,genomecorrdinate))
	fillterreads=[]
	readsstrand=defaultdict(dict)
	for i in reads.split("\n"):
		if i=="":
			continue
		i=i.rstrip()
		ele=i.split()
		length=len(ele[9])
		s,e=int(s),int(e)
		s-=length
		e+=length
		d=int(ele[1])&16
		if not s<int(ele[3])<e:
			continue
		if Strand_Specificity=="True":
			if (strand=="+" and d==0) or (strand=="-" and d==16):
				fillterreads.append(i)
				se=":".join(ele[0].split(":")[:-1])
				readsstrand[se][ele[0]]=1
		elif Strand_Specificity!="True" :
			fillterreads.append(i)
			#sreturn len(reads)
	if libtype=="SE":
		return len(fillterreads)
	elif libtype=="PE":
		num=[i for i in readsstrand if len(readsstrand[i])==2]
		return len(num)
def isdifexp_as(clu,sort_dict,astype,cf,conf):
	if astype=="NULL":
		return 0
	p_value=float(cf.get("DE option","p_value"))
	fdr=float(cf.get("DE option","fdr"))
	fcup=float(cf.get("DE option","fc"))
	fcdown=fcup/2
	libtype=cf.get("DE option","libtype")
	group1=cf.get("DE option","group1")
	group2=cf.get("DE option","group2")
	strand=sort_dict[0].split()[4]
	Strand_Specificity=cf.get("Wig option","Strand_Specificity")
	count=defaultdict(dict)
	outputdir=cf.get("outputdir","Output_dir")
	out=open("%s/temp/%s.R"%(outputdir,clu),"w")
	out.write("Symbol%s%s\n"%("\tA"*len(group1.split()),"\tB"*len(group2.split())))
	count=0
	for k in astype.split(","):
		count+=1
		(s,e)=k.split(":")
		genomecorrdinate="%s:%s-%s"%(clu.split(".")[0],s,e)
		out.write("%s_%s_%d"%(clu,k,count))
		numcount=0
		for i in group1.split():
			bamfile=conf[i.lower()].split()[1]
			num=countgene_num(genomecorrdinate,bamfile,libtype,Strand_Specificity,s,e,strand)
			numcount+=num
			out.write("\t%d"%(num))
		for i in group2.split():
			bamfile=conf[i.lower()].split()[1]
			num=countgene_num(genomecorrdinate,bamfile,libtype,Strand_Specificity,s,e,strand)
			numcount+=num
			out.write("\t%d"%(num))
		if numcount==0:
			return 0
		out.write("\n")
	out.close()
	cmd="Rscript scripts/edge.R %s/temp/%s.R %s/temp/%s.out"%(outputdir,clu,outputdir,clu)
	os.system(cmd)
	returnstring=""
	if not os.path.exists("%s/temp/%s.out"%(outputdir,clu)):
		return 0
	for i in open("%s/temp/%s.out"%(outputdir,clu),"r"):
		if i.startswith("logFC"):
			continue
		i=i.rstrip()
		ele=i.split()
		logFC,logCPM,PValue,FDR=(float(x) for x in ele[1:])
		FC=pow(2,abs(logFC))
		#print FC,fcup,fcdown
		if PValue<p_value and FDR <fdr:
			if FC>fcup or FC<fcdown:
				print ele[1:],FC,PValue,FDR,fcup,fcdown
				returnstring+="%s\t"%(ele[0])
	#print astype,returnstring
	return returnstring
def add(mapdict, key_a, key_b, val):
	if key_a in mapdict:
		mapdict[key_a].update({key_b: val})
	else:
		mapdict.update({key_a:{key_b: val}})
def hex2rgb(hexstring, digits=2):
    """Converts a hexstring color to a rgb tuple.

    Example: #ff0000 -> (1.0, 0.0, 0.0)

    digits is an integer number telling how many characters should be
    interpreted for each component in the hexstring.
    """
    if isinstance(hexstring, (tuple, list)):
        return hexstring

    top = float(int(digits * 'f', 16))
    r = int(hexstring[1:digits+1], 16)
    g = int(hexstring[digits+1:digits*2+1], 16)
    b = int(hexstring[digits*2+1:digits*3+1], 16)
    return r / top, g / top, b / top
def Denovel_APA(conf):
	#############
	loader = FastaLoader(conf["Reads"],verbose=True)
	ref=dict()
	if not os.path.exists("%s/temp"%(conf["Output_dir"])):
		os.makedirs("%s/temp"%(conf["Output_dir"]))
	else:
		shutil.rmtree("%s/temp"%(conf["Output_dir"]))
		os.makedirs("%s/temp"%(conf["Output_dir"]))
	for i in open("%s/cd_hit.clstr.format"%(conf["Output_dir"]),"r"):
		ele=i.strip("\n").split()
		if len(ele)==2:
			continue
		output=open("%s/temp/%s.seq"%(conf["Output_dir"],ele[0]),"w")
		for j in ele[1:]:
			length=loader.sequenceLength(j)
			start=length-10-4
			end=length-1
			seq=loader.subsequence(j,start,end)
			output.write(">%s\n%s\n"%(j,seq))
			sys.stderr.write("%s sequence Extract over\n"%(ele[0]))
		output.close()
	######################################################
	files=os.listdir("%s/temp"%(conf["Output_dir"]))
	Control(files,conf)
	files=os.listdir("%s/temp"%(conf["Output_dir"]))
	output=open("%s/Cluster.csv"%(conf["Output_dir"]),"w")
	for fl in files:
		if fl.endswith("clstr"):
			for i in open("%s/temp/%s"%(conf["Output_dir"],fl),"r"):
				i=i.strip("\n")
				if i.endswith("*"):
					output.write("%s\t%s\n"%(fl.split(".")[0],re.split(">|\.",i)[1]))
	output.close()
	###########################################################
	sys.stderr.write("Cating over\n")
	output=open("%s/Cluster_Seq.csv"%(conf["Output_dir"]),"w")
	for i in open("%s/Cluster.csv"%(conf["Output_dir"]),"r"):
		i=i.strip("\n")
		ele=i.split()
		length=loader.sequenceLength(ele[1])
		start=length-50
		end=length-1
		seq=loader.subsequence(ele[1],start,end)
		output.write("%s\t%s\n"%(i,seq))
	output.close()
	sys.stderr.write("Alternative Polya Extraction Complete\n")
#############################
#############################
def subcd_hit(fl,conf):
	cmd="cd-hit-est -i %s/temp/%s -o %s/temp/%s.cd-hit -c 0.9 -n 10 -d 0 -M 20000 -T 0 -r 1 1>/dev/null"%(conf["Output_dir"],fl,conf["Output_dir"],fl)
	os.system(cmd)
	sys.stderr.write("%s Cluster over\n"%(fl))
#############################
def Control(files,conf):
	if conf["Multile_processing"]!="True":
		for fl in files:
			subcd_hit(fl,conf)
	else:
		pool = multiprocessing.Pool()
		for fl in files:
			pool.apply_async(subcd_hit, (fl,conf, ))
		pool.close()
		pool.join()
#############################
def format_cd_hit(conf):
	sys.stderr.write('Cd_hit Formating...\n')
	output=open("%s/cd_hit.clstr.format"%(conf["Output_dir"]),"w")
	flag=0
	for i in open("%s/cd-hit-est.fasta.clstr"%(conf["Output_dir"]),"r"):
		i=i.strip("\n")
		ele=i.split()
		if i.startswith(">"):
			if flag==0:
				flag=1
			else:
				output.write("\n")
			output.write("Cluster%s\t"%(ele[-1]))
		else:
			output.write("%s\t"%(re.split("\.|>",i)[1]))
	output.close()
	sys.stderr.write('Cd_hit Formating finshed...\n')
def fillter_blat(path,conf):
	flag=0
	#format_cd_hit(path)
	ref=dict()
	for i in open("%s/cd_hit.clstr.format"%(path),"r"):
		ele=i.strip("\n").split()
		for j in ele[-1].split(";"):
			ref[j]=ele[0]
	""""
	sys.stderr.write('Blat Formating...\n')
	output=open("%s/blat.sim4.format"%(path),"w")
	for i in open("%s/blat.sim4"%(path),"r"):
		i=i.strip("\n")
		ele=i.split()
		if i=="":
			continue
		if i.startswith("seq"):
			if flag==0:
				flag=1
			else:
				if i.startswith("seq1"):
					output.write("\n")
			output.write("%s\t"%(re.split("=|,",i)[1]))
		else:
			if i=="(complement)":
				continue
			output.write("%s;%s\t"%(ele[0],re.split("\(|\)",ele[1])[1]))
	output.close()
	sys.stderr.write('Blat Formating Finshed...\n')
	##############
	sys.stderr.write('Blat Filltering...\n')
	pair=dict()
	output=open("%s/blat.sim4.format.fillter"%(path),"w")
	for i in open("%s/blat.sim4.format"%(path),"r"):
		i=i.strip("\n")
		ele=i.split()
		if ele[0]!=ele[1] and ref[ele[0]]==ref[ele[1]]:
			if not "%s_%s"%(ele[1],ele[0]) in pair:
				output.write("%s\t%s\n"%(ref[ele[0]],i))
				pair["%s_%s"%(ele[0],ele[1])]=1
	output.close()
	sys.stderr.write('Blat Filltering Finshed...\n')
	######fillter finshed
	##################
	"""
	sys.stderr.write('AS Finding Start...\n')     
	loader = FastaLoader(conf["Reads"],verbose=True)
	###################
	reads=dict()
	for i in open("%s/blat.sim4.format.fillter"%(path),"r"):
		i=i.strip("\n")
		ele=i.split()
		pgs1=[j.split(";")[0] for j in ele[3:]]
		pgs2=[j.split(";")[1] for j in ele[3:]]
		for j in range(len(pgs1)):
			if j==len(pgs1)-1:
				continue
			(s1,e1)=[int(k) for k in pgs1[j].split("-")]
			(s1n,e1n)=[int(k) for k in pgs1[j+1].split("-")]
			(s2,e2)=[int(k) for k in pgs2[j].split("-")]
			(s2n,e2n)=[int(k) for k in pgs2[j+1].split("-")]
			gap=s1n-e1
			gappair=s2n-e2
			if gap>1 and gappair ==1:
				gene=ele[1]
				start=e1-1
				end=s1n-1
				seq=loader.subsequence(gene,start,end)
				if seq in reads:
					add(reads,gene,seq,"%s%s:%s-%s|%s:%s-%s;"%(reads[gene][seq],ele[1],e1+1,s1n-1,ele[2],e2,s2n))
				else:
					add(reads,gene,seq,"%s:%s-%s|%s:%s-%s;"%(ele[1],e1+1,s1n-1,ele[2],e2,s2n))
			if gappair>1 and gap==1:
				gene=ele[2]
				start=e2-1
				end=s2n-1
				seq=loader.subsequence(gene,start,end)
				if seq in reads:
					add(reads,gene,seq,"%s%s:%s-%s|%s:%s-%s;"%(reads[gene][seq],ele[2],e2+1,s2n-1,ele[1],e1,s1n))
				else:
					add(reads,gene,seq,"%s:%s-%s|%s:%s-%s;"%(ele[2],e2+1,s2n-1,ele[1],e1,s1n))
	output=open("%s/AS.result"%(path),"w")
	for i in reads:
		for j in reads[i]:
			if len(j)>int(conf["DeNovel_Cutoff"]):
				output.write("%s\t%s\t%s\n"%(i,reads[i][j],j))
	output.close()
	AStype(path,conf)
	sys.stderr.write('AS Finding End...\n')
def AStype(path,conf):
	sys.stderr.write('AS Type Indentifing...\n')
	GTAG=open("%s/IR_GTAG"%(path),"w")
	GCAG=open("%s/IR_GCAG"%(path),"w")
	ATAC=open("%s/IR_ATAC"%(path),"w")
	ES=open("%s/ES"%(path),"w")
	GT=open("%s/AltD_GT"%(path),"w")
	GC=open("%s/AltD_GC"%(path),"w")
	AT=open("%s/AltD_AT"%(path),"w")
	AG=open("%s/AltA_AG"%(path),"w")
	AC=open("%s/AltA_AC"%(path),"w")
	for i in open("%s/AS.result"%(path),"r"):
		i=i.strip("\n")
		ele=i.split()
		if ele[-1].startswith("GT") and ele[-1].endswith("AG"):
			GTAG.write("%s\n"%(i))
			next
		if ele[-1].startswith("GC") and ele[-1].endswith("AG"):
			GCAG.write("%s\n"%(i))
			next
		if ele[-1].startswith("AT") and ele[-1].endswith("AC"):
			ATAC.write("%s\n"%(i))
			next
		if ele[-1].startswith("GT"):
			GT.write("%s\n"%(i))
			next
		if ele[-1].startswith("GC"):
			GC.write("%s\n"%(i))
			next
		if ele[-1].startswith("AT"):
			AT.write("%s\n"%(i))
			next
		if ele[-1].endswith("AG"):
			AG.write("%s\n"%(i))
			next
		if ele[-1].endswith("AC"):
			AC.write("%s\n"%(i))
			next
	GTAG.close()
	GCAG.close()
	ATAC.close()
	ES.close()
	GT.close()
	GC.close()
	AT.close()
	AG.close()
	AC.close()
	sys.stderr.write('AS Type Indentifing Ending...\n')
def doblat(conf):
	sys.stderr.write('Step2 Blating...\n')
	loader = FastaLoader(conf["Reads"],verbose=True)
	if not os.path.exists("%s/temp"%(conf["Output_dir"])):
		os.makedirs("%s/temp"%(conf["Output_dir"]))
	else:
		shutil.rmtree("%s/temp"%(conf["Output_dir"]))
		os.makedirs("%s/temp"%(conf["Output_dir"]))
	for i in open("%s/cd_hit.clstr.format"%(conf["Output_dir"]),"r"):
		ele=i.strip("\n").split()
		if len(ele)==2:
			continue
		output=open("%s/temp/%s.seq"%(conf["Output_dir"],ele[0]),"w")
		for j in ele[1:]:
			seq=loader.sequence(j)
			output.write(">%s\n%s\n"%(j,seq))
		output.close()
		sys.stderr.write('%s sequence extraction over...\n'%(ele[0]))
	files=os.listdir("%s/temp"%(conf["Output_dir"]))
	#########################################
	##Multile Procelling
	if conf["Multile_processing"]!="True":
		for fl in files:
			if fl.endswith("seq"):
				sub_blat(fl,conf)
	else:
		import multiprocessing
		pool = multiprocessing.Pool()
		for fl in files:
			pool.apply_async(sub_blat,(fl,conf, ))
		pool.close()
		pool.join()
	#######################################
	sys.stderr.write('Blat Formating...\n')
	files=os.listdir("%s/temp"%(conf["Output_dir"]))
	output=open("%s/sim4"%(conf["Output_dir"]),"w")
	flag=0
	for fl in files:
		if fl.endswith("sim4"):
			for i in open("%s/temp/%s"%(conf["Output_dir"],fl),"r"):
				i=i.strip("\n")
				ele=i.split()
				if i=="":
					continue
				if i.startswith("seq"):
					if flag==0:
						flag=1
					else:
						if i.startswith("seq1"):
							output.write("\n")
					output.write("%s\t"%(re.split("=|,",i)[1]))
				else:
					if i=="(complement)":
						continue
					output.write("%s;%s\t"%(ele[0],re.split("\(|\)",ele[1])[1]))
	output.close()
	########################################
	sys.stderr.write('Blat Formating Finshed...\n')
	sys.stderr.write('AS Finding Start...\n')   
	loader = FastaLoader(conf["Reads"],verbose=True)
	###################
	reads=dict()
	for i in open("%s/sim4"%(conf["Output_dir"]),"r"):
		i=i.strip("\n")
		ele=i.split()
		pgs1=[j.split(";")[0] for j in ele[3:]]
		pgs2=[j.split(";")[1] for j in ele[3:]]
		for j in range(len(pgs1)):
			if j==len(pgs1)-1:
				continue
			(s1,e1)=[int(k) for k in pgs1[j].split("-")]
			(s1n,e1n)=[int(k) for k in pgs1[j+1].split("-")]
			(s2,e2)=[int(k) for k in pgs2[j].split("-")]
			(s2n,e2n)=[int(k) for k in pgs2[j+1].split("-")]
			gap=s1n-e1
			gappair=s2n-e2
			if gap>1 and gappair ==1:
				gene=ele[1]
				start=e1-1
				end=s1n-1
				seq=loader.subsequence(gene,start,end)
				if seq in reads:
					add(reads,gene,seq,"%s%s:%s-%s|%s:%s-%s;"%(reads[gene][seq],ele[1],e1+1,s1n-1,ele[2],e2,s2n))
				else:
					add(reads,gene,seq,"%s:%s-%s|%s:%s-%s;"%(ele[1],e1+1,s1n-1,ele[2],e2,s2n))
			if gappair>1 and gap==1:
				gene=ele[2]
				start=e2-1
				end=s2n-1
				seq=loader.subsequence(gene,start,end)
				if seq in reads:
					add(reads,gene,seq,"%s%s:%s-%s|%s:%s-%s;"%(reads[gene][seq],ele[2],e2+1,s2n-1,ele[1],e1,s1n))
				else:
					add(reads,gene,seq,"%s:%s-%s|%s:%s-%s;"%(ele[2],e2+1,s2n-1,ele[1],e1,s1n))
	output=open("%s/AS.result"%(path),"w")
	for i in reads:
		for j in reads[i]:
			if len(j)>int(conf["DeNovel_Cutoff"]):
				output.write("%s\t%s\t%s\n"%(i,reads[i][j],j))
	output.close()
	AStype(conf["Output_dir"],conf)
	sys.stderr.write('AS Finding End...\n')
	##Multie Procelling ending	 
def sub_blat(fl,conf):	###########################
	cmd="blat -t=dna -q=rna -tileSize=18 -oneOff=0 -minIdentity=96 -out=sim4 -maxIntron=10000 %s/temp/%s %s/temp/%s %s/temp/%s.sim4"%(conf["Output_dir"],fl,conf["Output_dir"],fl,conf["Output_dir"],fl)
	os.system(cmd)
	sys.stderr.write('%s Blat Finshed...\n'%(fl))
def docd_hit(conf):
	sys.stderr.write('Step1 Clustering Reads...\n')
	cmd="cd-hit-est -i %s -o %s/cd-hit.fasta -c 0.9 -n 10 -d 0 -M 20000 -T 0 -r 1"%(conf["Reads"],conf["Output_dir"])
	os.system(cmd)
	sys.stderr.write('Step1 Finshed...\n')
def dogmap(cf):
####################################################
###Align
	GMAP_IndexesDir=cf.get("input file","gmap_indexesdir")
	GMAP_IndexesName=cf.get("input file","gmap_indexesname")
	MaxIntron=cf.get("GMAP option","maxintron")
	GMAP_Process=cf.get("GMAP option","gmap_process")
	Reads=cf.has_option("input file","Pacbio_reads")
	Output_dir=cf.get("outputdir","Output_dir")
	sys.stderr.write('Step1 Aligning...\n')
	cmd='gmap -D %s -d %s --no-chimeras --cross-species --expand-offsets 1 -B 5 -K %s -f 2 -n 1 -t %d %s >%s/Align.gff3 2>%s/Align.log'%(GMAP_IndexesDir,GMAP_IndexesName,MaxIntron,int(GMAP_Process),Reads,Output_dir,Output_dir)
	os.system(cmd)
	sys.stderr.write('Step1 Finshed...\n')
def Format_gff3(fl,par,strand):
	chrom=dict()
	path=os.path.split(fl)[0]
	fll=os.path.split(fl)[1]
	out=open("%s/%s.format"%(path,fll),"w")
	flag=0
	sys.stderr.write('gff %s  formating...\n'%(fll))
	for i in open(fl,"r"):
		ele=i.strip("\n").split()
		if i.startswith("#") or i=="":
			continue
		if ele==[]:
			continue
		if ele[2]=="gene":
			if flag==0:
				flag=1
			else:
				out.write("\n")
			if not ele[0]  in chrom:
				chrom[ele[0]]=0
			else:
				chrom[ele[0]]+=1
			genename=ele[-1].split(";")[0].split("=")[-1].upper()
			out.write("%s.%d\t%s\t%s\t%s\t%s\t"%(ele[0],chrom[ele[0]],ele[3],ele[4],ele[6],genename))
		elif ele[2]=="exon":
			out.write("%s:%s\t"%(ele[3],ele[4]))
		elif ele[2]=="CDS" and par=="Y":
			out.write("C:%s:%s\t"%(ele[3],ele[4]))
	out.close()
	### if this is right
		###########
	#check if it's file is right
	if strand=="Y":
		out=open("%s/%s.format.adjust"%(path,fll),"w")
		for i in open("%s/%s.format"%(path,fll),"r"):
			i=i.strip("\n")
			ele=i.split()
			exonnum=[x for x in ele[5:] if not x.startswith("C")]
			if len(exonnum)<=1 or ele[3]=="+" :
				out.write("%s\n"%(i))
				continue
			else:
				#print int(ele[5].split(":")[0]),int(ele[6].split(":")[0]),ele[4],ele[3]
				if int(ele[5].split(":")[0])<int(ele[6].split(":")[0]):
					out.write("%s\n"%(i))
				else:
					##
					for st in range(5,len(ele)):
						if ele[st].startswith("C"):
							finalst=st-1
							break
				##
					exon=[]
					for x in ele[5:finalst]:
						exon.append(x)
					sort_exon=sorted(exon,key=lambda d:(int(d.split(":")[0])), reverse = False)
					##
					tag="\t".join(ele[:5])
					exonline="\t".join(sort_exon)
					cdsline="\t".join(ele[(finalst+1):])
					#print exonline
					out.write("%s\t%s\t%s\n"%(tag,exonline,cdsline))
		out.close()
		cmd="cp %s/%s.format.adjust %s/%s.format"%(path,fll,path,fll)
		os.system(cmd)
	sys.stderr.write('gff %s  formating finshed...\n'%(fll))
#############################################
def AltD_old(exondict,introndict,gene,strand):
	altd=dict()
	seqaltd=""
	count=0
	for i in introndict:
		(from1,to1)=i.split(':')
		(from1,to1)=(int(from1),int(to1))
		for j in introndict:
			(from2,to2)=j.split(':')
			(from2,to2)=(int(from2),int(to2))
			if from2<from1 and to2==to1:
				if introndict[i].split(":")[0]==introndict[j].split(":")[0] and introndict[i].split(":")[3]==introndict[j].split(":")[3]:
					altd["%s:%s"%(from2,from1)]=1
					count+=1
					#seqaltd+="ID	GeneID	geneSymbol	chr	strand	longExonStart_0base	longExonEnd	shortES	shortEE	flankingES	flankingEE\n"
					seqaltd+="%d\tGene\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\n"%(count,gene,strand,int(introndict[i].split(":")[0]),from1,\
					int(introndict[i].split(":")[0]),from2,int(introndict[i].split(":")[2]),int(introndict[i].split(":")[3]))
	return ",".join(x for x in altd),seqaltd
def AltA_old(exondict,introndict,gene,strand):
	alta=dict()
	seqalta=""
	count=0
	for i in introndict:
		(fs,fe)=i.split(':')
		(fs,fe)=(int(fs),int(fe))
		for j in introndict:
			(ss,se)=j.split(':')
			(ss,se)=(int(ss),int(se))
			if fs==ss and se<fe:
				if introndict[i].split(":")[3]==introndict[j].split(":")[3] and introndict[i].split(":")[0]==introndict[j].split(":")[0]:
					alta["%s:%s"%(se,fe)]=1
					count+=1
					#seqalta+="ID	GeneID	geneSymbol	chr	strand	longExonStart_0base	longExonEnd	shortES	shortEE	flankingES	flankingEE\n"
					seqalta+="%d\tGene\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\n"%(count,gene,strand,se-1,\
					int(introndict[i].split(":")[3]),fe-1,int(introndict[i].split(":")[3]),int(introndict[i].split(":")[0])-1,ss)
	return ",".join(x for x in alta),seqalta
#################################################
def Altpos_old(exondict,introndict):
	altpos=dict()
	for i in introndict:
		(from1,to1)=(int(x) for x in i.split(':'))
		for j in introndict:
			if i!=j:
				(from2,to2)=(int(x) for x in j.split(':'))
				if (introndict[i].split(":")[0]==introndict[j].split(":")[0] and introndict[i].split(":")[-1]==introndict[j].split(":")[-1]) \
				and (from2< from1 and to1<to2):
					altpos[i]=1
	return ",".join(x for x in altpos)
def ES_old(exondict,introndict,gene,strand):
	es=dict()
	seqes=""
	count=0
	for i in exondict:
		(exs,exe)=i.split(':')
		(exs,exe)=(int(exs),int(exe))
		for j in introndict:
			(ins,ine)=j.split(':')
			(ins,ine)=(int(ins),int(ine))
			#print exondict[i]
			if (ins<exs and exe<ine) and int(exondict[i].split(":")[1])==ins and int(exondict[i].split(":")[2])==ine:
				es[i]=1
				count+=1
				#seqes+="ID	GeneID	geneSymbol	chr	strand	exonStart_0base	exonEnd	upstreamES	upstreamEE	downstreamES	downstreamEE\n"
				seqes+="%d\tGene\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\n"%(count,gene,strand,exs-1,exe,int(introndict[j].split(":")[0])-1,ins,ine-1,int(introndict[j].split(":")[3]))
	return ",".join(x for x in es),seqes
def IR_old(exondict,introndict,gene,strand):
	ir=dict()
	seqir=""
	count=0
	for i in exondict:
		(exs,exe)=i.split(':')
		(exs,exe)=(int(exs),int(exe))
		for j in introndict:
			(ins,ine)=j.split(':')
			(ins,ine)=(int(ins),int(ine))
			if (exs<ins and ine<exe) and (int(introndict[j].split(":")[0])==exs and int(introndict[j].split(":")[3])==exe):
				line="%s_%s"%(j,i)
				ir[j]=1
				count+=1
				#seqir+="ID	GeneID	geneSymbol	chr	strand	riExonStart_0base	riExonEnd	upstreamES	upstreamEE	downstreamES	downstreamEE\n"
				seqir+="%d\tGene\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\n"%(count,gene,strand,exs-1,exe,exs-1,ins,ine-1,exe)
	return ",".join(x for x in ir),seqir
def Cluster_Reads(fl):
	readDict = { }
	clusterDist = 50
	clusterMembers = 1
	cluster = collections.defaultdict(lambda:ClusterTree(clusterDist, 
                                                                clusterMembers))
	flag = 0
	path=os.path.split(fl)[0]
	fll=os.path.split(fl)[1]
	sys.stderr.write('Cluster %s...\n'%(fll))
	output=open("%s/%s.cluster"%(path,fll),"w")
	for i in open(fl,"r"):
		i=i.strip('\n')
		flag+=1
		ele=i.split()
		chrome=ele[0].split('.')[0]
		start=int(ele[1])
		end=int(ele[2])
		cluster[chrome].insert(start,end,flag)
		readDict[flag] = i
	for key in cluster.keys():
		num=0
		regions = cluster[key].getregions()
		for region in regions:
			num+=1
			for rid in region[-1]:
				output.write("%s.%d\t%s\n"%(key,num,readDict[rid]))
	output.close()
	sys.stderr.write('Cluster %s Finshed...\n'%(fll))
######################################################################
def Wig_count(bamfile,Gene_coordinate,strand,num,cf):
	wig=dict()
	typpd=dict()
	reads=commands.getoutput("samtools view %s %s"%(bamfile,Gene_coordinate))
	##############
	#strand
	for i in reads.split('\n'):
		dd=i.split()
		if not dd:
			continue
		if i.startswith("[main_samview]") or i.startswith("Warning"):
			continue
		(flag,pos,cigar,seq)=(int(dd[1]),int(dd[3]),dd[5],dd[9])
		Strand_Specificity=cf.get("Wig option","Strand_Specificity")
		if Strand_Specificity=='True':
			#print (flag&16)==0,strand
			if (flag&16)==0 and strand=='-':
				continue
			if (flag&16)==16 and strand=='+':
				continue
	#strand end
	#################
		#Mapping position
		if 'D' in cigar or 'I' in cigar:
			continue
		if 'N' in cigar:
			ele=[int(x) for y,x in enumerate(re.split('M|N',cigar)) if int(y)!=(len(re.split('M|N',cigar))-1)]
			#print ele
			#print i
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
	##Normailiation
	for j in wig:
		wig[j]*=10000000
		wig[j]/=num
	sortwig=sorted(wig.iteritems(), key=lambda d:d[0])
	###Normailation END	
	return wig
###############################################
def getPeaks(depths,cf):
    """
    Get polyA peaks for given set of depths
    """
    width_of_peaks=cf.get("Polya option","width_of_peaks")
    MinDist=cf.get("Polya option","MinDist")
    MinSupport=cf.get("Polya option","MinSupport")
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
###############################################
def parrse_cufflinks(cf):
	outputdir=cf.get("outputdir","Output_dir")
	cufflinksfile=cf.get("input file","Cuffmerge_file")
	out=open("%s/cufflinks.gtf.format"%(outputdir),"w")
	sys.stderr.write('cufflinks gff %s formating...\n'%(cufflinksfile))
	cufflinksdict=dict()
	for i in open(cufflinksfile,"r"):
		i=i.rstrip()
		ele=i.split()
		gene=re.split("transcript_id |;",i)[2]
		gene=gene.replace("\"","")
		add(cufflinksdict,gene,i,1)
	for i in cufflinksdict:
		scaff=cufflinksdict[i].keys()[0].split()[0]
		minpos=min(int(x.split()[3])for x in cufflinksdict[i])
		maxpos=max(int(x.split()[4])for x in cufflinksdict[i])
		strand=cufflinksdict[i].keys()[0].split()[6]
		exon=(":".join(x.split()[3:5]) for x in cufflinksdict[i])
		if strand=="-":
			exon=sorted(exon,key=lambda d:int(d.split(":")[0]), reverse=True)
		elif strand=="+":
			exon=sorted(exon,key=lambda d:int(d.split(":")[0]), reverse=False)
		exonline="\t".join(exon)
		out.write("%s\t%s\t%s\t%s\tcufflinks;%s\t%s\n"%(scaff,minpos,maxpos,strand,i,exonline))
	out.close()
