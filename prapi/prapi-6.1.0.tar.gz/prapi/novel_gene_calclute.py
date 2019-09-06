#!/usr/bin/env python
def novel_gene_calclute(mapdict,geneModel,output_dir,loader):
	output=open("%s/Novel_Gene.fa"%(output_dir),"w")
	output.write("Chrom\tStart\tEnd\tReads_Num\tReads_Id\tSeq\n"%())
	for i in mapdict:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split(';')[0]
		strand=list(set([x.split()[4] for x in mapdict[i]]))
		if len(strand)==2:
			continue
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		refGenes = geneModel.getGenesInRange(gene,minpos,maxpos)
		if len(refGenes)>=1:
		#genename='_'.join((x[0] for x in refGenes))
			genename='_'.join(str(reg).split(' (')[0] for reg in refGenes)
			writename=genename
		else:
			genename="%s\t%s\t%s"%(gene,minpos,maxpos)
			writename="Novel"
		if len(refGenes)==0:
			path="Novel_Gene"
		elif len(refGenes)==1:
			path="Annotation"
		elif len(refGenes)>1:
			path="Annotation_Miss"
		if path!="Novel_Gene":
			continue
		reads=[x.split()[5]for x in mapdict[i]]
	####
		exon=[]
		for iso in mapdict[i]:
			for j in iso.split()[6:]:
				s,e=(int(x) for x in j.split(":"))
				for pos in range(s,e+1):
					exon.append(pos)
	####
		exon=sorted(set(exon),key=lambda d:(d))
		seq=""
		for index,pos in enumerate(exon):
			if index==0:
				seq+=loader.subsequence(gene,pos-1,pos-1)
			else:
				if pos-exon[index-1]!=1:
					seq+=loader.subsequence(gene,exon[index-1]+1-1,pos-1-1).lower()
				seq+=loader.subsequence(gene,pos-1,pos-1)
		output.write("%s\t%d\t%s\t%s\n"%(genename,len(mapdict[i]),",".join(reads),seq))
	####
	output.close()
	####
