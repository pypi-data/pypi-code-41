import numpy, os
#import math
import gdal  #geospatial data abstraction
#import osr
#import ogr  #simple features library, vector data access, pawrt of GDAL
#from pyproj import Proj, transform
#foldername='../drondata/alfalfa'
import csv
import time
from skimage.segmentation import find_boundaries
#import cv2
#import matplotlib.pyplot as plt
global lastlinecount,misslabel
from sklearn.cluster import KMeans


tinyareas=[]
colortable={}
colormatch={}
labellist=[]
elesize=[]
avgarea=None
greatareas=[]
exceptions=[]
class node:
    def __init__(self,i,j):
        self.i=i
        self.j=j
        self.label=0
        self.check=False

def combinecrops(area,subarea,i,ele,ulx,uly,rlx,rly):
    print('combinecrops: i='+str(i)+' ele='+str(ele))
    localarea=numpy.asarray(area)
    if i<ele:
        localarea=numpy.where(localarea==ele,i,localarea)
    else:
        subarea=numpy.where(subarea==i,ele,subarea)
        localarea[uly:rly+1,ulx:rlx+1]=subarea
    unique = numpy.unique(localarea)
    print(unique)
    return localarea

def sortline(linelist,midx,midy,linenum):
    localy={}
    localx={}
    for ele in linelist:
        localy.update({ele:midy[ele]})
        localx.update({ele:midx[ele]})
    i=0
    for ele in sorted(localx,key=localx.get):
        try:
            tempcolordict={ele:labellist[i+sum(elesize[:linenum])]}
            colortable.update(tempcolordict)
            print(tempcolordict)
            i+=1
        except IndexError:
            pass


def relabel(area):
    unique=numpy.unique(area).tolist()
    unique=unique[1:]
    midx={}
    midy={}
    colortable.clear()
    misslabel=0
    for ele in unique:
        eleloc=numpy.where(area==ele)
        ylist=eleloc[0].tolist()
        xlist=eleloc[1].tolist()
        y=ylist[int(len(ylist)/2)]
        x=xlist[int(len(xlist)/2)]
        txdict={ele:x}
        tydict={ele:y}
        midx.update(txdict)
        midy.update(tydict)
    linelist=[]
    linecount=0
    for ele in sorted(midy,key=midy.get):
        linelist.append(ele)
        print(ele,midy[ele],midx[ele])
        #if len(linelist)%23==0:
        if linecount<len(elesize):
            if len(linelist)%elesize[linecount]==0:
                #sortline(linelist,midx,midy,linecount-1)
                sortline(linelist,midx,midy,linecount)
                linelist[:]=[]
                #colcount=1
                linecount+=1
                print(linecount)
                misslabel=0
                continue
            else:
                misslabel=elesize[linecount]-len(linelist)
                if misslabel==0:
                    misslabel=sum(elesize[:linecount])-sum(elesize)
        else:
            misslabel=0
            misslabel-=len(linelist)
    print(colortable)
    colorarea=numpy.zeros(area.shape)
    colorarea=colorarea.tolist()
    for i in range(len(area)):
        for j in range(len(area[0])):
            if area[i][j]!=0:
                try:
                    colorarea[i][j]=colormatch[colortable[area[i][j]]]
                except KeyError:
                    pass
    colorarea=numpy.asarray(colorarea)
    if misslabel==0:
        misslabel=len(labellist)-len(unique)
    return colorarea,misslabel

def labelgapnp(area):
    x=[0,-1,-1,-1,0,1,1,1]
    y=[1,1,0,-1,-1,-1,0,1]

    nodearea=numpy.where(area!=0)
    labelnum=2
    nodelist={}
    for k in range(len(nodearea[0])):
        tnode=node(nodearea[0][k],nodearea[1][k])
        tempdict={(nodearea[0][k],nodearea[1][k]):tnode}
        nodelist.update(tempdict)
    nodekeys=list(nodelist.keys())
    for key in nodekeys:
        if nodelist[key].check==False:
            nodelist[key].check=True
            nodelist[key].label=labelnum
            offspringlist=[]
            for m in range(len(y)):
                i=key[0]
                j=key[1]
                if (i+y[m],j+x[m]) in nodelist:
                    newkey=(i+y[m],j+x[m])
                    if nodelist[newkey].check==False:
                        nodelist[newkey].check=True
                        offspringlist.append(newkey)
            if len(offspringlist)==0:
                nodelist[key].label=0
            while(len(offspringlist)>0):
                currnodekey=offspringlist.pop(0)
                curri=currnodekey[0]
                currj=currnodekey[1]
                nodelist[currnodekey].label=labelnum
                for m in range(len(y)):
                    if (curri+y[m],currj+x[m]) in nodelist:
                        if nodelist[(curri+y[m],currj+x[m])].check==False:
                            nodelist[(curri+y[m],currj+x[m])].check=True
                            offspringlist.append((curri+y[m],currj+x[m]))
            labelnum+=1
    area=numpy.zeros(area.shape)
    for key in nodekeys:
        area[key[0],key[1]]=nodelist[key].label
    return area


def labelgap(area):
    x=[0,-1,-1,-1,0,1,1,1]
    y=[1,1,0,-1,-1,-1,0,1]
    nodearea=area.tolist()
    labelnum=2
    nodelist=[]
    for i in range(len(nodearea)):
        tempnodelist=[]
        for j in range(len(nodearea[0])):
            tnode=node(i,j)
            tempnodelist.append(tnode)
        nodelist.append(tempnodelist)
    for i in range(len(nodelist)):
        for j in range(len(nodelist[i])):
            if nodelist[i][j].check==False and nodearea[i][j]!=0:
                nodelist[i][j].check=True
                #print('nodelisti,j='+str(i)+','+str(j))
                nodelist[i][j].label=labelnum
                offspringlist=[]
                for k in range(len(y)):
                    if i+y[k]<len(nodelist) and i+y[k]>=0 and j+x[k]<len(nodelist[i]) and j+x[k]>=0:
                        if nodelist[i+y[k]][j+x[k]].check==False and nodearea[i+y[k]][j+x[k]]!=0:
                            nodelist[i+y[k]][j+x[k]].check=True
                            #print('nodelist i+ym,j+xn='+str(i+y[m])+','+str(j+x[n]))
                            offspringlist.append(nodelist[i+y[k]][j+x[k]])

                if len(offspringlist)==0:
                    nodelist[i][j].label=0
                while(len(offspringlist)>0):
                    currnode=offspringlist.pop(0)
                    curri=currnode.i
                    currj=currnode.j
                    nodelist[curri][currj].label=labelnum
                    for k in range(len(y)):
                        if curri+y[k]>=0 and curri+y[k]<len(nodelist) and currj+x[k]<len(nodelist[i]) and currj+x[k]>=0:
                            if nodelist[curri+y[k]][currj+x[k]].check==False and nodearea[curri+y[k]][currj+x[k]]!=0:
                                nodelist[curri+y[k]][currj+x[k]].check=True
                                #print('nodelist i+ym,j+xn='+str(i+y[m])+','+str(j+x[n]))
                                offspringlist.append(nodelist[curri+y[k]][currj+x[k]])
                labelnum+=1
    for i in range(len(nodearea)):
        for j in range(len(nodearea[0])):
            nodearea[i][j]=nodelist[i][j].label

    area=numpy.asarray(nodearea)
    return area

def get_boundary(area):
    contentlocs=numpy.where(area==1)
    boundaryres=numpy.zeros(area.shape)
    x=[0,-1,-1,-1,0,1,1,1]
    y=[1,1,0,-1,-1,-1,0,1]
    for m in range(len(contentlocs[0])):
        for k in range(len(y)):
            i=contentlocs[0][m]+y[k]
            j=contentlocs[1][m]+x[k]
            if i>=0 and i<area.shape[0] and j>=0 and j<area.shape[1]:
                if area[i,j]==0:
                    boundaryres[contentlocs[0][m],contentlocs[1][m]]=1
                    break
    return boundaryres


def boundarywatershed(area,segbondtimes,boundarytype):   #area = 1's
    if numpy.count_nonzero(area)<avgarea/2:
        return area
    x=[0,-1,-1,-1,0,1,1,1]
    y=[1,1,0,-1,-1,-1,0,1]
    #x=[0,-1,0,1]
    #y=[1,0,-1,0]
    #
    #temptif=cv2.GaussianBlur(area,(3,3),0,0,cv2.BORDER_DEFAULT)
    #areaboundary=cv2.Laplacian(area,cv2.CV_8U,ksize=5)
    #plt.imshow(areaboundary)
    areaboundary=find_boundaries(area,mode=boundarytype)
    #areaboundary=get_boundary(area)
    areaboundary=areaboundary*1   #boundary = 1's, nonboundary=0's
    temparea=area-areaboundary
    arealabels=labelgapnp(temparea)
    unique, counts = numpy.unique(arealabels, return_counts=True)
    if segbondtimes>=20:
        return area
    if(len(unique)>2):
        res=arealabels+areaboundary
        leftboundaryspots=numpy.where(areaboundary==1)
        res=res.tolist()
        for k in range(len(leftboundaryspots[0])):
            i=leftboundaryspots[0][k]
            j=leftboundaryspots[1][k]
            for m in range(len(y)):
                if i+y[m]>=0 and i+y[m]<len(res) and j+x[m]>=0 and j+x[m]<len(res[0]):
                    if areaboundary[i][j]>0:
                        diff=areaboundary[i][j]-res[i+y[m]][j+x[m]]
                        if diff<0:
                            res[i][j]=res[i+y[m]][j+x[m]]
                            break
        res=numpy.asarray(res)-1
        res=numpy.where(res<0,0,res)
        return res
    else:
        newarea=boundarywatershed(temparea,segbondtimes+1,boundarytype)*2
        res=newarea+areaboundary
        leftboundaryspots=numpy.where(res==1)
        res=res.tolist()
        for k in range(len(leftboundaryspots[0])):
            i=leftboundaryspots[0][k]
            j=leftboundaryspots[1][k]
            for m in range(len(y)):
                if i+y[m]>=0 and i+y[m]<len(res) and j+x[m]>=0 and j+x[m]<len(res[0]):
                    if res[i][j]==1:
                        diff=res[i][j]-res[i+y[m]][j+x[m]]
                        if diff<0:
                            res[i][j]=res[i+y[m]][j+x[m]]
                            break
        res=numpy.asarray(res)/2
        res=numpy.where(res<1,0,res)
        return res

def manualboundarywatershed(area,avgarea):
    if numpy.count_nonzero(area)<avgarea/2:
        return area
    x=[0,-1,-1,-1,0,1,1,1]
    y=[1,1,0,-1,-1,-1,0,1]
    leftboundaryspots=numpy.where(area==1)
    pixelcount=1
    label=1
    for k in range(len(leftboundaryspots[0])):
        i=leftboundaryspots[0][k]
        j=leftboundaryspots[1][k]
        area[i][j]=label
        pixelcount+=1
        if pixelcount==int(avgarea):
            pixelcount=1
            label+=1
    return area


def manualdivide(area,greatareas):
    global exceptions
    unique, counts = numpy.unique(area, return_counts=True)
    hist=dict(zip(unique,counts))
    del hist[0]
    meanpixel=sum(counts[1:])/len(counts)
    countseed=numpy.asarray(counts[1:])
    stdpixel=numpy.std(countseed)
    sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
    dimension=getdimension(area)
    values=list(dimension.values())
    meandimension=sum(values)/len(values)
    stddimension=numpy.std(numpy.array(values))
    updimention=min(meandimension+stddimension,meandimension*1.25)
    lowdimention=meandimension-stddimension
    while len(greatareas)>0:
        topkey=greatareas.pop(0)
        if topkey not in dimension:
            continue
        topkeydimension=dimension[topkey]
        if topkey not in exceptions:
            locs=numpy.where(area==topkey)
            ulx,uly=min(locs[1]),min(locs[0])
            rlx,rly=max(locs[1]),max(locs[0])
            subarea=area[uly:rly+1,ulx:rlx+1]
            tempsubarea=subarea/topkey
            newtempsubarea=numpy.where(tempsubarea!=1.,0,1)
            antitempsubarea=numpy.where((tempsubarea!=1.) & (tempsubarea!=0),tempsubarea,0)
            antitempsubarea=antitempsubarea*topkey.astype(int)
            newsubarea=manualboundarywatershed(newtempsubarea,meanpixel+stdpixel)#,windowsize)
            labelunique,labcounts=numpy.unique(newsubarea,return_counts=True)
            labelunique=labelunique.tolist()
            labcounts=labcounts.tolist()
            origin=labcounts[1]
            if topkeydimension<updimention:
                for i in range(2,len(labcounts)):
                    if labcounts[i]<origin/2:
                        labelunique.pop(i)
                        labcounts.pop(i)
                        exceptions.append(topkey)
            else:
                if len(labelunique)>2:
                    keepdevide=True
                    newlabelavgarea=sum(labcounts[1:])/len(labcounts[1:])
                    #if newlabelavgarea<=lowrange:
                    #if newlabelavgarea<=avgarea:
                    #    keepdevide=False

                    #if keepdevide:
                    newsubarea=newsubarea*topkey
                    newlabel=labelunique.pop(-1)
                    maxlabel=area.max()
                    add=1
                    while newlabel>1:
                        newsubarea=numpy.where(newsubarea==topkey*newlabel,maxlabel+add,newsubarea)
                        print('new label: '+str(maxlabel+add))
                        newlabelcount=len(numpy.where(newsubarea==maxlabel+add)[0].tolist())
                        #if newlabelcount>=meanpixel and newlabelcount<uprange:
                            #if (maxlabel+add) not in exceptions:    07102019
                                #exceptions.append(maxlabel+add)     07102019
                        print('add '+'label: '+str(maxlabel+add)+' count='+str(newlabelcount))
                        newlabel=labelunique.pop(-1)
                        add+=1

                newsubarea=newsubarea+antitempsubarea
                area[uly:rly+1,ulx:rlx+1]=newsubarea
                #labels=relabel(labels)
                unique, counts = numpy.unique(area, return_counts=True)
                hist=dict(zip(unique,counts))
                del hist[0]
                print('hist length='+str(len(counts)-1))
                print('max label='+str(area.max()))
                sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
                meanpixel=sum(counts[1:])/len(counts)
                countseed=numpy.asarray(counts[1:])
                stdpixel=numpy.std(countseed)
                uprange=meanpixel+stdpixel
                lowrange=meanpixel-stdpixel
                #zscore=(hist[topkey]-meanpixel)/stdpixel
                dimension=getdimension(area)
                values=list(dimension.values())
                meandimension=sum(values)/len(values)
                stddimension=numpy.std(numpy.array(values))
                updimention=min(meandimension+stddimension,meandimension*1.25)

def divideloop(area,misslabel,avgarea,layers,par):
    global greatareas
    #while hist[topkey]>meanpixel*1.1 and topkey not in exceptions:
    unique, counts = numpy.unique(area, return_counts=True)
    hist=dict(zip(unique,counts))
    del hist[0]
    #print('hist length='+str(len(counts)-1))
    #print('max label='+str(labels.max()))
    meanpixel=sum(counts[1:])/len(counts)
    countseed=numpy.asarray(counts[1:])
    stdpixel=numpy.std(countseed)
    uprange=meanpixel+stdpixel
    lowrange=meanpixel-stdpixel
    sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
    topkey=sortedkeys.pop(0)
    #while len(sortedkeys)>0 and hist[topkey]>uprange and topkey in exceptions:
    halflength=0.5*len(sortedkeys)
    zscore=(hist[topkey]-meanpixel)/stdpixel
    #while len(sortedkeys)>halflength and hist[topkey]>uprange:
    maxareacount=misslabel
    greatareas=[]
    if 2-par<1.25:
        times=1.25
    else:
        times=2-par
    while maxareacount>0 or hist[topkey]>min(avgarea*1.25,uprange):
    #while len(sortedkeys)>halflength and zscore>=2.5:
        print('topkey='+str(topkey),hist[topkey])
        if topkey not in greatareas and topkey not in exceptions:
        #topkey=sortedkeys.pop(0)
    #for i in sorted(hist,key=hist.get,reverse=True):
        #if j<firstfivepercent:
            #if hist[topkey]>meanpixel*1.5 and topkey not in exceptions:
            locs=numpy.where(area==topkey)
            ulx,uly=min(locs[1]),min(locs[0])
            rlx,rly=max(locs[1]),max(locs[0])
            width=rlx-ulx
            height=rly-uly
            #windowsize=min(width,height)
            #dividen=2
            subarea=area[uly:rly+1,ulx:rlx+1]
            tempsubarea=subarea/topkey
            newtempsubarea=numpy.where(tempsubarea!=1.,0,1)
            antitempsubarea=numpy.where((tempsubarea!=1.) & (tempsubarea!=0),tempsubarea,0)
            antitempsubarea=antitempsubarea*topkey.astype(int)
            '''
            noop=0
            for i in range(len(layers)):
                layertempsubarea=newtempsubarea-layers[i][uly:rly+1,ulx:rlx+1]
                layertempsubarea=numpy.where(layertempsubarea<=0,0,layertempsubarea)
                newsubarea=boundarywatershed(layertempsubarea,1,'inner')#,windowsize)

                labelunique,labcounts=numpy.unique(newsubarea,return_counts=True)
                labelunique=labelunique.tolist()
                if len(labcounts[1:])>0:
                    print(sum(labcounts[1:])/len(labcounts[1:]))
                    if(sum(labcounts[1:])/len(labcounts[1:])<avgarea/times):
                        noop+=1
                        continue
                else:
                    noop+=1
                    continue
            #if len(labelunique)<=2:
            #    newsubarea=newtempsubarea*topkey
            #    newsubareasize=len(numpy.where(newsubarea==topkey)[0].tolist())
            #    if newsubareasize>=meanpixel:
            #        if topkey not in exceptions:
            #            exceptions.append(topkey)
            #            print('add exceptions'+'label: '+str(topkey))
            #else:
                if len(labelunique)>2:
                    keepdevide=True
                    newlabelavgarea=sum(labcounts[1:])/len(labcounts[1:])
                    #if newlabelavgarea<=lowrange:
                    #if newlabelavgarea<=avgarea:
                    #    keepdevide=False

                    #if keepdevide:
                    newsubarea=newsubarea+1
                    newsubarea=numpy.where(newsubarea==1,0,newsubarea)
                    leftboundaryspots=numpy.where(layers[i][uly:rly+1,ulx:rlx+1]==1)
                    x=[0,-1,-1,-1,0,1,1,1]
                    y=[1,1,0,-1,-1,-1,0,1]
                    areaboundary=layers[i][uly:rly+1,ulx:rlx+1]
                    res=newsubarea+areaboundary
                    res=res.tolist()
                    for k in range(len(leftboundaryspots[0])):
                        i=leftboundaryspots[0][k]
                        j=leftboundaryspots[1][k]
                        for m in range(len(y)):
                            if i+y[m]>=0 and i+y[m]<len(res) and j+x[m]>=0 and j+x[m]<len(res[0]):
                                if areaboundary[i][j]>0:
                                    diff=areaboundary[i][j]-res[i+y[m]][j+x[m]]
                                    if diff<0:
                                        res[i][j]=res[i+y[m]][j+x[m]]
                                        break
                    res=numpy.asarray(res)-1
                    res=numpy.where(res<0,0,res)

                    maxlabel=max(numpy.unique(area).tolist())
                    #add=1
                    res=res*topkey*1e-6
                    uniqueres=numpy.unique(res).tolist()
                    for i in range(2,len(uniqueres)):
                        print('res='+str(uniqueres[i])+' change to'+str(maxlabel+i-1))
                        res=numpy.where(res==uniqueres[i],maxlabel+i-1,res)
                        newlabelcount=len(numpy.where(res==maxlabel+i-1)[0].tolist())
                        print('new label: '+str(maxlabel+i-1)+' count='+str(newlabelcount))
                    res=numpy.where(res==topkey*1e-6,topkey,res)
                    uniqueres=numpy.unique(res).tolist()
                    print(uniqueres)


                    #while newlabel>1:
                    #    newsubarea=numpy.where(newsubarea==topkey*newlabel,maxlabel+add,newsubarea)
                    #    print('new label: '+str(maxlabel+add))
                    #    newlabelcount=len(numpy.where(newsubarea==maxlabel+add)[0].tolist())
                        #if newlabelcount>=meanpixel and newlabelcount<uprange:
                            #if (maxlabel+add) not in exceptions:    07102019
                                #exceptions.append(maxlabel+add)     07102019
                    #    print('add '+'label: '+str(maxlabel+add)+' count='+str(newlabelcount))
                    #    newlabel=labelunique.pop(-1)
                    #    add+=1
                    print(res.max())

                    newsubarea=res+antitempsubarea
                    area[uly:rly+1,ulx:rlx+1]=newsubarea
                    #labels=relabel(labels)
                    unique, counts = numpy.unique(area, return_counts=True)
                    hist=dict(zip(unique,counts))
                    del hist[0]
                    print('hist length='+str(len(counts)-1))
                    print('max label='+str(area.max()))
                    sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
                    meanpixel=sum(counts[1:])/len(counts)
                    countseed=numpy.asarray(counts[1:])
                    stdpixel=numpy.std(countseed)
                    uprange=meanpixel+stdpixel
                    lowrange=meanpixel-stdpixel
                    #zscore=(hist[topkey]-meanpixel)/stdpixel
                    topkey=sortedkeys.pop(0)
                    maxareacount-=1
                    break
                else:
                    noop+=1
            '''
            #if noop==len(layers):
            newsubarea=boundarywatershed(newtempsubarea,1,'inner')#,windowsize)
            labelunique,labcounts=numpy.unique(newsubarea,return_counts=True)
            labelunique=labelunique.tolist()
            if len(labelunique)>2:
                keepdevide=True
                newlabelavgarea=sum(labcounts[1:])/len(labcounts[1:])
                #if newlabelavgarea<=lowrange:
                #if newlabelavgarea<=avgarea:
                #    keepdevide=False

                #if keepdevide:
                newsubarea=newsubarea*topkey
                newlabel=labelunique.pop(-1)
                maxlabel=area.max()
                add=1
                while newlabel>1:
                    newsubarea=numpy.where(newsubarea==topkey*newlabel,maxlabel+add,newsubarea)
                    print('new label: '+str(maxlabel+add))
                    newlabelcount=len(numpy.where(newsubarea==maxlabel+add)[0].tolist())
                    #if newlabelcount>=meanpixel and newlabelcount<uprange:
                        #if (maxlabel+add) not in exceptions:    07102019
                            #exceptions.append(maxlabel+add)     07102019
                    print('add '+'label: '+str(maxlabel+add)+' count='+str(newlabelcount))
                    newlabel=labelunique.pop(-1)
                    add+=1

                newsubarea=newsubarea+antitempsubarea
                area[uly:rly+1,ulx:rlx+1]=newsubarea
                #labels=relabel(labels)
                unique, counts = numpy.unique(area, return_counts=True)
                hist=dict(zip(unique,counts))
                del hist[0]
                print('hist length='+str(len(counts)-1))
                print('max label='+str(area.max()))
                sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
                meanpixel=sum(counts[1:])/len(counts)
                countseed=numpy.asarray(counts[1:])
                stdpixel=numpy.std(countseed)
                uprange=meanpixel+stdpixel
                lowrange=meanpixel-stdpixel
                #zscore=(hist[topkey]-meanpixel)/stdpixel
                topkey=sortedkeys.pop(0)
                maxareacount-=1
            else:
                if hist[topkey]>uprange:
                    greatareas.append(topkey)
                    topkey=sortedkeys.pop(0)
                else:
                    break

        else:
            topkey=sortedkeys.pop(0)
            #zscore=(hist[topkey]-meanpixel)/stdpixel
            #maxareacount-=1
    return area

def combineloop(area,misslabel,par):
    global tinyareas
    localarea=numpy.asarray(area)
    unique, counts = numpy.unique(localarea, return_counts=True)
    hist=dict(zip(unique,counts))
    del hist[0]
    #print('hist length='+str(len(counts)-1))
    #print('max label='+str(labels.max()))
    meanpixel=sum(counts[1:])/len(counts)
    countseed=numpy.asarray(counts[1:])
    stdpixel=numpy.std(countseed)
    uprange=meanpixel+stdpixel
    lowrange=meanpixel-stdpixel
    sortedkeys=list(sorted(hist,key=hist.get))
    topkey=sortedkeys.pop(0)
    halflength=0.5*len(sortedkeys)
    lowpercentile=numpy.percentile(countseed,25)
    highpercentile=numpy.percentile(countseed,75)
    #if len(sortedkeys)>0 and hist[topkey]<meanpixel:
    #while len(sortedkeys)>0 and hist[topkey]<lowrange and topkey in exceptions:
    zscore=(hist[topkey]-meanpixel)/stdpixel
    #while len(sortedkeys)>halflength and hist[topkey]<=lowrange:
    #while len(sortedkeys)>halflength and zscore<=-2.5:
    tinyareas=[]
    if 1+par<1.25:
        times=1+par
    else:
        times=1.25
    #while misslabel<=0:# or gocombine==True:
    while hist[topkey]<max(avgarea*0.75,lowrange):
        #topkey=sortedkeys.pop(0)
        print('uprange='+str(uprange))
        print('lowrange='+str(lowrange))
        print('combine part')
        i=topkey
        print(i,hist[i])
        if i not in tinyareas:
        #if hist[i]<meanpixel:
            locs=numpy.where(localarea==i)
            ulx,uly=min(locs[1]),min(locs[0])
            rlx,rly=max(locs[1]),max(locs[0])
            width=rlx-ulx
            height=rly-uly
            #windowsize=min(width,height)
            #dividen=2
            subarea=localarea[uly:rly+1,ulx:rlx+1]
            tempsubarea=subarea/i
            #four direction searches
            stop=False
            poscombines=[]
            for j in range(1,11):
                up_unique=[]
                down_unique=[]
                left_unique=[]
                right_unique=[]
                maxlabel={}
                tempcombines=[]
                if uly-j>=0 and stop==False and len(up_unique)<2:
                    uparray=localarea[uly-j:uly,ulx:rlx+1]
                    up_unique=numpy.unique(uparray)
                    for x in range(len(up_unique)):
                        if up_unique[x]>0:
                            tempdict={up_unique[x]:hist[up_unique[x]]}
                            maxlabel.update(tempdict)
                if rly+j<localarea.shape[0] and stop==False and len(down_unique)<2:
                    downarray=localarea[rly+1:rly+j+1,ulx:rlx+1]
                    down_unique=numpy.unique(downarray)
                    for x in range(len(down_unique)):
                        if down_unique[x]>0:
                            tempdict={down_unique[x]:hist[down_unique[x]]}
                            maxlabel.update(tempdict)
                if ulx-j>=0 and stop==False and len(left_unique)<2:
                    leftarray=localarea[uly:rly+1,ulx-j:ulx]
                    left_unique=numpy.unique(leftarray)
                    for x in range(len(left_unique)):
                        if left_unique[x]>0:
                            tempdict={left_unique[x]:hist[left_unique[x]]}
                            maxlabel.update(tempdict)
                if ulx+j<localarea.shape[1] and stop==False and len(right_unique)<2:
                    rightarray=localarea[uly:rly+1,rlx+1:rlx+j+1]
                    right_unique=numpy.unique(rightarray)
                    for x in range(len(right_unique)):
                        if right_unique[x]>0:
                            tempdict={right_unique[x]:hist[right_unique[x]]}
                            maxlabel.update(tempdict)
                print(up_unique,down_unique,left_unique,right_unique)
                tempcombines.append(up_unique)
                tempcombines.append(down_unique)
                tempcombines.append(left_unique)
                tempcombines.append(right_unique)
                poscombines.append(tempcombines)
            tinylist=[]
            while(len(poscombines)>0 and stop==False):
                top=poscombines.pop(0)
                tinylist.append(top)
                toplist=[]
                for j in range(4):
                    toparray=top[j]
                    topunique=numpy.unique(toparray)
                    for ele in topunique:
                        toplist.append(ele)
                toplist=numpy.array(toplist)
                combunique,combcount=numpy.unique(toplist,return_counts=True)
                toplist=dict(zip(combunique,combcount))
                toplist=list(sorted(toplist,key=toplist.get,reverse=True))
                while(len(toplist)>0):
                    top=toplist.pop(0)
                    if top!=0:
                        topcount=hist[top]
                        if hist[i]+topcount<=avgarea*times:
                            localarea=combinecrops(localarea,subarea,i,top,ulx,uly,rlx,rly)
                            stop=True
            if len(poscombines)==0 and stop==False:  #combine to the closest one
                tinyareas.append(topkey)
                misslabel+=1

            unique, counts = numpy.unique(localarea, return_counts=True)
            hist=dict(zip(unique,counts))
            sortedkeys=list(sorted(hist,key=hist.get))
            meanpixel=sum(counts[1:])/len(counts)
            countseed=numpy.asarray(counts[1:])
            stdpixel=numpy.std(countseed)
            uprange=meanpixel+stdpixel
            lowrange=meanpixel-stdpixel
            topkey=sortedkeys.pop(0)
            print('hist leng='+str(len(unique[1:])))
        else:
            topkey=sortedkeys.pop(0)
            misslabel+=1


    return localarea




'''
def combineloop(area,misslabel):
    localarea=numpy.asarray(area)
    unique, counts = numpy.unique(localarea, return_counts=True)
    hist=dict(zip(unique,counts))
    del hist[0]
    #print('hist length='+str(len(counts)-1))
    #print('max label='+str(labels.max()))
    meanpixel=sum(counts[1:])/len(counts)
    countseed=numpy.asarray(counts[1:])
    stdpixel=numpy.std(countseed)
    uprange=meanpixel+stdpixel
    lowrange=meanpixel-stdpixel
    sortedkeys=list(sorted(hist,key=hist.get))
    topkey=sortedkeys.pop(0)
    halflength=0.5*len(sortedkeys)
    lowpercentile=numpy.percentile(countseed,25)
    highpercentile=numpy.percentile(countseed,75)
    #if len(sortedkeys)>0 and hist[topkey]<meanpixel:
    #while len(sortedkeys)>0 and hist[topkey]<lowrange and topkey in exceptions:
    zscore=(hist[topkey]-meanpixel)/stdpixel
    #while len(sortedkeys)>halflength and hist[topkey]<=lowrange:
    #while len(sortedkeys)>halflength and zscore<=-2.5:
    while misslabel<=0:
        #topkey=sortedkeys.pop(0)
        print('uprange='+str(uprange))
        print('lowrange='+str(lowrange))
        print('combine part')
        i=topkey
        print(i,hist[i])
        if i not in exceptions:
        #if hist[i]<meanpixel:
            locs=numpy.where(localarea==i)
            ulx,uly=min(locs[1]),min(locs[0])
            rlx,rly=max(locs[1]),max(locs[0])
            width=rlx-ulx
            height=rly-uly
            #windowsize=min(width,height)
            #dividen=2
            subarea=localarea[uly:rly+1,ulx:rlx+1]
            tempsubarea=subarea/i
            #four direction searches
            j=1
            stop=False
            while(stop==False and j<=10):
                up_unique=[]
                down_unique=[]
                left_unique=[]
                right_unique=[]
                maxlabel={}
                if uly-j>=0 and stop==False and len(up_unique)<2:
                    uparray=localarea[uly-j:uly,ulx:rlx+1]
                    up_unique=numpy.unique(uparray)
                    for x in range(len(up_unique)):
                        if up_unique[x]>0:
                            tempdict={up_unique[x]:hist[up_unique[x]]}
                            maxlabel.update(tempdict)
                if rly+j<localarea.shape[0] and stop==False and len(down_unique)<2:
                    downarray=localarea[rly+1:rly+j+1,ulx:rlx+1]
                    down_unique=numpy.unique(downarray)
                    for x in range(len(down_unique)):
                        if down_unique[x]>0:
                            tempdict={down_unique[x]:hist[down_unique[x]]}
                            maxlabel.update(tempdict)
                if ulx-j>=0 and stop==False and len(left_unique)<2:
                    leftarray=localarea[uly:rly+1,ulx-j:ulx]
                    left_unique=numpy.unique(leftarray)
                    for x in range(len(left_unique)):
                        if left_unique[x]>0:
                            tempdict={left_unique[x]:hist[left_unique[x]]}
                            maxlabel.update(tempdict)
                if ulx+j<localarea.shape[1] and stop==False and len(right_unique)<2:
                    rightarray=localarea[uly:rly+1,rlx+1:rlx+j+1]
                    right_unique=numpy.unique(rightarray)
                    for x in range(len(right_unique)):
                        if right_unique[x]>0:
                            tempdict={right_unique[x]:hist[right_unique[x]]}
                            maxlabel.update(tempdict)
                print(up_unique,down_unique,left_unique,right_unique)
                labelpos={}
                for ele in maxlabel:
                    tempdict={ele:0}
                    try:
                        if ele in up_unique:
                            tempdict[ele]+=1
                    except TypeError:
                        pass
                    try:
                        if ele in down_unique:
                            tempdict[ele]+=1
                    except TypeError:
                        pass
                    try:
                        if ele in left_unique:
                            tempdict[ele]+=1
                    except TypeError:
                        pass
                    try:
                        if ele in right_unique:
                            tempdict[ele]+=1
                    except TypeError:
                        pass
                    labelpos.update(tempdict)
                if j==1:
                    combine=False
                    surhist={}
                    for ele in maxlabel:
                        surround=[]
                        if ele in subarea:
                            eleloc=numpy.where(subarea==ele)
                            for k in range(len(eleloc[0])):
                                try:
                                    surround.append(subarea[eleloc[0][k]-1][eleloc[1][k]])
                                except IndexError:
                                    pass
                                try:
                                    surround.append(subarea[eleloc[0][k]+1][eleloc[1][k]])
                                except IndexError:
                                    pass
                                try:
                                    surround.append(subarea[eleloc[0][k]][eleloc[1][k]-1])
                                except IndexError:
                                    pass
                                try:
                                    surround.append(subarea[eleloc[0][k]][eleloc[1][k]+1])
                                except IndexError:
                                    pass
                                if i in surround:
                                    combine=True
                        tempdict={ele:len(surround)}
                        surhist.update(tempdict)
                    if combine==True:
                        #uniq_label,count_label=numpy.unique(surround,return_counts=True)
                        #surhist=dict(zip(uniq_label,count_label))
                        for ele in sorted(surhist,key=surhist.get,reverse=True):
                            localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                            if maxlabel[ele]+hist[i]>=meanpixel and maxlabel[ele]+hist[i]<uprange:
                                if i<ele:
                                    if i not in exceptions:
                                        exceptions.append(i)
                                        print('add exceptions '+str(i))
                                else:
                                    if ele not in exceptions:
                                        exceptions.append(ele)
                                        print('add exceptions '+str(ele))
                            stop=True
                            break
                    for ele in sorted(labelpos,key=labelpos.get,reverse=True):
                        #if labelpos[ele]>1 and stop==False:
                        if stop==False:
                            if labelpos[ele]>1:
                                localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                if maxlabel[ele]+hist[i]>=meanpixel and maxlabel[ele]+hist[i]<uprange:
                                    if i<ele:
                                        if i not in exceptions:
                                            exceptions.append(i)
                                            print('add exceptions '+str(i))
                                    else:
                                        if ele not in exceptions:
                                            exceptions.append(ele)
                                            print('add exceptions '+str(ele))
                                stop=True
                                break
                    if stop==False:
                        for ele in sorted(maxlabel,key=maxlabel.get):
                            freq=maxlabel[ele]
                            if ele in up_unique or ele in down_unique:
                                if freq+hist[i]<meanpixel:
                                    localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                    stop=True
                                    break
                                else:
                                    if freq+hist[i]>=meanpixel and freq+hist[i]<=uprange:
                                        localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                        if i<ele:
                                            if i not in exceptions:
                                                exceptions.append(i)
                                                print('add exceptions '+str(i))
                                        else:
                                            if ele not in exceptions:
                                                exceptions.append(ele)
                                                print('add exceptions '+str(ele))
                                        stop=True
                                        break
                else:
                    if stop==False:
                        for ele in sorted(maxlabel,key=maxlabel.get):
                            freq=maxlabel[ele]
                            if len(up_unique)>0 and ele in up_unique:
                                if freq+hist[i]<meanpixel:
                                    localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                    stop=True
                                    break
                            if len(down_unique)>0 and ele in down_unique:
                                if freq+hist[i]<meanpixel:
                                    localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                    stop=True
                                    break

                            else:
                                if freq+hist[i]>=meanpixel and freq+hist[i]<=uprange:
                                    localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                    if i<ele:
                                        if i not in exceptions:
                                            exceptions.append(i)
                                            print('add exceptions '+str(i))
                                    else:
                                        if ele not in exceptions:
                                            exceptions.append(ele)
                                            print('add exceptions '+str(ele))
                                    stop=True
                                    break


                j+=1
            if j>=10 and stop==False:
                if topkey not in exceptions and hist[topkey]<math.floor(lowrange-2*stdpixel):
                    for ele in sorted(maxlabel,key=maxlabel.get):
                        if len(up_unique)>1 and ele in up_unique:
                            if hist[topkey]+maxlabel[ele]<uprange+stdpixel:
                                localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                if i<ele:
                                    if i not in exceptions:
                                        exceptions.append(i)
                                        print('add exceptions '+str(i))
                                else:
                                    if ele not in exceptions:
                                        exceptions.append(ele)
                                        print('add exceptions '+str(ele))
                                break
                        if len(down_unique)>1 and ele in down_unique:
                            if hist[topkey]+maxlabel[ele]<uprange+stdpixel:
                                localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                                if i<ele:
                                    if i not in exceptions:
                                        exceptions.append(i)
                                        print('add exceptions '+str(i))
                                else:
                                    if ele not in exceptions:
                                        exceptions.append(ele)
                                        print('add exceptions '+str(ele))
                                break

                        if len(up_unique)>1 and len(down_unique)<=1 and ele in up_unique and hist[topkey]+maxlabel[ele]<uprange+2*stdpixel:
                            localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                            if i<ele:
                                if i not in exceptions:
                                    exceptions.append(i)
                                    print('add exceptions '+str(i))
                            else:
                                if ele not in exceptions:
                                    exceptions.append(ele)
                                    print('add exceptions '+str(ele))
                            break
                        if len(down_unique)>1 and len(up_unique)<=1 and ele in down_unique and hist[topkey]+maxlabel[ele]<uprange+2*stdpixel:
                            localarea=combinecrops(localarea,subarea,i,ele,ulx,uly,rlx,rly)
                            if i<ele:
                                if i not in exceptions:
                                    exceptions.append(i)
                                    print('add exceptions '+str(i))
                            else:
                                if ele not in exceptions:
                                    exceptions.append(ele)
                                    print('add exceptions '+str(ele))
                            break

                if topkey in localarea and topkey not in exceptions:
                    exceptions.append(topkey)
                    print('add exceptions '+str(topkey))
            unique, counts = numpy.unique(localarea, return_counts=True)
            hist=dict(zip(unique,counts))
            sortedkeys=list(sorted(hist,key=hist.get))
            meanpixel=sum(counts[1:])/len(counts)
            countseed=numpy.asarray(counts[1:])
            stdpixel=numpy.std(countseed)
            uprange=meanpixel+stdpixel
            lowrange=meanpixel-stdpixel
            topkey=sortedkeys.pop(0)
            #i=topkey
            print('hist leng='+str(len(unique[1:])))
            misslabel+=1
        else:
            topkey=sortedkeys.pop(0)
            misslabel+=1
    #topkey=sortedkeys.pop(0)
    #meanpixel=sum(counts[1:])/len(counts)
    #countseed=numpy.asarray(counts[1:])
    #stdpixel=numpy.std(countseed)
    #uprange=meanpixel+stdpixel
    #lowrange=meanpixel-stdpixel
    #if len(unique)-1==len(labellist):
    #    break
    return localarea
'''

def checkvalid(mislabel,hist,sortedkeys,uprange,lowrange,avgarea):
    allpass=True
    godivide=False
    gocombine=False
    if mislabel>0:
        allpass=False
        godivide=True
        return allpass,godivide,gocombine
    if mislabel<0:
        allpass=False
        gocombine=True
        #if hist[sortedkeys[1]]>avgarea*1.25:
        #    godivide=True
        return allpass,godivide,gocombine
    #for key in sortedkeys:
    #    if hist[key]>max(uprange,avgarea*1.25) and key not in exceptions:
    #        allpass=False
    #        godivide=True
    #        break
    #for i in range(len(sortedkeys)-1,0):
    #    if hist[sortedkeys[i]]<min(lowrange,avgarea/1.25) and sortedkeys[i] not in exceptions:
    #        allpass=False
    #        gocombine=True
    #        break
    return allpass,godivide,gocombine

def getdimension(area):
    unique=numpy.unique(area)
    unique=unique.tolist()
    dimensiondict={}
    for ele in unique:
        if ele!=0 and ele!=1:
            eleloc=numpy.where(area==ele)
            xdist=max(eleloc[1])-min(eleloc[1])
            ydist=max(eleloc[0])-min(eleloc[0])
            dimension=xdist*ydist
            tempdict={ele:dimension}
            if ele not in dimensiondict:
                dimensiondict.update(tempdict)
    return dimensiondict

def processinput(input,avgarea,layers,ittimes=30):
    band=input
    row=band.shape[0]
    col=band.shape[1]

    '''breadfirst search method'''
    rep=[]
    '''
    trigger=False
    for i in range(len(band)):
        if sum(band[i])>0:
            trigger=True
        if trigger==True and sum(band[i])==0:
            rep.append(i)
            trigger=False
    '''
    boundaryarea=boundarywatershed(band,1,'inner')
    #unique=numpy.unique(boundaryarea).tolist()
    #for i in range(len(unique)):
    #    boundaryarea=numpy.where(boundaryarea==unique[i],i,boundaryarea)
    originmethod,misslabel=relabel(boundaryarea)

    band1=numpy.where(originmethod<0,0,originmethod)
    band2=255-band1
    band3=255-band1
    out_fn='originmethod.tif'
    gtiffdriver=gdal.GetDriverByName('GTiff')
    out_ds=gtiffdriver.Create(out_fn,col,row,3,3)
    out_band=out_ds.GetRasterBand(1)
    out_band.WriteArray(band1)
    out_band=out_ds.GetRasterBand(2)
    out_band.WriteArray(band2)
    out_band=out_ds.GetRasterBand(3)
    out_band.WriteArray(band3)
    out_ds.FlushCache()
    labels=numpy.where(boundaryarea<1,0,boundaryarea)
    #labels=boundaryarea
    unique, counts = numpy.unique(labels, return_counts=True)
    hist=dict(zip(unique,counts))
    dimention=getdimension(labels)
    #labels=labels.tolist()
    divide=0
    docombine=0

    meanpixel=sum(counts[1:])/len(counts[1:])
    countseed=numpy.asarray(counts[1:])
    stdpixel=numpy.std(countseed)
    zscore=numpy.abs((countseed-meanpixel)/stdpixel)
    print(zscore)
    uprange=meanpixel+stdpixel
    lowrange=meanpixel-stdpixel
    sortedkeys=list(sorted(hist,key=hist.get,reverse=True))

    allinexceptsions,godivide,gocombine=checkvalid(misslabel,hist,sortedkeys,lowrange,uprange,avgarea)
    par=0.0
    #while allinexceptsions is False:
    lastgreatarea=[]
    lasttinyarea=[]
    for it in range(ittimes):
        if godivide==False and gocombine==False:
            break
    #while godivide==True or gocombine==True:
        try:
            del hist[0]
        except KeyError:
            #continue
            pass
        print('hist length='+str(len(counts)-1))
        print('max label='+str(labels.max()))
        meanpixel=sum(counts[1:])/len(counts)
        countseed=numpy.asarray(counts[1:])
        stdpixel=numpy.std(countseed)
        uprange=meanpixel+stdpixel
        lowrange=meanpixel-stdpixel
        sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
        #j=0

        if godivide is True:
            labels=divideloop(labels,misslabel,avgarea,layers,par)
            #unique=numpy.unique(labels).tolist()
            #for i in range(len(unique)):
            #    labels=numpy.where(labels==unique[i],i,labels)
            unique, counts = numpy.unique(labels, return_counts=True)
            meanpixel=sum(counts[1:])/len(counts[1:])
            countseed=numpy.asarray(counts[1:])
            stdpixel=numpy.std(countseed)
            uprange=meanpixel+stdpixel
            lowrange=meanpixel-stdpixel
            divide+=1
            outputlabel,misslabel=relabel(labels)
            band1=numpy.where(outputlabel<0,0,outputlabel)
            band2=255-band1
            band3=255-band1
            out_fn='labeled_divide'+str(divide)+'.tif'
            gtiffdriver=gdal.GetDriverByName('GTiff')
            out_ds=gtiffdriver.Create(out_fn,col,row,3,3)
            out_band=out_ds.GetRasterBand(1)
            out_band.WriteArray(band1)
            out_band=out_ds.GetRasterBand(2)
            out_band.WriteArray(band2)
            out_band=out_ds.GetRasterBand(3)
            out_band.WriteArray(band3)
            out_ds.FlushCache()
            if lastgreatarea==greatareas and len(lastgreatarea)!=0:
                manualdivide(labels,greatareas)
            lastgreatarea[:]=greatareas[:]
        allinexceptsions,godivide,gocombine=checkvalid(misslabel,hist,sortedkeys,uprange,lowrange,avgarea)
        dimention=getdimension(labels)
        if gocombine is True:
            labels=combineloop(labels,misslabel,par)
            #unique=numpy.unique(labels).tolist()
            #for i in range(len(unique)):
            #    labels=numpy.where(labels==unique[i],i,labels)
            unique, counts = numpy.unique(labels, return_counts=True)
            meanpixel=sum(counts[1:])/len(counts[1:])
            countseed=numpy.asarray(counts[1:])
            stdpixel=numpy.std(countseed)
            uprange=meanpixel+stdpixel
            lowrange=meanpixel-stdpixel
            docombine+=1
            outputlabel,misslabel=relabel(labels)
            band1=numpy.where(outputlabel<0,0,outputlabel)
            band2=255-band1
            band3=255-band1
            out_fn='labeled_combine'+str(docombine)+'.tif'
            gtiffdriver=gdal.GetDriverByName('GTiff')
            out_ds=gtiffdriver.Create(out_fn,col,row,3,3)
            out_band=out_ds.GetRasterBand(1)
            out_band.WriteArray(band1)
            out_band=out_ds.GetRasterBand(2)
            out_band.WriteArray(band2)
            out_band=out_ds.GetRasterBand(3)
            out_band.WriteArray(band3)
            out_ds.FlushCache()
        par+=0.05
        unique, counts = numpy.unique(labels, return_counts=True)
        meanpixel=sum(counts[1:])/len(counts)
        countseed=numpy.asarray(counts[1:])
        stdpixel=numpy.std(countseed)
        hist=dict(zip(unique,counts))
        sortedkeys=list(sorted(hist,key=hist.get,reverse=True))
        for ele in sorted(hist,key=hist.get):
            if ele not in tinyareas:
                print(ele,hist[ele])

        allinexceptsions,godivide,gocombine=checkvalid(misslabel,hist,sortedkeys,uprange,lowrange,avgarea)
        dimention=getdimension(labels)
    #if len(greatareas)>0:
    #    manualdivide(labels,misslabel,avgarea)


    print('DONE!!!  counts='+str(len(counts)))
    time.sleep(5)
    colorlabels,misslabel=relabel(labels)
    band1=numpy.where(colorlabels<0,0,colorlabels)
    band2=255-band1
    band3=255-band1

    NDVIbounary=find_boundaries(labels,mode='inner')
    #NDVIbounary=get_boundary(labels)
    NDVIbounary=NDVIbounary*1

    NDVIbounary=NDVIbounary*255

    out_fn='modifiedsegmethod.tif'
    gtiffdriver=gdal.GetDriverByName('GTiff')
    out_ds=gtiffdriver.Create(out_fn,col,row,3,3)
    out_band=out_ds.GetRasterBand(1)
    out_band.WriteArray(band1)
    out_band=out_ds.GetRasterBand(2)
    out_band.WriteArray(band2)
    out_band=out_ds.GetRasterBand(3)
    out_band.WriteArray(band3)
    out_ds.FlushCache()

    restoredband=numpy.multiply(input,labels)
    res=NDVIbounary
    return labels,res,colortable,greatareas,tinyareas

def kmeansprocess(pixellocs,input,counts):
    global greatareas,tinyareas
    greatareas=[]
    tinyareas=[]
    pixelarray=[]
    for i in range(len(pixellocs[0])):
        pixelarray.append([pixellocs[0][i],pixellocs[1][i]])
    pixelarray=numpy.array(pixelarray)
    clf=KMeans(n_clusters=counts,init='k-means++',n_init=10,random_state=0)
    arraylabels=clf.fit_predict(pixelarray)
    labels=numpy.zeros((450,450))
    for i in range(len(pixellocs[0])):
        labels[pixellocs[0][i],pixellocs[1][i]]=arraylabels[i]
    colorlabels,misslabel=relabel(labels)
    band1=numpy.where(colorlabels<0,0,colorlabels)
    band2=255-band1
    band3=255-band1
    NDVIbounary=find_boundaries(labels,mode='inner')
    NDVIbounary=NDVIbounary*1
    NDVIbounary=NDVIbounary*255

    out_fn='modifiedsegmethod.tif'
    gtiffdriver=gdal.GetDriverByName('GTiff')
    out_ds=gtiffdriver.Create(out_fn,450,450,3,3)
    out_band=out_ds.GetRasterBand(1)
    out_band.WriteArray(band1)
    out_band=out_ds.GetRasterBand(2)
    out_band.WriteArray(band2)
    out_band=out_ds.GetRasterBand(3)
    out_band.WriteArray(band3)
    out_ds.FlushCache()

    restoredband=numpy.multiply(input,labels)
    res=NDVIbounary

    return labels,res,colortable,greatareas,tinyareas

def init(input,map,layers,ittimes):
    global avgarea,elesize
    '''load plantting map'''
    fields=[]
    rows=[]
    counts=0
    elesize=[]
    with open(map,mode='r',encoding='utf-8-sig') as f:
        csvreader=csv.reader(f)
        for row in csvreader:
            rows.append(row)
            temprow=[]
            for ele in row:
                if ele is not '':
                    temprow.append(ele)
            elesize.append(len(temprow))
    rowlen=len(rows[0])
    for i in range(len(rows)):
        for j in range(len(rows[i])):
            if rows[i][j]!='':
                labellist.append(rows[i][j])
                counts+=1
    avgarea=numpy.count_nonzero(input)/counts
    pixellocs=numpy.where(input!=0)
    ulx,uly=min(pixellocs[1]),min(pixellocs[0])
    rlx,rly=max(pixellocs[1]),max(pixellocs[0])
    squarearea=(rlx-ulx)*(rly-uly)
    occupiedratio=len(pixellocs[0])/squarearea
    print(avgarea,occupiedratio)
    uniquelabel,labelcounts=numpy.unique(labellist,return_counts=True)
    plantcount=len(labellist)
    print(plantcount)
    tempcount=3
    for i in range(len(labellist)):   #add color code for each labels
        tempdict={}
        if labellist[i].find('C')==-1:
            if tempcount<=255:
                tempdict={labellist[i]:tempcount}
            else:
                tempdict={labellist[i]:255-(tempcount)}
            tempcount+=1
        else:
            if labellist[i].find('C')!=-1 and labellist[i].find('U')!=-1:
                if tempcount<=255:
                    tempdict={labellist[i]:tempcount}
                else:
                    tempdict={labellist[i]:255-(tempcount)}
                tempcount+=1
            else:
                tempdict={labellist[i]:255}
        if labellist[i] not in colormatch:
            colormatch.update(tempdict)
    print(colormatch)
    #lastlinecount=lastline

    '''load tiff file'''
    if occupiedratio>=0.5:
        labels,res,colortable,greatareas,tinyareas=processinput(input,avgarea,layers)
    else:
        labels,res,colortable,greatareas,tinyareas=kmeansprocess(pixellocs,input,counts)

    return labels,res,colortable,greatareas,tinyareas

def manual(labels,map,boundary,colortable,greatareas,tinyareas):
    labels=manualdivide(labels,greatareas)


    return labels,boundary,colortable,greatareas,tinyareas

#inputimg=gdal.Open('tempNDVI400x400.tif')
#band=inputimg.GetRasterBand(1)
#band=band.ReadAsArray()
#mapfile='wheatmap.csv'

#layers=[]
#for i in range(2):
#    layer=gdal.Open('layersclass'+str(i)+'.tif')
#    lband=layer.GetRasterBand(1)
#    lband=lband.ReadAsArray()
#    layers.append(lband)

#ittimes=30

#init(band,mapfile,layers,ittimes)