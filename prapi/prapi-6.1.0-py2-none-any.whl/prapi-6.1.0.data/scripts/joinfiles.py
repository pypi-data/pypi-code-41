#!python
def joinfiles(mapdict,geneModel,ff,num,tpp):
	ifile=open(ff);title=ifile.readline();
	ilines=ifile.readlines();
	title="\t".join(title.split()[1:])
	output=open("%s_gene.csv"%(ff),"w");output.write("genename\t"+title+"\n")
	for i in ilines:
		i=i.rstrip()
		line=i
		ele=i.split()
		ids=ele[num]
		if tpp=="as":
			ids=";".join(ids.split("."))
		elif tpp=="de_nat":
			ids=ele[num].split("_")[0]
		minpos  = min(int(x.split()[2]) for x in mapdict[ids])
		maxpos  = max(int(x.split()[3]) for x in mapdict[ids])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=ele[num].split(';')[0]
		if tpp=="as":
			gene=ele[num].split('.')[0]
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		###################
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
		elif len(refGenes)==1:
			path="Annotation"
		elif len(refGenes)>1:
			path="Annotation_Miss"
		line="\t".join(ele[1:])
		#output.write("%s\t%s\t%s\n"%(genename,path,line))
		output.write("%s\t%s\n"%(genename,line))
	output.close()
