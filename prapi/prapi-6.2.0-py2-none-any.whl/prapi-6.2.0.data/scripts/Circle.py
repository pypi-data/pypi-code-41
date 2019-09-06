#!python
from __future__ import division
from collections import OrderedDict
from  collections import defaultdict
import cairo
import os,sys,collections,re,multiprocessing,commands,shutil
import numpy
from argparse import ArgumentParser
from SpliceGrapher.formats.loader import loadGeneModels
from SpliceGrapher.formats.FastaLoader import FastaLoader
from math import pi as p
##############
import ConfigParser
##############
parser = ArgumentParser(description='Circle tool  Build by BFPC')
parser.add_argument('-c', '--conf', dest="conf",
                    action='store', type=str, default='conf',
                    help='The configurition file you need')               
args = parser.parse_args()
###############
from utils import *
###############
#from Pacbio_mats import *
###############
global cf
cf = ConfigParser.ConfigParser()
cf.read(args.conf)
###############
def Control():
	Multile_processing=cf.get("Global option","Multile_processing")
	Output_dir=cf.get("outputdir","Output_dir")
	if Multile_processing=="True":
		pool = multiprocessing.Pool()
		for clu in mapdict:
			pool.apply_async(subcon, (clu,))
		pool.close()
		pool.join()
	else:
		for clu in mapdict:
			#########
			#if clu!="NM_134619":
			#	continue
			#########
			subcon(clu)
def subcon(clu):
	if not clu in circle_item:
		return 0
	global hh,ashigh
	for i in [clu]:
		extend_length=int(cf.get("Wig option","extend_length"))	
		minpos  = min(int(x.split()[3]) for x in mapdict[i])
		maxpos  = max(int(x.split()[4]) for x in mapdict[i])
		chro=list(set([x.split()[1]for x in mapdict[i]]))
		strand=list(set([x.split()[5]for x in mapdict[i]]))[0]
		if len(chro)!=1:
			print i+" has %d chrom"%(len(chro))
			continue
		minpos=int(minpos)
		maxpos=int(maxpos)
		#########################################################
		gene=i
		genename=i
		chrome=chro[0]
		#########################################################
		Gene_coordinate_lims="%s:%d-%d"%(chrome,minpos-extend_length,maxpos+extend_length)
		############################################
		# print other info
		Output_dir=cf.get("outputdir","Output_dir")
		#print other info
		###################
		minpos-=extend_length
		maxpos+=extend_length
		###################
		### if mark in this region
		###################
		######
		##### GFF Adapation
		#####
		###################
		Gene_coordinate="%s:%d-%d"%(chrome,minpos,maxpos)
		###################
		#print Gene_coordinate,Gene_coordinate_gene,Gene_coordinate_up,Gene_coordinate_down
		###################
		sort_dict= sorted(mapdict[i], key=lambda d:(int(d.split()[4])-int(d.split()[3])), reverse = False)
		###	Visual
		libnum=[]
		for libsub in conf:
			if libsub.startswith("lib"):
				libnum.append(libsub)
		hight_of=70+8+30*len(sort_dict)+40*len(libnum)+10+60+20
		Output_dir=cf.get("outputdir","Output_dir")
		surface = cairo.PDFSurface("%s/pdf/%s.pdf"%(Output_dir,gene), 500, hight_of)
		sys.stderr.write("	%s has processed\n"%(gene))
		cr = cairo.Context(surface)
		######
		allgene="NULL"
		nat="NULL"
		refGenes="NULL"
		difflib="NULL"
		######
		if len(sort_dict)-1 <12:
			h=4
		else:
			h=70/(len(sort_dict)+2)
		line=1*h/3
		arrayline=1*line/2
		scale=400/(maxpos-minpos+1)
		bar_high=35
		scale=400/(maxpos-minpos+1)
		posnum=(maxpos-minpos+1)//10
		example(cr,h,scale,line,arrayline,bar_high,nat,genename)
		##annotation gene 
		hh=70+10
		#################################
		transcripts_ath_ptr(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename)
		Wig_plot=cf.get("Wig option","Wig_plot")
		if Wig_plot=="True":
			wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib)
		ashigh=hh
		circle_plot(cr,minpos,maxpos,scale,genename,arrayline)
		footer(cr,minpos,maxpos,scale,Gene_coordinate,posnum)
		cr.show_page()
		surface.finish()
#################################
def circle_plot(cr,minpos,maxpos,scale,genename,arrayline):
	global ashigh
	circlelibh=0
	circle_line=2*arrayline
	circle_hex="#008000"
	ashigh+=40
	cr.set_source_rgb(0,0,0)
	cr.move_to(8,ashigh)
	cr.set_font_size(7)
	cr.save()
	cr.rotate(p*270/180)
	cr.show_text("Circle")
	cr.fill()
	cr.restore()
	for item in circle_item[genename]:
		chro,s,e=item.split()
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
#################################
def transcripts_ath_ptr(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename):
	global hh
	#AT1G06620	Chr1	AT1G06620.1	2025601	2027271	+	U5:2025601:2025617	CDS:2025618:2026141	CDS:2026434:2026755	CDS:2026843:2027094	U3:2027095:2027271
	for j in sort_dict:
		info=j.split()
		strand=info[5]
		hh+=200/(len(sort_dict)+23)
		strand=info[5]
		utrmin=[]
		utrmax=[]
		tpos=(int(info[3])+int(info[4]))/2
		cr.set_font_size(6)
		cr.move_to(50+(tpos-minpos)*scale-1.8*len(genename),hh-5)
		cr.show_text(genename)
		cr.fill()
		string="\t".join(info[6:])
		if not "C" in string:
			nocds()
			continue
		for subele in info[6:]:
			if subele.startswith("C"):
				minn=min(int(mm) for mm in subele.split(":")[1:])
				maxx=max(int(mm) for mm in subele.split(":")[1:])
				utrmin.append(minn)
				utrmax.append(maxx)
		for st in range(6,len(info)):
			if info[st].startswith("C"):
				finalst=st-1
				break
		for st in range(6,finalst+1):
			(s,e)=info[st].split(':')
			(s,e)=(int(s),int(e))
			if strand == '+':
				if finalst==6:
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
				if  st != finalst:
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
				if finalst==6:
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
				if st==6:
				#print s,min(utrmin),e
					cr.set_source_rgb(0.75,0.75,0.75)
					cr.rectangle(50+(s-minpos)*scale,hh,(min(utrmin)-s)*scale,h)
					cr.fill()
					cr.set_source_rgb(0,0,0)
					cr.rectangle(50+(min(utrmin)-minpos)*scale,hh,(e-min(utrmin))*scale,h)
					cr.fill()
					cr.set_source_rgb(0,0,0)
					cr.set_line_width(arrayline)
					cr.move_to(50+(s-minpos)*scale,hh+1*h/2)
					cr.line_to(50+(s-minpos)*scale-8,hh+1*h/2)
					cr.stroke()
					cr.move_to(50+(s-minpos)*scale-8,hh+1*h/2)
					cr.rel_line_to(2,-0.5)
					cr.rel_line_to(0,1)
					cr.close_path()
					cr.fill_preserve()
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
def wig(cr,h,scale,line,arrayline,sort_dict,refGenes,minpos,maxpos,genename,allgene,Gene_coordinate,nat,difflib):
	global hh
	Strand_Specificity=cf.get("Wig option","Strand_Specificity")
	strand=sort_dict[0].split()[5]
	high1=hh
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
				#scaleh=32/(max(eval(wiggdict[i])))
				(tpp,filee,rgb)=conf[i].strip('\n').split()
				(r,g,b)=hex2rgb(rgb)
				
				if nat!="True" or (nat=="True" and Strand_Specificity!="True"):
					wiggg=Wig_count(filee,Gene_coordinate,strand[0],bamlist[i],cf)
				elif nat=="True" and Strand_Specificity=="True":
					wigggforward=Wig_count(filee,Gene_coordinate,"+",bamlist[i],cf)
					wigggreverse=Wig_count(filee,Gene_coordinate,"-",bamlist[i],cf)
				hh+=40
				if nat!="True" or (nat=="True" and Strand_Specificity!="True"):	
					if not wiggg:
						continue
					scaleh=32/(max(eval(wiggdict[i]).keys()))
					cr.set_source_rgb(float(r),float(g),float(b))
					for gp in wiggg:
						if gp<minpos or maxpos<gp:
							continue
						cr.rectangle(50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh)
						cr.fill()
					maxacnum=max(eval(wiggdict[i]))
					cr.set_source_rgb(0,0,0)
					cr.move_to(8,hh)
					cr.set_font_size(7)
					cr.save()
					cr.rotate(p*270/180)
					cr.show_text(tpp)
					cr.fill()
					cr.restore()
					#########################################
					##aes
					cr.move_to(50-2,hh)
					#print max(wiggg[x] for x in wiggg)
					maxacnum=max(eval(wiggdict[i]))
					cr.line_to(50-2,hh-maxacnum*scaleh)
					cr.stroke()
					#########################################
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
					#libpos[i]=hh-maxacnum*scaleh/2
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
						hh+=40
					if wigggreverse:
						scaleh=32/(max(eval(wiggdict[i])["-"].keys()))
						maxhigh=max(eval(wiggdict[i])["-"].keys())
						cr.set_source_rgb(float(r),float(g),float(b))
						for gp in wigggreverse:
							if gp<minpos or maxpos<gp:
								continue
                                               	 #print 50+(gp-minpos)*scale,hh-wiggg[gp]*scaleh,1*scale,wiggg[gp]*scaleh,(100/(len(sort_dict)+len(open(args.conf,'r').readlines())+2)),(max(wiggg[x] for x in wiggg))
							cr.rectangle(50+(gp-minpos)*scale,hh-wigggreverse[gp]*scaleh,1*scale,wigggreverse[gp]*scaleh)
                                                 		#print 50+(gp-minpos)*scale,50+(gp-minpos+1)*scale
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
						cr.move_to(50-2,hh)
                                        #print max(wiggg[x] for x in wiggg)
						maxacnum=maxhigh
						cr.line_to(50-2,hh-maxacnum*scaleh)
						cr.stroke()
                                        ####################
						aesmin=maxacnum/4
						for stick in range(4+1):
                                                #print stick,aesmin
							cr.move_to(50-2,hh-aesmin*scaleh*stick)
							cr.line_to(50-2-2,hh-aesmin*scaleh*stick)
							cr.stroke()
							cr.move_to(50-2-2-4*len(str("%.1f"%(aesmin*stick))),hh-aesmin*scaleh*stick+0.4*h)
							cr.set_font_size(5)
							cr.show_text("%.1f"%(aesmin*stick))
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
				cr.stroke()
				"""
				cr.move_to(50+(pos-minpos)*scale,hh)
				cr.line_to(50+(pos-minpos)*scale,high1)
				cr.stroke()
def example(cr,h,scale,line,arrayline,bar_high,nat,genename):
	cr.move_to(50,bar_high)
	cr.rectangle(50,bar_high-h,10,h)
	cr.set_font_size(8)
	#cr.set_source_rgb(0.18,0.55,0.34)
	(r,g,b)=hex2rgb(conf["exon"])
	cr.set_source_rgb(r,g,b)
	cr.fill()
	cr.move_to(50+10+2,bar_high)
	cr.set_source_rgb(0,0,0)
	cr.show_text("Exon")
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
	cr.move_to(50,bar_high+10*2)
	cr.line_to(50+50*scale,bar_high+10*2)
	cr.set_source_rgb(0,0,0)
	cr.set_line_width(line)
	cr.stroke()
	cr.move_to(50+50*scale+2,bar_high+10*2)
	cr.show_text("50 bp")
	cr.fill()
	#######################
	## circle
	s,e=50+50*scale,50+50*scale+20
	ashigh=bar_high+10*3
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
	#########################################
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
		#numout=commands.getoutput("samtools view %s|cut -f 1|sort -T temp|uniq|wc -l "%(bamfile))
		#num=numout.split()[0]
		num=100000
		return libname,num
def check_jucton_length():
	readLength=int(cf.get("Wig option","readLength"))
	anchorLength=int(cf.get("Wig option","anchorLength"))
	junctionLength = 2*(readLength-anchorLength)
	return junctionLength
def convert_gff_circle(gff):
	###############
	create=locals()
	allgene=defaultdict(dict)
	out=open("%s.format"%(gff),"w")
	###############
	for i in open(gff,"r"):
		ele=i.strip("\n").split("\t")
		#######
		if i.startswith("#") or i=="" or ele==['']:
			continue
		#######
		if ele[2].lower()=="mrna" or ele[2].lower()=="mrna_te_gene" or ele[2].lower()=="ncrna" or ele[2].lower()=="mirna" or ele[2].lower()=="mrna_te_gene" or ele[2].lower()=="snorna" or ele[2].lower()=="snrna" or ele[2].lower()=="trna":
			############################################
			genename=re.search('(Parent=\w*[.-_]*\w*;*)',ele[-1]).group()
			genename=re.split("=|;",genename)[1]
			############################################
			try:
				mrnaname=re.search('(Name=\w*[.-_]*\w*;*)',ele[-1]).group()
			except:
				mrnaname=re.search('(ID=\w*[.-_]*\w*;*)',ele[-1]).group()
			###################
			mrnaname=re.split("=|;",mrnaname)[1]
			mrnaname=re.split(".MRNA",mrnaname.upper())[0]
			if "." in mrnaname:
				mrnaname="_".join(mrnaname.split("."))
			###################
			create[mrnaname]=defaultdict(dict)
			##################print 
			allgene[genename]["chr"]=ele[0]
			allgene[genename]["strand"]=ele[6]
			eval(mrnaname)["lims"]["%s:%s"%(ele[3],ele[4])]=1
			allgene[genename][mrnaname]=1
		elif ele[2].lower()=="cds":
			eval(mrnaname)["cds"]["%s:%s"%(ele[3],ele[4])]=1
			#out.write("CDS:%s:%s\t"%(ele[3],ele[4]))
		elif ele[2].lower()=="five_prime_utr":
			eval(mrnaname)["u5"]["%s:%s"%(ele[3],ele[4])]=1
			#out.write("U5:%s:%s\t"%(ele[3],ele[4]))
		elif ele[2].lower()=="three_prime_utr":
			eval(mrnaname)["u3"]["%s:%s"%(ele[3],ele[4])]=1
			#out.write("U3:%s:%s\t"%(ele[3],ele[4]))
		elif ele[2].lower()=="exon":
			eval(mrnaname)["exon"]["%s:%s"%(ele[3],ele[4])]=1
	################
	for gene in allgene:
		chrs=allgene[gene]["chr"]
		strand=allgene[gene]["strand"]
		for mrna in allgene[gene]:
			if mrna=="chr" or mrna=="strand":
				continue
			mrnaname=mrna
			##########
			s,e=eval(mrnaname)["lims"].keys()[0].split(":")
			out.write("%s\t%s\t%s\t%s\t%s\t%s\t"%(gene,chrs,mrna,s,e,strand))
			tpp=eval(mrnaname).keys()
			if "exon" in tpp:
				############
				exon=[x for x in eval(mrnaname)["exon"]]
				sort_exon=sorted(exon,key=lambda d:(int(d.split(":")[0])))
				exonline="\t".join(sort_exon)
				############
				cds=[x for x in eval(mrnaname)["cds"]]
				sort_cds=sorted(cds,key=lambda d:(int(d.split(":")[0])))
				sort_cds=["C:"+x for x in sort_cds]
				cdsline="\t".join(sort_cds)
				############
				out.write("%s\t%s\n"%(exonline,cdsline))
			else:
				############
				cds=[x for x in eval(mrnaname)["cds"]]
				sort_cds=sorted(cds,key=lambda d:(int(d.split(":")[0])))
				cdsline="\t".join(sort_cds)
				############
				############
				u5=[x for x in eval(mrnaname)["u5"]]
				sort_u5=sorted(u5,key=lambda d:(int(d.split(":")[0])))
				u3=[x for x in eval(mrnaname)["u3"]]
				sort_u3=sorted(u3,key=lambda d:(int(d.split(":")[0])))
				##############################
				exon=[]
				for i in u3:
					s,e=[int(x) for x in i.split(":")]
					for pos in range(s,e+1):
						exon.append(pos)
				for i in u5:
					s,e=[int(x) for x in i.split(":")]
					for pos in range(s,e+1):
						exon.append(pos)
				for i in cds:
					s,e=[int(x) for x in i.split(":")]
					for pos in range(s,e+1):
						exon.append(pos)	
				##############################
				exon=sorted(set(exon),key=lambda d:(d))
				exon_lim=[]
				left=exon[0]
				for index,i in enumerate(exon):
					if index==0:
						continue
					if i-exon[index-1]!=1:
						right=exon[index-1]
						exon_lim.append("%s:%s"%(left,right))
						left=i
				exon_lim.append("%s:%s"%(left,exon[-1]))
				sort_exon=sorted(exon_lim,key=lambda d:(int(d.split(":")[0])))
				exonline="\t".join(sort_exon)
				#############
				sort_cds=["C:"+x for x in sort_cds]
				cdsline="\t".join(sort_cds)
				#############
				out.write("%s\t%s\n"%(exonline,cdsline))
	out.close()
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
	######
if  __name__ == '__main__':
	sys.stderr.write('Initializtion...\n')
	global conf,bamlist,mapdict,geneModel,allgene
	bamlist=dict()
	conf=OrderedDict()
	"""
	Configurition reading in a variable
	"""
	######
	# check configuration
	if cf.has_section("outputdir") and cf.has_section("input file") and cf.has_section("Graph option") and cf.has_section("Global option") and cf.has_section("Wig option") and cf.has_section("Circle"):
		pass
	else:
		sys.exit("check the configuration file")
	######
	Genome_Annotion=cf.get("input file","genome_annotion")
	Output_dir=cf.get("outputdir","Output_dir")
	geneModel = loadGeneModels(Genome_Annotion, verbose=True)
	#######
	#######
	for fl in [Output_dir,"temp","%s/pdf"%(Output_dir)]:
		if not os.path.exists(fl):
			sys.stderr.write("Making %s dir\n"%(fl))
			os.makedirs(fl)
	######
	circle_ref(Output_dir)
	######
	conff=[]
	######
	Multile_processing=cf.get("Global option","Multile_processing")
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
	shutil.copy(Genome_Annotion,Output_dir)
	fa=cf.get("input file","Genome")
	lib_circle=cf.get("Circle","lib")
	(tpp,filee,rgb)=conf[lib_circle.lower()].strip('\n').split()
	bam_circle=filee
	cmd="CIRCexplorer.py -f %s -g %s -r %s/circle_gff.txt -o %s/result "%(bam_circle,fa,Output_dir,Output_dir)
	#--tmp
	os.system(cmd)
	convert_gff_circle("%s/%s"%(Output_dir,os.path.split(Genome_Annotion)[1]))
	Genome_Annotion_format="%s/%s.format"%(Output_dir,os.path.split(Genome_Annotion)[1])
	mapdict=defaultdict(dict)
	################################
	for i in open(Genome_Annotion_format,"r"):
		i=i.strip("\n")
		ele=i.split()
		mapdict[ele[0]][i]=1
	circle_item=defaultdict(dict)
	for i in open("%s/result_circ.txt"%(Output_dir),"r"):
		ele=i.rstrip().split()
		circle_item[ele[-4]]["\t".join(ele[:3])]=1
	Control()
	################################
