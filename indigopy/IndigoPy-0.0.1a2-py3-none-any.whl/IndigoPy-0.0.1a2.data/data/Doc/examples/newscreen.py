#!/usr/bin/python3
# -*- coding: UTF-8-*-
import IndigoPy.Protein.pdb as pdb
import IndigoPy.Math.coordinates as cdn
import IndigoPy.Math.Funcmaker as fmk
import numpy as np
import numpy.linalg
import os
import pypdb



def scoring(protein, scorefunction, thresholdfl, thresholdF, debug=False):
	protein.score=[]
	temscore=[]
	position=[]
	if len(protein.sheets)!=0:
		for i in protein.sheets:
			for j in range(len(i)):
				if i[j].type==-1:
					if i[j].inic==i[j-1].inic:
						if i[j].ini>i[j-1].end:
							if i[j].ini-i[j-1].end<15:
								if abs((i.link[j-1][1][1]-i[j].ini)-(i[j-1].end-i.link[j-1][0][1]))<2:
									position.append((i[j].inic,int((i[j].ini+i[j-1].end)/2), i[j-1].ini,i[j].end, i.link[j-1][0][1]+min((i.link[j-1][1][1]-i[j].ini),(i[j-1].end-i.link[j-1][0][1])), i.link[j-1][1][1]-min((i.link[j-1][1][1]-i[j].ini),(i[j-1].end-i.link[j-1][0][1]))))
						elif i[j-1].ini>i[j].end:
							if i[j-1].ini-i[j].end<15:
								if abs((i.link[j-1][0][1]-i[j-1].ini)-(i[j].end-i.link[j-1][1][1]))<2:
									position.append((i[j].inic,int((i[j-1].ini+i[j].end)/2), i[j].ini,i[j-1].end,i[j].end,i[j-1].ini, i.link[j-1][1][1]+min((i.link[j-1][0][1]-i[j-1].ini),(i[j].end-i.link[j-1][1][1])),i.link[j-1][0][1]-min((i.link[j-1][0][1]-i[j-1].ini),(i[j].end-i.link[j-1][1][1]))))
	
	if len(position)==0:
		print('**** Sheet is not found')
		return False
	else:
		if debug==True:
			print('**** Sheets are found')


	lenh=0
	for i in protein.helixes:
		lenh+=len(i)
	lens=0
	for i in protein.sheets:
		for j in i:
			lens+=len(j)
	lenf=protein.seqlen()
	lenl=lenf-lenh-lens
	lrscore=1-lenl/lenf
	srscore=lens/(lens+lenh)
	hrscore=lenh/(lens+lenh)
	flscore=scorefunction(protein.seqlen())
	if flscore>thresholdfl:
		if debug==True:
			print('**** Full length meet the condition')
	else:
		print('**** Full length did not meet the condition')
		return False

	for i in position:
		pscore=500-min(i[1]-protein[0][i[0]].residues[0].num,protein[0][i[0]].residues[-1].num-i[1])
		if pscore<0:
			pscore=0
		pscore=pscore/100


		ccc=(protein[0][i[0]][i[5]]['CA'].pos+protein[0][i[0]][i[4]]['CA'].pos)/2
		na=(protein[0][i[0]][i[5]]['CA'].pos-protein[0][i[0]][i[4]]['CA'].pos).unit()
		cplane=cdn.Plane([na,ccc])
		p1=protein[0][i[0]][i[4]]['C'].pos+cplane
		p2=protein[0][i[0]][i[5]]['N'].pos+cplane
		distence=abs(p1-p2)

		gscore=3-distence
		if gscore<0:
			gscore=0
		
		ccp=(p1+p2)/2
		nb=(ccc-ccp).unit()
		nc=(na**nb).unit()

		if (protein[0][i[0]][i[4]]['N'].pos-protein[0][i[0]][i[4]]['CA'].pos).linear_trans((na,nb,nc))[2]<0:
			if debug==True:
				print('**** Try 0, 2, -2')
			pA=protein[0][i[0]][i[5]]['CA'].pos+(7.1*na)+(4.3*nb)+(8*nc)
			rA=2.2
			pB=protein[0][i[0]][i[5]]['CA'].pos+(8.6*na)+(7.7*nb)-(3.4*nc)
			rB=4
			pC=protein[0][i[0]][i[4]]['CA'].pos-(8.2*na)-(2*nc)
			rC=2.5

			pD=protein[0][i[0]][i[5]]['CA'].pos-(8.2*na)-(12.2*nb)
			rD=6
			pE=protein[0][i[0]][i[5]]['CA'].pos+(7.1*na)-(9.6*nb)
			rE=9.6

			counter=0
			for c in protein[0]:
				for r in c:
					if abs(r['CA'].pos-pA)<rA or abs(r['CA'].pos-pB)<rB or abs(r['CA'].pos-pC)<rC:
						counter+=1
					elif abs(r['CA'].pos-pD)<rD or abs(r['CA'].pos-pE)<rE:
						counter-=2
			sscore=sshill(counter)
			if debug==True:
				print('**** 0-'+str(gscore)+'-'+str(sscore))


			#==========move down along te sheet============
			pA-=(6.6*nb)
			pB-=(6.6*nb)
			pC-=(6.6*nb)

			pD-=(6.6*nb)
			pE-=(6.6*nb)

			counter=0
			for c in protein[0]:
				for r in c:
					if abs(r['CA'].pos-pA)<rA or abs(r['CA'].pos-pB)<rB or abs(r['CA'].pos-pC)<rC:
						counter+=1
					elif abs(r['CA'].pos-pD)<rD or abs(r['CA'].pos-pE)<rE:
						counter-=5
			temsscore=sshill(counter)
			if debug==True:
				print('**** 2-'+str(gscore)+'-'+str(temsscore))
			if temsscore>sscore:
				sscore=temsscore
			else:
				if debug==True:
					print('**** 2-'+str(gscore)+'-'+str(sscore))


			#==========move up along te sheet============
			strres=i[4]-2
			endres=i[5]+2
			ccc=(protein[0][i[0]][endres]['CA'].pos+protein[0][i[0]][strres]['CA'].pos)/2
			na=(protein[0][i[0]][endres]['CA'].pos-protein[0][i[0]][strres]['CA'].pos).unit()
			cplane=cdn.Plane([na,ccc])
			p1=protein[0][i[0]][strres]['C'].pos+cplane
			p2=protein[0][i[0]][endres]['N'].pos+cplane
			distence=abs(p1-p2)

			temgscore=3-distence
			if temgscore<0:
				temgscore=0

			ccp=(p1+p2)/2
			nb=(ccc-ccp).unit()
			nc=(na**nb).unit()

			pA=protein[0][i[0]][endres]['CA'].pos+(7.1*na)+(4.3*nb)+(8*nc)
			rA=2.2
			pB=protein[0][i[0]][endres]['CA'].pos+(8.6*na)+(7.7*nb)-(3.4*nc)
			rB=4
			pC=protein[0][i[0]][strres]['CA'].pos-(8.2*na)-(2*nc)
			rC=2.5

			pD=protein[0][i[0]][endres]['CA'].pos-(8.2*na)-(12.2*nb)
			rD=6
			pE=protein[0][i[0]][endres]['CA'].pos+(7.1*na)-(9.6*nb)
			rE=9.6

			counter=0
			for c in protein[0]:
				for r in c:
					if abs(r['CA'].pos-pA)<rA or abs(r['CA'].pos-pB)<rB or abs(r['CA'].pos-pC)<rC:
						counter+=1
					elif abs(r['CA'].pos-pD)<rD or abs(r['CA'].pos-pE)<rE:
						counter-=5
			temsscore=sshill(counter)
			if debug==True:
				print('**** -2-'+str(gscore)+'-'+str(temsscore))
			if temsscore>sscore:
				sscore=temsscore
				gscore=temgscore
			else:
				if debug==True:
					print('**** -2-'+str(gscore)+'-'+str(sscore))
			
		else:
			#==========move up along te sheet============
			if debug==True:
				print('**** Try -1, 1')
			strres=i[4]-1
			endres=i[5]+1
			ccc=(protein[0][i[0]][endres]['CA'].pos+protein[0][i[0]][strres]['CA'].pos)/2
			na=(protein[0][i[0]][endres]['CA'].pos-protein[0][i[0]][strres]['CA'].pos).unit()
			cplane=cdn.Plane([na,ccc])
			p1=protein[0][i[0]][strres]['C'].pos+cplane
			p2=protein[0][i[0]][endres]['N'].pos+cplane
			distence=abs(p1-p2)

			gscore=3-distence
			if gscore<0:
				gscore=0

			ccp=(p1+p2)/2
			nb=(ccc-ccp).unit()
			nc=(na**nb).unit()

			pA=protein[0][i[0]][endres]['CA'].pos+(7.1*na)+(4.3*nb)+(8*nc)
			rA=2.2
			pB=protein[0][i[0]][endres]['CA'].pos+(8.6*na)+(7.7*nb)-(3.4*nc)
			rB=4
			pC=protein[0][i[0]][strres]['CA'].pos-(8.2*na)-(2*nc)
			rC=2.5

			pD=protein[0][i[0]][endres]['CA'].pos-(8.2*na)-(12.2*nb)
			rD=6
			pE=protein[0][i[0]][endres]['CA'].pos+(7.1*na)-(9.6*nb)
			rE=9.6

			counter=0
			for c in protein[0]:
				for r in c:
					if abs(r['CA'].pos-pA)<rA or abs(r['CA'].pos-pB)<rB or abs(r['CA'].pos-pC)<rC:
						counter+=1
					elif abs(r['CA'].pos-pD)<rD or abs(r['CA'].pos-pE)<rE:
						counter-=5
			sscore=sshill(counter)
			if debug==True:
				print('**** -1-'+str(gscore)+'-'+str(sscore))
			#==========move down along te sheet============
			pA-=(6.6*nb)
			pB-=(6.6*nb)
			pC-=(6.6*nb)

			pD-=(6.6*nb)
			pE-=(6.6*nb)

			counter=0
			for c in protein[0]:
				for r in c:
					if abs(r['CA'].pos-pA)<rA or abs(r['CA'].pos-pB)<rB or abs(r['CA'].pos-pC)<rC:
						counter+=1
					elif abs(r['CA'].pos-pD)<rD or abs(r['CA'].pos-pE)<rE:
						counter-=5
			temsscore=sshill(counter)
			if debug==True:
				print('**** 1-'+str(gscore)+'-'+str(temsscore))
			if temsscore>sscore:
				sscore=temsscore
			else:
				if debug==True:
					print('**** 1-'+str(gscore)+'-'+str(sscore))



		score=flscore*sscore
		score2=flscore*lrscore*pscore*sscore*gscore
		#========================
		newline=protein.name+' '+i[0]+' '+str(i[1])+' '+str(flscore)[0:7]+' '+str(lrscore)[0:7]+' '+str(hrscore)[0:7]+' '+str(srscore)[0:7]+' '+str(pscore)[0:7]+' '+str(sscore)[0:7]+' '+str(gscore)[0:7]+' '+str(score)[0:7]+' '+str(score2)[0:7]
		if debug==True:
			print(newline)
		temscore.append((score,newline))
	for i in temscore:
		if i[0]>thresholdF:
			protein.score.append(i)
	if len(protein.score)==0:
		print('**** score did not meet the condition')
		return False
	for i in protein.score:
		with open(os.getcwd()+os.sep+'screen_result','a') as f:
			f.write('\n'+i[1])
	return True


#========================================================================================================================
#=========================================================||||||=========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#=========================================================||||||=========================================================
#========================================================================================================================


header='name chain position full_length_score non-loop_ratio helix_ratio sheet_ratio position_score structure_scroe geometry_score score score2'

try:
	f=open(os.getcwd()+os.sep+'screen_result','r')
	f.close()
except:
	with open(os.getcwd()+os.sep+'screen_result','w') as f:
		f.write(header)


sshill=fmk.combinefunc(((0,0.9),(fmk.hill(2, 0, 0.9, halflife=1, point1=(5,1.5)),0.9,False,0b11)))


#===========================================Real Screen!!!!!!================================================
screenlist=pypdb.get_all()
screennum=len(screenlist)
for num in range(screennum):
	try:
		pdbidget=screenlist[num]
		pro=pdb.ProteinS(pdbidget,path=os.getcwd()+os.sep+'screen'+os.sep+pdbidget+'.pdb', debug=False, 
			precon=pdb.screxp, preconargs=(['ESCHERICHIA COLI'],),
			atmcon=pdb.scrsheet,
			score=scoring, 
			scoreargs=(fmk.longtail(100,100,300),60,120,False))
		print(str(num+1)+r'/'+str(screennum)+'-'+pdbidget+'- done')
	except:
		print(str(num+1)+r'/'+str(screennum)+'-'+pdbidget+' failed')
'''
#===========================================checking scoring performance================================================
screenlist=['2KKX','2n2t','4hqp','2jsv','2pcy','3fil']
screennum=len(screenlist)
for num in range(screennum):
	pro=pdb.ProteinS(screenlist[num],path=os.getcwd()+os.sep+'screen'+os.sep+screenlist[num]+'.pdb', debug=True, 
		precon=pdb.screxp, preconargs=(['ESCHERICHIA COLI'],),
		atmcon=pdb.scrsheet,
		score=scoring, 
		scoreargs=(fmk.longtail(100,100,300),60,100,True))
'''





#=======================A fake pdb input just for checking function performance===============================
"""


realtarget='''HEADER    PROTEIN BINDING                         25-OCT-12   ####              
TITLE     ALPHA7 NICOTINIC RECEPTOR CHIMERA AND ITS COMPLEX WITH ALPHA          
TITLE    2 BUNGAROTOXIN                                                         
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: ALPHA7 NICOTINIC RECEPTOR CHIMERA;                         
COMPND   3 CHAIN: A, B, C, D, E;                                                
COMPND   4 ENGINEERED: YES;                                                     
COMPND   5 MOL_ID: 2;                                                           
COMPND   6 MOLECULE: ALPHA-BUNGAROTOXIN ISOFORM V31;                            
COMPND   7 CHAIN: F, G, H, I, J;                                                
COMPND   8 SYNONYM: ALPHA-BTX V31, ALPHA-BGT(V31), BGTX V31, LONG NEUROTOXIN 1  
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS, LYMNAEA STAGNALIS;                
SOURCE   3 ORGANISM_COMMON: HUMAN, GREAT POND SNAIL;                            
SOURCE   4 ORGANISM_TAXID: 9606, 6523;                                          
SOURCE   5 EXPRESSION_SYSTEM: ESCHERICHIA COLI;                                  
SOURCE   6 EXPRESSION_SYSTEM_TAXID: 4922;                                       
SOURCE   7 MOL_ID: 2;                                                           
SOURCE   8 ORGANISM_SCIENTIFIC: BUNGARUS MULTICINCTUS;                          
SOURCE   9 ORGANISM_COMMON: MANY-BANDED KRAIT;                                  
SOURCE  10 ORGANISM_TAXID: 8616;                                                
SOURCE  11 ORGAN: VENOM                                                                
DBREF  4HQP F    1    73  UNP    P60616   NXL1V_BUNMU     22     94             
DBREF  4HQP G    1    73  UNP    P60616   NXL1V_BUNMU     22     94             
DBREF  4HQP H    1    73  UNP    P60616   NXL1V_BUNMU     22     94             
DBREF  4HQP I    1    73  UNP    P60616   NXL1V_BUNMU     22     94             
DBREF  4HQP J    1    73  UNP    P60616   NXL1V_BUNMU     22     94             
DBREF  4HQP A    3   204  PDB    4HQP     4HQP             3    204             
DBREF  4HQP B    3   204  PDB    4HQP     4HQP             3    204             
DBREF  4HQP C    3   204  PDB    4HQP     4HQP             3    204             
DBREF  4HQP D    3   204  PDB    4HQP     4HQP             3    204             
DBREF  4HQP E    3   204  PDB    4HQP     4HQP             3    204             
MODRES 4HQP ASN C   66  ASN  GLYCOSYLATION SITE                                 
MODRES 4HQP ASN A   66  ASN  GLYCOSYLATION SITE                                 
MODRES 4HQP ASN C  108  ASN  GLYCOSYLATION SITE                                 
MODRES 4HQP ASN B   66  ASN  GLYCOSYLATION SITE                                 
MODRES 4HQP ASN D   66  ASN  GLYCOSYLATION SITE                                 
MODRES 4HQP ASN B  108  ASN  GLYCOSYLATION SITE                                 
MODRES 4HQP ASN A  108  ASN  GLYCOSYLATION SITE                                 
HET    NAG  A 801      14                                                       
HET    NAG  A 802      14                                                       
HET    NAG  B 801      14                                                       
HET    NAG  B 802      14                                                       
HET    NAG  B 803      14                                                       
HET    NAG  C 801      14                                                       
HET    NAG  C 802      14                                                       
HET    NAG  D 801      14                                                       
HETNAM     NAG N-ACETYL-D-GLUCOSAMINE                                           
FORMUL  11  NAG    8(C8 H15 N O6)                                                
HELIX   12  12 VAL F   31  SER F   35  5                                   5    
SHEET    1   S 3 VAL F  40  ALA F  45  0                                        
SHEET    2   S 3 LEU F  22  MET F  27 -1  N  LYS F  26   O  GLU F  41           
SHEET    3   S 3 CYS F  59  CYS F  60 -1  O  CYS F  60   N  CYS F  23           
SSBOND   1 CYS A  125    CYS A  138                          1555   1555  2.03  
SSBOND   2 CYS A  186    CYS A  187                          1555   1555  2.04  
SSBOND   3 CYS B  125    CYS B  138                          1555   1555  2.03  
SSBOND   4 CYS B  186    CYS B  187                          1555   1555  2.05  
SSBOND   5 CYS C  125    CYS C  138                          1555   1555  2.03  
SSBOND   6 CYS C  186    CYS C  187                          1555   1555  2.04  
SSBOND   7 CYS D  125    CYS D  138                          1555   1555  2.03  
SSBOND   8 CYS D  186    CYS D  187                          1555   1555  2.05  
SSBOND   9 CYS E  125    CYS E  138                          1555   1555  2.03  
SSBOND  10 CYS E  186    CYS E  187                          1555   1555  2.05  
SSBOND  11 CYS F    3    CYS F   16                          1555   1555  2.04  
SSBOND  12 CYS F    3    CYS F   23                          1555   1555  2.03  
SSBOND  13 CYS F   16    CYS F   44                          1555   1555  2.03  
SSBOND  14 CYS F   29    CYS F   33                          1555   1555  2.03  
SSBOND  15 CYS F   48    CYS F   59                          1555   1555  2.03  
SSBOND  16 CYS F   60    CYS F   65                          1555   1555  2.03  
SSBOND  17 CYS G    3    CYS G   16                          1555   1555  2.04  
SSBOND  18 CYS G    3    CYS G   23                          1555   1555  2.03  
SSBOND  19 CYS G   16    CYS G   44                          1555   1555  2.03  
SSBOND  20 CYS G   29    CYS G   33                          1555   1555  2.03  
SSBOND  21 CYS G   48    CYS G   59                          1555   1555  2.03  
SSBOND  22 CYS G   60    CYS G   65                          1555   1555  2.03  
SSBOND  23 CYS H    3    CYS H   16                          1555   1555  2.04  
SSBOND  24 CYS H    3    CYS H   23                          1555   1555  2.03  
SSBOND  25 CYS H   16    CYS H   44                          1555   1555  2.03  
SSBOND  26 CYS H   29    CYS H   33                          1555   1555  2.03  
SSBOND  27 CYS H   48    CYS H   59                          1555   1555  2.03  
SSBOND  28 CYS H   60    CYS H   65                          1555   1555  2.03  
SSBOND  29 CYS I    3    CYS I   16                          1555   1555  2.04  
SSBOND  30 CYS I    3    CYS I   23                          1555   1555  2.03  
SSBOND  31 CYS I   16    CYS I   44                          1555   1555  2.03  
SSBOND  32 CYS I   29    CYS I   33                          1555   1555  2.03  
SSBOND  33 CYS I   48    CYS I   59                          1555   1555  2.03  
SSBOND  34 CYS I   60    CYS I   65                          1555   1555  2.03  
SSBOND  35 CYS J    3    CYS J   16                          1555   1555  2.04  
SSBOND  36 CYS J    3    CYS J   23                          1555   1555  2.04  
SSBOND  37 CYS J   16    CYS J   44                          1555   1555  2.03  
SSBOND  38 CYS J   29    CYS J   33                          1555   1555  2.03  
SSBOND  39 CYS J   48    CYS J   59                          1555   1555  2.03  
SSBOND  40 CYS J   60    CYS J   65                          1555   1555  2.03  
LINK         O4  NAG B 801                 C1  NAG B 802     1555   1555  1.41  
LINK         ND2 ASN C  66                 C1  NAG C 801     1555   1555  1.45  
LINK         ND2 ASN A  66                 C1  NAG A 801     1555   1555  1.45  
LINK         ND2 ASN C 108                 C1  NAG C 802     1555   1555  1.45  
LINK         ND2 ASN B  66                 C1  NAG B 801     1555   1555  1.46  
LINK         ND2 ASN D  66                 C1  NAG D 801     1555   1555  1.46  
LINK         ND2 ASN B 108                 C1  NAG B 803     1555   1555  1.46  
LINK         ND2 ASN A 108                 C1  NAG A 802     1555   1555  1.46  
CISPEP   1 SER F    9    PRO F   10          0         0.03                     
CISPEP   2 SER G    9    PRO G   10          0        -0.13                     
CISPEP   3 SER H    9    PRO H   10          0        -0.28                     
CISPEP   4 SER I    9    PRO I   10          0        -0.12                     
CISPEP   5 SER J    9    PRO J   10          0        -0.37                     
SITE     1 AC1  3 ASN A  66  SER A  68  GLU A  69                               
SITE     1 AC2  3 ASN A 108  SER A 110  HIS A 112                               
SITE     1 AC3  4 ASN B  66  SER B  68  GLU B  69  NAG B 802                    
SITE     1 AC4  2 NAG B 801  GLN E 157                                          
SITE     1 AC5  3 ASN B 108  SER B 110  HIS B 112                               
SITE     1 AC6  4 ASN C  66  SER C  68  GLU C  69  ASN J  21                    
SITE     1 AC7  4 ASN C 108  SER C 109  SER C 110  HIS C 112                    
SITE     1 AC8  3 ASN D  66  SER D  68  GLU D  69                               
CRYST1  142.150  142.150  518.135  90.00  90.00 120.00 P 65 2 2     60          
ORIGX1      1.000000  0.000000  0.000000        0.00000                         
ORIGX2      0.000000  1.000000  0.000000        0.00000                         
ORIGX3      0.000000  0.000000  1.000000        0.00000                         
SCALE1      0.007035  0.004062  0.000000        0.00000                         
SCALE2      0.000000  0.008123  0.000000        0.00000                         
SCALE3      0.000000  0.000000  0.001930        0.00000                         
ATOM   8241  N   ILE F   1      45.128  -9.184  36.017  1.00169.26           N  
ATOM   8242  CA  ILE F   1      45.688  -7.803  36.056  1.00169.17           C  
ATOM   8243  C   ILE F   1      44.906  -6.843  35.159  1.00168.93           C  
ATOM   8244  O   ILE F   1      44.924  -6.968  33.935  1.00169.00           O  
ATOM   8245  CB  ILE F   1      47.176  -7.802  35.627  1.00169.15           C  
ATOM   8246  CG1 ILE F   1      47.682  -6.364  35.501  1.00169.04           C  
ATOM   8247  CG2 ILE F   1      47.345  -8.558  34.317  1.00169.30           C  
ATOM   8248  CD1 ILE F   1      47.550  -5.556  36.771  1.00168.69           C  
ATOM   8249  N   VAL F   2      44.217  -5.887  35.776  1.00168.79           N  
ATOM   8250  CA  VAL F   2      43.431  -4.907  35.035  1.00168.85           C  
ATOM   8251  C   VAL F   2      44.295  -3.709  34.675  1.00168.66           C  
ATOM   8252  O   VAL F   2      45.025  -3.186  35.515  1.00168.75           O  
ATOM   8253  CB  VAL F   2      42.227  -4.409  35.857  1.00168.48           C  
ATOM   8254  CG1 VAL F   2      41.442  -3.384  35.058  1.00168.32           C  
ATOM   8255  CG2 VAL F   2      41.335  -5.577  36.230  1.00168.34           C  
ATOM   8256  N   CYS F   3      44.201  -3.270  33.426  1.00168.86           N  
ATOM   8257  CA  CYS F   3      44.992  -2.142  32.958  1.00169.05           C  
ATOM   8258  C   CYS F   3      44.178  -1.062  32.258  1.00168.89           C  
ATOM   8259  O   CYS F   3      42.967  -1.182  32.086  1.00168.80           O  
ATOM   8260  CB  CYS F   3      46.059  -2.614  31.977  1.00169.46           C  
ATOM   8261  SG  CYS F   3      47.390  -3.690  32.598  1.00170.04           S  
ATOM   8262  N   HIS F   4      44.878  -0.007  31.854  1.00168.87           N  
ATOM   8263  CA  HIS F   4      44.288   1.110  31.128  1.00169.07           C  
ATOM   8264  C   HIS F   4      44.845   1.023  29.713  1.00168.92           C  
ATOM   8265  O   HIS F   4      46.056   0.899  29.531  1.00168.96           O  
ATOM   8266  CB  HIS F   4      44.702   2.444  31.752  1.00169.16           C  
ATOM   8267  CG  HIS F   4      43.878   2.848  32.935  1.00169.44           C  
ATOM   8268  ND1 HIS F   4      42.524   3.090  32.851  1.00169.58           N  
ATOM   8269  CD2 HIS F   4      44.222   3.083  34.224  1.00169.58           C  
ATOM   8270  CE1 HIS F   4      42.070   3.459  34.036  1.00169.69           C  
ATOM   8271  NE2 HIS F   4      43.080   3.464  34.886  1.00169.68           N  
ATOM   8272  N   THR F   5      43.972   1.082  28.712  1.00168.93           N  
ATOM   8273  CA  THR F   5      44.422   0.994  27.327  1.00169.09           C  
ATOM   8274  C   THR F   5      43.990   2.186  26.486  1.00169.03           C  
ATOM   8275  O   THR F   5      42.902   2.730  26.668  1.00169.04           O  
ATOM   8276  CB  THR F   5      43.904  -0.290  26.653  1.00168.99           C  
ATOM   8277  OG1 THR F   5      44.412  -0.366  25.316  1.00168.97           O  
ATOM   8278  CG2 THR F   5      42.384  -0.294  26.612  1.00169.04           C  
ATOM   8279  N   THR F   6      44.859   2.584  25.564  1.00169.07           N  
ATOM   8280  CA  THR F   6      44.584   3.704  24.677  1.00169.09           C  
ATOM   8281  C   THR F   6      44.171   3.177  23.311  1.00169.02           C  
ATOM   8282  O   THR F   6      44.009   3.941  22.359  1.00169.04           O  
ATOM   8283  CB  THR F   6      45.821   4.604  24.512  1.00169.22           C  
ATOM   8284  OG1 THR F   6      46.927   3.819  24.052  1.00169.31           O  
ATOM   8285  CG2 THR F   6      46.183   5.253  25.834  1.00169.39           C  
ATOM   8286  N   ALA F   7      44.004   1.862  23.221  1.00169.00           N  
ATOM   8287  CA  ALA F   7      43.605   1.231  21.973  1.00168.99           C  
ATOM   8288  C   ALA F   7      42.125   1.482  21.729  1.00168.85           C  
ATOM   8289  O   ALA F   7      41.672   1.499  20.590  1.00168.98           O  
ATOM   8290  CB  ALA F   7      43.882  -0.262  22.031  1.00168.92           C  
ATOM   8291  N   THR F   8      41.376   1.686  22.809  1.00168.85           N  
ATOM   8292  CA  THR F   8      39.943   1.937  22.716  1.00168.88           C  
ATOM   8293  C   THR F   8      39.634   3.405  22.980  1.00168.71           C  
ATOM   8294  O   THR F   8      40.421   4.106  23.611  1.00168.68           O  
ATOM   8295  CB  THR F   8      39.171   1.087  23.732  1.00168.84           C  
ATOM   8296  OG1 THR F   8      39.585   1.437  25.057  1.00168.91           O  
ATOM   8297  CG2 THR F   8      39.441  -0.387  23.504  1.00168.92           C  
ATOM   8298  N   SER F   9      38.482   3.864  22.504  1.00168.74           N  
ATOM   8299  CA  SER F   9      38.085   5.252  22.692  1.00168.63           C  
ATOM   8300  C   SER F   9      36.670   5.377  23.240  1.00168.54           C  
ATOM   8301  O   SER F   9      35.721   4.875  22.644  1.00168.71           O  
ATOM   8302  CB  SER F   9      38.180   6.009  21.366  1.00168.72           C  
ATOM   8303  OG  SER F   9      37.771   7.356  21.518  1.00168.77           O  
ATOM   8304  N   PRO F  10      36.511   6.053  24.388  1.00168.91           N  
ATOM   8305  CA  PRO F  10      37.591   6.681  25.156  1.00168.73           C  
ATOM   8306  C   PRO F  10      38.481   5.640  25.828  1.00168.41           C  
ATOM   8307  O   PRO F  10      38.195   4.445  25.778  1.00168.60           O  
ATOM   8308  CB  PRO F  10      36.840   7.535  26.176  1.00168.70           C  
ATOM   8309  CG  PRO F  10      35.559   7.857  25.473  1.00168.73           C  
ATOM   8310  CD  PRO F  10      35.202   6.527  24.865  1.00168.70           C  
ATOM   8311  N   ILE F  11      39.561   6.098  26.452  1.00168.47           N  
ATOM   8312  CA  ILE F  11      40.475   5.197  27.139  1.00168.55           C  
ATOM   8313  C   ILE F  11      39.748   4.431  28.240  1.00168.38           C  
ATOM   8314  O   ILE F  11      39.367   4.998  29.263  1.00168.35           O  
ATOM   8315  CB  ILE F  11      41.670   5.965  27.753  1.00168.29           C  
ATOM   8316  CG1 ILE F  11      41.296   7.429  27.993  1.00168.25           C  
ATOM   8317  CG2 ILE F  11      42.869   5.877  26.837  1.00168.39           C  
ATOM   8318  CD1 ILE F  11      40.225   7.628  29.032  1.00168.03           C  
ATOM   8319  N   SER F  12      39.552   3.137  28.020  1.00168.36           N  
ATOM   8320  CA  SER F  12      38.865   2.292  28.989  1.00168.33           C  
ATOM   8321  C   SER F  12      39.846   1.405  29.741  1.00168.50           C  
ATOM   8322  O   SER F  12      41.033   1.363  29.422  1.00168.48           O  
ATOM   8323  CB  SER F  12      37.828   1.419  28.283  1.00168.33           C  
ATOM   8324  OG  SER F  12      38.440   0.588  27.312  1.00168.19           O  
ATOM   8325  N   ALA F  13      39.341   0.692  30.740  1.00168.48           N  
ATOM   8326  CA  ALA F  13      40.175  -0.194  31.536  1.00168.47           C  
ATOM   8327  C   ALA F  13      39.949  -1.646  31.138  1.00168.43           C  
ATOM   8328  O   ALA F  13      38.984  -2.272  31.570  1.00168.47           O  
ATOM   8329  CB  ALA F  13      39.870  -0.004  33.011  1.00168.59           C  
ATOM   8330  N   VAL F  14      40.841  -2.176  30.309  1.00168.39           N  
ATOM   8331  CA  VAL F  14      40.733  -3.559  29.861  1.00168.61           C  
ATOM   8332  C   VAL F  14      41.625  -4.449  30.715  1.00168.42           C  
ATOM   8333  O   VAL F  14      42.682  -4.020  31.176  1.00168.41           O  
ATOM   8334  CB  VAL F  14      41.155  -3.708  28.379  1.00168.41           C  
ATOM   8335  CG1 VAL F  14      42.623  -3.351  28.215  1.00168.44           C  
ATOM   8336  CG2 VAL F  14      40.896  -5.129  27.902  1.00168.44           C  
ATOM   8337  N   THR F  15      41.191  -5.686  30.928  1.00168.60           N  
ATOM   8338  CA  THR F  15      41.958  -6.637  31.722  1.00168.96           C  
ATOM   8339  C   THR F  15      43.169  -7.133  30.936  1.00169.06           C  
ATOM   8340  O   THR F  15      43.041  -7.981  30.051  1.00169.29           O  
ATOM   8341  CB  THR F  15      41.096  -7.847  32.121  1.00168.63           C  
ATOM   8342  OG1 THR F  15      40.583  -8.477  30.942  1.00168.46           O  
ATOM   8343  CG2 THR F  15      39.937  -7.405  33.001  1.00168.38           C  
ATOM   8344  N   CYS F  16      44.340  -6.589  31.264  1.00169.28           N  
ATOM   8345  CA  CYS F  16      45.590  -6.962  30.606  1.00169.99           C  
ATOM   8346  C   CYS F  16      45.614  -8.470  30.310  1.00169.34           C  
ATOM   8347  O   CYS F  16      45.732  -9.290  31.220  1.00169.59           O  
ATOM   8348  CB  CYS F  16      46.788  -6.572  31.494  1.00169.87           C  
ATOM   8349  SG  CYS F  16      47.675  -5.019  31.083  1.00170.17           S  
ATOM   8350  N   PRO F  17      45.497  -8.846  29.022  1.00168.86           N  
ATOM   8351  CA  PRO F  17      45.491 -10.227  28.521  1.00170.10           C  
ATOM   8352  C   PRO F  17      46.503 -11.173  29.167  1.00169.52           C  
ATOM   8353  O   PRO F  17      47.465 -10.735  29.796  1.00169.55           O  
ATOM   8354  CB  PRO F  17      45.746 -10.044  27.029  1.00169.16           C  
ATOM   8355  CG  PRO F  17      45.015  -8.782  26.741  1.00169.11           C  
ATOM   8356  CD  PRO F  17      45.429  -7.894  27.897  1.00169.29           C  
ATOM   8357  N   PRO F  18      46.292 -12.493  29.012  1.00169.23           N  
ATOM   8358  CA  PRO F  18      47.155 -13.548  29.560  1.00170.35           C  
ATOM   8359  C   PRO F  18      48.624 -13.397  29.175  1.00169.80           C  
ATOM   8360  O   PRO F  18      48.943 -12.917  28.088  1.00169.85           O  
ATOM   8361  CB  PRO F  18      46.541 -14.821  28.988  1.00169.94           C  
ATOM   8362  CG  PRO F  18      45.093 -14.479  28.915  1.00170.01           C  
ATOM   8363  CD  PRO F  18      45.126 -13.085  28.333  1.00169.95           C  
ATOM   8364  N   GLY F  19      49.509 -13.823  30.071  1.00169.79           N  
ATOM   8365  CA  GLY F  19      50.933 -13.722  29.811  1.00169.91           C  
ATOM   8366  C   GLY F  19      51.466 -12.350  30.178  1.00169.95           C  
ATOM   8367  O   GLY F  19      52.602 -12.210  30.636  1.00169.84           O  
ATOM   8368  N   GLU F  20      50.635 -11.332  29.976  1.00170.07           N  
ATOM   8369  CA  GLU F  20      51.002  -9.954  30.281  1.00170.31           C  
ATOM   8370  C   GLU F  20      50.462  -9.589  31.657  1.00170.48           C  
ATOM   8371  O   GLU F  20      49.253  -9.619  31.887  1.00170.51           O  
ATOM   8372  CB  GLU F  20      50.415  -9.010  29.227  1.00170.28           C  
ATOM   8373  CG  GLU F  20      50.724  -9.418  27.792  1.00170.24           C  
ATOM   8374  CD  GLU F  20      50.044  -8.528  26.769  1.00170.21           C  
ATOM   8375  OE1 GLU F  20      48.802  -8.402  26.822  1.00170.16           O  
ATOM   8376  OE2 GLU F  20      50.750  -7.959  25.909  1.00170.18           O  
ATOM   8377  N   ASN F  21      51.360  -9.244  32.572  1.00170.63           N  
ATOM   8378  CA  ASN F  21      50.954  -8.888  33.923  1.00170.73           C  
ATOM   8379  C   ASN F  21      51.440  -7.495  34.300  1.00170.84           C  
ATOM   8380  O   ASN F  21      51.428  -7.121  35.473  1.00170.92           O  
ATOM   8381  CB  ASN F  21      51.506  -9.915  34.911  1.00170.72           C  
ATOM   8382  CG  ASN F  21      51.185 -11.337  34.504  1.00170.66           C  
ATOM   8383  OD1 ASN F  21      50.020 -11.708  34.372  1.00170.62           O  
ATOM   8384  ND2 ASN F  21      52.220 -12.142  34.299  1.00170.62           N  
ATOM   8385  N   LEU F  22      51.859  -6.727  33.300  1.00170.96           N  
ATOM   8386  CA  LEU F  22      52.353  -5.381  33.543  1.00170.97           C  
ATOM   8387  C   LEU F  22      51.623  -4.322  32.732  1.00170.95           C  
ATOM   8388  O   LEU F  22      51.503  -4.436  31.512  1.00170.97           O  
ATOM   8389  CB  LEU F  22      53.847  -5.301  33.218  1.00171.01           C  
ATOM   8390  CG  LEU F  22      54.819  -6.112  34.071  1.00171.03           C  
ATOM   8391  CD1 LEU F  22      56.223  -5.982  33.501  1.00171.06           C  
ATOM   8392  CD2 LEU F  22      54.774  -5.615  35.504  1.00171.08           C  
ATOM   8393  N   CYS F  23      51.128  -3.296  33.416  1.00171.00           N  
ATOM   8394  CA  CYS F  23      50.455  -2.195  32.742  1.00171.06           C  
ATOM   8395  C   CYS F  23      51.561  -1.169  32.515  1.00171.22           C  
ATOM   8396  O   CYS F  23      52.459  -1.040  33.347  1.00171.26           O  
ATOM   8397  CB  CYS F  23      49.367  -1.586  33.627  1.00170.77           C  
ATOM   8398  SG  CYS F  23      48.091  -2.729  34.246  1.00170.41           S  
ATOM   8399  N   TYR F  24      51.514  -0.443  31.402  1.00171.42           N  
ATOM   8400  CA  TYR F  24      52.555   0.540  31.128  1.00171.72           C  
ATOM   8401  C   TYR F  24      52.038   1.853  30.559  1.00171.55           C  
ATOM   8402  O   TYR F  24      50.844   2.020  30.314  1.00171.59           O  
ATOM   8403  CB  TYR F  24      53.593  -0.053  30.169  1.00172.03           C  
ATOM   8404  CG  TYR F  24      53.146  -0.116  28.723  1.00172.39           C  
ATOM   8405  CD1 TYR F  24      53.177   1.017  27.912  1.00172.56           C  
ATOM   8406  CD2 TYR F  24      52.684  -1.308  28.168  1.00172.56           C  
ATOM   8407  CE1 TYR F  24      52.761   0.967  26.589  1.00172.61           C  
ATOM   8408  CE2 TYR F  24      52.265  -1.368  26.844  1.00172.61           C  
ATOM   8409  CZ  TYR F  24      52.306  -0.227  26.061  1.00172.61           C  
ATOM   8410  OH  TYR F  24      51.893  -0.279  24.752  1.00172.56           O  
ATOM   8411  N   ARG F  25      52.967   2.779  30.350  1.00171.47           N  
ATOM   8412  CA  ARG F  25      52.660   4.090  29.800  1.00171.28           C  
ATOM   8413  C   ARG F  25      53.888   4.631  29.084  1.00170.95           C  
ATOM   8414  O   ARG F  25      54.917   4.883  29.710  1.00170.92           O  
ATOM   8415  CB  ARG F  25      52.271   5.065  30.908  1.00171.72           C  
ATOM   8416  CG  ARG F  25      52.016   6.472  30.399  1.00172.33           C  
ATOM   8417  CD  ARG F  25      52.287   7.508  31.470  1.00172.93           C  
ATOM   8418  NE  ARG F  25      51.429   7.338  32.636  1.00173.48           N  
ATOM   8419  CZ  ARG F  25      51.503   8.093  33.726  1.00173.77           C  
ATOM   8420  NH1 ARG F  25      52.397   9.068  33.799  1.00173.96           N  
ATOM   8421  NH2 ARG F  25      50.681   7.873  34.742  1.00173.97           N  
ATOM   8422  N   LYS F  26      53.779   4.807  27.774  1.00170.61           N  
ATOM   8423  CA  LYS F  26      54.885   5.328  26.984  1.00170.20           C  
ATOM   8424  C   LYS F  26      54.477   6.691  26.439  1.00169.86           C  
ATOM   8425  O   LYS F  26      53.382   6.845  25.899  1.00170.01           O  
ATOM   8426  CB  LYS F  26      55.212   4.365  25.837  1.00170.10           C  
ATOM   8427  CG  LYS F  26      56.453   4.735  25.037  1.00169.96           C  
ATOM   8428  CD  LYS F  26      56.840   3.639  24.051  1.00169.77           C  
ATOM   8429  CE  LYS F  26      55.755   3.401  23.011  1.00169.65           C  
ATOM   8430  NZ  LYS F  26      56.147   2.356  22.024  1.00169.42           N  
ATOM   8431  N   MET F  27      55.352   7.681  26.589  1.00169.55           N  
ATOM   8432  CA  MET F  27      55.053   9.025  26.112  1.00169.24           C  
ATOM   8433  C   MET F  27      56.113   9.589  25.166  1.00168.77           C  
ATOM   8434  O   MET F  27      57.288   9.683  25.516  1.00168.83           O  
ATOM   8435  CB  MET F  27      54.871   9.967  27.304  1.00169.09           C  
ATOM   8436  CG  MET F  27      53.739   9.563  28.231  1.00168.94           C  
ATOM   8437  SD  MET F  27      53.539  10.680  29.628  1.00168.86           S  
ATOM   8438  CE  MET F  27      52.298  11.780  29.009  1.00168.67           C  
ATOM   8439  N   TRP F  28      55.682   9.957  23.962  1.00168.51           N  
ATOM   8440  CA  TRP F  28      56.571  10.528  22.956  1.00168.18           C  
ATOM   8441  C   TRP F  28      56.453  12.038  23.070  1.00167.83           C  
ATOM   8442  O   TRP F  28      55.827  12.552  23.995  1.00167.78           O  
ATOM   8443  CB  TRP F  28      56.137  10.123  21.545  1.00168.35           C  
ATOM   8444  CG  TRP F  28      55.766   8.687  21.392  1.00168.69           C  
ATOM   8445  CD1 TRP F  28      54.762   8.024  22.038  1.00168.76           C  
ATOM   8446  CD2 TRP F  28      56.379   7.733  20.517  1.00168.96           C  
ATOM   8447  NE1 TRP F  28      54.711   6.715  21.621  1.00168.94           N  
ATOM   8448  CE2 TRP F  28      55.693   6.508  20.687  1.00169.05           C  
ATOM   8449  CE3 TRP F  28      57.443   7.793  19.606  1.00169.13           C  
ATOM   8450  CZ2 TRP F  28      56.037   5.346  19.975  1.00169.22           C  
ATOM   8451  CZ3 TRP F  28      57.787   6.637  18.896  1.00169.27           C  
ATOM   8452  CH2 TRP F  28      57.083   5.431  19.089  1.00169.31           C  
ATOM   8453  N   CYS F  29      57.046  12.742  22.116  1.00167.51           N  
ATOM   8454  CA  CYS F  29      56.994  14.196  22.089  1.00167.14           C  
ATOM   8455  C   CYS F  29      57.117  14.622  20.633  1.00167.06           C  
ATOM   8456  O   CYS F  29      58.219  14.733  20.098  1.00167.08           O  
ATOM   8457  CB  CYS F  29      58.135  14.786  22.926  1.00167.06           C  
ATOM   8458  SG  CYS F  29      58.064  16.592  23.183  1.00166.86           S  
ATOM   8459  N   ASP F  30      55.973  14.842  19.992  1.00166.74           N  
ATOM   8460  CA  ASP F  30      55.944  15.239  18.591  1.00166.49           C  
ATOM   8461  C   ASP F  30      55.877  16.750  18.406  1.00166.49           C  
ATOM   8462  O   ASP F  30      56.351  17.512  19.247  1.00166.30           O  
ATOM   8463  CB  ASP F  30      54.757  14.580  17.883  1.00166.40           C  
ATOM   8464  CG  ASP F  30      53.432  14.922  18.528  1.00166.35           C  
ATOM   8465  OD1 ASP F  30      52.387  14.444  18.038  1.00166.32           O  
ATOM   8466  OD2 ASP F  30      53.440  15.668  19.527  1.00166.36           O  
ATOM   8467  N   VAL F  31      55.288  17.171  17.291  1.00166.27           N  
ATOM   8468  CA  VAL F  31      55.156  18.587  16.963  1.00166.21           C  
ATOM   8469  C   VAL F  31      54.232  19.323  17.925  1.00166.23           C  
ATOM   8470  O   VAL F  31      54.562  20.399  18.418  1.00165.97           O  
ATOM   8471  CB  VAL F  31      54.611  18.772  15.527  1.00166.54           C  
ATOM   8472  CG1 VAL F  31      55.598  18.214  14.512  1.00166.78           C  
ATOM   8473  CG2 VAL F  31      53.274  18.067  15.386  1.00166.83           C  
ATOM   8474  N   PHE F  32      53.072  18.734  18.186  1.00165.82           N  
ATOM   8475  CA  PHE F  32      52.087  19.329  19.077  1.00165.78           C  
ATOM   8476  C   PHE F  32      52.522  19.203  20.529  1.00165.91           C  
ATOM   8477  O   PHE F  32      51.924  19.806  21.417  1.00165.71           O  
ATOM   8478  CB  PHE F  32      50.733  18.637  18.894  1.00165.68           C  
ATOM   8479  CG  PHE F  32      50.199  18.694  17.488  1.00165.64           C  
ATOM   8480  CD1 PHE F  32      49.248  17.775  17.059  1.00165.64           C  
ATOM   8481  CD2 PHE F  32      50.637  19.667  16.596  1.00165.67           C  
ATOM   8482  CE1 PHE F  32      48.742  17.823  15.762  1.00165.67           C  
ATOM   8483  CE2 PHE F  32      50.138  19.724  15.298  1.00165.69           C  
ATOM   8484  CZ  PHE F  32      49.188  18.799  14.881  1.00165.69           C  
ATOM   8485  N   CYS F  33      53.566  18.417  20.767  1.00165.92           N  
ATOM   8486  CA  CYS F  33      54.075  18.197  22.119  1.00166.10           C  
ATOM   8487  C   CYS F  33      54.375  19.498  22.866  1.00166.19           C  
ATOM   8488  O   CYS F  33      54.566  19.493  24.082  1.00166.20           O  
ATOM   8489  CB  CYS F  33      55.330  17.311  22.063  1.00166.36           C  
ATOM   8490  SG  CYS F  33      56.125  16.958  23.669  1.00166.61           S  
ATOM   8491  N   SER F  34      54.402  20.612  22.141  1.00166.01           N  
ATOM   8492  CA  SER F  34      54.679  21.907  22.752  1.00165.89           C  
ATOM   8493  C   SER F  34      53.406  22.568  23.266  1.00165.83           C  
ATOM   8494  O   SER F  34      53.458  23.427  24.141  1.00165.86           O  
ATOM   8495  CB  SER F  34      55.351  22.840  21.744  1.00165.84           C  
ATOM   8496  OG  SER F  34      54.463  23.170  20.691  1.00165.64           O  
ATOM   8497  N   SER F  35      52.265  22.166  22.718  1.00165.74           N  
ATOM   8498  CA  SER F  35      50.986  22.737  23.122  1.00165.72           C  
ATOM   8499  C   SER F  35      50.026  21.684  23.671  1.00165.60           C  
ATOM   8500  O   SER F  35      49.534  21.807  24.792  1.00165.58           O  
ATOM   8501  CB  SER F  35      50.340  23.455  21.935  1.00165.70           C  
ATOM   8502  OG  SER F  35      50.176  22.574  20.839  1.00165.80           O  
ATOM   8503  N   ARG F  36      49.764  20.650  22.878  1.00165.50           N  
ATOM   8504  CA  ARG F  36      48.860  19.578  23.285  1.00165.50           C  
ATOM   8505  C   ARG F  36      49.468  18.693  24.368  1.00165.65           C  
ATOM   8506  O   ARG F  36      48.748  18.118  25.183  1.00165.61           O  
ATOM   8507  CB  ARG F  36      48.485  18.713  22.079  1.00165.23           C  
ATOM   8508  CG  ARG F  36      47.771  19.463  20.962  1.00164.86           C  
ATOM   8509  CD  ARG F  36      47.365  18.524  19.830  1.00164.49           C  
ATOM   8510  NE  ARG F  36      46.700  19.231  18.737  1.00164.16           N  
ATOM   8511  CZ  ARG F  36      46.204  18.641  17.653  1.00164.01           C  
ATOM   8512  NH1 ARG F  36      46.293  17.325  17.508  1.00163.91           N  
ATOM   8513  NH2 ARG F  36      45.619  19.367  16.711  1.00163.94           N  
ATOM   8514  N   GLY F  37      50.793  18.582  24.365  1.00165.72           N  
ATOM   8515  CA  GLY F  37      51.472  17.763  25.353  1.00165.90           C  
ATOM   8516  C   GLY F  37      52.121  16.530  24.755  1.00166.17           C  
ATOM   8517  O   GLY F  37      51.988  16.263  23.562  1.00166.04           O  
ATOM   8518  N   LYS F  38      52.827  15.773  25.587  1.00166.48           N  
ATOM   8519  CA  LYS F  38      53.497  14.562  25.134  1.00166.67           C  
ATOM   8520  C   LYS F  38      52.473  13.503  24.748  1.00166.95           C  
ATOM   8521  O   LYS F  38      51.455  13.350  25.415  1.00167.15           O  
ATOM   8522  CB  LYS F  38      54.399  14.018  26.244  1.00166.76           C  
ATOM   8523  CG  LYS F  38      55.457  14.995  26.720  1.00166.71           C  
ATOM   8524  CD  LYS F  38      56.313  14.389  27.817  1.00166.55           C  
ATOM   8525  CE  LYS F  38      57.391  15.355  28.268  1.00166.43           C  
ATOM   8526  NZ  LYS F  38      58.236  14.768  29.339  1.00166.27           N  
ATOM   8527  N   VAL F  39      52.742  12.775  23.669  1.00167.19           N  
ATOM   8528  CA  VAL F  39      51.835  11.725  23.220  1.00167.66           C  
ATOM   8529  C   VAL F  39      51.659  10.710  24.346  1.00167.37           C  
ATOM   8530  O   VAL F  39      52.628  10.341  25.005  1.00167.45           O  
ATOM   8531  CB  VAL F  39      52.396  10.994  21.989  1.00167.44           C  
ATOM   8532  CG1 VAL F  39      51.391   9.977  21.486  1.00167.52           C  
ATOM   8533  CG2 VAL F  39      52.734  11.995  20.904  1.00167.58           C  
ATOM   8534  N   VAL F  40      50.429  10.260  24.568  1.00167.75           N  
ATOM   8535  CA  VAL F  40      50.165   9.293  25.629  1.00168.04           C  
ATOM   8536  C   VAL F  40      49.766   7.933  25.080  1.00168.23           C  
ATOM   8537  O   VAL F  40      48.938   7.833  24.179  1.00168.32           O  
ATOM   8538  CB  VAL F  40      49.045   9.782  26.572  1.00167.97           C  
ATOM   8539  CG1 VAL F  40      48.817   8.767  27.678  1.00167.93           C  
ATOM   8540  CG2 VAL F  40      49.417  11.126  27.166  1.00168.03           C  
ATOM   8541  N   GLU F  41      50.363   6.886  25.637  1.00168.55           N  
ATOM   8542  CA  GLU F  41      50.080   5.520  25.219  1.00168.83           C  
ATOM   8543  C   GLU F  41      49.943   4.619  26.443  1.00169.01           C  
ATOM   8544  O   GLU F  41      50.773   4.663  27.351  1.00169.22           O  
ATOM   8545  CB  GLU F  41      51.205   5.003  24.322  1.00168.65           C  
ATOM   8546  CG  GLU F  41      51.009   3.575  23.839  1.00168.41           C  
ATOM   8547  CD  GLU F  41      52.156   3.092  22.971  1.00168.26           C  
ATOM   8548  OE1 GLU F  41      52.404   3.708  21.914  1.00168.14           O  
ATOM   8549  OE2 GLU F  41      52.811   2.096  23.345  1.00168.22           O  
ATOM   8550  N   LEU F  42      48.896   3.803  26.463  1.00169.35           N  
ATOM   8551  CA  LEU F  42      48.656   2.901  27.582  1.00169.57           C  
ATOM   8552  C   LEU F  42      48.307   1.512  27.061  1.00169.65           C  
ATOM   8553  O   LEU F  42      47.436   1.369  26.204  1.00169.55           O  
ATOM   8554  CB  LEU F  42      47.510   3.438  28.440  1.00169.71           C  
ATOM   8555  CG  LEU F  42      47.642   4.893  28.900  1.00169.88           C  
ATOM   8556  CD1 LEU F  42      46.384   5.319  29.635  1.00170.02           C  
ATOM   8557  CD2 LEU F  42      48.859   5.039  29.795  1.00170.08           C  
ATOM   8558  N   GLY F  43      48.983   0.489  27.578  1.00169.97           N  
ATOM   8559  CA  GLY F  43      48.711  -0.863  27.122  1.00170.40           C  
ATOM   8560  C   GLY F  43      49.180  -1.976  28.041  1.00170.72           C  
ATOM   8561  O   GLY F  43      49.346  -1.775  29.244  1.00170.79           O  
ATOM   8562  N   CYS F  44      49.394  -3.156  27.462  1.00171.06           N  
ATOM   8563  CA  CYS F  44      49.837  -4.332  28.209  1.00171.23           C  
ATOM   8564  C   CYS F  44      51.074  -4.978  27.604  1.00171.67           C  
ATOM   8565  O   CYS F  44      51.317  -4.876  26.401  1.00171.75           O  
ATOM   8566  CB  CYS F  44      48.709  -5.363  28.276  1.00170.99           C  
ATOM   8567  SG  CYS F  44      47.253  -4.694  29.126  1.00170.59           S  
ATOM   8568  N   ALA F  45      51.851  -5.650  28.447  1.00172.29           N  
ATOM   8569  CA  ALA F  45      53.061  -6.317  27.995  1.00172.90           C  
ATOM   8570  C   ALA F  45      53.634  -7.198  29.095  1.00173.30           C  
ATOM   8571  O   ALA F  45      53.653  -6.813  30.265  1.00173.39           O  
ATOM   8572  CB  ALA F  45      54.095  -5.286  27.562  1.00172.65           C  
ATOM   8573  N   ALA F  46      54.089  -8.386  28.713  1.00174.31           N  
ATOM   8574  CA  ALA F  46      54.679  -9.316  29.665  1.00175.29           C  
ATOM   8575  C   ALA F  46      55.975  -8.693  30.167  1.00175.71           C  
ATOM   8576  O   ALA F  46      56.208  -8.592  31.371  1.00176.00           O  
ATOM   8577  CB  ALA F  46      54.962 -10.650  28.989  1.00175.23           C  
ATOM   8578  N   THR F  47      56.812  -8.269  29.226  1.00176.41           N  
ATOM   8579  CA  THR F  47      58.083  -7.638  29.551  1.00177.00           C  
ATOM   8580  C   THR F  47      57.960  -6.138  29.324  1.00177.32           C  
ATOM   8581  O   THR F  47      57.613  -5.695  28.230  1.00177.46           O  
ATOM   8582  CB  THR F  47      59.216  -8.180  28.666  1.00176.90           C  
ATOM   8583  OG1 THR F  47      58.912  -7.919  27.291  1.00176.86           O  
ATOM   8584  CG2 THR F  47      59.375  -9.678  28.870  1.00176.86           C  
ATOM   8585  N   CYS F  48      58.241  -5.359  30.364  1.00177.85           N  
ATOM   8586  CA  CYS F  48      58.157  -3.908  30.274  1.00178.12           C  
ATOM   8587  C   CYS F  48      58.886  -3.405  29.028  1.00178.07           C  
ATOM   8588  O   CYS F  48      60.062  -3.705  28.821  1.00178.31           O  
ATOM   8589  CB  CYS F  48      58.754  -3.274  31.535  1.00178.46           C  
ATOM   8590  SG  CYS F  48      58.556  -1.468  31.622  1.00178.87           S  
ATOM   8591  N   PRO F  49      58.191  -2.629  28.178  1.00178.60           N  
ATOM   8592  CA  PRO F  49      58.775  -2.087  26.947  1.00178.33           C  
ATOM   8593  C   PRO F  49      60.040  -1.266  27.180  1.00178.43           C  
ATOM   8594  O   PRO F  49      60.124  -0.490  28.132  1.00178.50           O  
ATOM   8595  CB  PRO F  49      57.634  -1.254  26.366  1.00178.32           C  
ATOM   8596  CG  PRO F  49      56.903  -0.796  27.586  1.00178.26           C  
ATOM   8597  CD  PRO F  49      56.854  -2.058  28.411  1.00178.26           C  
ATOM   8598  N   SER F  50      61.021  -1.446  26.299  1.00178.79           N  
ATOM   8599  CA  SER F  50      62.290  -0.733  26.398  1.00178.99           C  
ATOM   8600  C   SER F  50      62.139   0.746  26.063  1.00179.17           C  
ATOM   8601  O   SER F  50      61.362   1.120  25.185  1.00179.20           O  
ATOM   8602  CB  SER F  50      63.323  -1.368  25.464  1.00178.98           C  
ATOM   8603  OG  SER F  50      62.855  -1.387  24.127  1.00179.04           O  
ATOM   8604  N   LYS F  51      62.892   1.582  26.770  1.00179.48           N  
ATOM   8605  CA  LYS F  51      62.845   3.021  26.555  1.00179.69           C  
ATOM   8606  C   LYS F  51      63.711   3.440  25.375  1.00179.93           C  
ATOM   8607  O   LYS F  51      64.840   2.978  25.227  1.00180.02           O  
ATOM   8608  CB  LYS F  51      63.317   3.759  27.811  1.00179.62           C  
ATOM   8609  CG  LYS F  51      63.433   5.267  27.634  1.00179.50           C  
ATOM   8610  CD  LYS F  51      64.048   5.935  28.854  1.00179.37           C  
ATOM   8611  CE  LYS F  51      64.229   7.431  28.631  1.00179.27           C  
ATOM   8612  NZ  LYS F  51      64.856   8.102  29.803  1.00179.19           N  
ATOM   8613  N   LYS F  52      63.169   4.315  24.535  1.00180.33           N  
ATOM   8614  CA  LYS F  52      63.891   4.824  23.376  1.00180.70           C  
ATOM   8615  C   LYS F  52      64.439   6.186  23.813  1.00180.71           C  
ATOM   8616  O   LYS F  52      63.896   6.809  24.726  1.00180.86           O  
ATOM   8617  CB  LYS F  52      62.931   4.971  22.191  1.00180.73           C  
ATOM   8618  CG  LYS F  52      63.583   4.855  20.820  1.00180.88           C  
ATOM   8619  CD  LYS F  52      62.541   4.822  19.710  1.00180.95           C  
ATOM   8620  CE  LYS F  52      63.189   4.679  18.340  1.00180.97           C  
ATOM   8621  NZ  LYS F  52      62.178   4.646  17.246  1.00180.83           N  
ATOM   8622  N   PRO F  53      65.523   6.665  23.177  1.00181.09           N  
ATOM   8623  CA  PRO F  53      66.123   7.957  23.529  1.00181.29           C  
ATOM   8624  C   PRO F  53      65.144   9.059  23.943  1.00181.38           C  
ATOM   8625  O   PRO F  53      65.210   9.571  25.063  1.00181.45           O  
ATOM   8626  CB  PRO F  53      66.903   8.316  22.272  1.00181.20           C  
ATOM   8627  CG  PRO F  53      67.413   6.983  21.838  1.00181.15           C  
ATOM   8628  CD  PRO F  53      66.195   6.088  21.997  1.00181.09           C  
ATOM   8629  N   TYR F  54      64.240   9.415  23.036  1.00181.56           N  
ATOM   8630  CA  TYR F  54      63.256  10.463  23.290  1.00181.70           C  
ATOM   8631  C   TYR F  54      62.020   9.989  24.049  1.00181.74           C  
ATOM   8632  O   TYR F  54      61.326  10.792  24.669  1.00181.71           O  
ATOM   8633  CB  TYR F  54      62.819  11.095  21.969  1.00181.85           C  
ATOM   8634  CG  TYR F  54      62.253  10.107  20.973  1.00182.00           C  
ATOM   8635  CD1 TYR F  54      63.056   9.115  20.411  1.00182.07           C  
ATOM   8636  CD2 TYR F  54      60.913  10.165  20.590  1.00182.08           C  
ATOM   8637  CE1 TYR F  54      62.541   8.206  19.489  1.00182.16           C  
ATOM   8638  CE2 TYR F  54      60.387   9.261  19.669  1.00182.17           C  
ATOM   8639  CZ  TYR F  54      61.207   8.284  19.122  1.00182.19           C  
ATOM   8640  OH  TYR F  54      60.696   7.388  18.208  1.00182.24           O  
ATOM   8641  N   GLU F  55      61.744   8.689  23.994  1.00181.78           N  
ATOM   8642  CA  GLU F  55      60.583   8.129  24.679  1.00181.83           C  
ATOM   8643  C   GLU F  55      60.707   8.174  26.200  1.00181.84           C  
ATOM   8644  O   GLU F  55      61.736   8.574  26.743  1.00181.92           O  
ATOM   8645  CB  GLU F  55      60.347   6.684  24.232  1.00181.79           C  
ATOM   8646  CG  GLU F  55      59.923   6.538  22.780  1.00181.75           C  
ATOM   8647  CD  GLU F  55      59.624   5.099  22.406  1.00181.75           C  
ATOM   8648  OE1 GLU F  55      59.269   4.847  21.235  1.00181.74           O  
ATOM   8649  OE2 GLU F  55      59.743   4.218  23.283  1.00181.78           O  
ATOM   8650  N   GLU F  56      59.643   7.755  26.876  1.00181.86           N  
ATOM   8651  CA  GLU F  56      59.596   7.741  28.332  1.00181.90           C  
ATOM   8652  C   GLU F  56      58.647   6.635  28.780  1.00181.80           C  
ATOM   8653  O   GLU F  56      57.428   6.797  28.726  1.00181.98           O  
ATOM   8654  CB  GLU F  56      59.097   9.091  28.841  1.00181.75           C  
ATOM   8655  CG  GLU F  56      59.022   9.201  30.346  1.00181.66           C  
ATOM   8656  CD  GLU F  56      58.454  10.531  30.789  1.00181.64           C  
ATOM   8657  OE1 GLU F  56      59.024  11.577  30.413  1.00181.61           O  
ATOM   8658  OE2 GLU F  56      57.438  10.532  31.512  1.00181.68           O  
ATOM   8659  N   VAL F  57      59.209   5.516  29.225  1.00181.73           N  
ATOM   8660  CA  VAL F  57      58.408   4.375  29.660  1.00181.69           C  
ATOM   8661  C   VAL F  57      58.191   4.339  31.172  1.00181.29           C  
ATOM   8662  O   VAL F  57      58.933   4.958  31.931  1.00181.31           O  
ATOM   8663  CB  VAL F  57      59.072   3.050  29.227  1.00181.70           C  
ATOM   8664  CG1 VAL F  57      58.128   1.887  29.475  1.00181.82           C  
ATOM   8665  CG2 VAL F  57      59.460   3.121  27.760  1.00181.83           C  
ATOM   8666  N   THR F  58      57.161   3.610  31.594  1.00181.03           N  
ATOM   8667  CA  THR F  58      56.824   3.462  33.007  1.00180.66           C  
ATOM   8668  C   THR F  58      55.925   2.241  33.173  1.00180.46           C  
ATOM   8669  O   THR F  58      54.853   2.174  32.574  1.00180.45           O  
ATOM   8670  CB  THR F  58      56.075   4.703  33.544  1.00180.67           C  
ATOM   8671  OG1 THR F  58      56.913   5.858  33.433  1.00180.67           O  
ATOM   8672  CG2 THR F  58      55.697   4.507  35.002  1.00180.62           C  
ATOM   8673  N   CYS F  59      56.364   1.278  33.980  1.00180.31           N  
ATOM   8674  CA  CYS F  59      55.586   0.063  34.211  1.00180.34           C  
ATOM   8675  C   CYS F  59      55.195  -0.132  35.672  1.00180.32           C  
ATOM   8676  O   CYS F  59      55.713   0.543  36.562  1.00180.45           O  
ATOM   8677  CB  CYS F  59      56.358  -1.165  33.719  1.00179.79           C  
ATOM   8678  SG  CYS F  59      56.563  -1.213  31.911  1.00179.28           S  
ATOM   8679  N   CYS F  60      54.270  -1.060  35.907  1.00180.62           N  
ATOM   8680  CA  CYS F  60      53.791  -1.363  37.254  1.00180.88           C  
ATOM   8681  C   CYS F  60      52.948  -2.637  37.272  1.00180.78           C  
ATOM   8682  O   CYS F  60      52.648  -3.206  36.220  1.00180.73           O  
ATOM   8683  CB  CYS F  60      52.982  -0.181  37.802  1.00181.19           C  
ATOM   8684  SG  CYS F  60      51.786   0.535  36.629  1.00181.70           S  
ATOM   8685  N   SER F  61      52.570  -3.079  38.469  1.00180.73           N  
ATOM   8686  CA  SER F  61      51.775  -4.294  38.623  1.00180.64           C  
ATOM   8687  C   SER F  61      50.369  -4.049  39.166  1.00180.60           C  
ATOM   8688  O   SER F  61      49.443  -4.797  38.859  1.00180.66           O  
ATOM   8689  CB  SER F  61      52.506  -5.279  39.537  1.00180.65           C  
ATOM   8690  OG  SER F  61      53.780  -5.608  39.013  1.00180.63           O  
ATOM   8691  N   THR F  62      50.211  -3.007  39.975  1.00180.45           N  
ATOM   8692  CA  THR F  62      48.912  -2.678  40.555  1.00180.68           C  
ATOM   8693  C   THR F  62      47.842  -2.521  39.475  1.00180.49           C  
ATOM   8694  O   THR F  62      48.153  -2.202  38.331  1.00180.54           O  
ATOM   8695  CB  THR F  62      48.987  -1.369  41.361  1.00180.33           C  
ATOM   8696  OG1 THR F  62      49.999  -1.487  42.367  1.00180.25           O  
ATOM   8697  CG2 THR F  62      47.652  -1.073  42.029  1.00180.21           C  
ATOM   8698  N   ASP F  63      46.584  -2.750  39.841  1.00180.56           N  
ATOM   8699  CA  ASP F  63      45.480  -2.617  38.894  1.00180.78           C  
ATOM   8700  C   ASP F  63      45.196  -1.142  38.621  1.00180.91           C  
ATOM   8701  O   ASP F  63      45.136  -0.332  39.547  1.00180.84           O  
ATOM   8702  CB  ASP F  63      44.218  -3.295  39.442  1.00180.65           C  
ATOM   8703  CG  ASP F  63      44.328  -4.809  39.465  1.00180.60           C  
ATOM   8704  OD1 ASP F  63      43.363  -5.467  39.909  1.00180.55           O  
ATOM   8705  OD2 ASP F  63      45.374  -5.344  39.039  1.00180.57           O  
ATOM   8706  N   LYS F  64      45.022  -0.802  37.347  1.00180.89           N  
ATOM   8707  CA  LYS F  64      44.753   0.575  36.947  1.00181.29           C  
ATOM   8708  C   LYS F  64      45.861   1.504  37.434  1.00181.54           C  
ATOM   8709  O   LYS F  64      45.599   2.632  37.848  1.00181.45           O  
ATOM   8710  CB  LYS F  64      43.410   1.044  37.513  1.00180.93           C  
ATOM   8711  CG  LYS F  64      42.211   0.252  37.020  1.00180.69           C  
ATOM   8712  CD  LYS F  64      40.915   0.815  37.583  1.00180.58           C  
ATOM   8713  CE  LYS F  64      39.710   0.035  37.084  1.00180.53           C  
ATOM   8714  NZ  LYS F  64      38.434   0.593  37.608  1.00180.54           N  
ATOM   8715  N   CYS F  65      47.100   1.025  37.377  1.00181.97           N  
ATOM   8716  CA  CYS F  65      48.248   1.810  37.818  1.00182.86           C  
ATOM   8717  C   CYS F  65      48.835   2.652  36.691  1.00183.36           C  
ATOM   8718  O   CYS F  65      49.705   3.488  36.924  1.00183.39           O  
ATOM   8719  CB  CYS F  65      49.331   0.885  38.379  1.00182.43           C  
ATOM   8720  SG  CYS F  65      50.010  -0.287  37.162  1.00182.11           S  
ATOM   8721  N   ASN F  66      48.353   2.434  35.471  1.00184.13           N  
ATOM   8722  CA  ASN F  66      48.836   3.177  34.310  1.00185.13           C  
ATOM   8723  C   ASN F  66      47.726   4.037  33.714  1.00185.70           C  
ATOM   8724  O   ASN F  66      47.334   3.852  32.564  1.00185.69           O  
ATOM   8725  CB  ASN F  66      49.358   2.205  33.249  1.00185.12           C  
ATOM   8726  CG  ASN F  66      48.263   1.327  32.671  1.00185.21           C  
ATOM   8727  OD1 ASN F  66      47.503   0.700  33.409  1.00185.28           O  
ATOM   8728  ND2 ASN F  66      48.186   1.276  31.346  1.00185.29           N  
ATOM   8729  N   PRO F  67      47.209   4.997  34.490  1.00186.54           N  
ATOM   8730  CA  PRO F  67      46.138   5.867  34.006  1.00187.12           C  
ATOM   8731  C   PRO F  67      46.645   7.010  33.145  1.00187.75           C  
ATOM   8732  O   PRO F  67      47.848   7.193  32.977  1.00187.90           O  
ATOM   8733  CB  PRO F  67      45.513   6.369  35.296  1.00187.02           C  
ATOM   8734  CG  PRO F  67      46.720   6.565  36.154  1.00186.82           C  
ATOM   8735  CD  PRO F  67      47.524   5.299  35.899  1.00186.61           C  
ATOM   8736  N   HIS F  68      45.708   7.775  32.601  1.00188.62           N  
ATOM   8737  CA  HIS F  68      46.037   8.922  31.775  1.00189.55           C  
ATOM   8738  C   HIS F  68      46.582   9.992  32.711  1.00189.77           C  
ATOM   8739  O   HIS F  68      46.088  10.160  33.824  1.00190.02           O  
ATOM   8740  CB  HIS F  68      44.779   9.430  31.070  1.00189.58           C  
ATOM   8741  CG  HIS F  68      45.001  10.652  30.237  1.00189.76           C  
ATOM   8742  ND1 HIS F  68      45.915  10.695  29.207  1.00189.84           N  
ATOM   8743  CD2 HIS F  68      44.414  11.871  30.268  1.00189.84           C  
ATOM   8744  CE1 HIS F  68      45.881  11.887  28.640  1.00189.88           C  
ATOM   8745  NE2 HIS F  68      44.978  12.620  29.265  1.00189.88           N  
ATOM   8746  N   PRO F  69      47.617  10.725  32.278  1.00190.45           N  
ATOM   8747  CA  PRO F  69      48.207  11.776  33.110  1.00190.59           C  
ATOM   8748  C   PRO F  69      47.180  12.726  33.725  1.00190.87           C  
ATOM   8749  O   PRO F  69      47.493  13.469  34.654  1.00190.94           O  
ATOM   8750  CB  PRO F  69      49.148  12.480  32.143  1.00190.67           C  
ATOM   8751  CG  PRO F  69      49.632  11.348  31.295  1.00190.62           C  
ATOM   8752  CD  PRO F  69      48.354  10.590  31.009  1.00190.51           C  
ATOM   8753  N   LYS F  70      45.954  12.695  33.209  1.00191.12           N  
ATOM   8754  CA  LYS F  70      44.896  13.562  33.716  1.00191.25           C  
ATOM   8755  C   LYS F  70      43.832  12.797  34.503  1.00191.35           C  
ATOM   8756  O   LYS F  70      42.692  13.248  34.616  1.00191.47           O  
ATOM   8757  CB  LYS F  70      44.241  14.324  32.559  1.00191.28           C  
ATOM   8758  CG  LYS F  70      45.219  15.128  31.706  1.00191.29           C  
ATOM   8759  CD  LYS F  70      45.930  16.215  32.507  1.00191.31           C  
ATOM   8760  CE  LYS F  70      44.989  17.348  32.882  1.00191.33           C  
ATOM   8761  NZ  LYS F  70      44.487  18.065  31.679  1.00191.42           N  
ATOM   8762  N   GLN F  71      44.207  11.640  35.040  1.00191.46           N  
ATOM   8763  CA  GLN F  71      43.289  10.826  35.835  1.00191.55           C  
ATOM   8764  C   GLN F  71      43.934  10.411  37.152  1.00191.41           C  
ATOM   8765  O   GLN F  71      44.924  11.001  37.584  1.00191.49           O  
ATOM   8766  CB  GLN F  71      42.858   9.569  35.072  1.00191.53           C  
ATOM   8767  CG  GLN F  71      41.916   9.819  33.909  1.00191.55           C  
ATOM   8768  CD  GLN F  71      40.991   8.641  33.656  1.00191.55           C  
ATOM   8769  OE1 GLN F  71      40.143   8.318  34.487  1.00191.55           O  
ATOM   8770  NE2 GLN F  71      41.154   7.991  32.510  1.00191.51           N  
ATOM   8771  N   ARG F  72      43.368   9.389  37.787  1.00191.38           N  
ATOM   8772  CA  ARG F  72      43.882   8.890  39.057  1.00191.29           C  
ATOM   8773  C   ARG F  72      44.149   7.392  38.980  1.00191.26           C  
ATOM   8774  O   ARG F  72      43.364   6.643  38.400  1.00191.24           O  
ATOM   8775  CB  ARG F  72      42.877   9.159  40.177  1.00191.26           C  
ATOM   8776  CG  ARG F  72      41.499   8.573  39.912  1.00191.27           C  
ATOM   8777  CD  ARG F  72      40.614   8.552  41.156  1.00191.37           C  
ATOM   8778  NE  ARG F  72      40.459   9.867  41.774  1.00191.50           N  
ATOM   8779  CZ  ARG F  72      41.325  10.401  42.631  1.00191.57           C  
ATOM   8780  NH1 ARG F  72      42.417   9.733  42.980  1.00191.61           N  
ATOM   8781  NH2 ARG F  72      41.097  11.604  43.142  1.00191.61           N  
ATOM   8782  N   PRO F  73      45.266   6.936  39.565  1.00191.44           N  
ATOM   8783  CA  PRO F  73      45.617   5.514  39.554  1.00191.19           C  
ATOM   8784  C   PRO F  73      44.523   4.645  40.178  1.00191.37           C  
ATOM   8785  O   PRO F  73      44.032   3.723  39.491  1.00191.37           O  
ATOM   8786  CB  PRO F  73      46.915   5.478  40.354  1.00191.33           C  
ATOM   8787  CG  PRO F  73      47.538   6.797  40.020  1.00191.30           C  
ATOM   8788  CD  PRO F  73      46.361   7.738  40.137  1.00191.28           C  
ATOM   8789  OXT PRO F  73      44.167   4.897  41.349  1.00191.41           O  
TER    8790      PRO F  73                                                           
END   '''

pro=pdb.ProteinS(file=realtarget,name='REAL',path=os.getcwd()+os.sep+'screen'+os.sep+screenlist[num]+'.pdb', debug=True, 
	precon=pdb.screxp, preconargs=(['ESCHERICHIA COLI'],),
	atmcon=pdb.scrsheet,
	score=scoring, 
	scoreargs=(fmk.longtail(100,100,300),60,0,True))

"""