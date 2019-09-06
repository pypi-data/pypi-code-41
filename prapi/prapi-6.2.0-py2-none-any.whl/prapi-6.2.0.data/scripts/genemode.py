#!python
import sys,os,re
from  collections import defaultdict
########################################################################
class genemode(object):
	def __init__(self,fl):
		self.fl =fl
		self.data=defaultdict(dict)
		for i in open(self.fl,"r"):
			if (i.startswith("#")) or (not i.rstrip()):
				continue
			ele=i.rstrip().split("\t")
			typ=ele[2]
			chro=ele[0]
			lim="%s:%s"%(ele[3],ele[4])
			##NC_003070.9	RefSeq	gene	3631	5899	.	+	.	ID=gene0;Dbxref=Araport:AT1G01010,TAIR:AT1G01010,GeneID:839580;Name=NAC001;gbkey=Gene;gene=NAC001;gene_biotype=protein_coding;gene_synonym=ANAC001,NAC domain containing protein 1,T25K16.1,T25K16_1;locus_tag=AT1G01010
			if typ!="mRNA":
				continue
			#names=re.findall("Name=\w+;",ele[-1],s)
			#print ele
			#print names
			#genename=re.split("=|;",names[0])[1]
			genename=re.split("ID=",ele[-1])[-1].split(";")[0]
			#print genename
			self.data[chro][lim]=genename
	def getGenesInRange(self,w_chro,w_s,w_e):
		returndict=[]
		#print self.data.keys()
		#print "Orign data w_chro"+"\t"+w_chro
		if not w_chro in self.data:
			print w_chro+"\tError!!"
			#print w_chro+"\tnot in this chromosome"
			#,self.data.keys()
		else:
			for i in self.data[w_chro]:
				s,e=(int(x) for x in i.split(":"))
				if w_e<s or w_s>e:
					pass
				else:
					returndict.append([self.data[w_chro][i],s,e])
		return returndict
#wilber=genemode(sys.argv[1])
#wilber.getGenesInRange("NC_003070.9",1,10042)
########################################################################

