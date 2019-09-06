#!/usr/bin/env python
def miss_annotation_gene(mapdict,geneModel,dir_o):
	output=open("%s/Miss_annotation.csv"%(dir_o),"w")
	output.write("Genename\tStrand\tSupport_Reads_Num\tSupport_Reads\n")
	for i in mapdict:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split(';')[0]
		strand=list(set([x.split()[4] for x in mapdict[i]]))
		if len(strand)==2:
			continue
		strand=strand[0]
		Gene_coordinate="%s:%d-%d"%(gene,minpos,maxpos)
		refGenes = geneModel.getGenesInRange(gene,minpos,maxpos)
		if len(refGenes)>=1:
			#genename='_'.join(reg.name for reg in refGenes)
			genename='_'.join(reg[0] for reg in refGenes)
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
		##########
		if path!="Annotation_Miss":
			continue
		#########
		reads=[x.split()[5]for x in mapdict[i]]
		stats=""
		#
		for trans in mapdict[i]:
			ele=trans.split()
			if len(ele[6:])==1:
				continue
			###################
			introns=[]
			exons=[x for x in ele[6:]]
			for index,value in enumerate(exons):
				if index==0:
					continue
				if strand=="+":
					s,e=exons[index-1].split(":")[-1],value.split(":")[0]
				elif strand=="-":
					s,e=exons[index-1].split(":")[0],value.split(":")[-1]
				s,e=int(s),int(e)
				introns.append((s,e))
			##################
			#print ele[5]
			#print introns
			##################
			ok=0
			for gene in genename.split("_"):
				intron_gene=geneModel.getIntrons(gene)
				#print gene
				#print intron_gene
				deng=""
				for little in introns:
					if little in intron_gene:
						deng="True"
						break
				if deng:
					ok+=1
			#print ok
			if ok>=2:
				stats="True"
				break
		readss="|".join(reads)
		#print readss
		if stats:
			output.write("%s\t%s\t%d\t%s\n"%(genename,strand,len(mapdict[i].keys()),readss))
	output.close()
