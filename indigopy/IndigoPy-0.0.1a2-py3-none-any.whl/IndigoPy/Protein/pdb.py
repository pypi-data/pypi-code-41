#!/usr/bin/python3
from urllib import request
from ..Math import coordinates as cdn
import copy
import os
import pickle
t3t1={'GLY':'G','ALA':'A','VAL':'V','LEU':'L','ILE':'I','PHE':'F','PRO':'P','SER':'S','THR':'T','HIS':'H','TRP':'W',
'CYS':'C','ASP':'D','GLU':'E','LYS':'K','TYR':'Y','MET':'M','ASN':'N','GLN':'Q','ARG':'R',
'G':'G','C':'C','A':'A','U':'U',
'DG':'g','DC':'c','DA':'a','DT':'t'}
dnaname=['DG','DC','DA','DT']
rnaname=['G','C','A','U']
resname=['GLY','ALA','VAL','LEU','ILE','PHE','PRO','SER','THR','HIS','TRP','CYS','ASP','GLU','LYS','TYR','MET','ASN','GLN','ARG']



#========================================================================================================================
#===========||====||||||==||||||==||||====||||||==||||||==||||||==||==||====||======||====||==||==||======||==||=========
#=========||||||==||||====||======||==||==||||||==||||||==||======||||||====||======||====||||====||======||||||=========
#=========||==||==||||||==||||||==||||====||||||==||======||||====||==||====||====||||====||==||==||||||==||||||=========
#========================================================================================================================
#===============================================Indigo Mad  vesion 0.01a1================================================
#========================================================================================================================
#=========||||||==||||||==||||======||||==||||======||||==||||||==||==||==||==||==||||||==||==||==||==||==||||===========
#=========||==||==||==||==||||======||||==||||======||======||====||==||==||==||==||||||====||======||======||===========
#=========||==||==||||||==||==========||==||==||==||||======||====||||||====||====||==||==||==||====||======||||=========
#========================================================================================================================




#========================================================================================================================
#=====================================================||||||||||||||=====================================================
#=====================================================||=================================================================
#=====================================================||=================================================================
#=====================================================||=================================================================
#=====================================================||=================================================================
#=====================================================||=================================================================
#=====================================================||||||||||||||=====================================================
#========================================================================================================================
#===================================================Classes definition===================================================

#========================================================================================================================
#=========================================================||||===========================================================
#=========================================================||||===========================================================
#=========================================================||=============================================================
#========================================================================================================================
#=======================================Basic position informations for a protein========================================
class Atom():
	def __init__(self,name,pos,ele):
		self.name=name
		self.pos=cdn.Position(pos)
		self.ele=ele
	def __str__(self):
		return self.name+" "+self.ele+str(self.pos)
	__repr__=__str__
	def __getitem__(self, key):
		if isinstance(key,str):
			if key=='x' or key=='X':
				return self.pos[0]
			elif key=='y' or key=='Y':
				return self.pos[1]
			elif key=='y' or key=='Y':
				return self.pos[2]
			else:
				raise KeyError("Expecting an intege or 'x','X','y','Y','Z','z' but a "+str(type(key))+"is given")
		elif isinstance(key,int):
			return self.pos[key]
		elif isinstance(key,slice):
			return self.pos[key]
		else:
			raise KeyError("Expecting an intege or 'x','X','y','Y','Z','z' but a "+str(type(key))+"is given")
	def __setitem__(self, key, value):
		if isinstance(key,str):
			if key=='x' or key=='X':
				self.pos[0]=value
			elif key=='y' or key=='Y':
				self.pos[1]=value
			elif key=='y' or key=='Y':
				self.pos[2]=value
			else:
				raise KeyError("Expecting an intege or 'x','X','y','Y','Z','z' but a "+str(type(key))+"is given")
		elif isinstance(key,int):
			self.pos[key]=value
		elif isinstance(key,slice):
			self.pos[key]=value
		else:
			raise KeyError("Expecting an intege or 'x','X','y','Y','Z','z' but a "+str(type(key))+"is given")






class Residue():
	def __init__(self,name,num,atomlist):
		self.name=name
		self.atoms=atomlist
		self.num=num
	def __getitem__(self, key):
		if isinstance(key,str):
			temlist=[]
			for i in self.atoms:
				if i.name==key:
					return i
					break
		elif isinstance(key,int):
			return self.atoms[key]
		elif isinstance(key,slice):
			return self.atoms[key]
		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")
	def __setitem__(self, key, value):
		if isinstance(key,str):
			temlist=[]
			for i in range(len(self.atoms)):
				if self.atoms[i].name==key:
					self.atoms[i]=value
					break
		elif isinstance(key,int):
			self.atoms[key]=value
		elif isinstance(key,slice):
			self.atoms[key]=value
		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")
	def __str__(self):
		return str(self.num)+" "+self.name
	__repr__=__str__
	def __len__(self):
		return len(self.atoms)
	def __iter__(self):
		return iter(self.atoms)


class Residue():
	def __init__(self,name,num,atomlist):
		self.name=name
		self.atoms=atomlist
		self.num=num
	def __getitem__(self, key):
		if isinstance(key,str):
			temlist=[]
			for i in self.atoms:
				if i.name==key:
					return i
					break
		elif isinstance(key,int):
			return self.atoms[key]
		elif isinstance(key,slice):
			return self.atoms[key]
		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")
	def __setitem__(self, key, value):
		if isinstance(key,str):
			temlist=[]
			for i in range(len(self.atoms)):
				if self.atoms[i].name==key:
					self.atoms[i]=value
					break
		elif isinstance(key,int):
			self.atoms[key]=value
		elif isinstance(key,slice):
			self.atoms[key]=value
		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")
	def __str__(self):
		return str(self.num)+" "+self.name
	__repr__=__str__
	def __len__(self):
		return len(self.atoms)
	def __iter__(self):
		return iter(self.atoms)







class Chain():
	def __init__(self,name,residueslist,nonstandardlist):
		self.name=name
		self.seq=''
		self.residues=residueslist
		self.nonstandard=nonstandardlist
	def __getitem__(self, key):
		if isinstance(key,str):
			temlist=[]
			rkey=key.upper()
			for i in self.residues:
				if i.name==rkey:
					temlist.append(i)
				elif t3t1.get(i.name)==key:
					temlist.append(i)
			for i in self.nonstandard:
				if i.name==key:
					temlist.append(i)
			return temlist
		elif isinstance(key,int):
			for i in self.residues:
				if i.num==key:
					return i
					break
		elif isinstance(key,slice):
			if key.start!=None:
				if key.stop!=None:
					return self.residues[self.residues.index(self[key.start]):self.residues.index(self[key.stop]):key.step]
				else:
					return self.residues[self.residues.index(self[key.start])::key.step]
			else:
				if key.stop!=None:
					return self.residues[:self.residues.index(self[key.stop]):key.step]
				else:
					return self.residues[::key.step]

		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")

	def __setitem__(self, key, value):
		if type(key)==int:
			for i in range(len(self.residues)):
				if self.residues[i].num==key:
					self.residues[i].num=value
					break
			temstr=''
			for i in range(self.residues[0].num,self.residues[-1].num+1):
				try:
					getres=self[i].name
				except:
					temstr=temstr+'-'
					print('[Warming]: no residues found at '+self.name+' '+str(i))
				else:
					try:
						temstr=temstr+t3t1[getres]
					except:
						temstr=temstr+'('+self[i].name+')'
						print('[Warming]:Unknow residue '+self[i].name+' included.')
			self.seq=temstr
		elif isinstance(key,slice):
			raise KeyError("Do not use slice to set values in a Chain")
		else:
			raise KeyError("Expecting an intege but a "+str(type(key))+"is given")
	def __str__(self):
		return self.name+"-"+str(self.residues[0].num)+'-'+self.seq+'-'+str(self.residues[-1].num)
	__repr__=__str__
	def __iter__(self):
		return iter(self.residues)
	def __len__(self):
		return len(self.residues)
	def seqlen(self):
		return len(self.seq)
	def sequence(self, beg, end):
		seqtem=''
		for i in range(beg,end+1):
			try:
				getres=self[i].name
			except:
				seqtem=seqtem+'-'
				print('[Warming]: no residues found at '+self.name+' '+str(i))
			else:
				try:
					seqtem=seqtem+t3t1[getres]
				except:
					seqtem=seqtem+'('+self[i].name+')'
					print('[Warming]:Unknow residue '+self[i].name+' included.')
		return seqtem
	def __setattr__(self,name,value):
		if name == "residues":
			self.__dict__[name] = value
			temstr=''
			for i in range(self.residues[0].num,self.residues[-1].num+1):
				try:
					getres=self[i].name
				except:
					temstr=temstr+'-'
					print('[Warming]: no residues found at '+self.name+' '+str(i))
				else:
					try:
						temstr=temstr+t3t1[getres]
					except:
						temstr=temstr+'('+self[i].name+')'
						print('[Warming]:Unknow residue '+self[i].name+' included.')
			self.seq=temstr
		else:
			self.__dict__[name] = value

	def counter(self,key):
		if key=='nonstandard':
			temdic={}
			for r in self.nonstandard:
				try:
					temdic[r.name]=temdic[r.name]+1
				except:
					temdic[r.name]=1
			return temdic

		elif key=='residues':
			temdic={}
			for r in self:
				try:
					temdic[r.name]=temdic[r.name]+1
				except:
					temdic[r.name]=1
			return temdic

		elif isinstance(key,str):
			temnum=0
			rkey=key.upper()
			for r in self:
				if r.name==rkey:
					temnum+=1
				elif r.name==key:
					temnum+=1
			for r in self.nonstandard:
				if r.name==key:
					temnum+=1		
			return temnum

		else:
			raise KeyError("Expecting a string but a "+str(type(key))+"is given")

			








class Model():
	def __init__(self,chainlist,dnalist,rnalist):
		self.chains=chainlist
		self.dna=dnalist
		self.rna=rnalist
	def __getitem__(self, key):
		if isinstance(key,str):
			temlist=[]
			for i in self.chains:
				if i.name==key:
					return i
					break
			for i in self.dna:
				if i.name==key:
					return i
					break
			for i in self.rna:
				if i.name==key:
					return i
					break
		elif isinstance(key,int):
			return self.chains[key]

		elif isinstance(key,slice):
			return self.chains[key]
		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")

	def __setitem__(self, key, value):
		if isinstance(key,str):
			temlist=[]
			for i in range(len(self.chains)):
				if self.chains[i].name==key:
					self.chains[i]=value
					break
		elif isinstance(key,int):
			self.chains[key]=value
		elif isinstance(key,slice):
			self.chains[key]=value
		else:
			raise KeyError("Expecting an intege or a string but a "+str(type(key))+"is given")
	def __iter__(self):
		return iter(self.chains)
	def __len__(self):
		return len(self.chains)
	def seqlen(self):
		temnum=0
		for i in self:
			temnum+=len(i)
		return temnum







#========================================================================================================================
#===========================================================||||=========================================================
#===========================================================||===========================================================
#=========================================================||||===========================================================
#========================================================================================================================
#==================================================Secondary structures==================================================



"""
				TYPE OF HELIX          CLASS NUMBER 
									   (COLUMNS 39 - 40)
	  ----------------------------------------------
	  Right-handed alpha (default)       1
	  Right-handed omega                 2
	  Right-handed pi                    3
	  Right-handed gamma                 4
	  Right-handed 310                   5
	  Left-handed alpha                  6
	  Left-handed omega                  7
	  Left-handed gamma                  8
	  27 ribbon/helix                    9
	  Polyproline                       10
"""

class Helix():
	def __init__(self,Protein,pdbstr):
		self.pro=Protein
		self.ini=int(pdbstr[21:25])
		self.inic=pdbstr[19]
		self.end=int(pdbstr[33:37])
		self.endc=pdbstr[31]
		self.type=int(pdbstr[38:40])
	def __str__(self):
		return "Helix"+str(len(self))+" "+self.inic+'-'+str(self.ini)+"-"+self.sequence()+'-'+str(self.end)
	def __len__(self):
		if (self.end-self.ini+1)<0:
			return 0
		return self.end-self.ini+1
	def seqlen(self):
		return self.end-self.ini+1
	def sequence(self):
		return self.pro[0][self.inic].sequence(self.ini,self.end)


'''
Sense of strand with respect to previous strand in the sheet. 
0 if first strand, 
1 if parallel,
-1 if anti-parallel.
'''
class Strand():
	def __init__(self,Protein,pdbstr):
		self.pro=Protein
		self.ini=int(pdbstr[22:26])
		self.inic=pdbstr[21]
		self.end=int(pdbstr[33:37])
		self.endc=pdbstr[32]
		try:
			self.type=int(pdbstr[38:40])
		except:
			self.type=None
	def __str__(self):
		return "Strand"+str(len(self))+" "+self.inic+str(self.ini)+"-"+self.endc+str(self.end)
	def __len__(self):
		if (self.end-self.ini+1)<0:
			return 0
		return self.end-self.ini+1

	def seqlen(self):
		return self.end-self.ini+1
	def sequence(self):
		return self.pro[0][self.inic].sequence(self.ini,self.end)

class Sheet():
	def __init__(self,Protein,pdblist):
		self.pro=Protein
		self.strands=pdblist
		self.link=[]
		for i in range(len(self.strands)):
			if i==0:
				self.strands[i]=Strand(self.pro,self.strands[i])
			else:
				try:
					self.link.append(((self.strands[i][64],int(self.strands[i][65:69]),self.strands[i][56:60].replace(' ','')),(self.strands[i][49],int(self.strands[i][50:54]),self.strands[i][41:45].replace(' ',''))))
				except:
					self.link=None
				self.strands[i]=Strand(self.pro,self.strands[i])

	def __str__(self):
		tem=''
		temlist=[]
		temnum=len(self.strands)-1
		try:
			for i in range(temnum+1):
				if i==0:
					temlist.append([self.strands[i].type,None,self.link[i][0][1],self.strands[i].inic,self.strands[i].ini,self.pro[0][self.strands[i].inic].sequence(self.strands[i].ini,self.strands[i].end)])
				elif i==temnum:
					temlist.append([self.strands[i].type,self.link[i-1][1][1],None,self.strands[i].inic,self.strands[i].ini,self.pro[0][self.strands[i].inic].sequence(self.strands[i].ini,self.strands[i].end)])
				else:
					temlist.append([self.strands[i].type,self.link[i-1][1][1],self.link[i][0][1],self.strands[i].inic,self.strands[i].ini,self.pro[0][self.strands[i].inic].sequence(self.strands[i].ini,self.strands[i].end)])
			for i in range(temnum+1):
				if i==0:
					temlist[i][0]='>'
				else:
					if temlist[i][0]==1:
						temlist[i][0]=temlist[i-1][0]
					else:
						if temlist[i-1][0]=='>':
							temlist[i][0]='<'
						else:
							temlist[i][0]='>'
			for i in range(temnum+1):
				if i==0:
					temlist[i].append(str(temlist[i][4])+temlist[i][3]+temlist[i][0])
					temlist[i].append(None)
					temlist[i].append(len(temlist[i][6])+temlist[i][2]-temlist[i][4])
					temlist[i][6]=temlist[i][6]+temlist[i][5]
				elif i==temnum:
					if temlist[i][0]=='>':
						temlist[i].append(str(temlist[i][4])+temlist[i][3]+temlist[i][0])
						temlist[i].append(len(temlist[i][6])+temlist[i][1]-temlist[i][4])
						temlist[i].append(None)
						temlist[i][6]=temlist[i][6]+temlist[i][5]
					else:
						temlist[i].append(temlist[i][0]+str(temlist[i][4])+temlist[i][3])
						temlist[i].append(len(temlist[i][6])+temlist[i][1]-temlist[i][4])
						temlist[i].append(None)
						temlist[i][6]=temlist[i][5][::-1]+temlist[i][6]
						temlist[i][7]=len(temlist[i][6])-temlist[i][7]-1
					gap=temlist[i-1][8]-temlist[i][7]
					if gap>0:
						temlist[i][6]=' '*gap+temlist[i][6]
						temlist[i][7]+=gap
					else:
						gap=-gap
						for j in range(i):
							temlist[j][6]=' '*gap+temlist[j][6]
				else:
					if temlist[i][0]=='>':
						temlist[i].append(str(temlist[i][4])+temlist[i][3]+temlist[i][0])
						temlist[i].append(len(temlist[i][6])+temlist[i][1]-temlist[i][4])
						temlist[i].append(len(temlist[i][6])+temlist[i][2]-temlist[i][4])
						temlist[i][6]=temlist[i][6]+temlist[i][5]
					else:
						temlist[i].append(temlist[i][0]+str(temlist[i][4])+temlist[i][3])
						temlist[i].append(len(temlist[i][6])+temlist[i][1]-temlist[i][4])
						temlist[i].append(len(temlist[i][6])+temlist[i][2]-temlist[i][4])
						temlist[i][6]=temlist[i][5][::-1]+temlist[i][6]
						temlist[i][7]=len(temlist[i][6])-temlist[i][7]-1
						temlist[i][8]=len(temlist[i][6])-temlist[i][8]-1
					gap=temlist[i-1][8]-temlist[i][7]
					if gap>0:
						temlist[i][6]=' '*gap+temlist[i][6]
						temlist[i][7]+=gap
						temlist[i][8]+=gap
					else:
						gap=-gap
						for j in range(i):
							temlist[j][6]=' '*gap+temlist[j][6]
			temlen=len(temlist)-1
			for i in range(temlen+1):
				if i==temlen:
					tem=tem+temlist[i][6]
				else:
					tem=tem+temlist[i][6]+'\n'
			return tem
		except:
			return None
		

	def __len__(self):
		return len(self.strands)

	def __getitem__(self, key):
		return self.strands[key]










#========================================================================================================================
#=========================================================||==||=========================================================
#=========================================================||||||=========================================================
#=========================================================||||||=========================================================
#========================================================================================================================
#==============================================Main classes describing a protien=========================================

#========================================================================================================================
#=====================================================A Uniform Protein =================================================
#========================================================================================================================
class Protein():
	def __init__(self,pdbid=None,**kargs):
		#Prepare file for processing
		if pdbid!=None:#It's a pdb ID, download it from the website.
			url='https://files.rcsb.org/download/'+pdbid+'.pdb'
			with request.urlopen(url) as f:
				if f.status== 200:
					f=f.read().decode()
				else:
					raise Exception("Failed to Download"+pdbid+'.pdb. Error '+f.status+' '+f.reason)
			try:
				self.name=kargs['name']
			except:
				self.name=pdbid
		else:#A given file
			try:
				f=kargs['file']
				try:
					self.name=kargs['name']
				except:
					self.name=None
					print('[Warning]Can not find the name of this protein, which can given by the argument: name=[the name of the protein]')
			except:
				raise Exception('pdb ID should be given or pass a string of pdb file with the argument: file=[the given string]')

		#Save the pdbfile
		try:
			downloadpath=kargs['path']
		except:
			pass
		else:
			fso = open(downloadpath, 'w')
			fso.write(f)
			fso.close()

		self.lines=f.split("\n")
		self.models=[]
		self.helixes=[]
		self.sheets=[]

		#==================Atoms Building======================
		#preprocess: chunks incision
		self._modelincision()
		del self.lines
		self._chainincision()
		self._residuesincision()
		self._atombuild()
		#=======================Secondary Structure Building=================
		self._ssbuild()



	def _modelincision(self):
		#models incision and helixes build
		modelendlist=[]
		for i in range(len(self.lines)):
			if self.lines[i].find('HELIX')==0:
				self.helixes.append(Helix(self,self.lines[i]))
			elif self.lines[i].find('SHEET')==0:
				self.sheets.append(self.lines[i])
			elif self.lines[i].find('MODEL')==0:
				self.models.append(i)
			elif self.lines[i].find('ENDMDL')==0:
				modelendlist.append(i)
		if len(self.models)==0:
			self.models.append(self.lines)
		else:
			for i in range(len(self.models)):
				self.models[i]=self.lines[self.models[i]+1:modelendlist[i]]

	def _chainincision(self):
		#chains incision
		for i in range(len(self.models)):
			temlist=[]
			for j in range(len(self.models[i])):
				if self.models[i][j].find('TER')==0:
					temlist.append(j)
			temnum=len(temlist)-1
			if temnum!= -1:
				temlist.append(self.models[i][temlist[-1]:])#nonstandard list is at the last.
				for k in range(temnum+1):
					j=temnum-k#Take segments form the back of the file
					if j==0:
						temlist[j]=self.models[i][0:temlist[j]]
					else:
						temlist[j]=self.models[i][temlist[j-1]:temlist[j]]
				self.models[i]=temlist
			else:
				self.models[i]=[self.models[i]]


	def _residuesincision(self):
	#residues incision
			for i in range(len(self.models)):
				for j in range(len(self.models[i])):
					chaintem=[]
					conuter=0
					residuestem=[]
					tematomlist=[]
					for k in self.models[i][j]:
						if k.find('ATOM')==0:
							tematomlist.append(k)
						elif k.find('HETATM')==0:
							if k[17:20]=='MSE':#replace MSE with MET
								temline=k.replace('MSE','MET')
								temline=temline.replace('HETATM','ATOM  ')
								if temline[12:14]=='SE':
									temline=temline.replace('SE',' S')
									temline=temline.replace('S   MET','SD  MET')
								tematomlist.append(temline)
							else:
								tematomlist.append(k)
					self.models[i][j]=tematomlist
					if len(self.models[i][j])!=0:
						counter=0
						residuestem=[]
						for k in range(len(self.models[i][j])):
							if k==0:
								counter=self.models[i][j][k][22:26]
								residuestem.append(self.models[i][j][k])
							else:
								if self.models[i][j][k][22:26]==counter:
									residuestem.append(self.models[i][j][k])
								else:
									chaintem.append((counter,residuestem[:]))
									counter=self.models[i][j][k][22:26]
									residuestem=[]
									residuestem.append(self.models[i][j][k])
						chaintem.append((counter,residuestem[:]))
						self.models[i][j]=chaintem
					else:
						self.models[i][j]=[]

	def _atombuild(self):
		#Build!
		for m in range(len(self.models)):
			clist=[]
			nstd=self.models[m].pop()#put the nonstandard aside, build the standard chain first.
			for c in self.models[m]:
				cname=c[0][1][0][21]
				rlist=[]
				for r in c:
					rname=r[1][0][17:20].replace(' ','')
					rnum=int(r[1][0][22:26])
					for a in range(len(r[1])):
						r[1][a]=Atom(r[1][a][12:16].replace(' ',''),(float(r[1][a][30:38]),float(r[1][a][38:46]),float(r[1][a][46:54])),r[1][a][76:78].replace(' ',''))
					rlist.append(Residue(rname,rnum,r[1]))
				clist.append(Chain(cname,rlist,[]))


			cnamelist=[]
			for c in clist:
				cnamelist.append([c.name,[]])
			for r in nstd:
				rname=r[1][0][17:20].replace(' ','')
				rnum=int(r[1][0][22:26])
				rchain=r[1][0][21]
				for a in range(len(r[1])):
					r[1][a]=Atom(r[1][a][12:16].replace(' ',''),(float(r[1][a][30:38]),float(r[1][a][38:46]),float(r[1][a][46:54])),r[1][a][76:78].replace(' ',''))
				for c in cnamelist:
					if c[0]==rchain:
						c[1].append(Residue(rname,rnum,r[1]))
			for c in range(len(cnamelist)):
				clist[c].nonstandard=cnamelist[c][1]

			#Decide whether the chain is a peptide, DNA or RNA
			mclist=[]
			mdlist=[]
			mrlist=[]
			for c in clist:
				counterres=0
				counterdna=0
				counterrna=0
				for r in c:
					try:
						resname.index(r.name)
						counterres+=1
					except:
						try:
							dnaname.index(r.name)
							counterdna+=1
						except:
							try:
								rnaname.index(r.name)
								counterrna+=1
							except:
								pass
				if max(counterres,counterdna,counterrna)==counterres:
					mclist.append(c)
				elif max(counterres,counterdna,counterrna)==counterdna:
					mdlist.append(c)
				elif max(counterres,counterdna,counterrna)==counterrna:
					mrlist.append(c)
			self.models[m]=Model(mclist,mdlist,mrlist)

	def _ssbuild(self):
		#Helixes processing have been done in preprocessing
		#Sheets groups incision
		temlastlist=[]
		temsheet=''
		if len(self.sheets)!=0:
			for i in range(len(self.sheets)):
				if i==0:
					temsheet=self.sheets[i][11:14]
					temlastlist.append(i)
				else:
					if temsheet!=self.sheets[i][11:14]:
						temlastlist.append(i)
						temsheet=self.sheets[i][11:14]
			temnum=len(temlastlist)-1
			for i in range(temnum+1):
				if i==temnum:
					temlastlist[i]=self.sheets[temlastlist[i]:]
				else:
					temlastlist[i]=self.sheets[temlastlist[i]:temlastlist[i+1]]
			self.sheets=temlastlist
			for i in range(temnum+1):
				self.sheets[i]=Sheet(self,self.sheets[i])


	def __getitem__(self, key):
		if isinstance(key,int):
			return self.models[key]
		elif isinstance(key,slice):
			return self.models[key]
		else:
			raise KeyError("Expecting an intege but a "+str(type(key))+"is given")
	def __setitem__(self, key, value):
		if isinstance(key,int):
			self.models[key]=value
		elif isinstance(key,slice):
			self.models[key]=value
		else:
			raise KeyError("Expecting an intege but a "+str(type(key))+"is given")

	def __str__(self):
		return self.name
	def __len__(self):
		return len(self.models)
	def seqlen(self):
		return self[0].seqlen()
	def __iter__(self):
		return iter(self.models)

	def getdetail(self):
		temstr='['+self.name+']\n'
		for s in range(len(self.sheets)):
			temstr=temstr+'Sheet '+str(s)+':\n'+str(self.sheets[s])+'\n'
		for h in self.helixes:
			temstr=temstr+str(h)+'\n'
		for m in range(len(self)):
			temstr=temstr+'Model '+str(m)+':\n'
			for c in self[m]:
				temstr=temstr+'	'+str(c)+'\n'
				temstr=temstr+'	nonstandard'+str(c.counter('nonstandard'))+'\n'
			for c in self[m].dna:
				temstr=temstr+'	DNA-'+str(c)+'\n'
				temstr=temstr+'	nonstandard'+str(c.counter('nonstandard'))+'\n'
			for c in self[m].rna:
				temstr=temstr+'	RNA-'+str(c)+'\n'
				temstr=temstr+'	nonstandard'+str(c.counter('nonstandard'))+'\n'
		return temstr

	def copy(self,newname=None, selectmodel=None, selectchian=None, selectresidue=None):
		tem=copy.deepcopy(self)
		if newname!=None:
			tem.name=newname
		if selectmodel!=None:
			try:
				temobj=selectmodel[0]
			except:
				tem.models=[tem[selectmodel]]
			else:
				temlist=[]
				for i in selectmodel:
					temlist.append(tem[i])
				tem.models=temlist
		if selectchian!=None:
			print('[warning]Secondary structures will not update')
			try:
				temobj=selectchian[0]
			except:
				for m in tem:
					m.chains=[m[selectchian]]
			else:
				for m in tem:
					temlist=[]
					for i in selectchian:
						temlist.append(m[i])
					m.chains=temlist
		if selectresidue!=None:
			print('[warning]Secondary structures will not update')
			try:
				temobj=selectresidue[0]
			except:
				for m in tem:
					for c in m:
						c.residues=[c[selectresidue]]
			else:
				for m in tem:
					for c in m:
						temlist=[]
						for i in selectresidue:
							temlist.append(c[i])
						c.residues=temlist
		return tem


	def exportfasta(self,path=None,selectmodel=0, selectchian=None):
		if path==None:
			path=os.getcwd()+os.sep+self.name+'.fasta'
		temstr=''
		if selectchian==None:
			for i in self[selectmodel]:
				newline='>'+self.name+'_'+i.name+'\n'+i.seq+'\n'
				temstr=temstr+newline
			temstr=temstr[:-1]
		else:
			for i in selectchian:
				temchain=self[selectmodel][i]
				newline='>'+self.name+'_'+temchain.name+'\n'+temchain.seq+'\n'
				temstr=temstr+newline
			temstr=temstr[:-1]

		with open(path,'w') as f:
			f.write(temstr)

				



	def exportpdb(self,path=None):
		if path==None:
			if self.name==None:
				exist=True
				index=1
				path=os.getcwd()+os.sep+'export'+str(index)+'.pdb'
				while os.path.isfile(path)==True:
					index+=1
					path=os.getcwd()+os.sep+'export'+str(index)+'.pdb'
			else:
				path=os.getcwd()+os.sep+self.name+'.pdb'
		with open(path,'a') as f:
			if len(self)==1:
				counter=1
				for c in self[0]:
					for r in c:
						for a in r:
							if len(a.name)<=3:
								f.write('ATOM  %5d  %-3s %3s %1s%4d    %8.3f%8.3f%8.3f                      %2s  \n'% (counter, a.name, r.name, c.name, r.num, a.pos[0], a.pos[1], a.pos[2], a.ele))
							else:
								f.write('ATOM  %5d %4s %3s %1s%4d    %8.3f%8.3f%8.3f                      %2s  \n'% (counter, a.name, r.name, c.name, r.num, a.pos[0], a.pos[1], a.pos[2], a.ele))
							counter+=1
					f.write('TER   %5d      %3s %1s% 4d                                                      \n'% (counter, r.name, c.name, r.num))
				f.write('END                                                                             ')
			else:
				for m in self:
					f.write('MODEL     % 4d                                                                  \n')
					counter=1
					for c in m:
						for r in c:
							for a in r:
								if len(a.name)<=3:
									f.write('ATOM  %5d  %-3s %3s %1s% 4d    %8.3f%8.3f%8.3f                      %2s  \n'% (counter, a.name, r.name, c.name, r.num, a.pos[0], a.pos[1], a.pos[2], a.ele))
								else:
									f.write('ATOM  %5d %4s %3s %1s% 4d    %8.3f%8.3f%8.3f                      %2s  \n'% (counter, a.name, r.name, c.name, r.num, a.pos[0], a.pos[1], a.pos[2], a.ele))
								counter+=1
						f.write('TER   %5d      %3s %1s%4d                                                      \n'% (counter, r.name, c.name, r.num))
					f.write('ENDMDL                                                                          \n')
				f.write('END                                                                             \n')

	#Two ends of the insert will align to the residues 'beg' and 'end' and then be removed.
	def couple(self,chain,beg,end,insert, name=None, score=False, debug=False):
		if name==None:
			tem=self.copy(newname=self.name+'ins',selectmodel=0)
		else:
			tem=self.copy(newname=name,selectmodel=0)
		newchain=tem[0][chain]
		begr=newchain[beg]
		endr=newchain[end]
		listA=newchain[:beg+1]
		listB=copy.deepcopy(insert)
		listC=newchain[end:]
		#renumber
		counter=beg
		for i in listB:
			i.num=counter
			counter+=1
		counter=counter-1-end
		for i in listC:
			i.num=i.num+counter


		#align insert to target
		p1=begr['CA'].pos
		p2=begr['C'].pos
		p3=endr['CA'].pos
		p4=endr['N'].pos

		q1=listB[0]['CA'].pos
		q2=listB[0]['C'].pos
		q3=listB[-1]['CA'].pos
		q4=listB[-1]['N'].pos

		ccp=(p1+p2+p3+p4)/4
		ccq=(q1+q2+q3+q4)/4
		cp24=(p2+p4)/2
		cq24=(q2+q4)/2
		mat=(cq24-ccq).rot_matrix(cp24-ccp)
		for i in listB:
			for j in i:
				j.pos=mat*(j.pos-ccq)+ccp
		q1=listB[0]['CA'].pos
		q2=listB[0]['C'].pos
		q3=listB[-1]['CA'].pos
		q4=listB[-1]['N'].pos
		ccq=(q1+q2+q3+q4)/4
		cq24=(q2+q4)/2
		cp34=(p3+p4)/2
		cq34=(q3+q4)/2
		cqplane=cdn.Plane((cq24-ccq,ccq))
		projcp34=cp34+cqplane
		projcq34=cq34+cqplane
		vp=projcp34-ccp
		vq=projcq34-ccq
		cosa=vp*vq/abs(vp)/abs(vq)
		rotafunc=cdn.rotation(ccq,ccq-cq24,cosa)

		for i in listB:
			for j in i:
				j.pos=rotafunc(j.pos)

		q1=listB[0]['CA'].pos
		q2=listB[0]['C'].pos
		q3=listB[-1]['CA'].pos
		q4=listB[-1]['N'].pos

		ascore=((p1-q1)**2)+((p2-q2)**2)+((p3-q3)**2)+((p4-q4)**2)
		if debug==True:
			print(ascore)
			#plot.pointviewer([[p1,q1],[p2,q2],[p3,q3],[p4,q4]])

		listBcopy=copy.deepcopy(listB)
		temascore=1000000
		temascorepre=10000000
		while temascore<temascorepre:
			q1=listBcopy[0]['CA'].pos
			q2=listBcopy[0]['C'].pos
			q3=listBcopy[-1]['CA'].pos
			q4=listBcopy[-1]['N'].pos
			ccq=(q1+q2+q3+q4)/4


			d1=(p1-q1)
			d3=(p3-q3)
			d=(d1-d3)/6
			t=q1+d
			m=(q1-ccq).rot_matrix(t-ccp)
			for i in listBcopy:
				for j in i:
					j.pos=(m*(j.pos-ccq))+ccp

			q1=listBcopy[0]['CA'].pos
			q2=listBcopy[0]['C'].pos
			q3=listBcopy[-1]['CA'].pos
			q4=listBcopy[-1]['N'].pos
			ccq=(q1+q2+q3+q4)/4

			d2=(p2-q2)
			d4=(p4-q4)
			d=(d2-d4)/6
			t=q2+d
			m=(q2-ccq).rot_matrix(t-ccp)
			for i in listBcopy:
				for j in i:
					j.pos=(m*(j.pos-ccq))+ccp


			
			temascorepre=temascore
			temascore=((p1-q1)**2)+((p2-q2)**2)+((p3-q3)**2)+((p4-q4)**2)

			if debug==True:
				print(temascore)
				#plot.pointviewer([[p1,q1],[p2,q2],[p3,q3],[p4,q4]])

		if temascore<ascore:
			ascore=temascore
			listB=listBcopy


		#build a new chain
		if debug==True:
			debugP=copy.deepcopy(tem)
			temlistA=listA[:]
			listA.extend(listC)
			newchain.residues=listA
			debugP[0][chain]=newchain
			debugP[0].chains.append(Chain('W',listB[:],[]))
			debugP.exportpdb(os.getcwd()+os.sep+debugP.name+'_debug.pdb')

		listB=listB[1:-1]
		listA.extend(listB)
		listA.extend(listC)
		newchain.residues=listA
		tem[0][chain]=newchain
		
		if score==True:
			with open(os.getcwd()+os.sep+'couple_scoring','a') as f:
				f.write(tem.name+' '+str(ascore)+'\n')
		elif isinstance(score,str):
			with open(score,'a') as f:
				f.write(tem.name+' '+str(ascore))
		return tem









#========================================================================================================================
#=================================================A Protein with screen tasks============================================
#========================================================================================================================


#A class for screening
class ProteinS(Protein):
	def __init__(self,pdbid=None,**kargs):
		debug=kargs.get('debug',False)
		if debug==True:
			print('#### Debug Mode Start')
		if pdbid!=None:#It's a pdb ID, download it from the website.
			url='https://files.rcsb.org/download/'+pdbid+'.pdb'
			with request.urlopen(url) as f:
				if f.status== 200:
					f=f.read().decode()
				else:
					raise Exception("Failed to Download"+pdbid+'.pdb. Error '+f.status+' '+f.reason)
			try:
				self.name=kargs['name']
			except:
				self.name=pdbid
			if debug==True:
				print('#### Start processing '+pdbid+' - '+self.name)
		else:
			try:
				f=kargs['file']
				try:
					self.name=kargs['name']
				except:
					self.name=None
					print('[Warning]Can not find the name of this protein, which can given by the argument: name=[the name of the protein]')
			except:
				raise Exception('pdb ID should be given or pass a string of pdb file with the argument: file=[the given string]')
			if debug==True:
				print('#### Start processing '+self.name)
		self.J=True
		self.lines=f.split("\n")
		self.models=[]
		self.helixes=[]
		self.sheets=[]
		self.score=None
		#===================Preprocess Conditions=====================
		if debug==True:
			print('#### Preprocess Conditions')
		try:
			conditions=kargs['precon']
		except:
			pass
		else:
			try:
				temcon=conditions[0]
			except:
				self.J=conditions(self,*(kargs.get('preconargs',())),**(kargs.get('preconkargs',{})))
			else:
				conlen=len(conditions)
				for i in range(conlen):
					if conditions[i](self,*(kargs.get('preconargs',[()]*conlen)[i]),**(kargs.get('preconkargs',[{}]*conlen)[i]))==False:
						self.J=False
						break
		#===================Preprocess: Chunks Incision=====================
		#preprocess: chunks incision
		if self.J==True:
			if debug==True:
				print('#### Preprocessing')
			#models incision
			modelendlist=[]
			for i in range(len(self.lines)):
				if self.lines[i].find('HELIX')==0:
					self.helixes.append(Helix(self,self.lines[i]))
				elif self.lines[i].find('SHEET')==0:
					self.sheets.append(self.lines[i])
				elif self.lines[i].find('MODEL')==0:
					self.models.append(i)
				elif self.lines[i].find('ENDMDL')==0:
					modelendlist.append(i)
				#condition for lines
				try:
					conditions=kargs['linetrue']
				except:
					pass
				else:
					try:
						temcon=conditions[0]#A list or not?
					except:
						self.J=(self.lines[i].find(conditions)!=-1)
					else:#a list
						for j in conditions:
							if self.lines[i].find(j)==-1:
								self.J=False
								break
				if self.J==False:
					break

				try:
					conditions=kargs['linefalse']
				except:
					pass
				else:
					try:
						temcon=conditions[0]#A list or not?
					except:
						self.J=(self.lines[i].find(conditions)==-1)
					else:#a list
						for j in conditions:
							if self.lines[i].find(j)!=-1:
								self.J=False
								break
				if self.J==False:
					break


				try:
					conditions=kargs['linecon']
				except:
					pass
				else:
					try:
						temcon=conditions[0]#A list or not?
					except:#just one function
						self.J=conditions(self,self.lines[i],*(kargs.get('lineconargs',())),**(kargs.get('lineconkargs',{})))
					else:#a list
						conlen=len(conditions)
						for j in range(conlen):
							if conditions[j](self,self.lines[i],*(kargs.get('lineconargs',[()]*conlen)[j]),**(kargs.get('lineconkargs',[{}]*conlen)[j]))==False:
								self.J=False
								break
				if self.J==False:
					break

			if self.J==True:
				if len(self.models)==0:
					self.models.append(self.lines)
				else:
					for i in range(len(self.models)):
						self.models[i]=self.lines[self.models[i]+1:modelendlist[i]]

				del self.lines
				self._chainincision()
				self._residuesincision()
				#==================Atoms Building Conditions======================
				if debug==True:
					print('#### Atoms Building Conditions')
				try:
					conditions=kargs['atmcon']
				except:
					pass
				else:
					try:
						temcon=conditions[0]
					except:
						self.J=conditions(self,*(kargs.get('atmconargs',())),**(kargs.get('atmconkargs',{})))
					else:
						conlen=len(conditions)
						for i in range(conlen):
							if conditions[i](self,*(kargs.get('atmconargs',[()]*conlen)[i]),**(kargs.get('atmconkargs',[{}]*conlen)[i]))==False:
								self.J=False
								break
				#==================Atoms Building======================
				if self.J==True:
					if debug==True:
						print('#### Building Atoms')
					self._atombuild()
					#=======================Secondary Structure Building=================
					self._ssbuild()
					#==================Scoring======================	
					if debug==True:
						print('#### Scoring')
					try:
						scoring=kargs['score']
					except:
						pass
					else:
						try:
							temcon=scoring[0]
						except:
							self.J=scoring(self,*(kargs.get('scoreargs',())),**(kargs.get('scorekargs',{})))
						else:
							conlen=len(scoring)
							for i in range(conlen):
								if scoring[i](self,*(kargs.get('scoreargs',[()]*conlen)[i]),**(kargs.get('scorekargs',[{}]*conlen)[i]))==False:
									self.J=False
									break

					#==================Download======================	
					if self.J==True:
						if debug==True:
							print('#### Downloading')
						try:
							downloadpath=kargs['path']
						except:
							pass
						else:
							fso = open(downloadpath, 'w')
							fso.write(f)
							fso.close()
					else:
						if debug==True:
							print('#### Conditions are not met, the downloading is aborted')
				else:
					if debug==True:
						print('#### Conditions are not met, the atoms building is aborted')
			else:
				if debug==True:
					print('#### Conditions are not met, the preprocessing is breaked off')
		else:
			if debug==True:
				print('#### Conditions are not met, the preprocessing is aborted')








#========================================================================================================================
#=====================================================||||||||||||||=====================================================
#=====================================================||==========||=====================================================
#=====================================================||=================================================================
#=====================================================||||||||||||||=====================================================
#=================================================================||=====================================================
#=====================================================||==========||=====================================================
#=====================================================||||||||||||||=====================================================
#========================================================================================================================
#=================================================Functions for scoring==================================================



#========================================================================================================================
#=========================================================||||===========================================================
#=========================================================||||===========================================================
#=========================================================||=============================================================
#========================================================================================================================
#================================================Preprocessing Conditions================================================






#==[Warning] Preprocessing Conditions below might be slow, use arguments 'linetrue' and 'linefalse' in ProteinS instead.=
#==[Warning] Preprocessing Conditions below might be slow, use arguments 'linetrue' and 'linefalse' in ProteinS instead.=
#==[Warning] Preprocessing Conditions below might be slow, use arguments 'linetrue' and 'linefalse' in ProteinS instead.=
#Return whether the protein is expressed by the specific systems, e.g. 'ESCHERICHIA COLI' or ['ESCHERICHIA COLI','HOMO SAPIENS']
def screxp(protein,expressionsystem):
	print("[Warning] function 'screxp' might be slow, use argument 'linetrue' in ProteinS instead.")
	if type(expressionsystem)==list:
		for i in range(len(protein.lines)):
			for j in expressionsystem:
				if protein.lines[i].find('EXPRESSION_SYSTEM: '+j+';')!=-1:
					return True
		return False
	else:
		for i in range(len(protein.lines)):
			if protein.lines[i].find('EXPRESSION_SYSTEM: '+expressionsystem+';')!=-1:
				return True
		return False


#Return whether the protein is not expressed by the specific systems, e.g. 'ESCHERICHIA COLI' or ['ESCHERICHIA COLI','HOMO SAPIENS']
def scrnotexp(protein,expressionsystem):
	print("[Warning] function 'scrnotexp' might be slow, use argument 'linefalse' in ProteinS instead.")
	if type(expressionsystem)==list:
		for i in range(len(protein.lines)):
			for j in expressionsystem:
				if protein.lines[i].find('EXPRESSION_SYSTEM: '+j+';')!=-1:
					return False
		return True
	else:
		for i in range(len(protein.lines)):
			if protein.lines[i].find('EXPRESSION_SYSTEM: '+expressionsystem+';')!=-1:
				return False
		return True


#Return whether the protein comes from the specific organism, e.g. 'ESCHERICHIA COLI' or ['ESCHERICHIA COLI','HOMO SAPIENS']
def scrorg(protein,expressionsystem):
	print("[Warning] function 'scrorg' might be slow, use argument 'linetrue' in ProteinS instead.")
	if type(expressionsystem)==list:
		for i in range(len(protein.lines)):
			for j in expressionsystem:
				if protein.lines[i].find('ORGANISM_SCIENTIFIC: '+j+';')!=-1:
					return True
		return False
	else:
		for i in range(len(protein.lines)):
			if protein.lines[i].find('ORGANISM_SCIENTIFIC: '+expressionsystem+';')!=-1:
				return True
		return False


#Return whether the protein comes from organisms except the specific organism, e.g. 'ESCHERICHIA COLI' or ['ESCHERICHIA COLI','PYROCOCCUS HORIKOSHII']
def scrnotorg(protein,expressionsystem):
	print("[Warning] function 'scrnotorg' might be slow, use argument 'linefalse' in ProteinS instead.")
	if type(expressionsystem)==list:
		for i in range(len(protein.lines)):
			for j in expressionsystem:
				if protein.lines[i].find('ORGANISM_SCIENTIFIC: '+j+';')!=-1:
					return False
		return True
	else:
		for i in range(len(protein.lines)):
			if protein.lines[i].find('ORGANISM_SCIENTIFIC: '+expressionsystem+';')!=-1:
				return False
		return True


#========================================================================================================================
#=========================================================||=============================================================
#=========================================================||=============================================================
#=========================================================||||||=========================================================
#========================================================================================================================
#================================================Lines Reading Conditions================================================

# Record the ORGANISM_SCIENTIFIC information
def recorg(protein, line):
	if line.find('ORGANISM_SCIENTIFIC: ')!=-1:
		protein.organism= line[line.find('ORGANISM_SCIENTIFIC: ')+21:line.find(';')]
	return True

# Record the EXPRESSION_SYSTEM information
def recexp(protein, line):
	if line.find('EXPRESSION_SYSTEM: ')!=-1:
		protein.expression= line[line.find('EXPRESSION_SYSTEM: ')+19:line.find(';')]	
	return True



#========================================================================================================================
#=========================================================||||||=========================================================
#=========================================================||||||=========================================================
#=========================================================||||||=========================================================
#========================================================================================================================
#=================================================Atoms Building Conditions==============================================



#Return whether the protein have a sheet/ sheets
def scrsheet(protein):
	if len(protein.sheets)==0:
		return False
	else:
		return True


#Return whether the protein is without any sheet
def scrnosheet(protein):
	if len(protein.sheets)==0:
		return True
	else:
		return False

#Return whether the protein have a helix/ helixes
def scrhelix(protein):
	if len(protein.helixes)==0:
		return False
	else:
		return True


#Return whether the protein is without any helix
def scrnohelix(protein):
	if len(protein.helixes)==0:
		return True
	else:
		return False


#========================================================================================================================
#===========================================================||||=========================================================
#===========================================================||===========================================================
#=========================================================||||===========================================================
#========================================================================================================================
#========================================================Scoring=========================================================

#score acorrding to the full length of the protein 
def scrfulllength(protein, scorefunction, threshold=None):
	protein.flscore=scorefunction(protein.seqlen())
	if threshold==None:
		return True
	else:
		if protein.flscore>threshold:
			return True
		else:
			return False

#score acorrding to the ratio of loops length to full length of the protein 
def scrloopratio(protein, scorefunction=lambda x:1-x, threshold=None):
	lenh=0
	for i in protein.helixes:
		lenh+=len(i)
	lens=0
	for i in protein.sheets:
		for j in i:
			lens+=len(j)
	lenf=protein.seqlen()
	lenl=lenf-lenh-lens
	protein.lrscore=scorefunction(lenl/lenf)
	if threshold==None:
		return True
	else:
		if protein.lrscore>threshold:
			return True
		else:
			return False

#score acorrding to the full length of the protein 
def scrsheetratio(protein, scorefunction=lambda x:x, threshold=None):
	lenh=0
	for i in protein.helixes:
		lenh+=len(i)
	lens=0
	for i in protein.sheets:
		for j in i:
			lens+=len(j)
	protein.srscore=scorefunction(lens/(lens+lenh))
	if threshold==None:
		return True
	else:
		if protein.srscore>threshold:
			return True
		else:
			return False


#score acorrding to the full length of the protein 
def scrhelixratio(protein, scorefunction=lambda x:x, threshold=None):
	lenh=0
	for i in protein.helixes:
		lenh+=len(i)
	lens=0
	for i in protein.sheets:
		for j in i:
			lens+=len(j)
	protein.hrscore=scorefunction(lenh/(lens+lenh))
	if threshold==None:
		return True
	else:
		if protein.hrscore>threshold:
			return True
		else:
			return False

#score acorrding to a position function. 
def scrposition(protein,positionfunction, scorefunction, threshold=None):
	protein.pscore=scorefunction(positionfunction(protein))
	if threshold==None:
		return True
	else:
		if protein.pscore>threshold:
			return True
		else:
			return False





#========================================================================================================================
#=====================================================||||||||||=========================================================
#=====================================================||========||=======================================================
#=====================================================||==========||=====================================================
#=====================================================||==========||=====================================================
#=====================================================||==========||=====================================================
#=====================================================||========||=======================================================
#=====================================================||||||||||=========================================================
#========================================================================================================================
#================================================Functions for database==================================================



def getwebinfo(pdbid):
	url='https://www.rcsb.org/structure/'+pdbid
	with request.urlopen(url) as f:
		if f.status== 200:
			f=f.read().decode()
	infodict={'pdbID':pdbid}


	start=f.find('carousel-footer')
	end=start

	temstart=f.find('Global Symmetry',start)
	if temstart!= -1:
		start=temstart+25
		end=f.find('&nbsp',start)
		gs=f[start:end].lstrip()
		infodict['Global Symmetry']=gs

	temstart=f.find('Global Stoichiometry',end)
	if temstart!= -1:
		start=temstart+30
		end=f.find('&nbsp',start)-2
		gs=f[start:end].lstrip()

		start=f.find('word-wrap:break-word',end)+23
		end=f.find('&nbsp',start)
		gs=f[start:end].lstrip()
		infodict['Global Stoichiometry Detail']=gs

	temstart=f.find('Total Structure Weight',end)
	if temstart!= -1:
		start=temstart+24
		end=f.find('&nbsp',start)
		gs=float(f[start:end])
		infodict['Total Structure Weight']=gs

	temstart=f.find('Atom Count',end)
	if temstart!= -1:
		start=temstart+12
		end=f.find('&nbsp',start)
		gs=float(f[start:end])
		infodict['Atom Count']=gs

	temstart=f.find('Residue Count',end)
	if temstart!= -1:
		start=temstart+15
		end=f.find('&nbsp',start)
		gs=int(f[start:end])
		infodict['Residue Count']=gs

	temstart=f.find('Unique protein chains',end,end+1000)
	if temstart!= -1:
		start=temstart
		end=f.find('</li>',start+23)
		gs=int(f[start+23:end])
		infodict['Unique protein chains']=gs

	temstart=f.find('Unique hybrid chains',end,end+1000)
	if temstart!= -1:
		start=temstart
		end=f.find('</li>',start+22)
		gs=int(f[start+22:end])
		infodict['Unique hybrid chains']=gs
	

	start=f.find('structureTitle',end)+16
	end=f.find('</span>',start)
	gs=f[start:end]
	infodict['Structure Title']=gs

	start=f.find('DOI:&nbsp',end)+20
	start=f.find('>',start)+1
	end=f.find('</a>',start)
	gs=f[start:end]
	infodict['DOI']=gs

	start=f.find('Classification:&nbsp',end)+32
	start=f.find('>',start)+1
	end=f.find('</a>',start)
	gs=f[start:end]
	infodict['Classification']=gs

	temstart=f.find('Organism(s):&nbsp',end)
	if temstart!= -1:
		start=temstart+32
		start=f.find('>',start)+1
		end=f.find('</a>',start)
		gs=f[start:end]
		infodict['Organism']=gs

	temstart=f.find('Expression System:&nbsp',end,end+500)
	if temstart!=-1:
		start=temstart+32
		start=f.find('>',start)+1
		end=f.find('</a>',start)
		gs=f[start:end]
		infodict['Expression System']=gs 

	temstart=f.find('Mutation(s):&nbsp',end,end+500)
	if temstart==-1:
		infodict['Mutation']=0
	else:
		start=temstart
		start=f.find('>',start)+1
		end=f.find('&nbsp',start)
		gs=f[start:end]
		infodict['Mutation']=gs


	start=f.find('Method:&nbsp',end)+15
	start=f.find('>',start)+1
	end=f.find('</li>',start)
	gs=f[start:end]
	infodict['Method']=gs 

	if infodict['Method']=='ELECTRON MICROSCOPY':
		start=f.find('Resolution:&nbsp',end)
		if start==-1:
			infodict['Resolution']=None
		else:
			start=f.find('>',start+17)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Resolution']=gs 

		start=f.find('Aggregation State:&nbsp',end)
		if start==-1:
			infodict['Aggregation State']=None
		else:
			start=f.find('>',start+25)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Aggregation State']=gs 

		start=f.find('Reconstruction Method:&nbsp',end)
		if start==-1:
			infodict['Reconstruction Method']=None
		else:
			start=f.find('>',start+28)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Reconstruction Method']=gs

	elif infodict['Method']=='X-RAY DIFFRACTION':
		start=f.find('Resolution:&nbsp',end)
		if start==-1:
			infodict['Resolution']=None
		else:
			start=f.find('>',start+17)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Resolution']=gs 

		start=f.find('R-Value Free:&nbsp',end)
		if start==-1:
			infodict['R-Value Free']=None
		else:
			start=f.find('>',start+20)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['R-Value Free']=gs 

		start=f.find('R-Value Work:&nbsp',end)
		if start==-1:
			infodict['R-Value Work']=None
		else:
			start=f.find('>',start+20)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['R-Value Work']=gs

	elif infodict['Method']=='SOLID-STATE NMR' or infodict['Method']=='SOLUTION NMR':
		start=f.find('Conformers Calculated:&nbsp',end)
		if start==-1:
			infodict['Conformers Calculated']=None
		else:
			start=f.find('>',start+27)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Conformers Calculated']=gs 

		start=f.find('Conformers Submitted:&nbsp',end)
		if start==-1:
			infodict['Conformers Submitted']=None
		else:
			start=f.find('>',start+20)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Conformers Submitted']=gs 

		start=f.find('Conformers Submitted:&nbsp',end)
		if start==-1:
			infodict['Conformers Submitted']=None
		else:
			start=f.find('>',start+20)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Conformers Submitted']=gs

		start=f.find('Selection Criteria:&nbsp',end)
		if start==-1:
			infodict['Selection Criteria']=None
		else:
			start=f.find('>',start+20)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Selection Criteria']=gs
	elif infodict['Method']=='NEUTRON DIFFRACTION':
		start=f.find('Resolution:&nbsp',end)
		if start==-1:
			infodict['Resolution']=None
		else:
			start=f.find('>',start+17)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Resolution']=gs 
	elif infodict['Method']=='ELECTRON CRYSTALLOGRAPHY':
		start=f.find('Aggregation State:&nbsp',end)
		if start==-1:
			infodict['Aggregation State']=None
		else:
			start=f.find('>',start+25)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Aggregation State']=gs 

		start=f.find('Reconstruction Method:&nbsp',end)
		if start==-1:
			infodict['Reconstruction Method']=None
		else:
			start=f.find('>',start+28)+1
			end=f.find('&nbsp',start)
			gs=f[start:end]
			infodict['Reconstruction Method']=gs

	url='https://www.rcsb.org/pdb/explore/macroMoleculeData.do?structureId='+pdbid
	with request.urlopen(url) as f:
		if f.status== 200:
			f=f.read().decode()
	firststart=f.find('id="collapsedHeader"')


	start=f.find('Domain Annotation: CATH',firststart)
	start=f.find('table-responsive',start)
	start=f.find('<tbody>',start)
	temstart=f.find('<tr',start,start+100)
	if temstart!=-1:# this is a real table
		temlist=[]
		while f.find('<tr',start,start+100)!= -1:
			start=f.find('<tr',start,start+100)
			temdict={}

			start=f.find('<td>',start)+4
			end=f.find('</td>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Chain']=gs

			start=f.find('<td>',end)+4
			end=f.find('</td>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Domain']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Class']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Architecture']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Topology']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Homology']=gs
			
			temlist.append(temdict)
			start=f.find('</tr',end)
		infodict['Domain Annotation: CATH']=temlist





	start=f.find('Gene Product Annotation',firststart)
	start=f.find('table-responsive',start)
	start=f.find('<tbody>',start)
	temstart=f.find('<tr',start,start+100)
	if temstart!=-1:# this is a real table
		temlist=[]
		while f.find('<tr',start,start+100)!= -1:
			start=f.find('<tr',start,start+100)
			temdict={}

			start=f.find('<td>',start)+4
			end=f.find('</td>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Chain']=gs

			start=f.find('<td>',end)+4
			end=f.find('</td>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Polymer']=gs


			tdstart=f.find('<td>',end)+4
			tdend=f.find('</td>',tdstart)
			start=f.find('<li>',tdstart,tdend)+4
			end=f.find('</li>',start,tdend)
			start=f.find('>',start,end)+1
			temend=f.find('<',start,end)
			if f.find('<li>',end,tdend)== -1:
				gs=f[start:temend].replace('\n','').lstrip().rstrip()
				if gs=='none':
					gs=None
				temdict['Molecular Function']=[gs]
			else:
				litemlist=[gs]
				while f.find('<li>',end,tdend)!= -1:
					start=f.find('<li>',end,tdend)+4
					end=f.find('</li>',start,tdend)
					start=f.find('>',start,end)+1
					temend=f.find('<',start,end)
					gs=f[start:temend].replace('\n','').lstrip().rstrip()
					litemlist.append(gs)
				temdict['Molecular Function']=litemlist

			tdstart=f.find('<td>',end)+4
			tdend=f.find('</td>',tdstart)
			start=f.find('<li>',tdstart,tdend)+4
			end=f.find('</li>',start,tdend)
			start=f.find('>',start,end)+1
			temend=f.find('<',start,end)
			if f.find('<li>',end,tdend)==-1:
				gs=f[start:temend].replace('\n','').lstrip().rstrip()
				if gs=='none':
					gs=None
				temdict['Biological Process']=[gs]
			else:
				litemlist=[gs]
				while f.find('<li>',end,tdend)!= -1:
					start=f.find('<li>',end,tdend)+4
					end=f.find('</li>',start,tdend)
					start=f.find('>',start,end)+1
					temend=f.find('<',start,end)
					gs=f[start:temend].replace('\n','').lstrip().rstrip()
					litemlist.append(gs)
				temdict['Biological Process']=litemlist
			
			tdstart=f.find('<td>',end)+4
			tdend=f.find('</td>',tdstart)
			start=f.find('<li>',tdstart,tdend)+4
			end=f.find('</li>',start,tdend)
			start=f.find('>',start,end)+1
			temend=f.find('<',start,end)
			if f.find('<li>',end,tdend)==-1:
				gs=f[start:temend].replace('\n','').lstrip().rstrip()
				if gs=='none':
					gs=None
				temdict['Cellular Component']=[gs]
			else:
				litemlist=[gs]
				while f.find('<li>',end,tdend)!= -1:
					start=f.find('<li>',end,tdend)+4
					end=f.find('</li>',start,tdend)
					start=f.find('>',start,end)+1
					temend=f.find('<',start,end)
					gs=f[start:temend].replace('\n','').lstrip().rstrip()
					litemlist.append(gs)
				temdict['Cellular Component']=litemlist
			
			temlist.append(temdict)
			start=f.find('</tr',end)
		infodict['Gene Product Annotation']=temlist





	start=f.find('Domain Annotation: SCOP Classification',firststart)
	start=f.find('table-responsive',start)
	start=f.find('<tbody>',start)
	temstart=f.find('<tr',start,start+100)
	if temstart!=-1:# this is a real table
		temlist=[]
		while f.find('<tr',start,start+100)!= -1:
			start=f.find('<tr',start,start+100)
			temdict={}

			start=f.find('<td>',start)+4
			end=f.find('</td>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Chain']=gs

			start=f.find('<td>',end)+4
			end=f.find('</td>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Domain Info']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Class']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Fold']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Superfamily']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Family']=gs

			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Domain']=gs
			
			start=f.find('href',end)+4
			start=f.find('>',start)+1
			end=f.find('</a>',start)
			gs=f[start:end].replace('\n','').lstrip().rstrip()
			temdict['Species']=gs

			temlist.append(temdict)
			start=f.find('</tr',end)
		infodict['Domain Annotation: SCOP Classification']=temlist

	return infodict


def getpdbinfo(pdbid):
	def scoring(Protein):
		infodict={'pdbID':pdbid}
		try:
			infodict['PDB organism']=Protein.organism
		except:
			pass
		try:
			infodict['PDB expression system']=Protein.expression
		except:
			pass

		#sheets infomation
		sheetlist=[]
		sheetlen=0
		sheetnum=len(Protein.sheets)
		infodict['Sheets count']=sheetnum
		for s in range(sheetnum):
			sheetdict={}
			sheetdict['Strand count']=len(Protein.sheets[s])
			try:
				sheetdict['Sheet structure']=str(Protein.sheets[s])
			except:
				sheetdict['Sheet structure']=None
			strandlist=[]
			for strand in Protein.sheets[s]:
				stranddict={}
				stranddict['Chain']=strand.inic
				stranddict['Begining']=strand.ini
				stranddict['End']=strand.end
				strandlen=len(strand)
				sheetlen+=strandlen
				stranddict['Length']=strandlen
				stranddict['Sequence']=strand.sequence()
				stranddict['Type']=strand.type
				strandlist.append(stranddict)
			sheetdict['Strands']=strandlist
			sheetlist.append(sheetdict)
		infodict['Sheets']=sheetlist
		infodict['Sheets structure length']=sheetlen

		#helixes infomation
		helixnum=len(Protein.helixes)
		helixeslen=0
		infodict['Helix count']=helixnum
		helixlist=[]
		for h in range(helixnum):
			helixdict={}
			helixdict['Chain']=Protein.helixes[h].inic
			helixdict['Begining']=Protein.helixes[h].ini
			helixdict['End']=Protein.helixes[h].end
			helixlen=len(Protein.helixes[h])
			helixeslen+=helixlen
			helixdict['Length']=helixlen
			helixdict['Sequence']=Protein.helixes[h].sequence()
			helixdict['Type']=Protein.helixes[h].type
			helixlist.append(helixdict)
		infodict['Helixes']=helixlist
		infodict['Helixes length']=helixeslen

		modelnum=len(Protein)
		infodict['Model count']=modelnum
		modellist=[]
		for m in range(modelnum):
			chainlist=[]
			DNAlist=[]
			RNAlist=[]
			chainnum=len(Protein[m])
			DNAnum=len(Protein[m].dna)
			RNAnum=len(Protein[m].rna)
			modeldict={'Chain count':chainnum,'DNA count':DNAnum, 'RNA count':RNAnum}
			chainlen=0
			dnalen=0
			rnalen=0
			counterlist=[]
			nonstandardlist=[]
			for c in Protein[m]:
				chaindict={}
				chaindict['Name']=c.name
				chaindict['Sequence']=c.seq
				counter=c.counter('residues')
				nonstandard=c.counter('nonstandard')
				counterlist.append(counter)
				nonstandardlist.append(nonstandard)
				chaindict['Residues']=counter
				chaindict['Nonstandard']=nonstandard
				length=c.seqlen()
				chaindict['Sequence length']=length
				chainlen+=length
				chainlist.append(chaindict)
			for c in Protein[m].dna:
				chaindict={}
				chaindict['Name']=c.name
				chaindict['Sequence']=c.seq
				counter=c.counter('residues')
				nonstandard=c.counter('nonstandard')
				counterlist.append(counter)
				nonstandardlist.append(nonstandard)
				chaindict['Residues']=counter
				chaindict['Nonstandard']=nonstandard
				length=c.seqlen()
				chaindict['Sequence length']=length
				dnalen+=length
				DNAlist.append(chaindict)
			for c in Protein[m].rna:
				chaindict={}
				chaindict['Name']=c.name
				chaindict['Sequence']=c.seq
				counter=c.counter('residues')
				nonstandard=c.counter('nonstandard')
				counterlist.append(counter)
				nonstandardlist.append(nonstandard)
				chaindict['Residues']=counter
				chaindict['Nonstandard']=nonstandard
				length=c.seqlen()
				chaindict['Sequence length']=length
				rnalen+=length
				RNAlist.append(chaindict)
			modeldict['Chains']=chainlist
			modeldict['DNAs']=DNAlist
			modeldict['RNAs']=RNAlist
			modeldict['Chains length']=chainlen
			modeldict['DNAs length']=dnalen
			modeldict['RNAs length']=rnalen
			modeldict['Residues count']=countermerge(counterlist)
			modeldict['Nonstandard count']=countermerge(nonstandardlist)
			modellist.append(modeldict)
		infodict['Models']=modellist
		temmodel=modellist[0]
		infodict['Chain count']=temmodel['Chain count']
		infodict['DNA count']=temmodel['DNA count']
		infodict['RNA count']=temmodel['RNA count']
		infodict['Protein length']=temmodel['Chains length']
		infodict['DNAs length']=temmodel['DNAs length']
		infodict['RNAs length']=temmodel['RNAs length']
		infodict['Residues count']=temmodel['Residues count']
		infodict['Nonstandard count']=temmodel['Nonstandard count']
		try:
			infodict['Helix ratio']=infodict['Helixes length']/(infodict['Helixes length']+infodict['Sheets structure length'])
		except:
			pass
		try:
			infodict['Sheet ratio']=infodict['Sheets structure length']/(infodict['Helixes length']+infodict['Sheets structure length'])
		except:
			pass
		try:
			infodict['Loop ratio']=1-((infodict['Helixes length']+infodict['Sheets structure length'])/infodict['Protein length'])
		except:
			pass
		Protein.infodict=infodict
		return True

	pro=ProteinS(pdbid,linecon=[recorg,recexp],score=scoring)

	return pro.infodict


def getcurlist():
	url = 'http://www.rcsb.org/pdb/rest/getCurrent'
	pdblist=None
	with request.urlopen(url) as f:
		if f.status== 200:
			pdblist=f.read().decode().split('\n')[2:-2]
		else:
			raise Exception('Failed to get list. Error '+f.status+' '+f.reason)
	for i in range(len(pdblist)):
		pdblist[i]=pdblist[i][20:24]
	return pdblist


def getinfo(pdbid):
	adict=getwebinfo(pdbid)
	bdict=getpdbinfo(pdbid)
	bdict.update(adict)
	return bdict



def dbuppdate(path=os.getcwd(),overwrite=False, pdblist=None,stopsignal=os.getcwd()+os.sep+'stop'):
	if pdblist==None:
		pdblist=getcurlist()

	failstr=''
	listlen=len(pdblist)
	firtwo='10'
	try:
		with open(path+os.sep+firtwo, 'rb') as f:
			tdict=pickle.load(f)
	except:
		tdict={}

	if overwrite==True:
		for i in range(listlen):
			getpdb=pdblist[i]
			if os.path.exists(stopsignal)==False:
				if getpdb[0:2]==firtwo:
					try:
						tdict[getpdb]=getinfo(getpdb)
						print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Done')
					except:
						failstr+=getpdb+'\n'
						print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Failed')
				else:
					with open(path+os.sep+firtwo, 'wb') as f:
						pickle.dump(tdict, f)
					firtwo=getpdb[0:2]
					try:
						with open(path+os.sep+firtwo, 'rb') as f:
							tdict=pickle.load(f)
					except:
						tdict={}
					try:
						tdict[getpdb]=getinfo(getpdb)
						print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Done')
					except:
						failstr+=getpdb+'\n'
						print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Failed')

			else:
				with open(path+os.sep+firtwo, 'wb') as f:
					pickle.dump(tdict, f)
				with open(path+os.sep+'failed', 'w') as f:
					f.write(failstr)
				with open(path+os.sep+'stopid', 'w') as f:
					f.write(getpdb+'-'+str(i))
				break

	else:
		for i in range(listlen):
			getpdb=pdblist[i]
			if os.path.exists(stopsignal)==False:
				if getpdb[0:2]==firtwo:
					if (getpdb in tdict)==False:
						try:
							tdict[getpdb]=getinfo(getpdb)
							print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Done')
						except:
							failstr+=getpdb+'\n'
							print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Failed')
					else:

						print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Skipped')
				else:
					with open(path+os.sep+firtwo, 'wb') as f:
						pickle.dump(tdict, f)
					firtwo=getpdb[0:2]
					try:
						with open(path+os.sep+firtwo, 'rb') as f:
							tdict=pickle.load(f)
					except:
						tdict={}
					if (getpdb in tdict)==False:
						try:
							tdict[getpdb]=getinfo(getpdb)
							print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Done')
						except:
							failstr+=getpdb+'\n'
							print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Failed')
					else:
						print(str(i)+'/'+str(listlen)+'-'+getpdb+'-Skipped')
			else:
				with open(path+os.sep+firtwo, 'wb') as f:
					pickle.dump(tdict, f)
				with open(path+os.sep+'failed', 'w') as f:
					f.write(failstr)
				with open(path+os.sep+'stopid', 'w') as f:
					f.write(getpdb+'-'+str(i))
				break





def countermerge(counterlist):
	merge={}
	for i in counterlist:
		for k,v in i.items():
			if k in merge:
				merge[k]=v+merge[k]
			else:
				merge[k]=v
	return merge