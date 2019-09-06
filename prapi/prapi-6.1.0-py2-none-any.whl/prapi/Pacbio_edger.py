from __future__ import division
from collections import OrderedDict
#2017/05/04 09:35:36
# add aditional nat as and apa 
#2017/05/03 11:45:00
# add aditional fpkm count 
#2017/05/02 08:53:21
# add nat supports
#2017/04/25 15:13:01
# add mats supports
#2017/04/20 14:29:08
# differential alternative spling identifing added
#2017/04/11 09:55:41
# differential apa site identifing added 
#2017/04/05 15:45:05
# add de apa site adentify
from  collections import defaultdict
from pyper import *
import cairo
import os,sys,collections,re,multiprocessing,commands,shutil
import numpy
from argparse import ArgumentParser
from SpliceGrapher.formats.loader import loadGeneModels
from math import pi as p
##############
import ConfigParser
##############
parser = ArgumentParser(description='Pacbio tool  Build by BFPC')
parser.add_argument('-c', '--conf', dest="conf",
                    action='store', type=str, default='conf',
                    help='The configurition file you need')               
args = parser.parse_args()
###############
sys.path.append("scripts")
from Pacbio_untils_edger import *
from asas import *
#from Pacbio_mats import *
###############
global cf
cf = ConfigParser.ConfigParser()
cf.read(args.conf)
###############
def Control(Genome_Annotion_format):
	Genome_Annotion=cf.get("input file","genome_annotion")
	Output_dir=cf.get("outputdir","Output_dir")
	Multile_processing=cf.get("Globe option","Multile_processing")
	allgene=dict()
	for i in open(Genome_Annotion_format,"r"):
		i=i.strip("\n")
		ele=i.split()
		allgene[ele[4]]=i
	for itelfile in ("temp","Annotation","Annotation_Miss","Novel_Gene","NAT/Head2Head","NAT/Tail2Tail","NAT/Full_overlap","NAT/Not","NAT/Yes"):
		if not os.path.exists("%s/%s"%(Output_dir,itelfile)):
			os.makedirs("%s/%s"%(Output_dir,itelfile))
	cmd="rm -rf %s/temp/*.csv"%(Output_dir)
	os.system(cmd)
	cmd="rm  %s/natpair.txt"%(Output_dir)
	os.system(cmd)
	if Multile_processing=="True":
		pool = multiprocessing.Pool()
		for clu in mapdict:
			#if clu!="PH01000426.11":
			#	continue
			pool.apply_async(subcon, (clu,allgene,))
		pool.close()
		pool.join()
	else:
		for clu in mapdict:
			#if clu!="PH01000164.15":
			#	continue
			subcon(clu,allgene)
def subcon(clu,allgene):
	DE_APA=cf.get("DE APA option","DE")
	DE_AS=cf.get("DE AS option","DE")
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split('.')[0]
		##########################
		### if mark in this region
		###################
		######
		##### GFF Adapation
		#####
		#####	gene=[x.split()[4] for x in mapdict[i]]
		###################
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		###################
		refGenes = geneModel.getGenesInRange(gene,minpos,maxpos)
		if len(refGenes)>=1:
			genename='_'.join(str(reg).split(' (')[0] for reg in refGenes)
			writename=genename
		else:
			genename="Novel_%s:%s-%s"%(gene,minpos,maxpos)
			writename="Novel"
		if len(refGenes)==0:
			path="Novel_Gene"
		elif len(refGenes)==1:
			path="Annotation"
		elif len(refGenes)>1:
			path="Annotation_Miss"
		#if genename!="PH01004969G0010_PH01004969G0020":
		#	continue
		sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = False)
		###	NAT fillter
		strand=dict()
		for k in sort_dict:
			if k.split()[4]==".":
				continue
			strand[k.split()[4]]=1
		Output_dir=cf.get("outputdir","Output_dir")
		if len(strand)==2:
			path="NAT"
			ir="NULL"
			cuffir="NULL"
			es="NULL"
			cuffes="NULL"
			altd="NULL"
			cuffaltd="NULL"
			alta="NULL"
			cuffalta="NULL"
			altp="NULL"
			cuffaltp="NULL"
			apapos="NULL"
			atipos="NULL"
			nat="True"
			deas=""
			if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
				difflibapa="NULL"
				#Visual_pacbio_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,ir,cuffir,es,cuffes,alta,cuffalta,altd,cuffaltd,altp,cuffaltp,nat,difflibapa)
				#sys.exit()
			elif cf.has_option("input file","Pacbio_reads"):
				status,pairs,fpkmcal=judge_nat(clu,Output_dir,genename)
				#######
				if status=="True":
					(ir_f,es_f,altd_f,alta_f,altp_f)=AS(clu,"pacbio","+")
					(ir_r,es_r,altd_r,alta_r,altp_r)=AS(clu,"pacbio","-")
					apapos_f=APA(clu,"+")
					atipos_f=ATI(clu,"+")
					apapos_r=APA(clu,"-")
					atipos_r=ATI(clu,"-")
					output=open("%s/temp/%s.nat"%(Output_dir,genename),"w")
					output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n"%(genename,ir_f,es_f,altd_f,alta_f,altp_f,ir_r,es_r,altd_r,alta_r,altp_r,apapos_f,atipos_f,apapos_r,atipos_r))
					output.close()
					de_nat_lib=de_nat_edger(genename,fpkmcal,cf,conf)
					#de_nat_lib=de_nat(genename,fpkmcal,cf,conf)
					if not de_nat_lib:
						continue
					else:
						print de_nat_lib
					#Visual_nat(clu,allgene,genename,refGenes,path,apapos_f,atipos_f,apapos_r,atipos_r,ir_f,es_f,alta_f,altd_f,altp_f,nat,"NULL",pairs,fpkmcal,ir_r,es_r,alta_r,altd_r,altp_r,de_nat_lib)
					#sys.exit()
				else:
					continue
				#sys.exit()
			elif cf.has_option("input file","Cuffmerge_file"):
				Visual_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,cuffir,cuffes,cuffalta,cuffaltd,cuffaltp,nat)	
		else:
			continue
			###	NAT
			###	AS Started
			nat="False"
			if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
				apapos=APA(clu)
				atipos=ATI(clu)
				if apapos==None:
					apapos="NULL"
				if atipos==None:
					atipos="NULL"
				if not strand:
					continue
				(ir,es,altd,alta,altp,seqir,seqes,seqalta,seqaltd)=AS(clu,"pacbio",gene,strand.keys()[0])
				if seqir or seqes or seqalta or seqaltd:
					#print len(seqir);print len(seqes);print len(seqalta);print len(seqaltd)
					if seqir:
						ir_handle=open("%s/temp/%s.IRmats"%(genename,Output_dir),"w")
						ir_handle.write(seqir)
						ir_handle.close()
					if seqes:
						## es
						es_handle=open("%s/temp/%s.ESmats"%(Output_dir,genename),"w")
						es_handle.write(seqes)
						es_handle.close()
					if seqalta:
						alta_handle=open("%s/temp/%s.AltAmats"%(Output_dir,genename),"w")
						alta_handle.write(seqalta)
						alta_handle.close()
					if seqaltd:
						altd_handle=open("%s/temp/%s.AltDmats"%(Output_dir,genename),"w")
						altd_handle.write(seqaltd)
						altd_handle.close()
					###
				else:
					continue
				(cuffir,cuffes,cuffaltd,cuffalta,cuffaltp,seqir,seqes,seqalta,seqaltd)=AS(clu,"cufflinks",gene,strand.keys()[0])
				output=open("%s/temp/%s.csv"%(Output_dir,genename),"w")
				output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(writename,path,Gene_coordinate,apapos,atipos,ir,cuffir,es,cuffes,alta,cuffalta,altd,cuffaltd
												,altp,cuffaltp,";".join(x.split()[5] for x in mapdict[i])))
				output.close()
				if DE_APA=="True":
					if not strand.keys():
						continue
					difflibapa=difference_expression_peaks(clu,mapdict[clu],apapos,cf,conf,strand.keys()[0],Gene_coordinate,genename)
					if difflibapa!="NULL":
						print difflibapa
					else:
						continue
				else:
					difflibapa="NULL"
				Visual_pacbio_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,ir,cuffir,es,cuffes,alta,cuffalta,altd,cuffaltd,altp,cuffaltp,nat,difflibapa)
				#sys.exit()
			elif cf.has_option("input file","Pacbio_reads"):
				apapos=APA(clu)
				atipos=ATI(clu)
				if apapos==None:
					apapos="NULL"
				if atipos==None:
					atipos="NULL"
				(ir,es,altd,alta,altp,seqir,seqes,seqalta,seqaltd)=AS(clu,"pacbio",gene,strand)
				output=open("%s/temp/%s.csv"%(Output_dir,genename),"w")
				output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(writename,path,Gene_coordinate,apapos,atipos,ir,es,alta,altd,altp,";".join(x.split()[5] for x in mapdict[i])))
				output.close()
				if DE_APA=="True":
					difflib=difference_expression_peaks(clu,mapdict[clu],apapos,cf,conf,strand.keys()[0],Gene_coordinate,genename)
				else:
					difflib="NULL"
				#Visual_pacbio_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,ir,cuffir,es,cuffes,alta,cuffalta,altd,cuffaltd,altp,cuffaltp,nat,difflib)
				Visual(clu,allgene,genename,refGenes,path,apapos,atipos,ir,es,alta,altd,altp,nat,difflib)
				sys.exit()
				#Visual(clu,allgene,genename,refGenes,path,apapos,atipos,ir,es,alta,altd,altp,nat)
			elif cf.has_option("input file","Cuffmerge_file"):
				(cuffir,cuffes,cuffaltd,cuffalta,cuffaltp)=AS(clu,"cufflinks")
				apapos,atipos="NULL","NULL"
				output=open("%s/temp/%s.csv"%(Output_dir,genename),"w")
				output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(writename,path,Gene_coordinate,cuffir,cuffes,cuffalta,cuffaltd,cuffaltp,";".join(x.split()[5] for x in mapdict[i])))
				output.close()
				Visual_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,cuffir,cuffes,cuffalta,cuffaltd,cuffaltp,nat)
def Visual_nat(clu,allgene,genename,refGenes,path,apapos,atipos,apapos_r,atipos_r,ir,es,alta,altd,altp,nat,difflib,pairs,fpkmcal,ir_r,es_r,alta_r,altd_r,altp_r,de_nat_lib):
	global hh,ashigh
	wiggg=dict()
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split('.')[0]
		############################
		#### GFF Adapation
		#################
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		##############################
		if nat=="True":
			sort_dict= sorted(mapdict[i], key=lambda d:(d.split()[4]), reverse = False)
		else:
			sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = False)
		##############################
		#	high of figure
		if genename.startswith("Novel"):
			angene=0
		else:
			angene=2*len(genename.split("_"))
		###################################
		atinum=[]
		for subati in atipos.split(","):
			atinum.append(subati)
		for subati in atipos_r.split(","):
			atinum.append(subati)
		####################################
		apanum=[]
		for subnum in apapos.split(","):
			apanum.append(subnum)
		for subnum in apapos_r.split(","):
			apanum.append(subnum)
		####################################
		asnum=0
		for subas in (ir,es,alta,altd,altp,ir_r,es_r,alta_r,altd_r,altp_r):
			if subas!="NULL":
				asnum+=1
		libnum=[]
		for libsub in conf:
			if libsub.startswith("lib"):
				libnum.append(libsub)
		#################################################
		if nat=="True":
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*2*len(libnum)+10+10*2*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		else:
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		#################################################
		Output_dir=cf.get("outputdir","Output_dir")
		surface = cairo.PDFSurface("%s/%s/%s.pdf"%(Output_dir,path,genename), 500, hight_of)
		sys.stderr.write("	%s has processed\n"%(genename))
		cr = cairo.Context(surface)
		######
		if len(sort_dict)-1 <12:
			h=4
		else:
			h=70/(len(sort_dict)+2)
		line=1*h/3
		arrayline=1*line/2
		scale=400/(maxpos-minpos+1)
		bar_high=35
		###
		##example
		if len(refGenes)!=0: 
			annomin=min(int(str(reg).split()[-3]) for reg in refGenes)
			annomax=max(int(str(reg).split()[-1]) for reg in refGenes)
			minpos=min(annomin,minpos)
			maxpos=max(annomax,maxpos)
		scale=400/(maxpos-minpos+1)
		posnum=(maxpos-minpos+1)//10
		example(cr,h,scale,line,arrayline,bar_high,nat,genename,de_nat_lib)
		###
		###
		##annotation gene 
		hh=70+10
		annotation(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene)
		###########################
		transcripts(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,nat,pairs)
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib,fpkmcal)
			#if deas!="":
			#	deasplot(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,deas)
		atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,"+")
		atiapa(atinum,apanum,atipos_r,apapos_r,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,"-")
		ashigh=hh
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,ir,es,alta,altd,altp,posnum,"+")
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,ir_r,es_r,alta_r,altd_r,altp_r,posnum,"-")
		footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum)
		cr.show_page()
		surface.finish()
def judge_nat(clu,Output_dir,genename):
	#"NAT/Head2Head","NAT/Tail2Tail","NAT/Full_overlap","NAT/Not"
	forward=[x for x in mapdict[clu] if x.split()[4]=="+"]
	reverse=[x for x in mapdict[clu] if x.split()[4]=="-"]
	mark="False"
	pairs=[]
	fpkmcal=defaultdict(dict)
	#countcal=defaultdict(dict)
	out=open("%s/temp/%s.natpair"%(Output_dir,genename),"w")
	for i in forward:
		(s,e)=(int(x) for x in i.split()[2:4])
		for j in reverse:
			ss,ee=(int(x) for x in j.split()[2:4])
			if s<ss<e and ee>e and e-ss>50:
				out.write("3'-3'_1\t%s\t%s\n"%(i,genename))
				out.write("3'-3'_2\t%s\t%s\n"%(j,genename))
				mark="True"
				pairs.append(["3'-3'",i.split()[1],j.split()[1]])
			elif s<ee<e and ss<s and ee-s>50:
				out.write("5'-5'_1\t%s\t%s\n"%(i,genename))
				out.write("5'-5'_2\t%s\t%s\n"%(j,genename))
				mark="True"
				pairs.append(["5'-5'",i.split()[1],j.split()[1]])
			elif (ss<s and e<ee) or (s<ss and ee<e):
				out.write("Fully_overlap_1\t%s\t%s\n"%(i,genename))
				out.write("Fully overlap_2\t%s\t%s\n"%(j,genename))
				mark="True"
				pairs.append(["Fully_overlap",i.split()[1],j.split()[1]])
	out.close()
	if mark!="False" and cf.get("DE NAT option","DE")=="True":
		pass
		lib=cf.get("DE APA option","DElib")
		libs=list(x for x in lib.split())
		comlibs=list(combinations(libs, len(libs)-1))
		chro=i.split(".")[0]
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
		"""
		######################
		r_s=min(int(x.split()[2]) for x in reverse)
		r_e=max(int(x.split()[3]) for x in reverse)
		lendict=[]
		for i in reverse:
			for j in i.split()[6:]:
				start,end=(int(x) for x in j.split(":"))
				for point in range(start,end+1):
					lendict.append(point)
		r_exonlength=len(set(lendict))
		#######################
		for i,j in comlibs:
			######
			(tpp,bamfile,rgb)=conf[i.lower()].strip('\n').split()
			num=bamlist[i.lower()]
			fpkmforward1=fpkm(bamfile,chro,"+",f_s,f_e,f_exonlength,num)
			fpkmreverse1=fpkm(bamfile,chro,"-",r_s,r_e,r_exonlength,num)
			######
			(tpp,bamfile,rgb)=conf[j.lower()].strip('\n').split()
			num=bamlist[j.lower()]
			fpkmforward2=fpkm(bamfile,chro,"+",f_s,f_e,f_exonlength,num)
			fpkmreverse2=fpkm(bamfile,chro,"-",r_s,r_e,r_exonlength,num)
			######
			print fpkmforward1,fpkmforward2,fpkmreverse1,fpkmreverse2
		"""
		out=open("%s/temp/%s.fpkm"%(Output_dir,genename),"w")
		out.write("%s\t"%(genename))
		for i in conf:
				if i.startswith("lib"):
					(tpp,bamfile,rgb)=conf[i].strip('\n').split()
					num=bamlist[i.lower()]
					fpkmforward,countf=fpkm(bamfile,chro,"+",f_s,f_e,f_exonlength,num)
					fpkmreverse,countr=fpkm(bamfile,chro,"-",r_s,r_e,r_exonlength,num)
					out.write("%f\t%f\t"%(fpkmforward,fpkmreverse))
					fpkmcal[i]["+"]=fpkmforward
					fpkmcal[i]["+_f"]=countf
					fpkmcal[i]["-"]=fpkmreverse
					fpkmcal[i]["-_r"]=countr
		out.close()
	return mark,pairs,fpkmcal
def Visual_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,ir,es,alta,altd,altp,nat):
	global hh,ashigh
	wiggg=dict()
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split('.')[0]
		############################
		#### GFF Adapation
		#################
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		#################
		if nat=="True":
			sort_dict= sorted(mapdict[i], key=lambda d:(d.split()[4]), reverse = False)
		else:
			sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = False)
		#############################
		#	high of figure
		if genename.startswith("Novel"):
			angene=0
		else:
			angene=2*len(genename.split("_"))
		atinum=[]
		for subati in atipos.split(","):
			atinum.append(subati)
		apanum=[]
		for subnum in apapos.split(","):
			apanum.append(subnum)
		asnum=0
		for subas in (ir,es,alta,altd,altp):
			if subas!="NULL":
				asnum+=1
		libnum=[]
		for libsub in conf:
			if libsub.startswith("lib"):
				libnum.append(libsub)
		#######################################################
		if nat=="True":
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*2*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		else:
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		#################################################
		Output_dir=cf.get("outputdir","Output_dir")
		surface = cairo.PDFSurface("%s/%s/%s.pdf"%(Output_dir,path,genename), 500, hight_of)
		sys.stderr.write("	%s has processed\n"%(genename))
		cr = cairo.Context(surface)
		######
		if len(sort_dict)-1 <12:
			h=4
		else:
			h=70/(len(sort_dict)+2)
		line=1*h/3
		arrayline=1*line/2
		scale=400/(maxpos-minpos+1)
		bar_high=35
		###
		##example
		if len(refGenes)!=0: 
			annomin=min(int(str(reg).split()[-3]) for reg in refGenes)
			annomax=max(int(str(reg).split()[-1]) for reg in refGenes)
			minpos=min(annomin,minpos)
			maxpos=max(annomax,maxpos)
		scale=400/(maxpos-minpos+1)
		posnum=(maxpos-minpos+1)//10
		example(cr,h,scale,line,arrayline,bar_high,nat,genename)
		###
		###
		##annotation gene 
		hh=70+10
		annotation(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene)
#################################
		transcripts(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,nat)
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat)
		atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat)
		ashigh=hh
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,ir,es,alta,altd,altp,posnum,"C")
		footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum)
#################################
def Visual_pacbio_cuff(clu,allgene,genename,refGenes,path,apapos,atipos,ir,cuffir,es,cuffes,alta,cuffalta,altd,cuffaltd,altp,cuffaltp,nat,difflib):
	global hh,ashigh
	wiggg=dict()
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split('.')[0]
		############################
		#### GFF Adapation
		#################
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		#################
		if nat=="True":
			sort_dict= sorted(mapdict[i], key=lambda d:(d.split()[4]), reverse = True)
			pacbio_dict=(x for x in mapdict[i] if not x.split()[5].startswith("cufflinks"))
			pacbio_dict_sort=sorted(pacbio_dict, key=lambda d:(d.split()[4]), reverse = True)
			cufflinks_dict=(x for x in mapdict[i] if  x.split()[5].startswith("cufflinks"))
			cufflinks_dict_sort=sorted(cufflinks_dict, key=lambda d:(d.split()[4]), reverse = True)
		else:
			sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = True)
			pacbio_dict=(x for x in mapdict[i] if not x.split()[5].startswith("cufflinks"))
			pacbio_dict_sort=sorted(pacbio_dict, key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = True)
			cufflinks_dict=(x for x in mapdict[i] if  x.split()[5].startswith("cufflinks"))
			cufflinks_dict_sort=sorted(cufflinks_dict, key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = True)
		##################
		#	high of figure
		if genename.startswith("Novel"):
			angene=0
		else:
			angene=2*len(genename.split("_"))
		atinum=[]
		if atipos!="NULL":
			for subati in atipos.split(","):
				atinum.append(subati)
		apanum=[]
		if apapos!="NULL":
			for subnum in apapos.split(","):
				apanum.append(subnum)
		asnum=0
		for subas in (ir,cuffir,es,cuffes,alta,cuffalta,altd,cuffaltd,altp,cuffaltp):
			if subas!="NULL":
				asnum+=1
		libnum=[]
		for libsub in conf:
			if libsub.startswith("lib"):
				libnum.append(libsub)
		#######################################################
		if nat=="True":
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*2*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		else:
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		#################################################
		Output_dir=cf.get("outputdir","Output_dir")
		surface = cairo.PDFSurface("%s/%s/%s.pdf"%(Output_dir,path,genename), 500, hight_of)
		sys.stderr.write("	%s has processed\n"%(genename))
		cr = cairo.Context(surface)
		######
		if len(sort_dict)-1 <12:
			h=4
		else:
			h=70/(len(sort_dict)+2)
		line=1*h/3
		arrayline=1*line/2
		scale=400/(maxpos-minpos+1)
		bar_high=35
		###
		##example
		if len(refGenes)!=0: 
			annomin=min(int(str(reg).split()[-3]) for reg in refGenes)
			annomax=max(int(str(reg).split()[-1]) for reg in refGenes)
			minpos=min(annomin,minpos)
			maxpos=max(annomax,maxpos)
		scale=400/(maxpos-minpos+1)
		posnum=(maxpos-minpos+1)//10
		example(cr,h,scale,line,arrayline,bar_high,nat,genename)
		##
		##
		##annotation gene 
		hh=70+10
#################################
		annotation(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene)
#################################
		if True:
			if pacbio_dict_sort:
				transcripts(cr,h,scale,line,arrayline,pacbio_dict_sort,refGenes,minpos,maxpos,genename,allgene,nat)
			if cufflinks_dict_sort:
				transcripts(cr,h,scale,line,arrayline,cufflinks_dict_sort,refGenes,minpos,maxpos,genename,allgene,nat)
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib)
		if apapos!="NULL" and atipos!="NULL":
			atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat)
		ashigh=hh
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,ir,es,alta,altd,altp,posnum,"P")
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,cuffir,cuffes,cuffalta,cuffaltd,cuffaltp,posnum,"C")
		footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum)
def annotation(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene):
	global hh
	if len(refGenes)!=0:
			#hh+=200/(len(sort_dict)+23)
			#annomin=min(int(str(reg).split()[-3]) for reg in refGenes)
			#annomax=max(int(str(reg).split()[-1]) for reg in refGenes)
			#minpos=min(annomin,minpos)
			#maxpos=max(annomax,maxpos)
			#scale=400/(maxpos-minpos+1)
			#print genename
			for annogene in genename.split("_"):
				hh+=200*2/(len(sort_dict)+23)
				linee=allgene[annogene]
				info=linee.split()
				strand=info[3]
				utrmin=[]
				utrmax=[]
				tpos=(int(info[2])+int(info[1]))/2
				cr.set_font_size(6)
				cr.move_to(50+(tpos-minpos)*scale-1.8*len(annogene),hh-5)
				cr.show_text(annogene)
				cr.fill()
				for subele in info[5:]:
					if subele.startswith("C"):
						minn=min(int(mm) for mm in subele.split(":")[1:])
						maxx=max(int(mm) for mm in subele.split(":")[1:])
						utrmin.append(minn)
						utrmax.append(maxx)
				for st in range(5,len(info)):
					if info[st].startswith("C"):
						finalst=st-1
						break
				for st in range(5,finalst+1):
					(s,e)=info[st].split(':')
					(s,e)=(int(s),int(e))
					if strand == '+':
						if finalst==5:
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(s-minpos)*scale,hh,(min(utrmin)-s)*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(min(utrmin)-minpos)*scale,hh,(max(utrmax)-min(utrmin))*scale,h)
							cr.fill()
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(max(utrmax)-minpos)*scale,hh,(e-max(utrmax))*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.set_line_width(arrayline)
							cr.move_to(50+(e-minpos)*scale,hh+1*h/2)
							cr.line_to(50+(e-minpos)*scale+8,hh+1*h/2)
							cr.stroke()
							cr.move_to(50+(e-minpos)*scale+8,hh+1*h/2)
							cr.rel_line_to(-2,-0.5)
							cr.rel_line_to(0,1)
							cr.close_path()
							cr.fill_preserve ()
							cr.stroke()
							continue
						if st==5:
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(s-minpos)*scale,hh,(min(utrmin)-s)*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(min(utrmin)-minpos)*scale,hh,(e-min(utrmin))*scale,h)
							cr.fill()
						elif st==(finalst):
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(max(utrmax)-minpos)*scale,hh,(e-max(utrmax))*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(s-minpos)*scale,hh,(max(utrmax)-s)*scale,h)
							cr.fill()
						else:
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
							cr.fill()
						if  st != finalst:
							(sn,en)=info[st+1].split(':')
							(sn,en)=(int(sn),int(en))
							cr.set_source_rgb(0,0,0)
							cr.set_line_width(line)
							cr.move_to((e-minpos)*scale+50,hh+1*h/2)
							cr.line_to((sn-minpos)*scale+50,hh+1*h/2)
							cr.stroke()
						else:
							cr.set_source_rgb(0,0,0)
							cr.set_line_width(arrayline)
							cr.move_to(50+(e-minpos)*scale,hh+1*h/2)
							cr.line_to(50+(e-minpos)*scale+8,hh+1*h/2)
							cr.stroke()
							cr.move_to(50+(e-minpos)*scale+8,hh+1*h/2)
							cr.rel_line_to(-2,-0.5)
							cr.rel_line_to(0,1)
							cr.close_path()
							cr.fill_preserve ()
							cr.stroke()
					elif strand == '-':						
						#################
						if finalst==5:
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(s-minpos)*scale,hh,(min(utrmin)-s)*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(min(utrmin)-minpos)*scale,hh,(max(utrmax)-min(utrmin))*scale,h)
							cr.fill()
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(max(utrmax)-minpos)*scale,hh,(e-max(utrmax))*scale,h)
							cr.fill()
						##################
							cr.set_source_rgb(0,0,0)
							cr.set_line_width(arrayline)
							cr.move_to(450-(maxpos-s)*scale,hh+1*h/2)
							cr.line_to(450-(maxpos-s)*scale-8,hh+1*h/2)
							cr.stroke()
							cr.move_to(450-(maxpos-s)*scale-8,hh+1*h/2)
							cr.rel_line_to(2,-0.5)
							cr.rel_line_to(0,1)
							cr.close_path()
							cr.fill_preserve ()
							cr.stroke()
							##############
							continue
						if st==5 :
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(s-minpos)*scale,hh,(min(utrmin)-s)*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(min(utrmin)-minpos)*scale,hh,(e-min(utrmin))*scale,h)
							cr.fill()
							###########
							###arryline
							cr.set_source_rgb(0,0,0)
							cr.set_line_width(arrayline)
							cr.move_to(450-(maxpos-s)*scale,hh+1*h/2)
							cr.line_to(450-(maxpos-s)*scale-8,hh+1*h/2)
							cr.stroke()
							cr.move_to(450-(maxpos-s)*scale-8,hh+1*h/2)
							cr.rel_line_to(2,-0.5)
							cr.rel_line_to(0,1)
							cr.close_path()
							cr.fill_preserve ()
							cr.stroke()
						elif st==finalst:
							cr.set_source_rgb(0.75,0.75,0.75)
							cr.rectangle(50+(max(utrmax)-minpos)*scale,hh,(e-max(utrmax))*scale,h)
							cr.fill()
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(s-minpos)*scale,hh,(max(utrmax)-s)*scale,h)
							cr.fill()
						else:
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
							cr.fill()
						##################
						if  st != finalst:
							(sn,en)=info[st+1].split(':')
							sn=int(sn)
							en=int(en)
							cr.set_source_rgb(0,0,0)
							cr.set_line_width(line)
							cr.move_to(50+(e-minpos)*scale,hh+1*h/2)
							cr.line_to(50+(sn-minpos)*scale,hh+1*h/2)
							cr.stroke()
	#############################################
def example(cr,h,scale,line,arrayline,bar_high,nat,genename,de_nat_lib):
	if de_nat_lib!="NULL":
		count=0
		cr.set_font_size(8)
		for x,y in de_nat_lib:
			#lib1=conf[x.lower()].strip('\n').split()[0]
			#lib2=conf[y.lower()].strip('\n').split()[0]
			lib1=x.upper()
			lib2=y.upper()
			count+=1
			cr.move_to(450,30+count*8)
			cr.show_text("%d\t%s\t%s"%(count,lib1,lib2))
	if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
			cr.move_to(50,bar_high)
			cr.rectangle(50,bar_high-h,10,h)
			cr.set_font_size(8)
			(r,g,b)=hex2rgb(conf["exon"])
			cr.set_source_rgb(r,g,b)
			cr.fill()
			cr.move_to(50+10+2,bar_high)
			cr.set_source_rgb(0, 0 ,0)
			cr.show_text("Pacbio Exon")
			cr.fill()
			cr.move_to(50+10+2+50,bar_high)
			cr.rectangle(50+10+2+50,bar_high-h,10,h)
			cr.set_font_size(8)
			(r,g,b)=hex2rgb(conf["cds"])
			cr.set_source_rgb(0.18,0.55,0.34)
			cr.fill()
			cr.move_to(50+10+2+62,bar_high)
			cr.set_source_rgb(0,0,0)
			cr.show_text("Cufflinks exon")
			cr.fill()
	elif cf.has_option("input file","Pacbio_reads"):
		cr.move_to(50,bar_high)
		cr.rectangle(50,bar_high-h,10,h)
		cr.set_font_size(8)
		#(r,g,b)=hex2rgb(conf["exon"])
		(r,g,b)=hex2rgb(conf["nat_f"])
		cr.set_source_rgb(r,g,b)
		cr.fill()
		cr.move_to(50+10+2,bar_high)
		cr.set_source_rgb(0,0,0)
		cr.show_text("Pacbio Forward Exon")
		cr.fill()
		#################
		L_R=100
		#################
		cr.move_to(50+L_R,bar_high)
		cr.rectangle(50+L_R,bar_high-h,10,h)
		cr.set_font_size(8)
		#(r,g,b)=hex2rgb(conf["exon"])
		(r,g,b)=hex2rgb(conf["nat_r"])
		cr.set_source_rgb(r,g,b)
		cr.fill()
		cr.move_to(50+10+2+L_R,bar_high)
		cr.set_source_rgb(0,0,0)
		cr.show_text("Pacbio Reverse Exon")
		cr.fill()
		##################
	elif cf.has_option("input file","Cuffmerge_file"):
		cr.move_to(50,bar_high)
		cr.rectangle(50,bar_high-h,10,h)
		cr.set_font_size(8)
		cr.set_source_rgb(0.18,0.55,0.34)
		cr.fill()
		cr.move_to(50+10+2,bar_high)
		cr.set_source_rgb(0,0,0)
		cr.show_text("Cufflinks exon")
	cr.move_to(50,bar_high+10)
	cr.line_to(50+10,bar_high+10)
	(r,g,b)=hex2rgb(conf["intron"])
	cr.set_source_rgb(r,g,b)
	cr.set_line_width(line)
	cr.stroke()
	cr.move_to(50+10+2,bar_high+10)
	cr.show_text("Intron")
	cr.fill()
	######################
	cr.move_to(50,bar_high+10+10+10)
	cr.line_to(50+200*scale,bar_high+10+10+10)
	cr.set_source_rgb(0,0,0)
	cr.set_line_width(line)
	cr.stroke()
	cr.move_to(50+200*scale+2,bar_high+10+10+10)
	cr.show_text("200 bp")
	cr.fill()
	#########################################
	cr.move_to(250-30,20)
	cr.show_text("%s"%(genename))
	cr.fill()
	###############################
	cr.move_to(50,bar_high+20)
	cr.rectangle(50,bar_high+20-h,10,h)
	cr.set_font_size(8)
	(r,g,b)=hex2rgb(conf["utr"])
	cr.set_source_rgb(r,g,b)
	cr.fill()
	cr.move_to(50+10+2,bar_high+20)
	cr.set_source_rgb(0,0,0)
	cr.show_text("UTR")
	cr.fill()
################################
	cr.move_to(50+10+2+20,bar_high+20)
	cr.rectangle(50+10+2+20,bar_high+20-h,10,h)
	cr.set_font_size(8)
	(r,g,b)=hex2rgb(conf["cds"])
	cr.set_source_rgb(0,0,0)
	cr.fill()
	cr.move_to(50+10+2+20+12,bar_high+20)
	cr.set_source_rgb(0,0,0)
	cr.show_text("CDS")
	cr.fill()
	###################
	cr.set_line_width(line)
	libpos=0
	(r,g,b)=hex2rgb(conf["5'-5'"])
	cr.set_source_rgb(r,g,b)
	cr.move_to(50+libpos,bar_high+40)
	cr.line_to(50+libpos,bar_high+35)
	cr.stroke()
	cr.move_to(50+libpos+20,bar_high+40)
	cr.set_source_rgb(0,0,0)
	cr.show_text("5'-5'")
	cr.fill()
	libpos+=50
	(r,g,b)=hex2rgb(conf["3'-3'"])
	cr.set_source_rgb(r,g,b)
	cr.move_to(50+libpos,bar_high+40)
	cr.line_to(50+libpos,bar_high+35)
	cr.stroke()
	cr.move_to(50+libpos+20,bar_high+40)
	cr.set_source_rgb(0,0,0)
	cr.show_text("3'-3'")
	cr.fill()
	libpos+=50
	(r,g,b)=hex2rgb(conf["Fully_overlap".lower()])
	cr.set_source_rgb(r,g,b)
	cr.move_to(50+libpos,bar_high+40)
	cr.line_to(50+libpos,bar_high+35)
	cr.stroke()
	cr.set_source_rgb(0,0,0)
	cr.move_to(50+libpos+20,bar_high+40)
	cr.show_text("Fully_overlap")
	cr.fill()
	###
def transcripts(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,nat,pairs):
	global hh
	think=dict()
	for j in sort_dict:
		info=j.split()
		strand=info[4]
		hh+=200/(len(sort_dict)+23)
		think[info[1]]=hh+1*h/2
		for st in range(6,len(info)):
			(s,e)=info[st].split(':')
			s=int(s)
			e=int(e)
			if strand =='.':
				cr.set_source_rgb(0.18,0.55,0.34)
				cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
				cr.fill()
			if strand == '+':
				if nat=="True":
					if info[5].startswith("cufflinks"):
						cr.set_source_rgb(0.18,0.55,0.34)
					elif not info[5].startswith("cufflinks"):
						(r,g,b)=hex2rgb(conf["nat_f"])
						cr.set_source_rgb(r,g,b)
						#cr.set_source_rgb(0,0,1)
				else:
					(r,g,b)=hex2rgb(conf["exon"])
					cr.set_source_rgb(r,g,b)
					if info[5].startswith("cufflinks"):
						cr.set_source_rgb(0.18,0.55,0.34)
				cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
				cr.fill()
				if  st != (len(info)-1):
					(sn,en)=info[st+1].split(':')
					sn=int(sn)
					en=int(en)
					cr.set_source_rgb(0,0,0)
					cr.set_line_width(line)
					cr.move_to((e-minpos)*scale+50,hh+1*h/2)
					cr.line_to((sn-minpos)*scale+50,hh+1*h/2)
					cr.stroke()
				else:
					cr.set_source_rgb(1,0,0)
					cr.set_line_width(arrayline)
					cr.move_to(50+(e-minpos)*scale,hh+1*h/2)
					cr.line_to(50+(e-minpos)*scale+8,hh+1*h/2)
					cr.stroke()
					cr.move_to(50+(e-minpos)*scale+8,hh+1*h/2)
					cr.rel_line_to(-2,-0.5)
					cr.rel_line_to(0,1)
					cr.close_path()
					cr.fill_preserve ()
					cr.stroke()
			if strand == '-':
				(r,g,b)=hex2rgb(conf["nat_r"])
				cr.set_source_rgb(r,g,b)
				#cr.set_source_rgb(0,0,1)
				if info[5].startswith("cufflinks"):
					cr.set_source_rgb(0.18,0.55,0.34)
				#elif not info[5].startswith("cufflinks"):
				#	cr.set_source_rgb(0,0,1)
				#if info[5].startswith("cufflinks"):
				#	cr.set_source_rgb(0.18,0.55,0.34)
				cr.rectangle(450-(maxpos-s)*scale,hh,(e-s)*scale,h)
				cr.fill()
				if  st != (len(info)-1):
					(sn,en)=info[st+1].split(':')
					sn=int(sn)
					en=int(en)
					cr.set_source_rgb(0,0,0)
					cr.set_line_width(line)
					cr.move_to(450-(maxpos-s)*scale,hh+1*h/2)
					cr.line_to(450-(maxpos-en)*scale,hh+1*h/2)
					cr.stroke()
				else:
					cr.set_source_rgb(1,0,0)
					cr.set_line_width(arrayline)
					cr.move_to(450-(maxpos-s)*scale,hh+1*h/2)
					cr.line_to(450-(maxpos-s)*scale-8,hh+1*h/2)
					cr.stroke()
					cr.move_to(450-(maxpos-s)*scale-8,hh+1*h/2)
					cr.rel_line_to(2,-0.5)
					cr.rel_line_to(0,1)
					cr.close_path()
					cr.fill_preserve ()
					cr.stroke()
	if pairs=="NULL":
		return 0
	xlen=0
	#cr.set_source_rgb(1,0,0)
	cr.set_line_width(1.5*arrayline)
	for types,xlib,ylib in pairs:
		print types,conf[types.lower()]
		(r,g,b)=hex2rgb(conf[types.lower()])
		cr.set_source_rgb(r,g,b)
		xlen+=6
		cr.move_to(450,think[xlib])
		cr.rel_line_to(xlen,0)
		cr.rel_line_to(0,think[ylib]-think[xlib])
		cr.rel_line_to(-xlen,0)
		cr.stroke()
def wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib,fpkmcal):
	global hh
	hh+=20
	Strand_Specificity=cf.get("Wig option","Strand_Specificity")
	strand=sort_dict[0].split()[4]
	#print strand
	high1=hh
	Scan_length=int(cf.get("DE APA option","Scan_length"))
	if difflib!="NULL":
		apapos=difflib[0][-1]
		libpos=dict()
	wiggdict= defaultdict(dict)
	wignormlib=cf.get("Wig option","Group")
	create=locals()
	for wignormlibed in wignormlib.split():
		create[wignormlibed]=defaultdict(dict)
		for x in wignormlibed.split("_"):
			wiggdict[x.lower()]=wignormlibed
	if True:
		if True:
			cr.set_font_size(5)
			maxhigh=[]
			maxforward=[]
			maxreverse=[]
			for i in conf:
				if i.startswith("lib"):
					(tpp,filee,rgb)=conf[i].strip('\n').split()
					(r,g,b)=hex2rgb(rgb)
					if nat=="True" and Strand_Specificity=="True":
						wigggforward=Wig_count(filee,Gene_coordinate,"+",bamlist[i],cf)
						wigggreverse=Wig_count(filee,Gene_coordinate,"-",bamlist[i],cf)
						if wigggforward:
							#if not wigggforward:
							#	continue
							#maxforward.append(max(wigggforward[x] for x in wigggforward))
							eval(wiggdict[i])["+"][max(wigggforward[x] for x in wigggforward)]=1
						if wigggreverse:
							#if not wigggreverse:
							#	continue
							#maxreverse.append(max(wigggreverse[x] for x in wigggreverse))
							eval(wiggdict[i])["-"][max(wigggreverse[x] for x in wigggreverse)]=1
					else:
						wiggg=Wig_count(filee,Gene_coordinate,strand[0],bamlist[i],cf)
						if not wiggg:
							continue
						maxx=max(wiggg[x] for x in wiggg)
						eval(wiggdict[i])[max(wiggg[x] for x in wiggg)]=1
						#for wignormlibed in wignormlib.split():
						#	if i.lower() in wignormlibed:
						#		wiggdict[wignormlibed][maxx]=1
						#maxhigh.append(max(wiggg[x] for x in wiggg))
			#if nat!="True" or (nat=="True" and Strand_Specificity!="True"):
			#	for wignormlibed in wignormlib.split():
			#		if eval(wignormlibed.lower()):
			"""			
			if wiggdict==[] and nat!="True":
				return 0
			#print wigggreverse
			#if wigggreverse:
			#	print "hello"
			if maxforward!=[]:
				scaleforward=32/max(maxforward)
			if maxreverse!=[]:
				scalereverse=32/max(maxreverse)
			#if maxhigh!=[]:
			if wiggdict!=[]: 
				scaleh=32/max(maxhigh)
			"""
			for i in conf:
				if not i.startswith("lib"):
					continue
				#scaleh=32/(max(eval(wiggdict[i])))
				(tpp,filee,rgb)=conf[i].strip('\n').split()
				(r,g,b)=hex2rgb(rgb)
				
				if nat!="True" or (nat=="True" and Strand_Specificity!="True"):
					wiggg=Wig_count(filee,Gene_coordinate,strand[0],bamlist[i],cf)
				elif nat=="True" and Strand_Specificity=="True":
					wigggforward=Wig_count(filee,Gene_coordinate,"+",bamlist[i],cf)
					wigggreverse=Wig_count(filee,Gene_coordinate,"-",bamlist[i],cf)
					#print wigggforward,wigggreverse
				#hh+=100/len(libnum)
				hh+=40
				if nat!="True" or (nat=="True" and Strand_Specificity!="True"):	
					if not wiggg:
						continue
						#scaleh=(100/(len(sort_dict)+len(open(args.conf,'r').readlines())+2))/(max(wiggg[x] for x in wiggg))
					#for k in apapos.split(","):
					#	k=int(k)
					#	print list("%d-%d"%(x,wiggg[x]) for x in wiggg if (k-Scan_length)<=x<(k+Scan_length))
					scaleh=32/(max(eval(wiggdict[i]).keys()))
					cr.set_source_rgb(float(r),float(g),float(b))
					for gp in wiggg:
						if gp<minpos or maxpos<gp:
							continue
						#print 50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh
						cr.rectangle(50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh)
						cr.fill()
						#print 
					cr.set_source_rgb(0,0,0)
					cr.move_to(8,hh)
					cr.set_font_size(7)
					cr.save()
					cr.rotate(p*270/180)
					cr.show_text(tpp)
					cr.fill()
					cr.restore()
						######################################
						##aes
					cr.move_to(50-2,hh)
						#print max(wiggg[x] for x in wiggg)
					maxacnum=max(eval(wiggdict[i]))
					cr.line_to(50-2,hh-maxacnum*scaleh)
					cr.stroke()
						####################
					aesmin=maxacnum/4
					for stick in range(4+1):
							#print stick,aesmin
							#print hh-aesmin*scaleh*(4-stick)
						cr.move_to(50-2,hh-aesmin*scaleh*stick)
						cr.line_to(50-2-2,hh-aesmin*scaleh*stick)
						cr.stroke()
						cr.move_to(50-2-2-4*len(str("%.1f"%(aesmin*stick))),hh-aesmin*scaleh*stick+0.4*h)
						cr.set_font_size(5)
						cr.show_text("%.1f"%(aesmin*stick))
					##libpos
					if cf.get("DE APA option","DE")=="True":
						libpos[i]=hh-maxacnum*scaleh/2
					####
				elif nat=="True" and Strand_Specificity=="True":
					if wigggforward:
						scaleh=32/(max(eval(wiggdict[i])["+"].keys()))
						maxhigh=max(eval(wiggdict[i])["+"].keys())
						cr.set_source_rgb(float(r),float(g),float(b))
						for gp in wigggforward:
							if gp<minpos or maxpos<gp:
								continue
                                        	#print 50+(gp-minpos)*scale,hh-wigggforward[gp]*scaleh,1*scale,wigggforward[gp]*scaleh
							cr.rectangle(50+(gp-minpos)*scale,hh-wigggforward[gp]*scaleh,1*scale,wigggforward[gp]*scaleh)
                                       		 #print 50+(gp-minpos)*scale,50+(gp-minpos+1)*scale
							cr.fill()
						cr.set_source_rgb(0,0,0)
						cr.move_to(6,hh)
						cr.set_font_size(5)
						cr.save()
						cr.rotate(p*270/180)
						cr.show_text("%s +"%(tpp))
						cr.fill()
						cr.restore()
                                	#############################################
                                	##aes
						cr.move_to(50-2,hh)
                                	#print max(wiggg[x] for x in wiggg)
						maxacnum=maxhigh
						scaleforward=scaleh
						cr.line_to(50-2,hh-maxacnum*scaleforward)
						cr.stroke()
                               	 	####################
						aesmin=maxacnum/4
						for stick in range(4+1):
                                        	#print stick,aesmin
                                        	#print hh-aesmin*scaleh*(4-stick)
							cr.move_to(50-2,hh-aesmin*scaleforward*stick)
							cr.line_to(50-2-2,hh-aesmin*scaleforward*stick)
							cr.stroke()
							cr.move_to(50-2-2-4*len(str("%.1f"%(aesmin*stick))),hh-aesmin*scaleforward*stick+0.4*h)
							cr.set_font_size(5)
							cr.show_text("%.1f"%(aesmin*stick))
						#######
						cr.set_font_size(8)
						cr.set_source_rgb(0,0,0)
						cr.move_to(450,hh-20)
						cr.show_text(str("%.2f"%(fpkmcal[i]["+"])))
						cr.fill()
						#######
						hh+=40
					if wigggreverse:
						scaleh=32/(max(eval(wiggdict[i])["-"].keys()))
						maxhigh=max(eval(wiggdict[i])["-"].keys())
						cr.set_source_rgb(float(r),float(g),float(b))
						for gp in wigggreverse:
							if gp<minpos or maxpos<gp:
								continue
                                               	 #print 50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh,(100/(len(sort_dict)+len(open(args.conf,'r').readlines())+2)),(max(wiggg[x] for x in wiggg))
							#### old version wig plot 
							#cr.rectangle(50+(gp-minpos)*scale,hh-wigggreverse[gp]*scaleh,1*scale,wigggreverse[gp]*scaleh)
                                                 		#print 50+(gp-minpos)*scale,50+(gp-minpos+1)*scale
							###
							cr.rectangle(50+(gp-minpos)*scale,hh-40,1*scale,wigggreverse[gp]*scaleh)
							###
							cr.fill()
						cr.set_source_rgb(0,0,0)
						cr.move_to(6,hh)
						cr.set_font_size(5)
						cr.save()
						cr.rotate(p*270/180)
						cr.show_text("%s -"%(tpp))
						cr.fill()
						cr.restore()
                                        #############################################
                                        ##aes
						cr.move_to(50-2,hh-40)
                                        #print max(wiggg[x] for x in wiggg)
						maxacnum=maxhigh
						cr.line_to(50-2,hh-40+maxacnum*scaleh)
						cr.stroke()
                                        ####################
						aesmin=maxacnum/4
						for stick in range(4+1):
                                                #print stick,aesmin
							######
							"""
							cr.move_to(50-2,hh-aesmin*scaleh*stick)
							cr.line_to(50-2-2,hh-aesmin*scaleh*stick)
							cr.stroke()
							cr.move_to(50-2-2-4*len(str("%.1f"%(aesmin*stick))),hh-aesmin*scaleh*stick+0.4*h)
							"""
							cr.move_to(50-2,hh-40+aesmin*scaleh*stick)
							cr.line_to(50-2-2,hh-40+aesmin*scaleh*stick)
							cr.stroke()
							cr.move_to(50-2-2-4*len(str("%.1f"%(aesmin*stick))),hh-40+aesmin*scaleh*stick+0.4*h)
							######
							cr.set_font_size(5)
							cr.show_text("%.1f"%(aesmin*stick))
						cr.set_font_size(8)
						cr.set_source_rgb(0,0,0)
						cr.move_to(450,hh-20)
						cr.show_text(str("%.2f"%(fpkmcal[i]["-"])))
						cr.fill()
			###
			##diff lib used
			###
			###
			if difflib=="NULL":
				return 0
			xlen=0
			cr.set_source_rgb(1,0,0)
			cr.set_line_width(1.5*arrayline)
			for xlib,ylib,apapos in difflib:
				xlen+=6
				xlib,ylib=xlib.lower(),ylib.lower()
				cr.move_to(450,libpos[xlib])
				cr.rel_line_to(xlen,0)
				cr.rel_line_to(0,libpos[ylib]-libpos[xlib])
				cr.rel_line_to(-xlen,0)
				cr.stroke()
			### apa differentcial site
			cr.set_line_width(0.7*arrayline)
			for pos in apapos.split(","):
				pos=int(pos)
				"""
				print pos-Scan_length,pos+Scan_length
				cr.move_to(50+(pos-minpos-Scan_length)*scale,hh)
				cr.rel_line_to(0,high1-hh)
				cr.rel_line_to(Scan_length*2*scale,0)
				cr.rel_line_to(0,hh-high1)
				cr.close_path()
140				cr.stroke()
				"""
				cr.move_to(50+(pos-minpos)*scale,hh)
				cr.line_to(50+(pos-minpos)*scale,high1)
				cr.stroke()
def atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,types):
	global hh
	strand=types
	hh+=20+10*max(len(atinum),len(apanum))
	#########
	cr.set_font_size(8)
	cr.set_source_rgb(0,0,0)
	cr.move_to(30,hh)
	cr.show_text(types)
	cr.fill()
	#########
	if True:
		atiline=2.5*arrayline
		ih=0
		for pp in atipos.split(","):
			if atipos=="NULL":
				break
				#continue
			pp=int(pp)
			ih+=4
			cr.set_source_rgb(0,0,0)
			if strand=="-":
				cr.set_line_width(atiline)
				cr.move_to((pp-minpos)*scale+50,hh)
				cr.line_to((pp-minpos)*scale+50,hh-ih)
				cr.stroke()
				cr.move_to((pp-minpos)*scale+50+atiline/2,hh-ih)
				cr.line_to((pp-minpos)*scale+50-6,hh-ih)
				cr.stroke()
				cr.move_to((pp-minpos)*scale+50-6,hh-ih)
				cr.rel_line_to(2,-0.5)
				cr.rel_line_to(0,1)
				cr.close_path()
				cr.fill_preserve()
				cr.stroke()
			elif strand=="+":
				cr.set_line_width(atiline)
				cr.move_to((pp-minpos)*scale+50,hh)
				cr.line_to((pp-minpos)*scale+50,hh-ih)
				cr.stroke()
				cr.move_to((pp-minpos)*scale+50-atiline/2,hh-ih)
				cr.line_to((pp-minpos)*scale+50+6,hh-ih)
				cr.stroke()
				cr.move_to((pp-minpos)*scale+50+6,hh-ih)
				cr.rel_line_to(-2,-0.5)
				cr.rel_line_to(0,1)
				cr.close_path()
				cr.fill_preserve()
				cr.stroke()
		###############
		#####Coordinate
		cr.set_source_rgb(0,0,0)
		posnum=(maxpos-minpos+1)//10
		cr.set_line_width(1)
		cr.move_to(50,hh)
		cr.line_to(450,hh)
		cr.stroke()
		cr.set_line_width(0.5)
		for stick in range(10+1):		
			cr.move_to(50+(posnum*stick)*scale,hh)
			cr.line_to(50+(posnum*stick)*scale,hh+4)
			cr.stroke()
			cr.set_font_size(8)
			cr.move_to(50+(posnum*stick)*scale-14,hh+10)
			#cr.show_text(str(posnum*stick+minpos))
		###	ATI ending
		################################
		##	APA
		#cr.set_line_join(cairo.LINE_JOIN_ROUND)
		apaseg1=8
		apaseg2=8
		apaseg3=16
		apafont=6
		apaline=1*arrayline
		ih=0
		for pp in apapos.split(","):
			if apapos=="NULL":
				continue
			pp=int(pp)
			ih+=10
			cr.set_source_rgb(0,0,0)
			cr.set_line_width(apaline)
			cr.move_to((pp-minpos)*scale+50,hh)
			cr.line_to((pp-minpos)*scale+50,hh-ih)
			cr.stroke()
			cr.move_to((pp-minpos)*scale+50,hh-ih-apaseg2)
			cr.rel_line_to(apaseg3,0)
			cr.rel_line_to(0,apaseg2)
			cr.rel_line_to(-apaseg3,0)
			cr.close_path()
			cr.stroke()
			###########
			cr.set_source_rgb(0,0,0)
			cr.set_font_size(apafont)
			cr.move_to((pp-minpos)*scale+50+apaseg3/2-apafont/2,hh-ih-apaseg2/2+apafont/2)
			cr.show_text("PA")
			cr.stroke()
def ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,ir,es,alta,altd,altp,posnum,tpd):
	global hh,ashigh
	showhigh=10
		#hh+=10+1*h/2
	if True:
		arraylineas=1.5*arrayline
		cr.set_font_size(8)
		if ir!="NULL":
			ashigh+=30
			cr.set_source_rgb(0,0,0)
			cr.set_line_width(1)
			cr.move_to(50,ashigh)
			cr.line_to(450,ashigh)
			cr.stroke()
			cr.move_to(50-10,ashigh)
			cr.save()
			cr.rotate(p*270/180)			
			cr.show_text("%s_IR"%(tpd))
			cr.fill()
			cr.restore()
			cr.set_line_width(0.5)
			for stick in range(10+1):
				#print scale,
				#print 50+s(posnum*stick+minpos)*scale,hh+10
				cr.move_to(50+(posnum*stick)*scale,ashigh)
				cr.line_to(50+(posnum*stick)*scale,ashigh+4)
				cr.stroke()
				cr.set_font_size(8)
				cr.move_to(50+(posnum*stick)*scale-14,ashigh+10)
				#cr.show_text(str(posnum*stick+minpos))
			for irsub in ir.split(","):
				(s,e)=irsub.split(":")
				(s,e)=(int(s),int(e))
				#cr.set_source_rgb(1,0,0.8)
				(r,g,b)=hex2rgb(conf["ir"])
				#(r,g,b)=(float(x) for x in conf["ir"].split(":"))
				cr.set_source_rgb(r,g,b)
				cr.set_line_width(arraylineas)
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.line_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				#cr.stroke()
				cr.move_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				cr.line_to(50+(e-minpos)*scale,ashigh)
				cr.stroke()
			#############stick end
		#######################################################################################
		if es!="NULL":
			ashigh+=30
			cr.set_source_rgb(0,0,0)
			cr.set_line_width(1)
			cr.move_to(50,ashigh)
			cr.line_to(450,ashigh)
			cr.stroke()
			cr.move_to(50-10,ashigh)
			cr.save()
			cr.rotate(p*270/180)
			cr.show_text("%s_ES"%(tpd))
			cr.fill()
			cr.restore()
			cr.set_line_width(0.5)
			cr.set_source_rgb(0,0,0)
			for stick in range(10+1):			
				cr.move_to(50+(posnum*stick)*scale,ashigh)
				cr.line_to(50+(posnum*stick)*scale,ashigh+4)
				cr.stroke()
				cr.set_font_size(8)
				cr.move_to(50+(posnum*stick)*scale-14,ashigh+10)
				#cr.show_text(str(posnum*stick+minpos))
			
			for essub in es.split(","):
				(s,e)=essub.split(":")
				(s,e)=(int(s),int(e))
				(r,g,b)=hex2rgb(conf["es"])
				cr.set_source_rgb(r,g,b)
				cr.set_line_width(arraylineas)
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.line_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				#cr.stroke()
				cr.move_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				cr.line_to(50+(e-minpos)*scale,ashigh)
				cr.stroke()
				#############stick end
		########################################################################################
		if alta!="NULL":
			ashigh+=30
			cr.set_source_rgb(0,0,0)
			cr.set_line_width(1)
			cr.move_to(50,ashigh)
			cr.line_to(450,ashigh)
			cr.stroke()
			cr.move_to(50-10,ashigh)
			cr.save()
			cr.rotate(p*270/180)
			cr.show_text("%s_AltA"%(tpd))
			cr.fill()
			cr.restore()
			cr.set_line_width(0.5)
			cr.set_source_rgb(0,0,0)
			for stick in range(10+1):
				#print scale,
				#print 50+s(posnum*stick+minpos)*scale,hh+10			
				cr.move_to(50+(posnum*stick)*scale,ashigh)
				cr.line_to(50+(posnum*stick)*scale,ashigh+4)
				cr.stroke()
				cr.set_font_size(8)
				cr.move_to(50+(posnum*stick)*scale-14,ashigh+10)
				#cr.show_text(str(posnum*stick+minpos))
			
			for altasub in alta.split(","):
				(s,e)=altasub.split(":")
				(s,e)=(int(s),int(e))
				#cr.set_source_rgb(1,0,0.2)
				#(r,g,b)=(float(x) for x in conf["alta"].split(":"))
				(r,g,b)=hex2rgb(conf["alta"])
				cr.set_source_rgb(r,g,b)
				cr.set_line_width(arraylineas)
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.line_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				#cr.stroke()
				cr.move_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				cr.line_to(50+(e-minpos)*scale,ashigh)
				cr.stroke()
	###########################################################################################
		if altd!="NULL":
			ashigh+=30
			cr.set_source_rgb(0,0,0)
			cr.set_line_width(1)
			cr.move_to(50,ashigh)
			cr.line_to(450,ashigh)
			cr.stroke()
			cr.move_to(50-10,ashigh)
			cr.save()
			cr.rotate(p*270/180)
			cr.show_text("%s_AltD"%(tpd))
			cr.fill()
			cr.restore()
			cr.set_line_width(0.5)
			for stick in range(10+1):
				#print scale,
				#print 50+s(posnum*stick+minpos)*scale,hh+10			
				cr.move_to(50+(posnum*stick)*scale,ashigh)
				cr.line_to(50+(posnum*stick)*scale,ashigh+4)
				cr.stroke()
				cr.set_font_size(8)
				cr.move_to(50+(posnum*stick)*scale-14,ashigh+10)
				#cr.show_text(str(posnum*stick+minpos))
			for altdsub in altd.split(","):
				(s,e)=altdsub.split(":")
				(s,e)=(int(s),int(e))
				#cr.set_source_rgb(1,1,0.2)
				#(r,g,b)=(float(x) for x in conf["altd"].split(":"))
				(r,g,b)=hex2rgb(conf["altd"])
				cr.set_source_rgb(r,g,b)
				cr.set_line_width(arraylineas)
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.line_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				#cr.stroke()
				cr.move_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
				cr.line_to(50+(e-minpos)*scale,ashigh)
				cr.stroke()
				cr.set_source_rgb(0,0,0)
	##############################################################################################
		if altp!="NULL":
			ashigh+=30
			cr.set_source_rgb(0,0,0)
                        cr.set_line_width(1)
                        cr.move_to(50,ashigh)
                        cr.line_to(450,ashigh)
                        cr.stroke()
                        cr.move_to(50-10,ashigh)
                        cr.save()
                        cr.rotate(p*270/180)
                        cr.show_text("%s_AltP"%(tpd))
                        cr.fill()
                        cr.restore()
                        cr.set_line_width(0.5)
			for stick in range(10+1):
                                #print scale,
                                #print 50+s(posnum*stick+minpos)*scale,hh+10                    
                                cr.move_to(50+(posnum*stick)*scale,ashigh)
                                cr.line_to(50+(posnum*stick)*scale,ashigh+4)
                                cr.stroke()
                                cr.set_font_size(8)
                                cr.move_to(50+(posnum*stick)*scale-14,ashigh+10)
                                #cr.show_text(str(posnum*stick+minpos))
                        for altpsub in altp.split(","):
                                (s,e)=altpsub.split(":")
                                (s,e)=(int(s),int(e))
                                #cr.set_source_rgb(1,1,0.2)
                                (r,g,b)=hex2rgb(conf["altp"])
                                cr.set_source_rgb(r,g,b)
                                cr.set_line_width(arraylineas)
                                cr.move_to(50+(s-minpos)*scale,ashigh)
                                cr.line_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
                                #cr.stroke()
                                cr.move_to(50+((s+e)/2-minpos)*scale,ashigh-showhigh)
                                cr.line_to(50+(e-minpos)*scale,ashigh)
                                cr.stroke()
				cr.set_source_rgb(0,0,0)
def footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum):
	global ashigh
	cr.set_line_width(0.5)
	cr.set_source_rgb(0,0,0)
	ashigh+=30
	cr.set_source_rgb(0,0,0)
	cr.set_line_width(1)
	cr.move_to(50,ashigh)
	cr.line_to(450,ashigh)
	cr.stroke()
	cr.set_source_rgb(0,0,0)
	cr.set_line_width(1)
		#############################
	if True:
		for stick in range(10+1):
                                #print scale,
                                #print 50+s(posnum*stick+minpos)*scale,hh+10                    
			cr.move_to(50+(posnum*stick)*scale,ashigh)
			cr.line_to(50+(posnum*stick)*scale,ashigh+4)
			cr.stroke()
			cr.set_font_size(8)
			cr.move_to(50+(posnum*stick)*scale-14,ashigh+10)
			cr.show_text(str(posnum*stick+minpos))
		cr.set_source_rgb(0,0,0)
		cr.set_font_size(10)
		cr.move_to(250-30,ashigh+20)
		cr.show_text("%s"%(Gene_coordinate))
def Visual(clu,allgene,genename,refGenes,path,apapos,atipos,ir,es,alta,altd,altp,nat,difflib,pairs,fpkmcal):
	global hh,ashigh
	wiggg=dict()
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split('.')[0]
		############################
		#### GFF Adapation
		#################
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		##############################
		if nat=="True":
			sort_dict= sorted(mapdict[i], key=lambda d:(d.split()[4]), reverse = False)
		else:
			sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = False)
		##############################
		#	high of figure
		if genename.startswith("Novel"):
			angene=0
		else:
			angene=2*len(genename.split("_"))
		atinum=[]
		for subati in atipos.split(","):
			atinum.append(subati)
		apanum=[]
		for subnum in apapos.split(","):
			apanum.append(subnum)
		asnum=0
		for subas in (ir,es,alta,altd,altp):
			if subas!="NULL":
				asnum+=1
		libnum=[]
		for libsub in conf:
			if libsub.startswith("lib"):
				libnum.append(libsub)
		#######################################################
		if nat=="True":
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*2*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		else:
			hight_of=70+8+200*(len(sort_dict)+angene)/(len(sort_dict)+23)+40*len(libnum)+10+10*max(len(atinum),len(apanum))+30*(asnum+1)+40*3
		#################################################
		Output_dir=cf.get("outputdir","Output_dir")
		surface = cairo.PDFSurface("%s/%s/%s.pdf"%(Output_dir,path,genename), 500, hight_of)
		sys.stderr.write("	%s has processed\n"%(genename))
		cr = cairo.Context(surface)
		######
		if len(sort_dict)-1 <12:
			h=4
		else:
			h=70/(len(sort_dict)+2)
		line=1*h/3
		arrayline=1*line/2
		scale=400/(maxpos-minpos+1)
		bar_high=35
		###
		##example
		if len(refGenes)!=0: 
			annomin=min(int(str(reg).split()[-3]) for reg in refGenes)
			annomax=max(int(str(reg).split()[-1]) for reg in refGenes)
			minpos=min(annomin,minpos)
			maxpos=max(annomax,maxpos)
		scale=400/(maxpos-minpos+1)
		posnum=(maxpos-minpos+1)//10
		example(cr,h,scale,line,arrayline,bar_high,nat,genename)
		###
		###
		##annotation gene 
		hh=70+10
		annotation(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene)
		###########################
		transcripts(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,nat,pairs)
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib,fpkmcal)
			#if deas!="":
			#	deasplot(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,deas)
		atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat)
		ashigh=hh
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,ir,es,alta,altd,altp,posnum,"P")
		footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum)
		cr.show_page()
		surface.finish()
#################################
#################################################################################################	
def deasplot(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,deas):
	cr.set_line_width(arrayline)
	for i in deas.split():
		(s,e)=(int(x) for x in i.split("_")[1].split(":"))
		cr.set_source_rgb(0,0,0)
		cr.move_to(50+(s-minpos)*scale,100)
		cr.rel_line_to((e-s+1)*scale,0)
		cr.rel_line_to(0,hh-80)
		cr.rel_line_to((-(e-s+1))*scale,0)
		cr.close_path()
		cr.stroke()
def ATI(clu,strand):
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
		minpos=min(polyamap)
		maxpos=max(polyamap)
		depth = numpy.zeros( maxpos-minpos+1, int)
		offset = min(polyamap)
		for loc in polyamap:
			depth[loc-offset] += 1
		peaks,counts = getPeaks(depth,cf)
		position=','.join([str(x+offset) for x in peaks])
		if position=="":
			position="NULL"
		position=",".join(sorted(position.split(","), key=lambda d:(int(d)),reverse=False))
		return position
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
		#print polyamap
		minpos=min(polyamap)
		maxpos=max(polyamap)
		depth = numpy.zeros( maxpos-minpos+1, int)
		offset = min(polyamap)
		for loc in polyamap:
			depth[loc-offset] += 1
		peaks,counts = getPeaks(depth,cf)
		position=','.join([str(x+offset) for x in peaks])
		if position=="":
			position="NULL"
		position=",".join(sorted(position.split(","), key=lambda d:(int(d)),reverse=False))
		if strand=="-":
			position=",".join(map(str,[int(x)-1 for x in position.split(",")]))
		return position
def AS(clu,tpd,strand):
	for i in [clu]:
		introndict=dict()
		exondict=dict()
		intron=[]
		ir=dict()
		es=dict()
		esdict=dict()
		altd=dict()
		alta=dict()
		"""
		if tpd=="cufflinks":
			minpos  = min(x.split()[2] for x in mapdict[i] if x.split()[5].startswith("cufflinks"))
			maxpos  = max(x.split()[3] for x in mapdict[i] if x.split()[5].startswith("cufflinks"))
		elif tpd=="pacbio":
			minpos  = min(x.split()[2] for x in mapdict[i] if not x.split()[5].startswith("cufflinks"))
			maxpos  = max(x.split()[3] for x in mapdict[i] if not x.split()[5].startswith("cufflinks"))
		#minpos  = min(x.split()[2] for x in mapdict[i])
		#maxpos  = max(x.split()[3] for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		"""
		gene=i.split('.')[0]
		#strand=mapdict[i].keys()[0].split()[4]
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			for y in x.split()[6:]:
				exondict[y]=1
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			for y in x.split()[7:-1]:
				esdict[y]=1
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			intron=[idd for idd in x.split()[6:]]
			for y in range(len(intron)-1):
				if strand=='+':
					lim="%s:%s"%(intron[y].split(':')[-1],intron[y+1].split(':')[0])
					introndict[lim]="%s:%s"%(intron[y],intron[y+1])
				if strand=='-':
					lim="%s:%s"%(intron[y+1].split(':')[-1],intron[y].split(':')[0])
					introndict[lim]="%s:%s"%(intron[y+1],intron[y])
		###############
		#inron retation
		ir=IR(exondict,introndict)
		es=ES(esdict,introndict)
		altpos=Altpos(exondict,introndict)
		if strand=="+":
			altd=AltD(exondict,introndict)
			alta=AltA(exondict,introndict)
		else:
			altd=AltA(exondict,introndict)
			alta=AltD(exondict,introndict)
		if ir=="":
			ir="NULL"
		if es=="":
			es="NULL"
		if alta=="":
			alta="NULL"
		if altd=="":
			altd="NULL"
		if altpos=="":
			altpos="NULL"
		return ir,es,alta,altd,altpos
def AS_old(clu,tpd,gene,strand):
	for i in [clu]:
		introndict=dict()
		exondict=dict()
		intron=[]
		ir=dict()
		es=dict()
		esdict=dict()
		altd=dict()
		alta=dict()
		"""
		if tpd=="cufflinks":
			minpos  = min(x.split()[2] for x in mapdict[i] if x.split()[5].startswith("cufflinks"))
			maxpos  = max(x.split()[3] for x in mapdict[i] if x.split()[5].startswith("cufflinks"))
		elif tpd=="pacbio":
			minpos  = min(x.split()[2] for x in mapdict[i] if not x.split()[5].startswith("cufflinks"))
			maxpos  = max(x.split()[3] for x in mapdict[i] if not x.split()[5].startswith("cufflinks"))
		#minpos  = min(x.split()[2] for x in mapdict[i])
		#maxpos  = max(x.split()[3] for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		"""
		gene=i.split('.')[0]
		#strand=mapdict[i].keys()[0].split()[4]
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			#for y in x.split()[6:-1]:
			#	exon[y]=1
			exon=[idd for idd in x.split()[6:-1]]
			for y in range(len(exondict)):
				if strand=='+':
					lim="%s:%s"%(exon[y].split(':')[-1],exon[y+1].split(':')[0])
					exondict[y]="%s:%s"%(exon[y-1],exon[y+1])
				if strand=='-':
					lim="%s:%s"%(exon[y+1].split(':')[-1],exon[y].split(':')[0])
					exondict[y]="%s:%s"%(exon[y+1],exon[y-1])
		############
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			for y in x.split()[7:-1]:
				esdict[y]=1
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			intron=[idd for idd in x.split()[6:]]
			for y in range(len(intron)-1):
				if strand=='+':
					lim="%s:%s"%(intron[y].split(':')[-1],intron[y+1].split(':')[0])
					introndict[lim]="%s:%s"%(intron[y],intron[y+1])
				if strand=='-':
					lim="%s:%s"%(intron[y+1].split(':')[-1],intron[y].split(':')[0])
					introndict[lim]="%s:%s"%(intron[y+1],intron[y])
		###############
		#inron retation
		seqir,seqes,seqalta,seqaltd=("","","","")
		ir,seqir=IR(exondict,introndict,gene,strand)
		es,seqes=ES(exondict,introndict,gene,strand)
		altpos=Altpos(exondict,introndict)
		if strand=="+":
			altd,seqaltd=AltD(exondict,introndict,gene,strand)
			alta,seqalta=AltA(exondict,introndict,gene,strand)
		else:
			altd,seqaltd=AltA(exondict,introndict,gene,strand)
			alta,seqalta=AltD(exondict,introndict,gene,strand)
		if ir=="":
			ir="NULL"
		if es=="":
			es="NULL"
		if alta=="":
			alta="NULL"
		if altd=="":
			altd="NULL"
		if altpos=="":
			altpos="NULL"
		return ir,es,alta,altd,altpos,seqir,seqes,seqalta,seqaltd
##################################################################
def writesummary(path):
		if cf.has_option("input file","Pacbio_reads") and cf.has_option("input file","Cuffmerge_file"):
			cmd="perl -e 'print\"Genename\tType\tGene_coordinate\tAPApos\tATIpos\tIRlim\tcuff_IRlim\tESlim\tcuff_ESlim\tAltAlim\tcuff_AltAlim\tAltDlim\tcuff_AltDlim\tAltPlim\tcuff_AltPlim\tPacbioReads\n\";'>%s/Sumary_Detail.csv"%(path)
			os.system(cmd)
			cmd="cat %s/temp/*.csv >>%s/Sumary_Detail.csv"%(path,path)
			os.system(cmd)
			cmd="cat %s/temp/*.nat >>%s/Sumary_NAT.csv"%(path,path)
			os.system(cmd)
			####DE APA sites
			out=open("%s/DE_APA.csv"%(path),"w")
			files=os.listdir("%s/temp"%(path))
			for ff in files:
				if ff.endswith("plot"):
					filehander=open("%s/temp/%s"%(path,ff),"r").readlines()
					#print filehander
					if not filehander:
						continue
					if len(filehander)!=4 or len(filehander[1].rstrip().split())!=3 or len(filehander[2].rstrip().split())!=3:
						print filehander,ff
						continue
					#print print filehander
					ele=re.split("_|\.",ff)
					if ele[2:-1]==1:
						genename=ele[2]
					else:
						genename="_".join(ele[2:-1])
					pos1,pos2=filehander[0].rstrip().split()
					lib1,lib1pos1num,lib1pos2num=filehander[1].rstrip().split()
					lib2,lib2pos1num,lib2pos2num=filehander[2].rstrip().split()
					pvalue=filehander[3].rstrip()
					out.write("%s\t%s_VS_%s\t%s_VS_%s\t%s:%s:%s\t%s:%s:%s\t%s:%s:%s\t%s:%s:%s\t%s\n"%(genename,lib1,lib2,pos1,pos2,lib1,pos1,lib1pos1num,lib1,pos2,lib1pos2num
														,lib2,pos1,lib2pos1num,lib2,pos2,lib2pos2num,pvalue))
			out.close()
		elif cf.has_option("input file","Pacbio_reads"):
			cmd="perl -e 'print\"Genename\tType\tGene_coordinate\tAPApos\tATIpos\tIRlim\tESlim\tAltAlim\tAltDlim\tAltPlim\tPacbioReads\n\";'>%s/Sumary_Detail.csv"%(path)
			os.system(cmd)
			cmd="cat %s/temp/*.csv >>%s/Sumary_Detail.csv"%(path,path)
			os.system(cmd)
			cmd="cat %s/temp/*.nat >>%s/Sumary_NAT.csv"%(path,path)
			os.system(cmd)
			cmd="echo \"Gene\tir_f\tes_f\taltd_f\talta_f\taltp_f\tir_r\tes_r\taltd_r\talta_r\taltp_r\tapapos_f\tatipos_f\tapapos_r\tatipos_r\n\">%s/nat_as_apa.txt"%(path)
			os.system(cmd)
			cmd="cat %s/temp/*.nat >>%s/nat_as_apa.txt"%(path,path)
			os.system(cmd)
		elif cf.has_option("input file","Cuffmerge_file"):
			cmd="perl -e 'print\"Genename\tType\tGene_coordinate\tAPApos\tATIpos\tIRlim\tESlim\tAltAlim\tAltDlim\tAltPlim\tPacbioReads\n\";'>%s/Sumary_Detail.csv"%(path)
			os.system(cmd)
			cmd="cat %s/temp/*.csv >>%s/Sumary_Detail.csv"%(path,path)
			os.system(cmd)
			cmd="cat %s/temp/*.nat >>%s/Sumary_NAT.csv"%(path,path)
			os.system(cmd)
def countnum(libname,bamfile):
		numout=commands.getoutput("samtools view %s|cut -f 1|sort -T temp|uniq|wc -l "%(bamfile))
		num=numout.split()[0]
		#num=100000
		return libname,num
def check_jucton_length():
	readLength=int(cf.get("Wig option","readLength"))
	anchorLength=int(cf.get("Wig option","anchorLength"))
	junctionLength = 2*(readLength-anchorLength)
	return junctionLength
def rmats():
	outdir="%s/rMATS"%(Output_dir)
	Output_dir=cf.get("outputdir","Output_dir")
	if not os.path.exists(outdir):
		os.makedirs(outdir)
		####
	readLength=int(cf.get("Wig option","readLength"))
	anchorLength=int(cf.get("Wig option","anchorLength"))
	junctionLength = 2*(readLength-anchorLength)
	###
	bam1=cf.get("Wig option","Lib1")
	bam2=cf.get("Wig option","Lib2")
	bampair1="%s,%s"%(bam1.split()[1],bam2.split()[1])
	###
	bam3=cf.get("Wig option","Lib3")
	bam4=cf.get("Wig option","Lib4")
	bampair2="%s,%s"%(bam3.split()[1],bam4.split()[1])
	###############
	files=os.listdir("%s/temp"%(Output_dir))
	for types in ["ES","AltD","AltA","IR"]:
		#out=open("%s/%s.txt"%(outdir,types),"w")
		cmd="rm %s/%s.txt"%(outdir,types)
		os.system(cmd)
		ends="%smats"%(types)
		for ff in files:
			if ff.endswith(ends):
				cmd="cat %s/temp/%s >>%s/%s.txt"%(Output_dir,ff,outdir,types)
				os.system(cmd)
	###############
	"""
	cmd="python scripts/Pacbio_mats.py %d %d %s/ES.txt %s/AltD.txt %s/AltA.txt %s/IR.txt %s %s %s %s"%(readLength,234,outdir,\
	outdir,outdir,outdir,bampair1,bampair2,outdir,"NULL")
	os.system(cmd)
	"""
	#cmd="sh scripts/Pacbio_mats_s2.sh %s"%(outdir)
	#os.system(cmd)
if  __name__ == '__main__':
	sys.stderr.write('Initializtion...\n')
	if sys.version_info < (2,6) or sys.version_info >= (3,0):
		sys.stderr.write("Python Version error: must use phthon 2.6 or greater (not supporting python 3 yet)\n")
		sys.exit(-1);
	else:
		sys.stderr.write("	Passed version test\n")
	"""
	Version Test Fisned
	"""
	global conf,bamlist,mapdict
	bamlist=dict()
	conf=OrderedDict()
	"""
	Configurition reading in a variable
	"""
	Genome_Annotion=cf.get("input file","genome_annotion")
	Output_dir=cf.get("outputdir","Output_dir")
	geneModel = loadGeneModels(Genome_Annotion, verbose=True)
	if not os.path.exists(Output_dir):
		sys.stderr.write("Making output dir\n")
		os.makedirs(Output_dir)
	if not os.path.exists("temp"):
		sys.stderr.write("Making sort temportery dir\n")
		os.makedirs("temp")
	######
	#First: if we have Pabio
	if cf.has_option("input file","Pacbio_reads") and cf.has_option("input file","Cuffmerge_file"):
		sys.stderr.write("Pacbio Reads and Cufflinks used\n")
		if cf.get("Globe option","Test_version")=="True":
			pass
		else:
			#dogmap(cf)
			Format_gff3("%s/Align.gff3"%(Output_dir),"N","N")
			parrse_cufflinks(cf)
			pacbioformat="%s/Align.gff3.format"%(Output_dir)
			cufflinkformat="%s/cufflinks.gtf.format"%(Output_dir)
			cmd="cat %s %s >%s/merge.format"%(pacbioformat,cufflinkformat,Output_dir)
			os.system(cmd)
	elif cf.has_option("input file","Pacbio_reads"):
		sys.stderr.write("Pacbio Reads used\n")
		#dogmap(cf)
		Format_gff3("%s/Align.gff3"%(Output_dir),"N","N")
		pacbioformat="%s/Align.gff3.format"%(Output_dir)
		cmd="cp %s %s/merge.format"%(pacbioformat,Output_dir)
		os.system(cmd)
	elif cf.has_option("input file","Cuffmerge_file"):
		sys.stderr.write("Cufflinks used\n")
		parrse_cufflinks(cf)
		cufflinkformat="%s/cufflinks.gtf.format"%(Output_dir)
		cmd="cp %s %s/merge.format"%(cufflinkformat,Output_dir)
		os.system(cmd)
	#if cf.get("Globe option","Test_version")=="True":
	#	pass
	#else:
	Cluster_Reads("%s/merge.format"%(Output_dir))
	sys.stderr.write('Reading Cluster file...\n')
	cluster=open("%s/merge.format.cluster"%(Output_dir),'r')
	mapdict=dict()
	for line in cluster:
		line=line.strip('\n')
		name=line.split()[0]
		add(mapdict,name,line,1)
	sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
	######
	conff=[]
	####
	Multile_processing=cf.get("Globe option","Multile_processing")
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
	for x in cf.items("Wig option"):
		if x[0].startswith("lib"):
			ele=x[1].split()
			conff.append("%s;%s"%(x[0],x[1]))
	####
	conff=sorted(conff,key=lambda d:d.split(";")[0])
	#conf[x.split(";")[0]]=x.split(";")[1] 
	for x in conff:
		conf[x.split(";")[0]]=x.split(";")[1] 
	for x in cf.items("Graph option"):
		conf[x[0]]=x[1]
	if cf.get("Globe option","Test_version")=="True":
		pass
	else:
		shutil.copy(Genome_Annotion,Output_dir)
		Format_gff3("%s/%s"%(Output_dir,os.path.split(Genome_Annotion)[1]),"Y","Y")
	Genome_Annotion_format="%s/%s.format"%(Output_dir,os.path.split(Genome_Annotion)[1])
	Control(Genome_Annotion_format)
	DE_AS=cf.get("DE AS option","DE")
	print DE_AS
	if DE_AS=="True":
		rmats()
	writesummary(Output_dir)
	sys.stderr.write('Compute Finshed...\n')
