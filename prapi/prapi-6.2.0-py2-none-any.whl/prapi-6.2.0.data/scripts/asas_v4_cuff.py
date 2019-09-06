#!python
import os,sys,re
from  collections import defaultdict
def AltD(exondict,introndict,gene,strand,genename):
	string=""
	for i in introndict:
		(from1,to1)=i.split(':')
		(from1,to1)=(int(from1),int(to1))
		for j in introndict:
			(from2,to2)=j.split(':')
			(from2,to2)=(int(from2),int(to2))
			if from2<from1 and to2==to1:
				if introndict[i].split(":")[0]==introndict[j].split(":")[0] and introndict[i].split(":")[-1]==introndict[j].split(":")[-1]:
					string+="%s\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t\n"%(genename,gene,strand,int(introndict[i].split(":")[0])-1,from1,int(introndict[i].split(":")[0])-1,from2,to1-1,int(introndict[i].split(":")[-1]))
	return string
def AltA(exondict,introndict,gene,strand,genename):
	string=""
	for i in introndict:
		(from1,to1)=i.split(':')
		(from1,to1)=(int(from1),int(to1))
		for j in introndict:
			(from2,to2)=j.split(':')
			(from2,to2)=(int(from2),int(to2))
			if from2==from1 and to2<to1:
				if introndict[i].split(":")[0]==introndict[j].split(":")[0] and introndict[i].split(":")[-1]==introndict[j].split(":")[-1]:
					string+="%s\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t\n"%(genename,gene,strand,to2-1,int(introndict[i].split(":")[-1]),to1-1,int(introndict[i].split(":")[-1]),int(introndict[i].split(":")[0])-1,from1)
	return string
#################################################
def Altpos(exondict,introndict,gene,strand,genename):
	altpos=[]
	for i in introndict:
		(from1,to1)=(int(x) for x in i.split(':'))
		for j in introndict:
			if i!=j:
				(from2,to2)=(int(x) for x in j.split(':'))
				if (introndict[i].split(":")[0]==introndict[j].split(":")[0] and introndict[i].split(":")[-1]==introndict[j].split(":")[-1]) and (from2< from1 and to1<to2):
					altpos.append(i)
	return ",".join(x for x in altpos)
def ES(exondict,introndict,gene,strand,genename):
	string=""
	for i in exondict:
		(exs,exe)=i.split(':')
		(exs,exe)=(int(exs),int(exe))
		for j in introndict:
			(ins,ine)=j.split(':')
			(ins,ine)=(int(ins),int(ine))
			if ins<exs and exe<ine:
				f1_0,f1_1=(int(x) for x in exondict[i][0].split(":"))
				f2_0,f2_1=(int(x) for x in exondict[i][1].split(":"))
				if f1_1==ins and f2_0==ine: 
					string+="%s\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t\n"%(genename,gene,strand,exs-1,exe,f1_0-1,f1_1,f2_0-1,f2_1)
	return string
def IR(exondict,introndict,gene,strand,genename):
	string=""
	for i in exondict:
		(exs,exe)=i.split(':')
		(exs,exe)=(int(exs),int(exe))
		for j in introndict:
			(ins,ine)=j.split(':')
			(ins,ine)=(int(ins),int(ine))
			f1_0,f1_1,ce_0,ce_1=(int(x) for x in introndict[j].split(":"))
			if exs<ins and ine<exe:
			#and f1_0==exs and ce_1==exe:
				string+="%s\tNA\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t\n"%(genename,gene,strand,exs-1,exe,f1_0-1,ins,ine-1,ce_1)
	return string
###############
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
############
oFile_3 = open(outdir+'/as.A3SS.txt', 'w'); ## alt-3 SS output file
oFile_5 = open(outdir+'/as.A5SS.txt', 'w'); ## alt-5 SS output file
oFile_se = open(outdir+'/as.SE.txt', 'w'); ## skipped exon (cassette exon) output file
oFile_ri = open(outdir+'/as.RI.txt', 'w'); ## retained intron output file
############
### write out header
seHeader = "ID\tGeneID\tgeneSymbol\tchr\tstrand\texonStart_0base\texonEnd\tupstreamES\tupstreamEE\tdownstreamES\tdownstreamEE";
oFile_se.write(seHeader+'\n');
altSSHeader = "ID\tGeneID\tgeneSymbol\tchr\tstrand\tlongExonStart_0base\tlongExonEnd\tshortES\tshortEE\tflankingES\tflankingEE";
oFile_3.write(altSSHeader+'\n');
oFile_5.write(altSSHeader+'\n');
riHeader = "ID\tGeneID\tgeneSymbol\tchr\tstrand\triExonStart_0base\triExonEnd\tupstreamES\tupstreamEE\tdownstreamES\tdownstreamEE";
oFile_ri.write(riHeader+'\n');
############
############
sys.stderr.write('complute as events...\n')
for i in mapdict:
	introndict=dict()
	exondict=dict()
	intron=[]
	ir=dict()
	es=dict()
	esdict=dict()
	altd=dict()
	alta=dict()
	gene=i.split(';')[0]
	strand=list(set([x.split()[4] for x in mapdict[i]]))
	if len(strand)==2:
		continue
	strand=strand[0]
	for x in mapdict[i]:
		if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
			continue
		if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
			continue
		if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
			continue
		#print "ok"
		for y in x.split()[6:]:
			exondict[y]=1
		for x in mapdict[i]:
			if (tpd=="cufflinks") and (not x.split()[5].startswith("cufflinks")):
				continue
			if tpd=="pacbio" and x.split()[5].startswith("cufflinks"):
				continue
			if (strand=="+" and x.split()[4]=="-")or(strand=="-" and x.split()[4]=="+"):
				continue
			for y in range(len(x.split())-1):
				if y<7:
					continue
				if strand=="+":
					esdict[x.split()[y]]=[x.split()[y-1],x.split()[y+1]]
				elif strand=="-":
					esdict[x.split()[y]]=[x.split()[y+1],x.split()[y-1]]
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
	############################
	############################
	genename=".".join(i.split(";"))
	ir=IR(exondict,introndict,gene,strand,genename)
	oFile_ri.write(ir)
	es=ES(esdict,introndict,gene,strand,genename)
	oFile_se.write(es)
	if strand=="+":
		altd=AltD(exondict,introndict,gene,strand,genename)
		alta=AltA(exondict,introndict,gene,strand,genename)
	else:
		altd=AltA(exondict,introndict,gene,strand,genename)
		alta=AltD(exondict,introndict,gene,strand,genename)
	oFile_3.write(alta)
	oFile_5.write(altd)
	#for y in ["es","ir","alta","altd"]:
	#	if eval(y):
	#		print i,y
oFile_se.close()
oFile_ri.close()
oFile_5.close()
oFile_3.close()
################################
oFile_3 = open(outdir+'/as.A3SS.txt', 'r'); ## alt-3 SS output file
oFile_5 = open(outdir+'/as.A5SS.txt', 'r'); ## alt-5 SS output file
oFile_se = open(outdir+'/as.SE.txt', 'r'); ## skipped exon (cassette exon) output file
oFile_ri = open(outdir+'/as.RI.txt', 'r'); ## retained intron output file
###############################
oFile_3b = open(outdir+'/as.A3SS.txt.bak', 'w'); ## alt-3 SS output file
oFile_5b = open(outdir+'/as.A5SS.txt.bak', 'w'); ## alt-5 SS output file
oFile_seb = open(outdir+'/as.SE.txt.bak', 'w'); ## skipped exon (cassette exon) output file
oFile_rib = open(outdir+'/as.RI.txt.bak', 'w'); ## retained intron output file
###############################
c=-1
for i in oFile_3:
	c+=1
	if c==0:
		oFile_3b.write(i)
	else:
		oFile_3b.write(str(c)+"\t"+i)
oFile_3b.close()
cmd="cp %s/as.A3SS.txt.bak %s/as.A3SS.txt"%(outdir,outdir)
os.system(cmd)
print "there is %d A3SS events"%(c)
#############################
###############################
c=-1
for i in oFile_5:
	c+=1
	if c==0:
		oFile_5b.write(i)
	else:
		oFile_5b.write(str(c)+"\t"+i)
oFile_5b.close()
cmd="cp %s/as.A5SS.txt.bak %s/as.A5SS.txt"%(outdir,outdir)
os.system(cmd)
print "there is %d A5SS events"%(c)
#############################
###############################
c=-1
for i in oFile_se:
	c+=1
	if c==0:
		oFile_seb.write(i)
	else:
		oFile_seb.write(str(c)+"\t"+i)
oFile_seb.close()
cmd="cp %s/as.SE.txt.bak %s/as.SE.txt"%(outdir,outdir)
os.system(cmd)
print "there is %d SE events"%(c)
#############################
###############################
c=-1
for i in oFile_ri:
	c+=1
	if c==0:
		oFile_rib.write(i)
	else:
		oFile_rib.write(str(c)+"\t"+i)
oFile_rib.close()
cmd="cp %s/as.RI.txt.bak %s/as.RI.txt"%(outdir,outdir)
os.system(cmd)
print "there is %d RI events"%(c)
#############################
