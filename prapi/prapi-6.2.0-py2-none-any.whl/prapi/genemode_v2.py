#!/usr/bin/env python
import sys,os,re
from  collections import defaultdict
########################################################################
class genemode(object):
	def __init__(self,fl):
		self.fl =fl
		self.data=defaultdict(dict)
		self.gene=defaultdict(dict)
		self.intron=defaultdict(dict)
		for i in open(self.fl,"r"):
			if (i.startswith("#")) or (not i.rstrip()):
				continue
			ele=i.rstrip().split()
			###############
			chro=ele[2]
			lim="%s:%s"%(ele[4],ele[5])
			genename=ele[0]
			#print genename
			self.data[genename][lim]=1
			self.data[genename]["chro"]=chro
			###############
			s_l=[int(x)+1 for x in ele[-2].split(",")[:-1]]
			e_l=[int(x) for x in ele[-1].split(",")[:-1]]
			for index in range(len(s_l)):
				if index==0:
					continue
				#self.intron[genename][(s_l[index-1],e_l[index])]=1
				self.intron[genename][(e_l[index-1],s_l[index])]=1
			###############
		for genename in self.data:
			chro=self.data[genename]["chro"]
			s=min([int(x.split(":")[0]) for x in self.data[genename]if x!="chro"])
			e=max([int(x.split(":")[-1]) for x in self.data[genename]if x!="chro"])
			self.gene[chro]["%s:%s"%(s,e)]=genename
			################
	def getIntrons(self,gene):
		return self.intron[gene].keys()
	def getGenesInRange(self,w_chro,w_s,w_e):
		returndict=[]
		if not w_chro in self.gene:
			return returndict
		else:
			for i in self.gene[w_chro]:
				s,e=(int(x) for x in i.split(":"))
				if w_e<s or w_s>e:
					pass
				else:
					returndict.append([self.gene[w_chro][i],s,e])
		return returndict
#wilber=genemode(sys.argv[1])
#genes=wilber.getGenesInRange("PH01003373",29091,38033)
#print genes
########################################################################
