#!/usr/bin/env python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.9
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
from __future__ import division
from collections import OrderedDict
#2017/05/15 21:38:37
# add supports 
#2017/05/08 09:22:21
# add adtional de as
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
import cairo
import os,sys,collections,re,multiprocessing,commands,shutil
import numpy
from argparse import ArgumentParser
#from SpliceGrapher.formats.loader import loadGeneModels
from SpliceGrapher.formats.FastaLoader import FastaLoader
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
from utils import *
#from asas_v3 import *
###############
from visual_de_as import *
############
## de apa
from visual_de_apa_pacbio import *
from visual_de_apa_all import *
############
## de nat 
from visual_de_nat_pacbio import *
from visual_de_nat_all import *
############
## de as 
from visual_de_as_pacbio import *
from visual_de_as_all import *
############
## de circle
from visual_de_circle_pacbio import *
############
# circle
from visual_circle_pacbio import *
## basic
from visual_basic_pacbio import *
from visual_basic_all import *
############
# novel gene
from novel_gene_calclute import *
#############
# annotation miss
from miss_annotation_gene import *
############
from joinfiles import *
from genemode_v2 import *
#from Pacbio_mats import *
###############
global cf
cf = ConfigParser.ConfigParser()
cf.read(args.conf)
###############
def de_nat_dict():
	nat=defaultdict(dict)
	for j in open("%s/NAT/de_nat.txt"%(Output_dir),"r"):
		ele=j.rstrip().split()
		#genename=ele[1].split("\"")[1]
		if j.startswith("ID"):
			continue
		ids,lib1,lib2,strand=ele[0].split("_")
		nat[ids][lib1,lib2,strand]=1
	return nat
def as_de_de(de_option):
	RI=defaultdict(dict)
	SE=defaultdict(dict)
	A3SS=defaultdict(dict)
	A5SS=defaultdict(dict)
	for i in ["RI","SE","A3SS","A5SS"]:
		files="%s/JC/%s.MATS.ReadsOnTargetAndJunctionCount.txt"%(Output_dir,i)
		for j in open(files,"r"):
			ele=j.rstrip().split()
			#genename=ele[1].split("\"")[1]
			if j.startswith("ID"):
				continue
			else:
				if de_option=="True":
					#genename=ele[1].split("\"")[1]
					#genename=ele[1]
					genename=";".join(ele[1].split("."))
					if float(ele[-4])>0.01 or float(ele[-5])>0.01:
						continue
				else:
					#genename=ele[1]
					genename=";".join(ele[1].split("."))
				if i=="RI":
					s,e=(int(x) for x in ele[8:10])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="SE":
					s,e=(int(x) for x in [ele[5],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="A5SS" :
					if ele[4]=="-":
						s,e=(int(x) for x in [ele[5],ele[7]])
					elif ele[4]=="+":
						s,e=(int(x) for x in [ele[8],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="A3SS":
					if ele[4]=="+":
						s,e=(int(x) for x in [ele[5],ele[7]])
					elif ele[4]=="-":
						s,e=(int(x) for x in [ele[8],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
	return RI,SE,A3SS,A5SS
def cufflinks_isoform():
	cluster=open("%s/cufflinks.gtf.format.cluster"%(Output_dir),'r')
	cuffd=dict()
	cufflim=dict()
	for line in cluster:
		line=line.strip('\n')
		name=line.split()[0]
		add(cuffd,name,line,1)
	for i in cuffd:
		minpos  = min(int(x.split()[2]) for x in cuffd[i])
		maxpos  = max(int(x.split()[3]) for x in cuffd[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		name=i.split(";")[0]
		#for j in xrange(minpos,maxpos+1):
		lims="%s,%s"%(minpos,maxpos)
		add(cufflim,name,lims,i)
	return cuffd,cufflim
	sys.stderr.write('Reading  cufflinks Cluster file finshed...\n')
def de_apa_dict():
	apa=defaultdict(dict)
	for j in open("%s/APA/de_apa.txt"%(Output_dir),"r"):
		ele=j.rstrip().split()
		#genename=ele[1].split("\"")[1]
		if j.startswith("ID"):
			continue
		lib1,lib2=ele[2].split("_VS_")
		pos1,pos2=ele[3].split(",")
		pos1,pos2=int(pos1),int(pos2)
		apa[ele[0]][lib1,lib2,pos1,pos2]=1
	return apa
###############
def apa_ati_dict():
	apa=defaultdict(dict)
	ati=defaultdict(dict)
	for j in open("%s/APA/apa.txt"%(Output_dir),"r"):
		ele=j.rstrip().split()
		#genename=ele[1].split("\"")[1]
		if j.startswith("ID"):
			continue
		apa[ele[0]]=ele[-1]
	for j in open("%s/ATI/ati.txt"%(Output_dir),"r"):
		ele=j.rstrip().split()
		#genename=ele[1].split("\"")[1]
		if j.startswith("ID"):
			continue
		ati[ele[0]]=ele[-1]
	return apa,ati
def as_cufflinks_dict():
	RI=defaultdict(dict)
	SE=defaultdict(dict)
	A3SS=defaultdict(dict)
	A5SS=defaultdict(dict)
	for i in ["RI","SE","A3SS","A5SS"]:
		files="%s/AS_cufflinks/gtf/gtf/as.%s.txt"%(Output_dir,i)
		for j in open(files,"r"):
			ele=j.rstrip().split()
			#genename=ele[1].split("\"")[1]
			if j.startswith("ID"):
				continue
			else:
				genename=ele[1]
				if i=="RI":
					s,e=(int(x) for x in ele[8:10])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="SE":
					s,e=(int(x) for x in [ele[5],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="A5SS" :
					if ele[4]=="-":
						s,e=(int(x) for x in [ele[5],ele[7]])
					elif ele[4]=="+":
						s,e=(int(x) for x in [ele[8],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="A3SS":
					if ele[4]=="+":
						s,e=(int(x) for x in [ele[5],ele[7]])
					elif ele[4]=="-":
						s,e=(int(x) for x in [ele[8],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
	return RI,SE,A3SS,A5SS
def as_de_dict(de_option):
	if de_option=="True":
		pvalue=float(cf.get("DE AS option","p_value_set"))
		fdr=float(cf.get("DE AS option","fdr"))
	RI=defaultdict(dict)
	SE=defaultdict(dict)
	A3SS=defaultdict(dict)
	A5SS=defaultdict(dict)
	for i in ["RI","SE","A3SS","A5SS"]:
		#print "%s/JC/%s.MATS.ReadsOnTargetAndJunctionCount.txt"%(Output_dir,i)
		if de_option=="True":
			files="%s/JC/%s.MATS.ReadsOnTargetAndJunctionCount.txt"%(Output_dir,i)
		else:
			files="%s/AS/as.%s.txt"%(Output_dir,i)
		for j in open(files,"r"):
			ele=j.rstrip().split()
			#genename=ele[1].split("\"")[1]
			if j.startswith("ID"):
				continue
			else:
				if de_option=="True":
					#genename=ele[1].split("\"")[1]
					#genename=ele[1]
					genename=";".join(ele[1].split("."))
					if float(ele[-4])>pvalue or float(ele[-5])>fdr:
						continue
				else:
					#genename=ele[1]
					genename=";".join(ele[1].split("."))
				if i=="RI":
					s,e=(int(x) for x in ele[8:10])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="SE":
					s,e=(int(x) for x in [ele[5],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="A5SS" :
					if ele[4]=="-":
						s,e=(int(x) for x in [ele[5],ele[7]])
					elif ele[4]=="+":
						s,e=(int(x) for x in [ele[8],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
				elif i=="A3SS":
					if ele[4]=="+":
						s,e=(int(x) for x in [ele[5],ele[7]])
					elif ele[4]=="-":
						s,e=(int(x) for x in [ele[8],ele[6]])
					eval(i)[genename]["%d:%d"%(s,e)]=1
	return RI,SE,A3SS,A5SS
def Control(Genome_Annotion_format):
	Genome_Annotion=cf.get("input file","genome_annotion")
	Output_dir=cf.get("outputdir","Output_dir")
	Multile_processing=cf.get("Global option","Multile_processing")
	allgene=defaultdict(dict)
	for i in open(Genome_Annotion_format,"r"):
		i=i.strip("\n")
		ele=i.split()
		allgene[ele[0]][i]=1
	for itelfile in ("Annotation_Gene","Novel_Gene"):
		if not os.path.exists("%s/Graph/%s"%(Output_dir,itelfile)):
			os.makedirs("%s/Graph/%s"%(Output_dir,itelfile))
	if cf.has_section("DE AS option"):
		RI,SE,A3SS,A5SS=as_de_de("True")
	else:
		RI,SE,A3SS,A5SS=as_de_dict("False")
	APA,ATI=apa_ati_dict()
	if cf.has_section("DE APA option"):
		deapa=de_apa_dict()
	else:
		deapa="NULL"
	if cf.has_section("DE NAT option"):
		DENAT=de_nat_dict()
	else:
		DENAT="NULL"
	############
	############
	if cf.has_option("input file","Cuffmerge_file"):
		cuffd,cufflim=cufflinks_isoform()
		RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff=as_cufflinks_dict()
	else:
		cuffd,cufflim="NULL","NULL"
		RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff="NULL","NULL","NULL","NULL"
	#############
	#############
	if Multile_processing=="True":
		pool = multiprocessing.Pool()
		for clu in mapdict:
			if (cf.has_section("DE AS option")) and (clu not in RI) and (clu not in SE) and (clu not in A3SS) and (clu not in A5SS):
				continue
			pool.apply_async(subcon, (clu,allgene,RI,SE,A3SS,A5SS,APA,ATI,deapa,cuffd,cufflim,RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff,DENAT,))
		pool.close()
		pool.join()
	else:
		#print RI.keys(),SE.keys(),A3SS.keys(),A5SS.keys()
		for clu in mapdict:
			if (cf.has_section("DE AS option")) and (clu not in RI) and (clu not in SE) and (clu not in A3SS) and (clu not in A5SS):
				continue
			subcon(clu,allgene,RI,SE,A3SS,A5SS,APA,ATI,deapa,cuffd,cufflim,RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff,DENAT)
def subcon(clu,allgene,RI,SE,A3SS,A5SS,APA,ATI,DEAPA,cuffd,cufflim,RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff,DENAT):
	DE_APA=cf.has_section("DE APA option")
	DE_AS=cf.has_section("DE AS option")
	DE_NAT=cf.has_section("DE NAT option")
	DE_Circle=cf.has_section("DE Circle")
	Circle=cf.has_section("Circle")
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split(';')[0]
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		refGenes = geneModel.getGenesInRange(gene,minpos,maxpos)
		if len(refGenes)>=1:
			#genename='_'.join(str(reg).split(' (')[0] for reg in refGenes)
			genename='_'.join(reg[0] for reg in refGenes)
			writename=genename
		else:
			genename="Novel_%s:%s-%s"%(gene,minpos,maxpos)
			writename="Novel"
		if len(refGenes)==0:
			path="Novel_Gene"
		else:
			path="Annotation_Gene"
		sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[3])-int(d.split()[2])), reverse = False)
		########
		if cf.has_section("DE Circle"):
			if not genename in name_lib:
				return 0
		########
		###	NAT fillter
		strand=dict()
		for k in sort_dict:
			if k.split()[4]==".":
				continue
			strand[k.split()[4]]=1
		Output_dir=cf.get("outputdir","Output_dir")
		if len(strand)==2:
			nat="True"
			if not DE_NAT:
				continue
			if not clu in DENAT:
				continue
			difflib=DENAT[clu]
			(ir_f,es_f,altd_f,alta_f,altp_f)=AS(clu,"pacbio","+")
			(ir_r,es_r,altd_r,alta_r,altp_r)=AS(clu,"pacbio","-")
			apapos_f=APA_old(clu,"+")
			atipos_f=ATI_old(clu,"+")
			apapos_r=APA_old(clu,"-")
			atipos_r=ATI_old(clu,"-")
			status,pairs,fpkmcal=judge_nat(clu,Output_dir,genename)
			if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
				cuffid="NULL"
				if gene in cufflim:
					for x in cufflim[gene]:
						s,e=x.split(",")
						s,e=int(s),int(e)
						if (maxpos<s)or(e<minpos):
							continue
						else:
							cuffid=cufflim[gene][x]
							break
				visual_de_nat_all(clu,allgene,genename,refGenes,path,apapos_f,atipos_f,apapos_r,atipos_r,ir_f,es_f,alta_f,altd_f,altp_f,nat,\
				"NULL",pairs,fpkmcal,ir_r,es_r,alta_r,altd_r,altp_r,difflib,mapdict,conf,cf,bamlist,cuffid,cuffd)
			elif cf.has_option("input file","Pacbio_reads"):
				visual_de_nat_pacbio(clu,allgene,genename,refGenes,path,apapos_f,atipos_f,apapos_r,atipos_r,ir_f,es_f,alta_f,altd_f,altp_f,nat,\
				"NULL",pairs,fpkmcal,ir_r,es_r,alta_r,altd_r,altp_r,difflib,mapdict,conf,cf,bamlist)
		else:
			#continue
			###	NAT
			###	AS Started
			nat="False"
			if cf.has_option("input file","Pacbio_reads"):
				difflib="NULL"
				apapos=",".join(APA)
				atipos=",".join(ATI)
				if DE_AS==True:
					apapos=APA[clu]
					atipos=ATI[clu]
					if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
						cuffid="NULL"
						if gene in cufflim:
							for x in cufflim[gene]:
								#print x
								s,e=x.split(",")
								s,e=int(s),int(e)
								#print minpos,s,e,maxpos
								if (maxpos<s)or(e<minpos):
									continue
								else:
									cuffid=cufflim[gene][x]
									break
						visual_de_as_all(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS,cuffid,cuffd,RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff)
					elif cf.has_option("input file","Pacbio_reads"):
						visual_de_as_pacbio(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS)
				elif DE_APA==True:
					if not clu in DEAPA:
						continue
					apapos=APA[clu]
					atipos=ATI[clu]
					difflib=DEAPA[clu]
					if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
						#cuffd,cufflim
						cuffid="NULL"
						if gene in cufflim:
							for x in cufflim[gene]:
								#print x
								s,e=x.split(",")
								s,e=int(s),int(e)
								#print minpos,s,e,maxpos
								if (maxpos<s)or(e<minpos):
									continue
								else:
									cuffid=cufflim[gene][x]
									break
						visual_de_apa_all(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS,cuffid,cuffd,RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff)
					elif cf.has_option("input file","Pacbio_reads"):
						visual_de_apa_pacbio(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS)
				elif DE_Circle==True:
					#de_lib
					#name_lib
					apapos=APA[clu]
					atipos=ATI[clu]
					visual_de_circle_pacbio(clu,allgene,genename,refGenes,path,apapos,atipos,nat,de_lib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS,name_lib[genename])
				elif Circle==True:
					apapos=APA[clu]
					atipos=ATI[clu]
					visual_circle_pacbio(clu,allgene,genename,refGenes,path,apapos,atipos,nat,de_lib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS,name_lib[genename])
				elif DE_NAT==True:
					continue
				else:
					apapos=APA[clu]
					atipos=ATI[clu]
					if cf.has_option("input file","Cuffmerge_file") and cf.has_option("input file","Pacbio_reads"):
						cuffid="NULL"
						if gene in cufflim:
							for x in cufflim[gene]:
								#print x
								s,e=x.split(",")
								s,e=int(s),int(e)
								#print minpos,s,e,maxpos
								if (maxpos<s)or(e<minpos):
									continue
								else:
									cuffid=cufflim[gene][x]
									break
						visual_basic_all(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS,cuffid,cuffd,RI_cuff,SE_cuff,A3SS_cuff,A5SS_cuff)
					elif cf.has_option("input file","Pacbio_reads"):
						visual_basic_pacbio(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand.keys()[0],RI,SE,A3SS,A5SS,name_lib)
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
		return ir,es,alta,altd,altpos
def write_mats_single(seqir,seqes,seqalta,seqaltd):
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
		##################
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
	if mark!="False" and cf.has_section("DE NAT option"):
		lib=cf.get("DE NAT option","DElib")
		libs=list(x for x in lib.split())
		comlibs=list(combinations(libs, len(libs)-1))
		chro=i.split(";")[0]
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
		out=open("%s/temp/%s.fpkm"%(Output_dir,genename),"w")
		out.write("%s\t"%(genename))
		for i in conf:
				if i.startswith("lib"):
					(tpp,bamfile,rgb)=conf[i].strip('\n').split()
					num=bamlist[i.lower()]
					fpkmforward=fpkm(bamfile,chro,"+",f_s,f_e,f_exonlength,num)
					fpkmreverse=fpkm(bamfile,chro,"-",r_s,r_e,r_exonlength,num)
					out.write("%f\t%f\t"%(fpkmforward,fpkmreverse))
					fpkmcal[i]["+"]=fpkmforward
					fpkmcal[i]["-"]=fpkmreverse
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
				for mrna in allgene[annogene]:
					hh+=200*2/(len(sort_dict)+23)
					linee=mrna
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
							if  st!=finalst:
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
	########	#####################################
def example(cr,h,scale,line,arrayline,bar_high,nat,genename,de_nat_lib):
	if de_nat_lib!="NULL":
		count=0
		cr.set_font_size(8)
		for x,y in de_nat_lib:
			lib1=conf[x.lower()].strip('\n').split()[0]
			lib2=conf[y.lower()].strip('\n').split()[0]
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
						hh+=50
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
def Visual(clu,allgene,genename,refGenes,path,apapos,atipos,ir,es,alta,altd,altp,nat,difflib):
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
		transcripts(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,nat,"NULL")
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,"NULL","NULL")
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
def ATI_old(clu,strand):
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
def APA_old(clu,strand):
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
def cluster_convert(files,outfile):
	output=open(outfile,"w")
	for i in open(files,"r"):
		ele=i.rstrip().split()
		c=0
		for j in ele[6:]:
			c+=1
			s,e=j.split(":")
			output.write("%s\tCufflinks\texon\t%s\t%s\t.\t%s\t.\tgene_id \"%s\"; transcript_id \"%s\"; exon_number \"%d\"; oId \"CUFF.18.1\"; tss_id \"TSS1\";\n"%(ele[0].split(".")[0],s,e,ele[4],ele[0],ele[1],c))
	output.close()
def joins():
	#######
	files="%s/APA/apa.txt"%(Output_dir)
	if os.path.exists(files):
		joinfiles(mapdict,geneModel,files,0)
	#######
	files="%s/APA/de_apa.txt"%(Output_dir)
	if os.path.exists(files):
		joinfiles(mapdict,geneModel,files,0)
	files="%s/ATI/ati.txt"%(Output_dir)
	if os.path.exists(files):
		joinfiles(mapdict,geneModel,files,0)
	#########
	#as analysis
	for i in ["RI","SE","A5SS","A3SS"]:
		files="%s/AS/gtf/as.%s.txt"%(Output_dir,i)
		if os.path.exists(files):
			joinfiles(mapdict,geneModel,files,1)
def rmsummary(Output_dir):
	if  cf.has_option("input file","Pacbio_reads"):
		## fix 
		files="%s/fix"%(Output_dir)
		os.system("mv %s %s/temp"%(files,Output_dir))
		## cluster
		files="%s/merge*"%(Output_dir)
		os.system("mv %s %s/temp"%(files,Output_dir))
		## gff
		Genome_Annotion=cf.get("input file","genome_annotion")
		files="%s/%s*"%(Output_dir,os.path.split(Genome_Annotion)[1])
		os.system("mv %s %s/temp"%(files,Output_dir))
		## as bak
		files="%s/AS/*.bak"%(Output_dir)
		os.system("rm %s"%(files))
		###
		## as analysis temp file delete
		for i in ["RI","SE","A5SS","A3SS"]:
			files="%s/AS/as.%s.txt"%(Output_dir,i)
			if os.path.exists(files):
				os.system("mv %s %s/temp"%(files,Output_dir))
		###
		## apa analysis temp file delete
		files="%s/APA/apa.txt"%(Output_dir)
		if os.path.exists(files):
			os.system("mv %s %s/temp"%(files,Output_dir))
		######
		## ati analysis temp file delete
		files="%s/ATI/ati.txt"%(Output_dir)
		if os.path.exists(files):
			os.system("mv %s %s/temp"%(files,Output_dir))
	if   cf.get("DE AS option","DE")=="True":
		###### add gene info
		for i in ["RI","SE","A5SS","A3SS"]:
			files="%s/JC/%s.MATS.ReadsOnTargetAndJunctionCount.txt"%(Output_dir,i)
			if os.path.exists(files):
				os.system("mv %s %s/temp"%(files,Output_dir))
		######
	if 	cf.get("DE APA option","DE")=="True":
		#######
		files="%s/APA/de_apa.txt"%(Output_dir)
		if os.path.exists(files):
			os.system("mv %s %s/temp"%(files,Output_dir))
		files="%s/APA/de_apa.txt_gene.csv"%(Output_dir)
		if os.path.exists(files):
			os.system("mv %s %s/temp"%(files,Output_dir))
		########
	if  cf.get("DE NAT option","DE")=="True":
		files="%s/NAT/de_nat.txt"%(Output_dir)
		if os.path.exists(files):
			joinfiles(mapdict,geneModel,files,0,"de_nat")
		files="%s/NAT/de_nat.txt"%(Output_dir)
		os.system("mv %s %s/temp"%(files,Output_dir))
def deg_seq(fl1,lib1,fl2,lib2,path,name_lib,de_lib):
	gene_count=defaultdict(dict)
	#####################################
	for i in open(fl1,"r"):
		ele=i.rstrip().split()
		gene_count["%s|%s:%s-%s"%(ele[14].split("|")[0],ele[0],ele[1],ele[2])][lib1]=ele[12]
	for i in open(fl2,"r"):
		ele=i.rstrip().split()
		gene_count["%s|%s:%s-%s"%(ele[14].split("|")[0],ele[0],ele[1],ele[2])][lib2]=ele[12]
	output=open("%s/%s_VS_%s.txt"%(path,lib1,lib2),"w")
	####################################
	for gene in gene_count:
		########
		if lib1 in gene_count[gene]:
			count1=gene_count[gene][lib1]
		else:
			count1=0
		########
		if lib2 in gene_count[gene]:
			count2=gene_count[gene][lib2]
		else:
			count2=0
		########
		output.write("%s\t%s\t%s\n"%(gene,count1,count2))
		########
	output.close()
	cmd="DEGseq_circv1.R %s/%s_VS_%s.txt %s/%s_degseq_%s"%(path,lib1,lib2,path,lib1,lib2)
	os.system(cmd)
	#####################################
	######################################
	for i in open("%s/%s_degseq_%s/output_score.txt"%(path,lib1,lib2),"r"):
		ele=i.split()
		if i.startswith("\"GeneNames\""):
			continue
		if not ele[-1]=="TRUE":
			continue
		print ele
		name,pos=ele[0].split("|")
		de_lib[ele[0]]["%s:%s"%(lib1,lib2)]=1
		name_lib[name][pos]=1
	######################################
	return name_lib,de_lib
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
	global conf,bamlist,mapdict,geneModel
	bamlist=dict()
	conf=OrderedDict()
	"""
	Configurition reading in a variable
	"""
	Genome_Annotion=cf.get("input file","genome_annotion")
	Output_dir=cf.get("outputdir","Output_dir")
	#geneModel = loadGeneModels(Genome_Annotion, verbose=True)
	geneModel = genemode(Genome_Annotion)
	if not os.path.exists(Output_dir):
		sys.stderr.write("Making output dir\n")
		os.makedirs(Output_dir)
	if not os.path.exists("temp"):
		sys.stderr.write("Making sort temportery dir\n")
		os.makedirs("temp")
	######
	if (cf.has_section("DE AS option") and cf.has_section("DE APA option")) or(cf.has_section("DE NAT option") and cf.has_section("DE APA option")):
		sys.stderr.write("Can't both take de as analysis and de apa analysis \nor de nat analysis and de apa analysis\n")
		sys.exit()
	######
	GMAP_Process=cf.get("GMAP option","gmap_process")
	GMAP_IndexesDir=cf.get("input file","gmap_indexesdir")
	GMAP_IndexesName=cf.get("input file","gmap_indexesname")
	Reads=cf.get("input file","Pacbio_reads")
	fa=cf.get("input file","Genome")
	######
	if not cf.has_option("input file","Pacbio_reads"):
		sys.stderr.write("Pacbio Reads used\n")
		cmd="alignPacBio.py -o %s/fix -p %s %s %s %s %s"%(Output_dir,GMAP_Process,GMAP_IndexesDir,GMAP_IndexesName,fa,Reads)
		os.system(cmd)
		cmd="sam_to_gff_trim_5.py %s/fix/aligned.bam >%s/merge.format.5"%(Output_dir,Output_dir)
		os.system(cmd)
		cmd="sam_to_gff_trim_3.py %s/fix/aligned.bam >%s/merge.format.3"%(Output_dir,Output_dir)
		os.system(cmd)
		cmd="sam_to_gff_trim_none.py %s/fix/aligned.bam >%s/merge.format.none"%(Output_dir,Output_dir)
		os.system(cmd)
		Cluster_Reads("%s/merge.format.none"%(Output_dir))
	#######
	elif cf.has_option("input file","Cuffmerge_file"):
		sys.stderr.write("Cufflinks used\n")
		parrse_cufflinks(cf)
		cufflinkformat="%s/cufflinks.gtf.format"%(Output_dir)
		cmd="cp %s %s/merge.format"%(cufflinkformat,Output_dir)
		os.system(cmd)
	##############################################################################
	sys.stderr.write('Reading Cluster file...\n')
	cluster=open("%s/merge.format.none.cluster"%(Output_dir),'r')
	mapdict=dict()
	for line in cluster:
		line=line.strip('\n')
		name=line.split()[0]
		#print name
		add(mapdict,name,line,1)
	sys.stderr.write('Reading  Pacbio Cluster file finshed...\n')
	################################################################################
	conff=[]
	######
	Multile_processing=cf.get("Global option","Multile_processing")
	if cf.get("Wig option","Wig_plot")=="True":
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
	for x in conff:
		conf[x.split(";")[0]]=x.split(";")[1]
	for x in cf.items("Graph option"):
		conf[x[0]]=x[1]
	####################################################################
	shutil.copy(Genome_Annotion,Output_dir)
	#Format_genome_annotion("%s/%s"%(Output_dir,os.path.split(Genome_Annotion)[1]),"True")
	#convert_gff("%s/%s"%(Output_dir,os.path.split(Genome_Annotion)[1]))
	gff_gpd_format("%s/%s"%(Output_dir,os.path.split(Genome_Annotion)[1]))
	## change 1
	Genome_Annotion_format="%s/%s.format"%(Output_dir,os.path.split(Genome_Annotion)[1])
	#DE_AS=cf.get("DE AS option","DE")
	##
	if  not cf.has_option("input file","Pacbio_reads"):
		################
		## novel gene
		loader = FastaLoader(fa, verbose=True)
		#############
		if not os.path.exists("%s/Novel_Gene"%(Output_dir)):
			sys.stderr.write("Making novel gene temportery dir\n")
			os.makedirs("%s/Novel_Gene"%(Output_dir))
		novel_gene_calclute(mapdict,geneModel,"%s/Novel_Gene"%(Output_dir),loader)
		## novel gene end
		## miss annotation
		if not os.path.exists("%s/Annotation_miss"%(Output_dir)):
			sys.stderr.write("Making Annotation_miss temportery dir\n")
			os.makedirs("%s/Annotation_miss"%(Output_dir))
		miss_annotation_gene(mapdict,geneModel,"%s/Annotation_miss"%(Output_dir))
		## miss annotation end
		## as analysis
		if not os.path.exists("%s/AS"%(Output_dir)):
			sys.stderr.write("Making alternative splicing  temportery dir\n")
			os.makedirs("%s/AS"%(Output_dir))
		cmd="asas_v3.py %s/merge.format.none.cluster %s/AS %s pacbio"%(Output_dir,Output_dir,Output_dir)
		os.system(cmd)
		###### add gene info#######
		for i in ["RI","SE","A5SS","A3SS"]:
			files="%s/AS/as.%s.txt"%(Output_dir,i)
			if os.path.exists(files):
				joinfiles(mapdict,geneModel,files,1,"as")
		######
		## apa analysis
		width_of_peaks=cf.get("Polya option","width_of_peaks")
		MinDist=cf.get("Polya option","MinDist")
		MinSupport=cf.get("Polya option","MinSupport")
		if  not os.path.exists("%s/APA"%(Output_dir)):
			sys.stderr.write("Making APA  temportery dir\n")
			os.makedirs("%s/APA"%(Output_dir))
		cmd="apa_v1.py %s/merge.format.none.cluster %s/APA %s pacbio %s %s %s %s/merge.format.3"%(Output_dir,Output_dir,Output_dir,width_of_peaks,MinDist,MinSupport,Output_dir)
		os.system(cmd)
		######
		## add gene info
		files="%s/APA/apa.txt"%(Output_dir)
		if os.path.exists(files):
			joinfiles(mapdict,geneModel,files,0,"apa")
		######
		## ati analysis
		width_of_peaks=cf.get("ati option","width_of_peaks")
		MinDist=cf.get("ati option","MinDist")
		MinSupport=cf.get("ati option","MinSupport")
		if not os.path.exists("%s/ATI"%(Output_dir)):
			sys.stderr.write("Making ATI  temportery dir\n")
			os.makedirs("%s/ATI"%(Output_dir))
		cmd="ati_v1.py %s/merge.format.none.cluster %s/ATI %s pacbio %s %s %s %s/merge.format.5"%(Output_dir,Output_dir,Output_dir,width_of_peaks,MinDist,MinSupport,Output_dir)
		os.system(cmd)
		######
		## add gene info
		files="%s/ATI/ati.txt"%(Output_dir)
		if os.path.exists(files):
			joinfiles(mapdict,geneModel,files,0,"ati")
		######
	if   cf.has_option("input file","Cuffmerge_file"):
		parrse_cufflinks(cf)
		pacbioformat="%s/Align.gff3.format"%(Output_dir)
		cufflinkformat="%s/cufflinks.gtf.format"%(Output_dir)
		Cluster_Reads("%s/cufflinks.gtf.format"%(Output_dir))
		## as analysis
		if not os.path.exists("%s/AS_cufflinks/gtf"%(Output_dir)):
			sys.stderr.write("Making alternative splicing  temportery dir\n")
			os.makedirs("%s/AS_cufflinks/gtf/gtf"%(Output_dir))
		cmd="asas_v3.py %s/cufflinks.gtf.format.cluster %s/AS_cufflinks/gtf/gtf %s cufflinks"%(Output_dir,Output_dir,Output_dir)
		os.system(cmd)
		######
		## nat analysis
		if not os.path.exists("%s/NAT_cufflinks"%(Output_dir)):
			sys.stderr.write("Making NAT  temportery dir\n")
			os.makedirs("%s/NAT_cufflinks"%(Output_dir))
		cmd="nat_v1.py %s/cufflinks.gtf.format.cluster %s/NAT_cufflinks %s pacbio"%(Output_dir,Output_dir,Output_dir)
		os.system(cmd)
		######
	if   cf.has_section("DE AS option"):
		#cluster_convert("%s/merge.format.cluster"%(Output_dir),"%s/merge.format.cluster.gtf"%(Output_dir))
		if not os.path.exists("%s/JC/temp"%(Output_dir)):
			sys.stderr.write("Making alternative splicing  temportery dir\n")
			os.makedirs("%s/JC/temp"%(Output_dir))
		readLength=int(cf.get("Wig option","readLength"))
		junctionLength=check_jucton_length()
		libs=cf.get("DE AS option","delib")
		group1= [conf[x.lower()].strip('\n').split()[1] for x in libs.split()[0].split("_")]
		group1str=",".join(group1)
		group2= [conf[x.lower()].strip('\n').split()[1] for x in libs.split()[1].split("_")]
		group2str=",".join(group2)
		cmd="Pacbio_mats.py %d %d %s/AS %s %s %s/JC/temp"%(readLength,junctionLength,Output_dir,group1str,group2str,Output_dir)
		os.system(cmd)
		cmd="Pacbio_mats.sh %s"%(Output_dir)
		os.system(cmd)
		###### add gene info
		for i in ["RI","SE","A5SS","A3SS"]:
			files="%s/JC/%s.MATS.ReadsOnTargetAndJunctionCount.txt"%(Output_dir,i)
			if os.path.exists(files):
				joinfiles(mapdict,geneModel,files,1,"as")
		######
	if 	cf.has_section("DE APA option"):
		cmd="de_apa_v1.py %s/merge.format.none.cluster %s/APA %s pacbio %s %s"%(Output_dir,Output_dir,Output_dir,Multile_processing,args.conf)
		print cmd
		os.system(cmd)
		### add gene info
		files="%s/APA/de_apa.txt"%(Output_dir)
		if os.path.exists(files):
			joinfiles(mapdict,geneModel,files,0,"de_apa")
		### add fdr
		cmd="FDR.py %s/APA/de_apa.txt_gene.csv %s/APA/de_apa.txt.gene.fdr.csv"%(Output_dir,Output_dir)
		os.system(cmd)
		###
	if  cf.has_section("DE NAT option"):
		if not os.path.exists("%s/NAT"%(Output_dir)):
			sys.stderr.write("Making NAT  temportery dir\n")
			os.makedirs("%s/NAT"%(Output_dir))
		if not os.path.exists("%s/temp"%(Output_dir)):
			sys.stderr.write("Making temportery dir\n")
			os.makedirs("%s/temp"%(Output_dir))
		cmd="de_nat_v1.py %s/merge.format.none.cluster %s/NAT %s pacbio %s %s"%(Output_dir,Output_dir,Output_dir,Multile_processing,args.conf)
		os.system(cmd)
		### add gene info
		files="%s/NAT/de_nat.txt"%(Output_dir)
		if os.path.exists(files):
			joinfiles(mapdict,geneModel,files,0,"de_nat")
	#######
	global de_lib,name_lib
	de_lib=defaultdict(dict)
	name_lib=defaultdict(dict)
	########
	if  (not cf.has_section("DE Circle")) and (cf.has_section("Circle")):
		if not os.path.exists("%s/circle"%(Output_dir)):
			sys.stderr.write("Making circle temportery dir\n")
			os.makedirs("%s/circle"%(Output_dir))
		circle_ref_isoform("%s/circle"%(Output_dir),geneModel,mapdict)
		lib_circle=cf.get("Circle","lib")
		libs=list(x for x in lib_circle.split())
		for i in libs:
			(tpp,filee,rgb)=conf[i.lower()].strip('\n').split()
			bam_circle=filee
			cmd="CIRCexplorer.py -f %s -g %s -r %s/circle/circle_gff.txt -o %s/circle/%s "%(bam_circle,fa,Output_dir,Output_dir,i)
			os.system(cmd)
	#########
	if  cf.has_section("DE Circle"):
		if not os.path.exists("%s/circle"%(Output_dir)):
			sys.stderr.write("Making circle temportery dir\n")
			os.makedirs("%s/circle"%(Output_dir))
		circle_ref_isoform("%s/circle"%(Output_dir),geneModel,mapdict)
		fa=cf.get("input file","Genome")
		lib_circle=cf.get("DE Circle","DElib")
		libs=list(x for x in lib_circle.split())
		comlibs=list(combinations(libs,2))
		for i,j in comlibs:
			(tpp,filee,rgb)=conf[i.lower()].strip('\n').split()
			bam_circle=filee
			cmd="CIRCexplorer.py -f %s -g %s -r %s/circle/circle_gff.txt -o %s/circle/%s "%(bam_circle,fa,Output_dir,Output_dir,i)
			os.system(cmd)
			(tpp,filee,rgb)=conf[j.lower()].strip('\n').split()
			bam_circle=filee
			cmd="CIRCexplorer.py -f %s -g %s -r %s/circle/circle_gff.txt -o %s/circle/%s "%(bam_circle,fa,Output_dir,Output_dir,j)
			os.system(cmd)
			name_lib,de_lib=deg_seq("%s/circle/%s_circ.txt"%(Output_dir,i),i,"%s/circle/%s_circ.txt"%(Output_dir,j),j,"%s/circle"%(Output_dir),name_lib,de_lib)
	#######
	Control(Genome_Annotion_format)
	#rmsummary(Output_dir)
	sys.stderr.write('Compute Finshed...\n')
	#########
