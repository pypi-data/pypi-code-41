#!python
from __future__ import division
import sys,os,re
import cairo,pysam
from  collections import defaultdict
import collections,commands,numpy
from math import pi as p
def visual_circle_pacbio(clu,allgene,genename,refGenes,path,apapos,atipos,nat,difflib,mapdict,conf,cf,bamlist,strand,RI,SE,A3SS,A5SS,circlenames):
	def Wig_count(bamfile,Gene_coordinate,strand,num,cf):
		wig=dict()
		typpd=dict()
		reads=commands.getoutput("samtools view %s %s"%(bamfile,Gene_coordinate))
		##############
		#strand
		for i in reads.split('\n'):
			i=i.strip("Error,")
			dd=i.split()
			if not dd:
				continue
			if i.startswith("[main_samview]") or i.startswith("Warning"):
				continue
			(flag,pos,cigar,seq)=(int(dd[1]),int(dd[3]),dd[5],dd[9])
			Strand_Specificity=cf.get("Wig option","Strand_Specificity")
			if Strand_Specificity=='True':
			#print (flag&16)==0,strand
				if (flag&16)==0 and strand=='-':
					continue
				if (flag&16)==16 and strand=='+':
					continue
	#strand end
	#################
		#Mapping position
			if 'D' in cigar or 'I' in cigar:
				continue
			if 'N' in cigar:
				ele=[int(x) for y,x in enumerate(re.split('M|N',cigar)) if int(y)!=(len(re.split('M|N',cigar))-1)]
				#print ele
				#print i
				for j in range(0,len(ele),2):
					if j==0:
						for k in range(0,ele[0]):
							if k+pos not in wig:
								wig[k+pos]=1
							else:
								wig[k+pos]+=1
						#print k+pos,
					else:
						for k in range(sum(x-1 for x in ele[:j]),sum(x-1 for x in ele[:j+1])+1):
							if k+pos not in wig:
								wig[k+pos]=1
							else:
								wig[k+pos]+=1
				continue
		##Mapping position 
		#########################
		#All position
			for j in range(len(seq)):
				if j+pos not in wig:
					wig[j+pos]=1
				else:
					wig[j+pos]+=1
	##############
	##Normailiation
		for j in wig:
			wig[j]*=10000000
			wig[j]/=num
		sortwig=sorted(wig.iteritems(), key=lambda d:d[0])
		###Normaliation END	
		return wig
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
				e,s=int(e),int(s)
				if strand =='.':
					cr.set_source_rgb(0.18,0.55,0.34)
					cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
					cr.fill()
				if strand == '+':
					if nat=="True":
						if info[5].startswith("cufflinks"):
							cr.set_source_rgb(0.18,0.55,0.34)
						else:
							#(r,g,b)=hex2rgb(conf["nat_f"])
							(r,g,b)=hex2rgb(conf["exon"])
							cr.set_source_rgb(r,g,b)
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
					#(r,g,b)=hex2rgb(conf["nat_r"])
					(r,g,b)=hex2rgb(conf["exon"])
					cr.set_source_rgb(r,g,b)
					if info[5].startswith("cufflinks"):
						cr.set_source_rgb(0.18,0.55,0.34)
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
	def hex2rgb(hexstring, digits=2):
		if isinstance(hexstring, (tuple, list)):
			return hexstring
		top = float(int(digits * 'f', 16))
		r = int(hexstring[1:digits+1], 16)
		g = int(hexstring[digits+1:digits*2+1], 16)
		b = int(hexstring[digits*2+1:digits*3+1], 16)
		return r / top, g / top, b / top
	def atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,types):
		global hh
		print atipos,apapos
		strand=types
		hh+=20+10*max(len(atinum),len(apanum))
		#########
		cr.set_font_size(8)
		cr.set_source_rgb(0,0,0)
		cr.move_to(30,hh)
		cr.show_text(types)
		cr.fill()
	#########
		atiline=2.5*arrayline
		ih=0
		for pp in atipos.split(","):
			if atipos=="NULL":
				break
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
	def ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,posnum,tpd):
		##########################
		##########################
		global hh,ashigh
		showhigh=10
		#hh+=10+1*h/2
		arraylineas=1.5*arrayline
		cr.set_font_size(8)
		#RI,SE,A3SS,A5SS
		if RI[clu]:
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
			for irsub in RI[clu]:
				#print irsub
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
				########
				## arear
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.rel_line_to(0,50-ashigh)
				cr.rel_line_to((e-s)*scale,0)
				cr.rel_line_to(0,ashigh-50)
				cr.close_path()
				cr.stroke()
				#########
			#############stick end
		#######################################################################################
		if SE[clu]:
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
			for essub in SE[clu]:
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
				## arear
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.rel_line_to(0,50-ashigh)
				cr.rel_line_to((e-s)*scale,0)
				cr.rel_line_to(0,ashigh-50)
				cr.close_path()
				cr.stroke()
				#########
		########################################################################################
		if A3SS[clu]:
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
			for altasub in A3SS[clu]:
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
				#######
				## arear
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.rel_line_to(0,50-ashigh)
				cr.rel_line_to((e-s)*scale,0)
				cr.rel_line_to(0,ashigh-50)
				cr.close_path()
				cr.stroke()
				#########
	###########################################################################################
		if A5SS[clu]:
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
			for altdsub in A5SS[clu]:
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
				######
				## arear
				cr.move_to(50+(s-minpos)*scale,ashigh)
				cr.rel_line_to(0,50-ashigh)
				cr.rel_line_to((e-s)*scale,0)
				cr.rel_line_to(0,ashigh-50)
				cr.close_path()
				cr.stroke()
				#########
	##############################################################################################
		"""
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
				"""
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
	def wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib,fpkmcal):
		global hh
		hh+=20
		Strand_Specificity=cf.get("Wig option","Strand_Specificity")
		strand=sort_dict[0].split()[4]
		#print strand
		high1=hh
		#Scan_length=int(cf.get("DE APA option","Scan_length"))
		if difflib!="NULL":
#			apapos=difflib[0][-1]
			libpos=dict()
		wiggdict= defaultdict(dict)
		wignormlib=cf.get("Wig option","Group")
		create=locals()
		for wignormlibed in wignormlib.split():
			create[wignormlibed]=defaultdict(dict)
			for x in wignormlibed.split("_"):
				wiggdict[x.lower()]=wignormlibed
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
							eval(wiggdict[i])["+"][max(wigggforward[x] for x in wigggforward)]=1
						if wigggreverse:
							eval(wiggdict[i])["-"][max(wigggreverse[x] for x in wigggreverse)]=1
					else:
						wiggg=Wig_count(filee,Gene_coordinate,strand[0],bamlist[i],cf)
						if not wiggg:
							continue
						maxx=max(wiggg[x] for x in wiggg)
						eval(wiggdict[i])[max(wiggg[x] for x in wiggg)]=1
			for i in conf:
				if not i.startswith("lib"):
					continue
				(tpp,filee,rgb)=conf[i].strip('\n').split()
				(r,g,b)=hex2rgb(rgb)
				if nat!="True" or (nat=="True" and Strand_Specificity!="True"):
					wiggg=Wig_count(filee,Gene_coordinate,strand[0],bamlist[i],cf)
				elif nat=="True" and Strand_Specificity=="True":
					wigggforward=Wig_count(filee,Gene_coordinate,"+",bamlist[i],cf)
					wigggreverse=Wig_count(filee,Gene_coordinate,"-",bamlist[i],cf)
				hh+=40
				if nat!="True" or (nat=="True" and Strand_Specificity!="True"):	
					#if not wiggg:
					#	continue
					scaleh=32/(max(eval(wiggdict[i]).keys()))
					cr.set_source_rgb(float(r),float(g),float(b))
					for gp in wiggg:
						if gp<minpos or maxpos<gp:
							continue
						#print 50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh
						cr.rectangle(50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh)
						cr.fill()
					cr.set_source_rgb(0,0,0)
					cr.move_to(8,hh)
					cr.set_font_size(7)
					cr.save()
					cr.rotate(p*270/180)
					cr.show_text(tpp)
					cr.fill()
					cr.restore()
					cr.move_to(50-2,hh)
					maxacnum=max(eval(wiggdict[i]))
					cr.line_to(50-2,hh-maxacnum*scaleh)
					cr.stroke()
						####################
					aesmin=maxacnum/4
					for stick in range(4+1):
						cr.move_to(50-2,hh-aesmin*scaleh*stick)
						cr.line_to(50-2-2,hh-aesmin*scaleh*stick)
						cr.stroke()
						cr.move_to(50-2-2-4*len(str("%.1f"%(aesmin*stick))),hh-aesmin*scaleh*stick+0.4*h)
						cr.set_font_size(5)
						cr.show_text("%.1f"%(aesmin*stick))
					##libpos
					#if cf.get("DE APA option","DE")=="True":
					if difflib!="NULL":
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
			if difflib=="NULL":
				return 0
			xlen=0
			cr.set_source_rgb(1,0,0)
			cr.set_line_width(1.5*arrayline)
			####
			for circle_pos in circlenames:
				#print re.split("\||:|-",circle_pos)
				ss,ee=[int(x) for x in re.split("\||:|-",circle_pos)[1:]]
				middle_pos=(ss+ee)/2
				#print libpos
				for strings in difflib["%s|%s"%(genename,circle_pos)]:
					#print strings
					lib1,lib2=[x.lower() for x in strings.split(":")]
					xlen+=6
					if not lib1 in libpos:
						libpos[lib1]=libpos[lib2]
					if not lib2 in libpos:
						libpos[lib2]=libpos[lib1]
					cr.move_to(50+(middle_pos-minpos)*scale,libpos[lib1])
					cr.line_to(450,libpos[lib1])
					cr.stroke()
					cr.move_to(450,libpos[lib1])
					cr.rel_line_to(xlen,0)
					cr.rel_line_to(0,libpos[lib2]-libpos[lib1])
					cr.rel_line_to(-xlen,0)
					cr.stroke()
				##################
			####
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
			(r,g,b)=hex2rgb(conf["exon"])
			cr.set_source_rgb(r,g,b)
			cr.fill()
			cr.move_to(50+10+2,bar_high)
			cr.set_source_rgb(0,0,0)
			cr.show_text("Pacbio Exon")
			cr.fill()
			"""
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
			"""
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
		##################
		## circle
		#s,e=50+50*scale,50+50*scale+20
		s,e=50,50+20
		ashigh=bar_high+10*4
		circlelibh=0
		(x1,y1)=(s,ashigh-2)
		(x2,y2)=((e+s)/2,ashigh-10-circlelibh)
		(x3,y3)=(e,ashigh-2)
		circle_hex="#008000"
		(r,g,b)=hex2rgb(circle_hex)
		cr.set_source_rgb(r,g,b)
		cr.move_to(x1,y1)
		cr.curve_to(x1,y1,x2,y2,x3,y3)
		cr.stroke()
		cr.set_source_rgb(0,0,0)
		cr.move_to(x3+2,y3)
		cr.show_text("Circle")
		cr.fill()
		cr.move_to(250-30,20)
		cr.show_text("%s"%(genename))
		cr.fill()
	#######################################
	def annotation_smart(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene):
		global hh
		if len(refGenes)!=0:
			for annogene in genename.split("_"):
				for linee in allgene["%s:%s"%(chroms,annogene)]:
					hh+=200*2/(len(sort_dict)+23)
					info=linee.split()
					strand=info[3]
					#######################
					cds=[]
					exon=[]
					#######################
					for subele in info[5:]:
						if subele.startswith("C"):
							s,e=[int(i) for i in subele.split(":")[1:]]
							for pos in range(s,e+1):
								cds.append(pos)
						else:
							s,e=[int(i) for i in subele.split(":")]
							for pos in range(s,e+1):
								exon.append(pos)
					########################
					exon=sorted(exon)
					for index,pos in enumerate(exon):
						if not pos in cds:
							(r,g,b)=hex2rgb(conf["utr"])
							cr.set_source_rgb(r,g,b)
						else:
							(r,g,b)=hex2rgb(conf["cds"])
							cr.set_source_rgb(r,g,b)
						cr.rectangle(50+(pos-0.5-minpos)*scale,hh,1*scale,h)
						cr.fill()
						if index!=0:
							cr.set_line_width(line)
							cr.move_to(50+(exon[index-1]+0.5-minpos)*scale,hh+1*h/2)
							cr.line_to(50+(pos-0.5-minpos)*scale,hh+1*h/2)
							cr.stroke()
						cr.set_source_rgb(0,0,0)
						if strand=="-" and index==0:
							cr.set_line_width(arrayline)
							cr.move_to(50+(pos-0.5-minpos)*scale,hh+1*h/2)
							cr.line_to(50+(pos-0.5-minpos)*scale-8,hh+1*h/2)
							cr.stroke()
							cr.move_to(50+(pos-0.5-minpos)*scale-8,hh+1*h/2)
							cr.rel_line_to(2,-0.5)
							cr.rel_line_to(0,1)
							cr.close_path()
							cr.fill_preserve ()
							cr.stroke()
						if strand=="+" and index==len(exon)-1:
							cr.set_line_width(arrayline)
							cr.move_to(50+(pos+0.5-minpos)*scale,hh+1*h/2)
							cr.line_to(50+(pos+0.5-minpos)*scale+8,hh+1*h/2)
							cr.stroke()
							cr.move_to(50+(pos+0.5-minpos)*scale+8,hh+1*h/2)
							cr.rel_line_to(-2,-0.5)
							cr.rel_line_to(0,1)
							cr.close_path()
							cr.fill_preserve()
							cr.stroke()
	def annotation(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene):
		global hh
		if len(refGenes)!=0:
			for annogene in genename.split("_"):
				for linee in allgene["%s:%s"%(chroms,annogene)]:
					hh+=200*2/(len(sort_dict)+23)
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
					finalst=len(info)
					utrmin.append(minpos)
					utrmax.append(maxpos)
					for st in range(5,finalst):
						(s,e)=info[st].split(':')
						(s,e)=(int(s),int(e))
						if strand == '+':
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
							cr.fill()
							if  st != (finalst-1):
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
							cr.set_source_rgb(0,0,0)
							cr.rectangle(50+(s-minpos)*scale,hh,(e-s)*scale,h)
							cr.fill()
							if st==5:
                                                                cr.set_source_rgb(0,0,0)
                 						cr.set_line_width(arrayline)
								cr.move_to(50+(s-minpos)*scale,hh+1*h/2)
								cr.line_to(50+(s-minpos)*scale-8,hh+1*h/2)
								cr.stroke()
								cr.line_to(50+(s-minpos)*scale-8,hh+1*h/2)
								cr.rel_line_to(2,-0.5)
								cr.rel_line_to(0,1)
                                      				cr.close_path()
                             					cr.fill_preserve ()
								cr.stroke()
							##################
							if st!=(finalst-1):
								(sn,en)=info[st+1].split(':')
								sn=int(sn)
								en=int(en)
								cr.set_source_rgb(0,0,0)
								cr.set_line_width(line)
								cr.move_to(50+(e-minpos)*scale,hh+1*h/2)
								cr.line_to(50+(sn-minpos)*scale,hh+1*h/2)
								cr.stroke()
							##################
	###################################
	def circle_plot(cr,minpos,maxpos,scale,genename,arrayline):
		global ashigh
		circlelibh=0
		circle_line=2*arrayline
		circle_hex="#008000"
		line_hex="#BFBFBF"
		ashigh+=40
		cr.set_source_rgb(0,0,0)
		cr.move_to(40,ashigh)
		cr.set_font_size(8)
		cr.save()
		cr.rotate(p*270/180)
		cr.show_text("Circle")
		cr.fill()
		cr.restore()
		###################################
		cr.set_source_rgb(0,0,0)
		cr.set_line_width(1)
		cr.move_to(50,ashigh)
		cr.line_to(450,ashigh)
		cr.stroke()
		cr.set_line_width(0.5)
		for stick in range(10+1):
			cr.move_to(50+(posnum*stick)*scale,ashigh)
			cr.line_to(50+(posnum*stick)*scale,ashigh+4)
			cr.stroke()
		###################################
		##################
		for item in circlenames:
			chro,s,e=re.split(":|-",item)
			s,e=int(s),int(e)
			circlelibh+=15
			(r,g,b)=hex2rgb(circle_hex)
			cr.set_source_rgb(r,g,b)
			cr.set_line_width(circle_line)
			(x1,y1)=(50+(s-minpos)*scale,ashigh-2)
			(x2,y2)=(50+((e+s)/2-minpos)*scale,ashigh-2-circlelibh)
			(x3,y3)=(50+(e-minpos)*scale,ashigh-2)
			cr.move_to(x1,y1)
			cr.curve_to(x1,y1,x2,y2,x3,y3)
			cr.stroke()
			####### two lines
			(r,g,b)=hex2rgb(line_hex)
			cr.set_source_rgb(r,g,b)
			cr.move_to(x1,80)
			cr.line_to(x1,y1)
			cr.stroke()
			cr.move_to(x3,80)
			cr.line_to(x3,y3)
			cr.stroke()
			######## line ends
	###################################
	global hh,ashigh,chroms
	wiggg=dict()
	for i in [clu]:
		minpos  = min(int(x.split()[2]) for x in mapdict[i])
		maxpos  = max(int(x.split()[3]) for x in mapdict[i])
		minpos=int(minpos)
		maxpos=int(maxpos)
		gene=i.split(';')[0]
		chroms=gene
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
		###############
		atinum=[]
		if atipos:
			for subati in atipos.split(","):
				atinum.append(subati)
		else:
			atipos="NULL"
		#########################################3
		apanum=[]
		if apapos:
			for subnum in apapos.split(","):
				apanum.append(subnum)
		else:
			apapos="NULL"
		asnum=0
		#for subas in (ir,es,alta,altd,altp):
		#	if subas!="NULL":
		#		asnum+=1
		asnum=4
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
		#################################################
		surface = cairo.PDFSurface("%s/Graph/%s/%s.pdf"%(Output_dir,path,genename), 500, hight_of)
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
		##example
		if len(refGenes)!=0: 
			#annomin=min(int(str(reg).split()[-3]) for reg in refGenes)
			#annomax=max(int(str(reg).split()[-1]) for reg in refGenes)
			annomin=min(reg[-2] for reg in refGenes)
			annomax=max(reg[-1] for reg in refGenes)
			minpos=min(annomin,minpos)
			maxpos=max(annomax,maxpos)
		scale=400/(maxpos-minpos+1)
		posnum=(maxpos-minpos+1)//10
		example(cr,h,scale,line,arrayline,bar_high,nat,genename,"NULL")
		###
		###
		##annotation gene
		hh=70+10
		#print allgene.keys()[:10]
		annotation_smart(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene)
		###########################
		transcripts(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,nat,"NULL")
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib,"NULL")
		
		atiapa(atinum,apanum,atipos,apapos,cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,strand)
		ashigh=hh
		ass(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,posnum,"P")
		circle_plot(cr,minpos,maxpos,scale,genename,arrayline)
		footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum)
		cr.show_page()
		surface.finish()
		#sys.exit()
		############################
