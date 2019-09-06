#!/usr/bin/env python
from __future__ import division
import numpy as np
import sys,os,re,commands
import numpy,pysam
from fisher import pvalue
from  collections import defaultdict
from itertools import combinations
import ConfigParser
global cf
cf = ConfigParser.ConfigParser()
cf.read(sys.argv[-1])
def de_nat_edger(genename,fpkmcal):
	genenamedot=".".join(genename.split(";"))
	outputdir=cf.get("outputdir","Output_dir")
	libgroup=cf.get('DE NAT option','delib')
	#myr = R()
	libs=list(x for x in libgroup.split())
	comlibs=list(combinations(libs,2))
	p_value=float(cf.get("DE NAT option","p_value_set"))
	fdr=float(cf.get("DE NAT option","fdr_set"))
	#fcup=float(cf.get("DE NAT option","fc"))
	returndict=[]
	for i,j in comlibs:
		lib1=conf[i.split("_")[0].lower()].strip('\n').split()[0]
		lib11=re.sub("\d+","",lib1)
		lib2=conf[j.split("_")[0].lower()].strip('\n').split()[0]
		lib22=re.sub("\d+","",lib2)
		out=open("%s/temp/%s_%s_%s.R"%(outputdir,genenamedot,lib11,lib22),"w")
		ii=i.split("_")
		jj=j.split("_")
		out.write("Symbol\tA\tA\tA\tB\tB\tB\n")	
		out.write("%s_%s_%s_+\t%d\t%d\t%d\t"%(genename,lib11,lib22,fpkmcal[ii[0].lower()]["+_f"],fpkmcal[ii[1].lower()]["+_f"],fpkmcal[ii[2].lower()]["+_f"]))
		out.write("%d\t%d\t%d\n"%(fpkmcal[jj[0].lower()]["+_f"],fpkmcal[jj[1].lower()]["+_f"],fpkmcal[jj[2].lower()]["+_f"]))
		#####
		out.write("%s_%s_%s_-\t%d\t%d\t%d\t"%(genename,lib11,lib22,fpkmcal[ii[0].lower()]["-_r"],fpkmcal[ii[1].lower()]["-_r"],fpkmcal[ii[2].lower()]["-_r"]))
		out.write("%d\t%d\t%d\n"%(fpkmcal[jj[0].lower()]["-_r"],fpkmcal[jj[1].lower()]["-_r"],fpkmcal[jj[2].lower()]["-_r"]))
		out.close()
		#####
		clu=genename
		cmd="edge.R %s/temp/%s_%s_%s.R %s/temp/%s_%s_%s.out 1>/dev/null 2>/dev/null"%(outputdir,genenamedot,lib11,lib22,outputdir,genenamedot,lib11,lib22)
		os.system(cmd)
		if not os.path.exists("%s/temp/%s_%s_%s.out"%(outputdir,genenamedot,lib11,lib22)):
			return 0
		else:
			pass
			#print "%s\thave results"%(genename)
		for line in open("%s/temp/%s_%s_%s.out"%(outputdir,genenamedot,lib11,lib22),"r"):
				if line.startswith("logFC"):
					continue
				line=line.rstrip()
				ele=line.split()
				logFC,logCPM,PValue,FDR=(float(x) for x in ele[1:])
				FC=pow(2,abs(logFC))
				if PValue<p_value and FDR <fdr:
					returndict.append(line)
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
def judge_nat(clu,Output_dir):
	genename=clu
	forward=[x for x in mapdict[clu] if x.split()[4]=="+"]
	reverse=[x for x in mapdict[clu] if x.split()[4]=="-"]
	mark="False"
	pairs=[]
	fpkmcal=defaultdict(dict)
	#countcal=defaultdict(dict)
	#out=open("%s/temp/%s.natpair"%(Output_dir,genename),"w")
	for i in forward:
		(s,e)=(int(x) for x in i.split()[2:4])
		for j in reverse:
			ss,ee=(int(x) for x in j.split()[2:4])
			if s<ss<e and ee>e and e-ss>50:
				#out.write("3'-3'_1\t%s\t%s\n"%(i,genename))
				#out.write("3'-3'_2\t%s\t%s\n"%(j,genename))
				mark="True"
				pairs.append(["3'-3'",i.split()[1],j.split()[1]])
			elif s<ee<e and ss<s and ee-s>50:
				#out.write("5'-5'_1\t%s\t%s\n"%(i,genename))
				#out.write("5'-5'_2\t%s\t%s\n"%(j,genename))
				mark="True"
				pairs.append(["5'-5'",i.split()[1],j.split()[1]])
			elif (ss<s and e<ee) or (s<ss and ee<e):
				#out.write("Fully_overlap_1\t%s\t%s\n"%(i,genename))
				#out.write("Fully overlap_2\t%s\t%s\n"%(j,genename))
				mark="True"
				pairs.append(["Fully_overlap",i.split()[1],j.split()[1]])
	#out.close()
	if mark!="False" and cf.has_section("DE NAT option"):
		lib=cf.get("DE NAT option","DElib")
		libs=list(x for x in lib.split())
		comlibs=list(combinations(libs, len(libs)-1))
		chro=clu.split(";")[0]
		#####################
		f_s=min(int(x.split()[2]) for x in forward)
		f_e=max(int(x.split()[3]) for x in forward)
		r_s=min(int(x.split()[2]) for x in reverse)
		r_e=max(int(x.split()[3]) for x in reverse)
		lendict=[]
		for i in forward:
			for j in i.split()[6:]:
				start,end=(int(x) for x in j.split(":"))
				for point in range(start,end+1):
					lendict.append(point)
		f_exonlength=len(set(lendict))
		lendict=[]
		for i in reverse:
			for j in i.split()[6:]:
				start,end=(int(x) for x in j.split(":"))
				for point in range(start,end+1):
					lendict.append(point)
		r_exonlength=len(set(lendict))
		#out=open("%s/temp/%s.fpkm"%(Output_dir,genename),"w")
		#out.write("%s\t"%(genename))
		for i in conf:
				if i.startswith("lib"):
					(tpp,bamfile,rgb)=conf[i].strip('\n').split()
					num=bamlist[i.lower()]
					fpkmforward,countf=fpkm(bamfile,chro,"+",f_s,f_e,f_exonlength,num)
					fpkmreverse,countr=fpkm(bamfile,chro,"-",r_s,r_e,r_exonlength,num)
					#out.write("%f\t%f\t"%(fpkmforward,fpkmreverse))
					fpkmcal[i]["+"]=fpkmforward
					fpkmcal[i]["+_f"]=countf
					fpkmcal[i]["-"]=fpkmreverse
					fpkmcal[i]["-_r"]=countr
		#out.close()
	return mark,pairs,fpkmcal
def countnum(libname,bamfile):
	numout=commands.getoutput("samtools view %s|cut -f 1|sort -T temp|uniq|wc -l "%(bamfile))
	num=numout.split()[0]
	return libname,num
###########
cluster_file=sys.argv[1]
outdir=sys.argv[2]
Output_dir=sys.argv[3]
tpd=sys.argv[4]
Multile_processing=sys.argv[5]
###########
global conf
conf=dict()
for x in cf.items("Wig option"):
	if x[0].startswith("lib"):
		conf[x[0]]=x[1]
#########
sys.stderr.write('Reading Cluster file...\n')
cluster=open("%s/merge.format.none.cluster"%(Output_dir),'r')
Output_dir=cf.get("outputdir","Output_dir")
###########################
mapdict=defaultdict(dict)
for line in cluster:
	line=line.strip('\n')
	name=line.split()[0]
	mapdict[name][line]=1
sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
###########################
oFile = open(outdir+'/de_nat.txt', 'w'); ## alt-3 SS output file
oFileHeader ="ID	logFC	logCPM	PValue	FDR";
oFile.write(oFileHeader+'\n');
##########################
bamlist=dict()
Multile_processing=cf.get("Global option","Multile_processing")
if Multile_processing=="True":
	results = []
	pool = multiprocessing.Pool()
	for x in cf.items("Wig option"):
		if x[0].startswith("lib"):
			ele=x[1].split()
			result=pool.apply_async(countnum, (x[0],ele[1],))
			results.append(result)
	pool.close()
	pool.join()
	for result in results:
		libname,num=result.get()
		bamlist[libname]=int(num)
else:
	for x in cf.items("Wig option"):
		if x[0].startswith("lib"):
			ele=x[1].split()
			libname,num=countnum(x[0],ele[1])
			bamlist[libname]=int(num)
###################################
MAX_VALUE = len(mapdict.keys())-1
sys.stderr.write('complute de nat ...\n')
denatcount=0
for i in mapdict:
	gene=i.split(';')[0]
	strand=list(set([x.split()[4] for x in mapdict[i]]))
	if len(strand)!=2:
		continue
	strand=strand[0]
	########################
	minpos  = min(int(x.split()[2]) for x in mapdict[i])
	maxpos  = max(int(x.split()[3]) for x in mapdict[i])
	minpos=int(minpos)
	maxpos=int(maxpos)
	Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
	########################
	status,pairs,fpkmcal=judge_nat(i,Output_dir)
	if status!="True":
		continue
	de_nat_lib=de_nat_edger(i,fpkmcal)
	if (not de_nat_lib) or de_nat_lib=="None":
		continue
	else:
		denatcount+=1
		for x in de_nat_lib:
			oFile.write(x+"\n")
oFile.close()
print "there is %d denatcounts "%(denatcount)
####################################
