#from tkinter import LabelFrame,Label,Button,Frame,Menu,Entry,LEFT,END,Listbox,Scrollbar,Variable,Canvas,Toplevel,Message,Text,DISABLED,NORMAL,Tk,Radiobutton,RIGHT,Y,CENTER,N,W
#import PIL as pil
from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as filedialog
import cv2
import csv
import numpy as np
import gdal
import matplotlib as plt
import matplotlib.pyplot as pyplt
plt.use('TkAgg')
#import rasterio
#from rasterio.plot import show
#import os
from scipy import *
import tkintercore
#import dronprocess
from sklearn.cluster import KMeans
from functools import partial
import calculator
#import tkinterclustering

panelA=None
panelB=None
panelTree=None

RGB=None
Infrared=None
Height=None
NDVI=None

bandarrays={}
workbandarrays={}
tiflayers=[]

nodataposition=None
modified_tif=None

RGBlabel=None
Inflabel=None
Heightlabel=None
comboleft=None
comboright=None
out_png='tempNDVI.jpg'
rotation=None
threshold=None
degreeentry=None
mapfile=''
temptif=None
labels=None
modified_boundary=None
boundarychoice=None
plantchoice=None
w=None  #canvas
erasercoord=[]
paintrecord=[]

labels=None
border=None
colortable=None
greatareas=None
tinyareas=None




class img():
    def __init__(self,size,bands):
        self.size=size
        self.bands=bands

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def startextract(modified_tif,mapfile,tiflayers,iteration):
    global panelA,labels,border,colortable,greatareas,tinyareas
    itertime=int(iteration.get())
    #tkinterclustering.init(modified_tif,mapfile,tiflayers,itertime)
    labels,border,colortable,greatareas,tinyareas=tkintercore.init(modified_tif,mapfile,tiflayers,itertime)

    print(colortable)
    tempbands=np.zeros((450,450,3),np.uint8)
    tempbands[:,:,0]=border
    tempbands[:,:,1]=modified_tif*150
    tempbands[:,:,2]=border
    pyplt.imsave(out_png,tempbands)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=1,column=0)





def drawboundary():
    global panelB,treelist
    inserttop(4)
    insertbottom(4)
    panelTree.grid_forget()
    if mapfile=='':
        messagebox.showerror('Map File',message='Need to load map file.')
        return
    #else:
    #    if threshold is None:
    #        modified_tif=np.where(modified_tif<0,0,1)
        #modified_tif=fillholes(modified_tif)
    if len(tiflayers)==0:
        messagebox.showerror('No image',message='Need to load image.')
        return
    out_fn='tempNDVI400x400.tif'
    gtiffdriver=gdal.GetDriverByName('GTiff')
    out_ds=gtiffdriver.Create(out_fn,modified_tif.shape[1],modified_tif.shape[0],1,3)
    out_band=out_ds.GetRasterBand(1)
    out_band.WriteArray(modified_tif)
    out_ds.FlushCache()


    for i in range(len(tiflayers)):
        out_fn='layersclass'+str(i)+'.tif'
        gtiffdriver=gdal.GetDriverByName('GTiff')
        out_ds=gtiffdriver.Create(out_fn,tiflayers[i].shape[1],tiflayers[i].shape[0],1,3)
        out_band=out_ds.GetRasterBand(1)
        out_band.WriteArray(tiflayers[i])
        out_ds.FlushCache()
    if panelB is not None:
        panelB.destroy()
    panelB=LabelFrame(ctr_right)
    panelB.grid(row=0,column=0)
    #panelA.image=modified_tif
    start=LabelFrame(panelB,text='Set # iteration')
    start.grid(row=0,column=0)
    iterdes=Label(start,text='Iteration')
    iterdes.pack(side=LEFT)
    iterentry=Entry(start)
    iterentry.pack(side=LEFT)
    iterentry.insert(END,30)
    iterbutton=Button(start,text='Start',command=partial(startextract,modified_tif,mapfile,tiflayers,iterentry))
    iterbutton.pack(side=LEFT)
    #manual=LabelFrame(panelB,text='Combine and Divide (OPTIONAL)')
    #manual.grid(row=1,column=0)
    #manualdes=Label(manual,text='If there are borders placed incorrectly, click the button to modify that.')
    #manualdes.grid(row=0,column=0,columnspan=1)
    #manualbutton=Button(manual,text='Modify')
    #manualbutton.grid(row=1,column=1)



    #tkintercore.init(modified_tif,mapfile,tiflayers)
    #if rotation!=0:
    #    smalltif=rotat(rotation,newNDVI)
    #else:
    #    smalltif=cv2.resize(newNDVI,(450,450),interpolation=cv2.INTER_NEAREST)



def setthreshold():
    global threshold,panelA,modified_tif
    threshold=float(thresholdentry.get())
    modified_tif=np.where(modified_tif<threshold,0,modified_tif)
    pyplt.imsave(out_png,modified_tif)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=1,column=0)


def resetrotate():
    global modified_tif,panelA,rotation,workbandarrays
    rotation=0
    if len(bandarrays.keys())==1:
        bandname='NDVI'
    else:
        try:
            bandname=treelist.selection_get()
        except:
            bandname='NDVI'
    band=bandarrays[bandname]
    keys=workbandarrays.keys()
    for key in keys:
        workbandarrays[key]=cv2.resize(bandarrays[key],(450,450),interpolation=cv2.INTER_LINEAR)
    modified_tif=cv2.resize(band,(450,450),interpolation=cv2.INTER_NEAREST)
    pyplt.imsave(out_png,modified_tif)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=1,column=0)

def antirotatecv(degreeentry):
    global modified_tif,panelA,rotation,workbandarrays
    try:
        if type(rotation)==type(None):
            rotation=float(degreeentry.get())
        else:
            rotation+=float(degreeentry.get())
        localrotate=float(degreeentry.get())
    except ValueError:
        messagebox.showerror('Error',message='No Degree entry!')
        return
    center=(225,225)
    #center=(RGB.size[0]/2,RGB.size[1]/2)
    M=cv2.getRotationMatrix2D(center,localrotate,1.0)
    keys=workbandarrays.keys()
    for key in keys:
        workbandarrays[key]=cv2.warpAffine(workbandarrays[key],M,dsize=(450,450),flags=cv2.INTER_LINEAR)
    #modified_tif=cv2.warpAffine(modified_tif,M,dsize=(450,450),flags=cv2.INTER_LINEAR)
    try:
        key=treelist.selection_get()
        #modified_tif=cv2.resize(workbandarrays[key],(450,450),interpolation=cv2.INTER_LINEAR)
        modified_tif=workbandarrays[key]
    except:
        modified_tif=workbandarrays['NDVI']
        #modified_tif=cv2.resize(workbandarrays['NDVI'],(450,450),interpolation=cv2.INTER_LINEAR)
    pyplt.imsave(out_png,modified_tif)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=1,column=0)

def rotationpanel():
    global panelB,panelTree,root
    inserttop(2)
    insertbottom(2)
    if len(bandarrays)==0:
        messagebox.showerror('No 2D tif',message='No 2D tif is loaded.')
        return
    if panelB is not None:
        panelB.destroy()
    panelTree.grid_forget()

    panelB=Label(ctr_right)
    panelB.grid(row=0,column=0)
    anticlockrotdes=Label(master=panelB,text='Rotation Degree',justify=LEFT)
    anticlockrotdes.grid(row=1,column=0)
    degreeentry=Entry(master=panelB)
    degreeentry.grid(row=1,column=1)
    anticlockrotbutton=Button(master=panelB,text='Rotate',command=partial(antirotatecv,degreeentry))
    anticlockrotbutton.grid(row=1,column=2)
    #cloclrotdes=Label(master=panelB,text='Clockwise Rotation')
    #cloclrotdes.grid(row=2,column=0)
    #clockrotbutton=Button(master=panelB,text='+15 degree',command=rotate)
    #clockrotbutton.grid(row=2,column=1)
    notedes=Label(master=panelB,text='Note: Rotations lose information of your image.\n Please rotate to the extent you need.'
                                     '\n Once the last plot of your top-down first line\n is higher than the first plot of your second line,\n it is fine',width=35,justify=LEFT,anchor=W)
    notedes.grid(row=2,column=0,columnspan=1)
    resetdes=Label(master=panelB,text='Reset Image(if needed)')
    resetdes.grid(row=3,column=0)
    resetbutton=Button(master=panelB,text='Reset',command=resetrotate)
    resetbutton.grid(row=3,column=1)

def widthinterpreter(width):
    if width=='1':
        return 1
    if width=='2':
        return 2
    if width=='3':
        return 3
    if width=='4':
        return 4
    if width=='5':
        return 5
def release(e):
    global w
    #print('click at',e.x,e.y)
    w.old_coords=None
    w.old_drawcoords=None

def drag(e,widthchoice):
    global w
    #global mousex,mousey
    mousex=e.x
    mousey=e.y
    #if w.old_coords:
        #x1,y1=w.old_coords
        #w.create_line(mousex,mousey,x1,y1,width=widthchoice.get())
    w.create_rectangle(mousex,mousey,mousex+widthchoice.get(),mousey+widthchoice.get(),fill='black',outline="")
   # w.old_coords=mousex,mousey
    for i in range(widthchoice.get()+1):
        erasercoord.append([e.x,e.y])
        erasercoord.append([e.x,e.y+i])
        erasercoord.append([e.x+i,e.y])
        erasercoord.append([e.x+i,e.y+i])
        print('click at',e.x+i,e.y+i)

def drawdrag(e,widthchoice):
    global w
    mousex=e.x
    mousey=e.y
    #if w.old_drawcoords:
        #x1,y1=w.old_drawcoords
        #w.create_line(mousex,mousey,x1,y1,fill='green',width=widthchoice.get())
    w.create_rectangle(mousex,mousey,mousex+widthchoice.get(),mousey+widthchoice.get(),fill='yellow',outline="")
    #w.old_drawcoords=mousex,mousey
    for i in range(widthchoice.get()+1):
        paintrecord.append([e.x,e.y])
        paintrecord.append([e.x,e.y+i])
        paintrecord.append([e.x+i,e.y])
        paintrecord.append([e.x+i,e.y+i])
        print('draw at',e.x+i,e.y+i)

def eraser(panelC):
    global w
    w.config(cursor='cross')

    widthframe=LabelFrame(panelC,text='Width Selection')
    widthframe.grid(row=1,columnspan=4)
    widthchoice=IntVar()
    widthchoice.set(1)
    for i in range(5):
        widthbutton=Radiobutton(widthframe,text=str(i+1),value=i,variable=widthchoice)
        widthbutton.pack(side=LEFT)
        if i==0:
            widthbutton.select()
    w.bind('<ButtonRelease-1>',release)
    w.bind('<B1-Motion>',lambda event,arg=widthchoice:drag(event,widthchoice))

def paint(panelC):
    global w
    w.config(cursor='pencil')

    widthframe=LabelFrame(panelC,text='Width Selection')
    widthframe.grid(row=1,columnspan=4)
    widthchoice=IntVar()
    for i in range(5):
        widthbutton=Radiobutton(widthframe,text=str(i+1),value=i,variable=widthchoice)
        widthbutton.pack(side=LEFT)
        if i==0:
            widthbutton.select()
    w.bind('<ButtonRelease-1>',release)
    w.bind('<B1-Motion>',lambda event,arg=widthchoice:drawdrag(event,widthchoice))

def canvasreset(inputimage):
    global w,erasercoord,paintrecord
    w.old_coords=None
    w.create_image(0,0,image=inputimage,anchor=NW)
    erasercoord=[]
    paintrecord=[]

def canvasok(window,manualtoolframe):
    global panelA,modified_tif
    if len(erasercoord)>0:
        for i in range(len(erasercoord)):
            x=erasercoord[i][0]
            y=erasercoord[i][1]
            if x>=0 and x<450 and y>=0 and y<450:
                modified_tif[y,x]=0
    if len(paintrecord)>0:
        for i in range(len(paintrecord)):
            x=paintrecord[i][0]
            y=paintrecord[i][1]
            if x>=0 and x<450 and y>=0 and y<450:
                modified_tif[y,x]=1
    pyplt.imsave(out_png,modified_tif)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=0,column=0)
    manualtoolframe.grid_forget()
    window.destroy()


def manualeraser(inputimage,manultoolframe):
    global temptif,panelA,modified_tif,plantchoice,tiflayers,w
    panelC=Toplevel()
    toolselectionframe=LabelFrame(panelC,text='Tools')
    toolchoice=None
    eraserbutton=Radiobutton(toolselectionframe,text='Eraser',value=0,command=partial(eraser,panelC),variable=toolchoice)
    paintbutton=Radiobutton(toolselectionframe,text='Pen',value=1,command=partial(paint,panelC),variable=toolchoice)
    canvasframe=LabelFrame(panelC,text='Canvas')
    w=Canvas(canvasframe,width=450,height=450,bg='white')
    w.old_coords=None
    w.old_drawcoords=None
    #w.bind('<Enter>',w.config(cursor="cross"))


    #w.bind('<Leave>',cursor="arrow")
    w.create_image(0,0,image=inputimage,anchor=NW)
    okeybutton=Button(panelC,text='OK',command=partial(canvasok,panelC,manultoolframe))
    restartbutton=Button(panelC,text='Reset',command=partial(canvasreset,inputimage))

    toolselectionframe.grid(row=0,column=0,columnspan=2)
    eraserbutton.pack(side=LEFT)
    paintbutton.pack(side=LEFT)

    canvasframe.grid(row=2,column=0,columnspan=2)
    w.grid(row=0,column=0)
    okeybutton.grid(row=3,column=1)
    restartbutton.grid(row=3,column=0)
    CreateToolTip(canvasframe,'Modify areas here')
    CreateToolTip(okeybutton,'Save modification and exit')
    CreateToolTip(restartbutton,'Reset to origin image')

def generateplant(checkboxdict):
    global temptif,panelA,modified_tif,plantchoice,tiflayers,panelB,erasercoord,paintrecord
    plantchoice=[]
    keys=checkboxdict.keys()
    for key in keys:
        plantchoice.append(checkboxdict[key].get())
    modified_tif=np.zeros(temptif.shape)
    tiflayers=[]
    for i in range(len(plantchoice)):
        tup=plantchoice[i]
        if '1' in tup:
            modified_tif=np.where(temptif==i,1,modified_tif)
            zerograph=np.zeros(temptif.shape)
            zerograph=np.where(temptif==i,1,zerograph)
            tiflayers.append(zerograph)

    #resizemodifiedtif=cv2.resize(modified_tif,(RGB.size[1],RGB.size[0]),interpolation=cv2.INTER_LINEAR)
    #resizemodifiedtif=np.array(bandarrays['NDVI'])*resizemodifiedtif
    #resizemodifiedtif=np.where(resizemodifiedtif<=float(threshold.get()),0,1)
    #modified_tif=cv2.resize(resizemodifiedtif,(450,450),interpolation=cv2.INTER_LINEAR)
    #baseimg=cv2.resize(np.array(bandarrays['NDVI']),(450,450),interpolation=cv2.INTER_LINEAR)
    #baseimg=np.where(baseimg<=float(threshold.get()),0,baseimg)
    #modified_tif=np.where(modified_tif<=float(threshold.get()),0,1)


    pyplt.imsave(out_png,modified_tif)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=0,column=0)
    erasercoord=[]
    paintrecord=[]
    print(temptif)
    manualtoolframe=LabelFrame(panelB,text='Manually modify pre-processed image (OPTIONAL)')
    manualtoolframe.grid(row=6,columnspan=3)
    manualtoolbutton=Button(manualtoolframe,text='Modify image',command=partial(manualeraser,image,manualtoolframe))
    print(plantchoice)
    #manualeraser(image)
    manualtoolbutton.pack()

def kmeansclassify(bandchoice,classentry):
    global modified_tif,temptif,panelB,panelA
    wchildren=panelB.winfo_children()
    #for i in range(len(wchildren)):
    #    if wchildren[i].name=='kmeansresult':
    #        wchildren[i].grid_forget()

    keys=bandchoice.keys()
    numindec=0
    choicelist=[]
    for key in keys:
        tup=bandchoice[key].get()
        if '1' in tup:
            numindec+=1
            choicelist.append(key)
    reshapemodified_tif=np.zeros((modified_tif.shape[0]*modified_tif.shape[1],numindec))
    for i in range(numindec):
        #tempband=bandarrays[choicelist[i]]
        tempband=workbandarrays[choicelist[i]]
        #tempband=cv2.resize(tempband,(450,450),interpolation=cv2.INTER_LINEAR)
        reshapemodified_tif[:,i]=tempband.reshape(tempband.shape[0]*tempband.shape[1],1)[:,0]




    #reshapemodified_tif=modified_tif.reshape(modified_tif.shape[0]*modified_tif.shape[1],1)
    clusternumber=int(classentry.get())
    clf=KMeans(n_clusters=clusternumber,init='k-means++',n_init=10,random_state=0)
    if len(choicelist)==0:
        messagebox.showerror('No Indices is selected',message='Please select indicies to do KMeans Classification.')
        return
    labels=clf.fit_predict(reshapemodified_tif)
    temptif=labels.reshape(modified_tif.shape[0],modified_tif.shape[1])
    checkboxframe=LabelFrame(panelB,text='Select classes (check/empty boxes to see results)',name='kmeansresult')
    checkboxframe.grid(row=5,columnspan=3)
    #checkboxframe.grid_propagate(False)
    checkboxdict={}
    for i in range(clusternumber):
        dictkey='class '+str(i+1)
        if i==1 or i==2 or i==4:
            tempdict={dictkey:Variable(value='1')}
        else:
            tempdict={dictkey:Variable()}
        checkboxdict.update(tempdict)
        ch=ttk.Checkbutton(checkboxframe,text=dictkey,command=partial(generateplant,checkboxdict),variable=checkboxdict[dictkey])
        ch.grid(row=int(i/5),column=int(i%5))
    #generateplantargs=partial(generateplant,ch0,ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8,ch9)
    #genchbutton=Button(checkboxframe,text='Generate plant',command=partial(generateplant,checkboxdict))
    #genchbutton.grid(row=0,column=5)
    #gendes=Label(checkboxframe,text='(Light color represents plant)')
    #gendes.grid(row=1,column=5)
    CreateToolTip(checkboxframe,'Select classes to check results of single class or combined classes')

    #modified_tif=np.where((temptif==3) | (temptif==2),1,0)
    #plantmap=LabelFrame(panelB,text='map plant scheme to plants (no boundary)')
    #plantmap.grid(row=7,column=1)
    #mapplant=Button(plantmap,text='Map planting shceme',command=drawboundary)
    #mapplant.grid(row=0,column=0)
    return checkboxframe


def medianblurplus(entbox):
    global modified_tif,panelA
    val=int(entbox.get("1.0",END))
    entbox.insert(str(val))
    modified_tif=cv2.medianBlur(modified_tif,val+1)
    panelA.configure(image=modified_tif)



def KMeansPanel():
    global panelB,panelTree
    inserttop(3)
    insertbottom(3)
    if len(bandarrays)==0:
        messagebox.showerror('No 2D layers',message='No 2D layer is loaded')
        return
    if panelB is not None:
        panelB.destroy()
    panelB=Label(ctr_right)
    panelB.grid(row=0,column=0)
    #panelTree.grid_forget()
    chframe=LabelFrame(panelB,text='Pick indicies below')
    chframe.grid(row=0,column=0,columnspan=2)
    chcanvas=Canvas(chframe,width=400,height=30)
    chcanvas.pack(side=LEFT)
    chscroller=Scrollbar(chframe)
    chscroller.pack(side=RIGHT,fill=Y)
    chcanvas.config(yscrollcommand=chscroller.set)
    chscroller.config(command=chcanvas.yview)
    bandkeys=bandarrays.keys()
    bandchoice={}
    for key in bandkeys:
        tempdict={key:Variable()}
        bandchoice.update(tempdict)
        ch=ttk.Checkbutton(chcanvas,text=key,variable=bandchoice[key])
        ch.pack()

    #thresholddes=Label(master=panelB,text='Set Threshold (0,1)',justify=LEFT)
    #thresholddes.grid(row=3,column=0)
    #thresholdentry=Entry(master=panelB)
    #thresholdentry.insert(END,0)
    #thresholdentry.grid(row=3,column=1)
    #thresholdbutton=Button(master=panelB,text='Set',command=setthreshold)
    #thresholdbutton.grid(row=3,column=2)
    clusternumberdes=Label(panelB,text='Set # of classes')
    clusternumberdes.grid(row=3,column=0)
    clusternumberentry=Entry(panelB)
    clusternumberentry.insert(END,5)
    clusternumberentry.grid(row=3,column=1)
    kmeansdes=Label(master=panelB,text='KMeans Clustering',justify=LEFT)
    kmeansdes.grid(row=4,column=0)
    kmeansbutton=Button(master=panelB,text='Classify',command=partial(kmeansclassify,bandchoice,clusternumberentry))
    kmeansbutton.grid(row=4,column=1)
    CreateToolTip(kmeansbutton,'1. Select indicies you want to cluster with K-Means algorithm\n 2.Click "Classify" button to start K-Means\n 3. You can classify manytimes, as long as you click the "Classify" button')
    #blurframe=LabelFrame(panelB,text='MedianBlur')
    #blurframe.grid(row=4,column=0)
    #entbox=Entry(blurframe)
    #entbox.insert(0)
    #medianplus=Button(blurframe,text='+',command=)

def Generate_NDVI():
    global panelA,NDVI,panelB,modified_tif,thresholdentry,degreeentry
    if Infrared is not None and RGB is not None and Infrared.size==RGB.size:
        upper=Infrared.bands[0,:,:]-RGB.bands[0,:,:]
        lower=Infrared.bands[0,:,:]+RGB.bands[0,:,:]
        lower=np.where(lower==0,1,lower)
        NDVI=upper/lower
        out_fn='tempNDVI.tif'
        gtiffdriver=gdal.GetDriverByName('GTiff')
        out_ds=gtiffdriver.Create(out_fn,upper.shape[1],upper.shape[0],1,3)
        out_band=out_ds.GetRasterBand(1)
        out_band.WriteArray(NDVI)
        out_ds.FlushCache()

        modified_tif=cv2.resize(NDVI,(450,450),interpolation=cv2.INTER_NEAREST)
        pyplt.imsave(out_png,modified_tif)
        image=cv2.imread(out_png)
        image=Image.fromarray(image)
        image=ImageTk.PhotoImage(image)
        if panelA is not None:
            panelA.destroy()
        panelA=Label(ctr_left,image=image)
        panelA.image=image
        panelA.grid(row=1,column=0)
        #if panelB is not None:
        #    panelB.destory()

        #thresholddes=Label(master=panelB,text='Step 1. Set Threshold (0,1)',justify=LEFT)
        #thresholddes.grid(row=1,column=0)
        #thresholdentry=Entry(master=panelB)
        #thresholdentry.grid(row=1,column=1)
        #thresholdbutton=Button(master=panelB,text='Set',command=setthreshold)
        #thresholdbutton.grid(row=1,column=2)
        kmeansdes=Label(master=panelB,text='Step 2. Classify pixels (10 categories)',justify=LEFT)
        kmeansdes.grid(row=4,column=0)
        kmeansbutton=Button(master=panelB,text='Classify',command=kmeansclassify)
        kmeansbutton.grid(row=4,column=1)

        #boundarybutton=Button(master=panelB,text='draw boundary',command=drawboundary)
        #boundarybutton.grid(row=8,column=1)


def Open_HEIGHTfile(entbox):
    global Height,Heightlabel
    entbox.config(stat=NORMAL)
    entbox.delete("1.0",END)
    entbox.tag_config("wrap",wrap=CHAR)
    QGISNIRFILE=filedialog.askopenfilename()
    if len(QGISNIRFILE)>0:
        if QGISNIRFILE.endswith('.tif') is False:
            messagebox.showerror('Wrong file formate',message='Open tif formate file')
            return
        #messagebox.showinfo(title='Open Height file',message='open Height GeoTiff file:'+QGISNIRFILE)
        entbox.insert(END,QGISNIRFILE,"wrap")
        entbox.config(stat=DISABLED)
        NIRrsc=gdal.Open(QGISNIRFILE)
        NIRsize=(NIRrsc.RasterYSize,NIRrsc.RasterXSize)
        bands=[]
        bandrank={}
        for j in range(1):
            band=NIRrsc.GetRasterBand(j+1)
            stats = band.GetStatistics( True, True )
            print("[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (
                    stats[0], stats[1], stats[2], stats[3] ))
            tempdict={j:stats[1]}
            bandrank.update(tempdict)
            nodata=band.GetNoDataValue()
            if type(nodata)==type(None):
                nodata=0
            band=band.ReadAsArray()
            band=np.where(band==nodata,1e-6,band)
            bands.append(band)
        bands=np.array(bands)
        Height=img(NIRsize,bands)
        print(bands)
        Heightlabel.text='Open file: '+QGISNIRFILE
    #Generate_NDVI()


def Open_NIRfile(entbox):
    global Infrared,Inflabel
    entbox.config(stat=NORMAL)
    entbox.delete("1.0",END)
    entbox.tag_config("wrap",wrap=CHAR)
    QGISNIRFILE=filedialog.askopenfilename()
    if len(QGISNIRFILE)>0:
        if QGISNIRFILE.endswith('.tif') is False:
            messagebox.showerror('Wrong file formate',message='Open tif formate file')
            return
        entbox.insert(END,QGISNIRFILE,"wrap")
        entbox.config(stat=DISABLED)
        #messagebox.showinfo(title='Open NIR file',message='open NIR GeoTiff file:'+QGISNIRFILE)
        NIRrsc=gdal.Open(QGISNIRFILE)
        NIRsize=(NIRrsc.RasterYSize,NIRrsc.RasterXSize)
        bands=[]
        bandrank={}
        for j in range(3):
            band=NIRrsc.GetRasterBand(j+1)
            stats = band.GetStatistics( True, True )
            print("[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (
                    stats[0], stats[1], stats[2], stats[3] ))
            tempdict={j:stats[1]}
            bandrank.update(tempdict)
            nodata=band.GetNoDataValue()
            if type(nodata)==type(None):
                nodata=0
            if nodata<stats[0] or nodata>stats[1]:
                nodata=0
            band=band.ReadAsArray()
            band=np.where(band==nodata,1e-6,band)
            bands.append(band)
        bands=np.array(bands)
        NIRbands=np.zeros(bands.shape)
        i=0
        for e in sorted(bandrank,key=bandrank.get,reverse=True):
            NIRbands[i,:,:]=bands[e,:,:]
            i=i+1
        Infrared=img(NIRsize,NIRbands)
        Inflabel.text='Open file: '+QGISNIRFILE
        print(NIRbands)
    #Generate_NDVI()

def Open_RGBfile(entbox):
    global RGB,RGBlabel,nodataposition
    entbox.config(stat=NORMAL)
    entbox.delete("1.0",END)
    entbox.tag_config("wrap",wrap=CHAR)
    QGISRGBFILE=filedialog.askopenfilename()
    if len(QGISRGBFILE)>0:
        if QGISRGBFILE.endswith('.tif') is False:
            messagebox.showerror('Wrong file formate',message='Open tif formate file')
            return
        #messagebox.showinfo(title='Open RGB file',message='open RGB GeoTiff file:'+QGISRGBFILE)
        entbox.insert(END,QGISRGBFILE,"wrap")
        entbox.config(stat=DISABLED)
        RGBrsc=gdal.Open(QGISRGBFILE)
        RGBsize=(RGBrsc.RasterYSize,RGBrsc.RasterXSize)
        bands=[]
        bandrank={}
        for j in range(3):
            band=RGBrsc.GetRasterBand(j+1)
            stats = band.GetStatistics( True, True )
            print("[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (
                    stats[0], stats[1], stats[2], stats[3]))
            tempdict={j:stats[1]}
            bandrank.update(tempdict)
            nodata=band.GetNoDataValue()
            if type(nodata)==type(None):
                nodata=0
            if nodata<stats[0] or nodata>stats[1]:
                nodata=0
            band=band.ReadAsArray()
            nodataposition=np.where(band==nodata)
            band=np.where(band==nodata,1e-6,band)
            bands.append(band)
        bands=np.array(bands)
        RGBbands=np.zeros(bands.shape)
        i=0
        for e in sorted(bandrank,key=bandrank.get,reverse=True):
            RGBbands[i,:,:]=bands[e,:,:]
            i=i+1
        RGB=img(RGBsize,RGBbands)
        RGBlabel.text='Open file: '+QGISRGBFILE
        print(RGBbands)
    #Generate_NDVI()

def inserttop(step):
    global panelWelcome
    topconteont=['1. Open File','2. Band Calculation', '3. Rotation', '4. Classification','5. Crop Extraction','6. Export']
    panelWelcome.config(stat=NORMAL)
    panelWelcome.delete("1.0",END)
    panelWelcome.tag_config("font",font='Helvetia 14')
    panelWelcome.tag_config("bfont",font='Helvetia 14 bold',foreground='red')
    for i in range(len(topconteont)):
        if i==step:
            panelWelcome.insert(END,' '+topconteont[i],"bfont")
        else:
            panelWelcome.insert(END,' '+topconteont[i],"font")
    panelWelcome.config(stat=DISABLED)
    CreateToolTip(panelWelcome,text="The software is sensitive with noise pixel, please process image that only contains your plant. You can use shapefile to cut the area out via QGIS.\n "
                         "The software processes TIF format image, please convert JPEG formate into TIF. You can use QGIS to do that.\n"
                         "steps:\n"
                         "1. Open RGB and NIR image, if you have HEIGHT image, the software also support that."
                         "Map file is a csv file, you can generate yourself.\n Map file should contain the labels (labels can be number or words) of your plants, and the labels should be arranged in the same way as your plants.\n "
                         "2. You can rotate your image, using 'Rotation' under 'tools'.\n Rotation image usually will lose information, you only need to rotate the image if it tilt over (+/-) 45 degrees.\n"
                         "3. Band calculation let you define your own equation (select 'custom'), the software will present results of your equation. NDVI is default.\n"
                         "4. Classify will do K-Means cluster for bands. At least one band have to be selected to run it. You can select multiple bands as indices to implement K-Means.\n The classes you select within the K-Means results will be the prototype image to process.\n"
                         "5. Extract crop will identify boundaries for each of your crops. Default iteration time is 30.\n"
                         "6. You can export the results using the 'Export' function. The software export three type of files:\n"
                         " A tif image that have the boundaries on your original RGB image.\n"
                         " A tif image have the labeles on each crops. A csv file containing\n"
                         " the NDVI data for each labelled crops.'")

def on_enter(conenttext,contentwindow):
    contentwindow.config(text=conenttext)

def on_leave(contentwindow):
    contentwindow.config(text="")

def insertbottom(step):
    global btm_frame
    for widget in btm_frame.winfo_children():
        widget.pack_forget()
    commands=[partial(QGIS_NDVI),partial(bands_calculation),partial(rotationpanel),partial(KMeansPanel),partial(drawboundary),partial(export_result)]
    tips=['Step 1, open files','Step 2, implement band calculations','Step 3, rotate your image to certain degree to process\n if it is not tilt too much, you can skip to next step,',
          'Step 4, Use K-Means cluster your band calculation results, you can select indecies for K-Means',
          'Step 5, Extract crops from your pre-processed image',
          'Step 6, Export results including a tif image with your original crops with boundaries,\n'
          'a tif that each crop is labeled with a specific number for other analysis,\n'
          'a csv file including #pixel, sum-NDVI, avg-NDVI, std-NDVI'
        ]
    if step!=0:
        lastaction=commands[step-1]
        lastactiontipcontent=tips[step-1]
    else:
        lastaction=None
        lastactiontipcontent='Not valid now'
    if step!=5:
        futureaction=commands[step+1]
        futureactiontipcontent=tips[step+1]
    else:
        futureaction=None
        futureactiontipcontent='Not valid now'
    LastactionButton=Button(btm_frame,text='< Last Step',command=lastaction)
    CreateToolTip(LastactionButton,text=lastactiontipcontent)
    FutureacitonButton=Button(btm_frame,text='Next Step >',command=futureaction)
    CreateToolTip(FutureacitonButton,text=futureactiontipcontent)
    RestartButton=Button(btm_frame,text='Restart',command=QGIS_NDVI)
    CreateToolTip(RestartButton,text='Go back to Step 1. Cancel all steps you have processed')
    if type(lastaction)==type(None):
        LastactionButton.config(state=DISABLED)
    if type(futureaction)==type(None):
        FutureacitonButton.config(state=DISABLED)
    LastactionButton.pack(side=LEFT,padx=5,pady=5)
    RestartButton.pack(side=LEFT,padx=5,pady=5)
    FutureacitonButton.pack(side=LEFT,padx=5,pady=5)

def QGIS_NDVI():
    global panelA,panelB,RGBlabel,Inflabel,Heightlabel,panelTree,treelist,rotation,root,panelWelcome
    #panelWelcome.configure(text='')
    #root.geometry("")
    inserttop(0)
    insertbottom(0)
    if panelA is not None:
        panelA.destroy()
    if panelB is not None:
        panelB.destroy()
    rotation=None
    panelTree.grid_forget()
    treelist.delete(0,END)
    panelA=Label(ctr_left)
    panelA.grid(row=1,column=0)
    bandarrays.clear()
    workbandarrays.clear()
    modified_tif=None

    RGBlabel=Text(panelA,height=2,width=40)
    RGBlabel.config(stat=DISABLED)
    Inflabel=Text(panelA,height=2,width=40)
    Inflabel.config(stat=DISABLED)
    Heightlabel=Text(panelA,height=2,width=40)
    Heightlabel.config(stat=DISABLED)
    Maplabel=Text(panelA,height=2,width=40)
    Maplabel.config(stat=DISABLED)
    Notelabel=Label(panelA,text='Note: If you do not have NIR image, open the RGB image as the NIR file.')

    QGISRGBbutton=Button(panelA,text='Open RGB file (*.tif)',command=partial(Open_RGBfile,RGBlabel))
    QGISNIRbutton=Button(panelA,text='Open NIR file (*.tif)',command=partial(Open_NIRfile,Inflabel))
    QGISHeightbutton=Button(panelA,text='Open HEIGHT file (*.tif)',command=partial(Open_HEIGHTfile,Heightlabel))
    QGISMapbutton=Button(panelA,text='Open Map file (*.csv)',command=partial(select_map,Maplabel))

    QGISRGBbutton.grid(row=1,column=0,sticky=N)
    QGISNIRbutton.grid(row=2,column=0,sticky=N)
    QGISHeightbutton.grid(row=3,column=0,sticky=N)
    QGISMapbutton.grid(row=4,column=0,sticky=N)
    RGBlabel.grid(row=1,column=1)
    Inflabel.grid(row=2,column=1)
    Heightlabel.grid(row=3,column=1)
    Maplabel.grid(row=4,column=1)
    Notelabel.grid(row=5,column=0,sticky=N)

    '''
    else:
            image=gdal.Open(path)
            band=image.GetRasterBand(1)
            band=band.ReadAsArray()
            size=band.shape
            rpath=path.replace(" ","\ ")
            commandline="gdalwarp -of GTiff -ts 400 400 "+rpath+'rgboutput.tif'
            os.system('rm rgboutput.tif')
            os.system('gdalwarp -of GTiff -ts 400 400 '+rpath+' rgboutput.tif')
            modified_image=gdal.Open('rgboutput.tif')
            bands=[]
            for j in range(3):
                band=modified_image.GetRasterBand(j+1)
                band=band.ReadAsArray()
                if (j+1)!=4:
                    bands.append(band)
            #modified_image=cv2.resize(bands,(450,450),interpolation=cv2.INTER_AREA)
            bands=np.array(bands)
            RGB=img(size,image)
            #image=Image.fromarray(bands)
            image=rasterio.open('rgboutput.tif')
            show(image)
    '''


def select_image():
    global panelA,RGB,RGBlabel
    if panelA is not None:
        panelA.destroy()

    path=filedialog.askopenfilename()

    if len(path)>0:
        image=cv2.imread(path)
        image=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        size=Image.fromarray(image)
        modified_image=cv2.resize(image,(450,450),interpolation=cv2.INTER_LINEAR)
        greenlowerbound=np.array([30,20,20])
        greenupperbound=np.array([90,255,255])
        H=modified_image[:,:,0]
        S=modified_image[:,:,1]
        V=modified_image[:,:,2]
        H=np.where((H<90) & (H>30),H,0)
        S=np.where((S<255) & (S>20),S,0)
        V=np.where((V<255) & (V>20),V,0)
        modified_image[:,:,0]=H
        modified_image[:,:,1]=S
        modified_image[:,:,2]=V
        image=Image.fromarray(modified_image)
        RGB=img(size.size,modified_image)
        image=ImageTk.PhotoImage(image)
        if panelA is None: #or panelB is None:
            panelA=Label(ctr_left,image=image)
            panelA.image=image
            #panelA.pack(side="left",padx=10,pady=10)
            panelA.pack()
            #panelB=Label(image=edged)
            #RGBlabel.grid(row=3,column=0)
        else:
            panelA.destroy()
            panelA=Label(ctr_left,image=image)
            panelA.image=image
            panelA.pack()




def select_inf_image():
    global panelB,Infrared,Inflabel

    path=filedialog.askopenfilename()
    if panelB is not None:
        panelB.destroy()

    if len(path)>0:
        #if path.endswith('.jpg'):
        image=cv2.imread(path)
        image=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        size=Image.fromarray(image)
        modified_image=cv2.resize(image,(450,450),interpolation=cv2.INTER_LINEAR)
        greenlowerbound=np.array([30,20,20])
        greenupperbound=np.array([90,255,255])
        H=modified_image[:,:,0]
        S=modified_image[:,:,1]
        V=modified_image[:,:,2]
        H=np.where((H<90) & (H>30),H,0)
        S=np.where((S<255) & (S>20),S,0)
        V=np.where((V<255) & (V>20),V,0)
        modified_image[:,:,0]=H
        modified_image[:,:,1]=S
        modified_image[:,:,2]=V

        #image=cv2.cvtColor(modified_image,cv2.COLOR_BGR2RGB)
        image=Image.fromarray(modified_image)
        Infrared=img(size.size,modified_image)
        image=ImageTk.PhotoImage(image)
        if panelB is None:
            panelB=Label(ctr_right,image=image)
            panelB.image=image
            #panelB.pack(side="right",padx=10,pady=10)
            panelB.pack()
            #Inflabel=Label(text="size of Infrared="+str(size.size[0])+'x'+str(size.size[1]))
            #Inflabel.grid(row=3,column=1)
        else:
            panelB.configure(image=image)
            panelB.image=image
            #Inflabel=Label(text="size of Infrared="+str(size.size[0])+'x'+str(size.size[1]))
            #Inflabel.grid(row=3,column=1)


def select_map(entbox):
    global panelC,mapfile
    path=filedialog.askopenfilename()
    entbox.config(stat=NORMAL)
    entbox.delete("1.0",END)
    entbox.tag_config("wrap",wrap=CHAR)

    if len(path)>0:
        #panelC=Toplevel()
        #panelC.title("about map file...")
        #msg=Message(panelC,text="map file opened: "+path)
        #msg.pack(side="top",padx=5,pady=5)
        #button=Button(panelC,text="Dismiss",command=panelC.destroy)
        #button.pack()
        entbox.insert(END,path,"wrap")
        entbox.config(stat=DISABLED)
        mapfile=path
        #panelC.text="map file: "+path
        #label.pack(side="bottom")
        #label.place(side="bottom",height=10,width=300)
    #else:
        #panelWelcome=Label(text="Welcome to use PlantExtraction!\nPlease use the menubar on top to begin your image processing.")
        #panelWelcome.text="Welcome to use PlantExtraction!\nPlease use the menubar on top to begin your image processing."

def export_result():
    global labels,border,colortable,greatareas,tinyareas
    inserttop(5)
    insertbottom(5)
    if type(labels)==type(None):
        messagebox.showerror('No processed image',message='Please process image first.')
        return
    path=filedialog.askdirectory()
    if type(rotation)!=type(None):
        if rotation!=0:
            center=(225,225)
            a=rotation*-1.0
            print(a)
            M=cv2.getRotationMatrix2D(center,a,1.0)
            border=cv2.warpAffine(border.astype('float32'),M,dsize=(450,450),flags=cv2.INTER_LINEAR)
            labels=cv2.warpAffine(labels.astype('float32'),M,dsize=(450,450),flags=cv2.INTER_LINEAR)
    if len(path)>0:
        messagebox.showinfo('Save process',message='Program is saving results to'+path)
        border=border.astype('float32')
        print(border)
        realborder=cv2.resize(src=border,dsize=(RGB.size[1],RGB.size[0]),interpolation=cv2.INTER_LINEAR)
        out_img=path+'/OutputRGBwithBorder.tif'
        band1=RGB.bands[0]+realborder*255
        band2=RGB.bands[1]
        band3=RGB.bands[2]
        gtiffdriver=gdal.GetDriverByName('GTiff')
        out_ds=gtiffdriver.Create(out_img,RGB.size[1],RGB.size[0],3,3)
        #out_ds.SetGeoTransform(in_gt)
        #out_ds.SetProjection(dataproj)
        out_band=out_ds.GetRasterBand(1)
        out_band.WriteArray(band1)
        out_band=out_ds.GetRasterBand(2)
        out_band.WriteArray(band2)
        out_band=out_ds.GetRasterBand(3)
        out_band.WriteArray(band3)
        out_ds.FlushCache()
        out_img=path+'/Labeleddata.tif'
        floatlabels=labels.astype('float32')
        floatlabels=cv2.resize(src=floatlabels,dsize=(RGB.size[1],RGB.size[0]),interpolation=cv2.INTER_LINEAR)
        lastone=np.zeros(floatlabels.shape,dtype='float32')
        unikeys=list(colortable.keys())
        #for uni in colortable:
        for i in range(len(unikeys)):
            lastone=np.where(floatlabels==float(unikeys[i]),i,lastone)

        band1=lastone
        out_ds=gtiffdriver.Create(out_img,RGB.size[1],RGB.size[0],1,3)
        out_band=out_ds.GetRasterBand(1)
        out_band.WriteArray(band1)
        out_ds.FlushCache()

        indicekeys=list(bandarrays.keys())
        indeclist=[ 0 for i in range(len(indicekeys)*3)]
        restoredband=np.multiply(labels,modified_tif)
        restoredband=restoredband.astype('float32')
        restoredband=cv2.resize(src=restoredband,dsize=(RGB.size[1],RGB.size[0]),interpolation=cv2.INTER_LINEAR)

        datatable={}
        origindata={}
        for key in indicekeys:
            data=bandarrays[key]
            data=data.tolist()
            tempdict={key:data}
            origindata.update(tempdict)
        for uni in colortable:
            print(uni,colortable[uni])
            uniloc=np.where(restoredband==float(uni))
            if len(uniloc)==0 or len(uniloc[1])==0:
                continue
            #width=max(uniloc[0])-min(uniloc[0])
            #length=max(uniloc[1])-min(uniloc[1])

            #subarea=restoredband[min(uniloc[0]):max(uniloc[0])+1,min(uniloc[1]):max(uniloc[1])+1]
            #findcircle(subarea)
            ulx,uly=min(uniloc[1]),min(uniloc[0])
            rlx,rly=max(uniloc[1]),max(uniloc[0])
            width=rlx-ulx
            length=rly-uly
            print(width,length)
            subarea=restoredband[uly:rly+1,ulx:rlx+1]
            subarea=subarea.tolist()
            amount=len(uniloc[0])
            print(amount)
            templist=[amount,length,width]
            tempdict={colortable[uni]:templist+indeclist}  #NIR,Redeyes,R,G,B,NDVI,area
            for ki in range(len(indicekeys)):
                #originNDVI=bandarrays[indicekeys[ki]]
                #originNDVI=originNDVI.tolist()
                originNDVI=origindata[indicekeys[ki]]
                pixellist=[]
                for k in range(len(uniloc[0])):
                    #tempdict[colortable[uni]][5]+=databand[uniloc[0][k]][uniloc[1][k]]
                    #tempdict[colortable[uni]][0]+=infrbands[0][uniloc[0][k]][uniloc[1][k]]
                    #tempdict[colortable[uni]][1]+=infrbands[2][uniloc[0][k]][uniloc[1][k]]
                    #tempdict[colortable[uni]][2]+=rgbbands[1][uniloc[0][k]][uniloc[1][k]]
                    #tempdict[colortable[uni]][3]+=rgbbands[0][uniloc[0][k]][uniloc[1][k]]
                    #tempdict[colortable[uni]][4]+=rgbbands[2][uniloc[0][k]][uniloc[1][k]]
                    #tempdict[colortable[uni]][6]+=NDVI[uniloc[0][k]][uniloc[1][k]]
                    tempdict[colortable[uni]][3+ki*3]+=originNDVI[uniloc[0][k]][uniloc[1][k]]
                    tempdict[colortable[uni]][4+ki*3]+=originNDVI[uniloc[0][k]][uniloc[1][k]]
                    pixellist.append(originNDVI[uniloc[0][k]][uniloc[1][k]])
                #for i in range(7):
                tempdict[colortable[uni]][ki*3+3]=tempdict[colortable[uni]][ki*3+3]/amount
                tempdict[colortable[uni]][ki*3+5]=np.std(pixellist)
            datatable.update(tempdict)


        filename=path+'/NDVIdata.csv'
        with open(filename,mode='w') as f:
            csvwriter=csv.writer(f)
            rowcontent=['Index','Plot','Area(#pixel)','Length(#pixel)','Width(#pixel)']
            for key in indicekeys:
                rowcontent.append('avg-'+str(key))
                rowcontent.append('sum-'+str(key))
                rowcontent.append('std-'+str(key))
            #csvwriter.writerow(['ID','NIR','Red Edge','Red','Green','Blue','NIRv.s.Green','NDVI','area(#of pixel)'])
            #csvwriter.writerow(['Index','Plot','Area(#pixels)','avg-NDVI','sum-NDVI','std-NDVI','Length(#pixel)','Width(#pixel)'])#,'#holes'])
            csvwriter.writerow(rowcontent)
            i=0
            for uni in datatable:
                row=[i,uni]
                for j in range(len(datatable[uni])):
                    row.append(datatable[uni][j])
                #row=[i,uni,datatable[uni][0],datatable[uni][1],datatable[uni][2],datatable[uni][5],datatable[uni][3],datatable[uni][4]]#,
                     #datatable[uni][5]]
                i+=1
                print(row)
                csvwriter.writerow(row)
        messagebox.showinfo('Saved',message='Results are saved to '+path)



def Green_calculation():
    global panelA
    sumbands=np.sum(RGB.bands,axis=2)
    sumbands=np.where(sumbands==0,1,sumbands)
    RGBr=RGB.bands[:,:,0]/sumbands
    RGBg=RGB.bands[:,:,1]/sumbands
    RGBb=RGB.bands[:,:,2]/sumbands
    greenness=2*RGBg+RGBb-2*RGBr
    image=Image.fromarray(greenness)
    image=ImageTk.PhotoImage(image)
    panelA.configure(image=image)
    panelA.image=image

def NDVI_calculation():
    global panelA
    RGBr=RGB.bands[:,:,0]
    RGBg=RGB.bands[:,:,1]
    RGBb=RGB.bands[:,:,2]
    Inf0=Infrared.bands[:,:,0]
    Inf1=Infrared.bands[:,:,1]
    Inf2=Infrared.bands[:,:,2]
    leftband,rightband=None,None
    if comboleft.get()=='RGB band 1':
        leftband=RGBr
    if comboleft.get()=='RGB band 2':
        leftband=RGBg
    if comboleft.get()=='RGB band 3':
        leftband=RGBb
    if comboleft.get()=='Infrared band 1':
        leftband=Inf0
    if comboleft.get()=='Infrared band 2':
        leftband=Inf1
    if comboleft.get()=='Infrared band 3':
        leftband=Inf2
    #messagebox.showinfo('band choice 1',comboleft.get())

    if comboright.get()=='RGB band 1':
        rightband=RGBr
    if comboright.get()=='RGB band 2':
        rightband=RGBg
    if comboright.get()=='RGB band 3':
        rightband=RGBb
    if comboright.get()=='Infrared band 1':
        rightband=Inf0
    if comboright.get()=='Infrared band 2':
        rightband=Inf1
    if comboright.get()=='Infrared band 3':
        rightband=Inf2
    upper=leftband-rightband
    lower=leftband+rightband
    lower=np.where(lower==0,1,lower)
    image=upper/lower
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    panelA.configure(image=image)
    panelA.image=image
    if panelA is not None:
            panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=1,column=0)

def default_NDVI():
    global panelA,modified_tif,bandarrays,workbandarrays
    if RGB is not None and Infrared is not None and Infrared.size==RGB.size:

        #upper=-(Inf0-RGBg)
        #lower=Inf0+RGBg
        #lower=np.where(lower==0,1,lower)

        upper=Infrared.bands[0,:,:]-RGB.bands[0,:,:]
        lower=Infrared.bands[0,:,:]+RGB.bands[0,:,:]
        lower=np.where(lower==0,1,lower)
        NDVI=upper/lower
        tempdict={'NDVI':NDVI}
        bandarrays.update(tempdict)
        if 'NDVI' not in workbandarrays:
            worktempdict={'NDVI':cv2.resize(NDVI,(450,450),interpolation=cv2.INTER_LINEAR)}
            workbandarrays.update(worktempdict)
        out_fn='tempNDVI.tif'
        gtiffdriver=gdal.GetDriverByName('GTiff')
        out_ds=gtiffdriver.Create(out_fn,upper.shape[1],upper.shape[0],1,3)
        out_band=out_ds.GetRasterBand(1)
        out_band.WriteArray(NDVI)
        out_ds.FlushCache()
        modified_tif=cv2.resize(NDVI,(450,450),interpolation=cv2.INTER_NEAREST)
        pyplt.imsave(out_png,modified_tif)
        image=cv2.imread(out_png)
        image=Image.fromarray(image)
        image=ImageTk.PhotoImage(image)
        if panelA is not None:
            panelA.destroy()
        panelA=Label(ctr_left,image=image)
        panelA.image=image
        panelA.grid(row=0,column=0)


def calculatecustom(entbox):
    global bandarrays,panelA,treelist,modified_tif,workbandarrays
    equation=entbox.get("1.0",END)
    if 'Band' not in equation:
        if 'Height' not in equation:
            messagebox.showerror('No band selected',message='Select bands you want to calculate.')
        return
    equation=equation.split()
    checklist=['RGBBand1','RGBBand2','RGBBand3','InfraredBand1','InfraredBand2','InfraredBand3','HeightBand',
               '+','-','*','/','^','(',')']
    for ele in equation:
        if ele not in checklist:
            try:
                float(ele)
            except:
                messagebox.showerror('Invalid input',message='input: '+ele+' is invalid')
                return
    leftpar=equation.count('(')
    rightpar=equation.count(')')
    if leftpar!=rightpar:
        messagebox.showerror('Invalid input',message='input is invalid')
        return
    else:
        if '(' in equation:
            leftpar=equation.index('(')
            rightpar=equation.index(')')
            if rightpar<leftpar:
                messagebox.showerror('Invalid input',message='input is invalid')
                return


    tempband=calculator.init(RGB,Infrared,Height,equation,nodataposition)
    if type(tempband)==type(None):
        return
    bandname="".join(equation)
    if bandname not in bandarrays:
        tempdict={"".join(equation):tempband}
        bandarrays.update(tempdict)
        currentkey="".join(equation)
        if currentkey not in workbandarrays:
            img=cv2.resize(tempband,(450,450),interpolation=cv2.INTER_LINEAR)
            if type(rotation)!=type(None):
                if rotation!=0:
                    center=(225,225)
                    M=cv2.getRotationMatrix2D(center,rotation,1.0)
                    img=cv2.cv2.warpAffine(img,M,dsize=(450,450),flags=cv2.INTER_LINEAR)
            worktempdict={currentkey:img}
            workbandarrays.update(worktempdict)
        treelist.insert(END,"".join(equation))
        modified_tif=cv2.resize(tempband,(450,450),interpolation=cv2.INTER_NEAREST)
        pyplt.imsave(out_png,modified_tif)
        image=cv2.imread(out_png)
        image=Image.fromarray(image)
        image=ImageTk.PhotoImage(image)
        if panelA is not None:
            panelA.destroy()
        panelA=Label(ctr_left,image=image)
        panelA.image=image
        panelA.grid(row=0,column=0)
    entbox.config(stat=NORMAL)
    entbox.delete("1.0",END)
    entbox.config(stat=DISABLED)


def Entrydelete(entbox):
    entbox.config(stat=NORMAL)
    entbox.delete("1.0",END)
    entbox.config(stat=DISABLED)

def Entryinsert(content,entbox):
    if content=='Height' and Height is None:
        messagebox.showerror('No Height',message='No Height is loaded.')
        return
    entbox.config(stat=NORMAL)
    entbox.insert(END,content)
    print(content)
    entbox.config(stat=DISABLED)
    #need to check Height available




def custom_cal():
    global panelB,root
    root.geometry("")
    calframe=LabelFrame(panelB,text='Band Calculator')
    calframe.grid(row=1,column=0,padx=5,pady=5)
    RGBframe=LabelFrame(calframe,text='RGB bands')
    RGBframe.grid(row=0,column=0)
    Infframe=LabelFrame(calframe,text='Infrared band')
    Infframe.grid(row=0,column=1,padx=5,pady=5)
    Heightframe=LabelFrame(calframe,text='Height')
    Heightframe.grid(row=0,column=2,padx=5,pady=5)
    Opframe=LabelFrame(calframe,text='operations')
    Opframe.grid(row=1,column=0)
    Numframe=LabelFrame(calframe,text='Number')
    Numframe.grid(row=2,column=0,padx=5,pady=5)
    Entframe=LabelFrame(calframe,text='Entry box')
    Entframe.grid(row=1,column=1,columnspan=2,rowspan=2,padx=5,pady=5)
    entbox=Text(Entframe,height=3,width=30)
    entbox.config(state=DISABLED)
    entbox.pack(side='left')
    button=Button(Entframe,text='Calculate',command=partial(calculatecustom,entbox))
    button.pack(side='left')


    for i in range(3):
        button=Button(RGBframe,text='Band'+str(i+1),command=partial(Entryinsert,'RGBBand'+str(i+1),entbox))
        button.pack(side='left')
    for i in range(3):
        button=Button(Infframe,text='Band'+str(i+1),command=partial(Entryinsert,'InfraredBand'+str(i+1),entbox))
        button.pack(side='left')
    button=Button(Heightframe,text='Height',command=partial(Entryinsert,'HeightBand',entbox))
    button.pack(side='left')
    button=Button(Opframe,text='+',command=partial(Entryinsert,' + ',entbox))
    button.pack(side='left')
    button=Button(Opframe,text='-',command=partial(Entryinsert,' - ',entbox))
    button.pack(side='left')
    button=Button(Opframe,text='*',command=partial(Entryinsert,' * ',entbox))
    button.pack(side='left')
    button=Button(Opframe,text='/',command=partial(Entryinsert,' / ',entbox))
    button.pack(side='left')
    button=Button(Opframe,text='(',command=partial(Entryinsert,' ( ',entbox))
    button.pack(side='left')
    button=Button(Opframe,text=')',command=partial(Entryinsert,' ) ',entbox))
    button.pack(side='left')
    button=Button(Opframe,text='clear',command=partial(Entrydelete,entbox))
    button.pack(side='left')
    for i in range(10):
        button=Button(Numframe,text=str(i),command=partial(Entryinsert,str(i),entbox))
        button.pack(side='left')
    button=Button(Numframe,text='.',command=partial(Entryinsert,'.',entbox))
    button.pack(side='left')

def treelistop(e):
    global panelA,modified_tif
    if e.widget.get(0)=='':
        messagebox.showerror('No Data',message='2D array list is empty. Need to add or compute 2D array')
        return
    w=e.widget
    print('treelist select: '+w.selection_get())
    #tempband=bandarrays[w.selection_get()]
    tempband=workbandarrays[w.selection_get()]
    #out_fn='temppanelA.tif'
    #gtiffdriver=gdal.GetDriverByName('GTiff')
    #out_ds=gtiffdriver.Create(out_fn,tempband[1],tempband[0],1,3)
    #out_band=out_ds.GetRasterBand(1)
    #out_band.WriteArray(tempband)
    #out_ds.FlushCache()
    modified_tif=cv2.resize(tempband,(450,450),interpolation=cv2.INTER_NEAREST)
    pyplt.imsave(out_png,modified_tif)
    image=cv2.imread(out_png)
    image=Image.fromarray(image)
    image=ImageTk.PhotoImage(image)
    if panelA is not None:
        panelA.destroy()
    panelA=Label(ctr_left,image=image)
    panelA.image=image
    panelA.grid(row=0,column=0)


def bands_calculation():
    global Inflabel,comboleft,comboright,panelB,panelA,treelist,bandarrays,modified_tif,panelTree,workbandarrays
    inserttop(1)
    insertbottom(1)
    if panelB is not None:
        panelB.destroy()
    #panelB.destory()
    if RGB is None:
        messagebox.showerror('No RGB',message="No RGB file\n Cannot extract R, G, B bands.")
    if Infrared is None:
        messagebox.showerror('No Infrared',message='No infrared file.\n Cannot extract Infrared bands.')
    if RGB is not None and Infrared is not None:
        if Infrared.size!=RGB.size:
            messagebox.showerror('Image size issue',message='Size of RGB and Infrared image is different.')
            return
        if Height is not None and Height.size!=RGB.size:
            messagebox.showerror('Image size issue',message='Size of Height differs from RGB and Infrared image.'
                                                            'Height size='+str(Height.size)+', RGB size='+str(RGB.size))
            return
        panelTree.grid(row=0,column=0)
        upper=Infrared.bands[0,:,:]-RGB.bands[0,:,:]
        lower=Infrared.bands[0,:,:]+RGB.bands[0,:,:]
        lower=np.where(lower==0,1,lower)
        NDVI=upper/lower
        out_fn='tempNDVI.tif'
        gtiffdriver=gdal.GetDriverByName('GTiff')
        out_ds=gtiffdriver.Create(out_fn,upper.shape[1],upper.shape[0],1,3)
        out_band=out_ds.GetRasterBand(1)
        out_band.WriteArray(NDVI)
        out_ds.FlushCache()
        messagebox.showinfo('NDVI image',message='Default image is NDVI image without any image processing.')
        tempdict={'NDVI':NDVI}
        if 'NDVI' not in bandarrays:
            bandarrays.update(tempdict)
            worktempdict={'NDVI':cv2.resize(NDVI,(450,450),interpolation=cv2.INTER_LINEAR)}
            workbandarrays.update(worktempdict)
            treelist.insert(END,'NDVI')
        modified_tif=cv2.resize(NDVI,(450,450),interpolation=cv2.INTER_NEAREST)
        pyplt.imsave(out_png,modified_tif)
        image=cv2.imread(out_png)
        image=Image.fromarray(image)
        image=ImageTk.PhotoImage(image)
        if panelA is not None:
            panelA.destroy()
        panelA=Label(ctr_left,image=image)
        panelA.image=image
        panelA.grid(row=0,column=0)

        panelB=Label(ctr_right)
        panelB.grid(row=0,column=0)
        calframe=LabelFrame(panelB,text='Calculation Type')
        calframe.grid(row=0,column=0)
        choice=None
        calradio0=Radiobutton(calframe,text='NDVI(defalut)',value=0,command=default_NDVI,variable=choice)
        calradio1=Radiobutton(calframe,text='Cutsom',value=1,command=custom_cal,variable=choice)
        calradio0.pack(side='left')
        calradio1.pack(side='left')

def blur_panel():
    global panelA,panelB
    if panelB is not None:
        panelB.destroy()


def instructions():
    panelC=Toplevel()
    panelC.title("Instructions")
    msg=Message(panelC,text="The software is sensitive with noise pixel, please process image that only contains your plant. You can use shapefile to cut the area out via QGIS.\n "
                         "The software processes TIF format image, please convert JPEG formate into TIF. You can use QGIS to do that.\n"
                         "steps:\n"
                         "1. Open RGB and NIR image, if you have HEIGHT image, the software also support that.\n"
                         "2. Map file is a csv file, you can generate yourself.\n It should contain the labels (labels can be number or words) of your plants, and the labels should be arranged in the same way as your plants.\n "
                         "3. You can rotate your image, using 'Rotation' under 'tools'.\n Rotation image usually will lose information, you only need to rotate the image if it tilt over (+/-) 45 degrees.\n"
                         "4. Band calculation let you define your own equation (select 'custom'), the software will present results of your equation. NDVI is default.\n"
                         "5. Classify will do K-Means cluster for bands. At least one band have to be selected to run it. You can select multiple bands as indices to implement K-Means.\n The classes you select within the K-Means results will be the prototype image to process.\n"
                         "6. Extract crop will identify boundaries for each of your crops. Default iteration time is 30.\n"
                         "7. You can export the results using the 'Export' function. The software export three type of files:\n"
                         " A tif image that have the boundaries on your original RGB image.\n"
                         " A tif image have the labeles on each crops. A csv file containing\n"
                         " the NDVI data for each labelled crops.'")
    msg.pack(side="top",padx=5,pady=5)
    button=Button(panelC,text="Close",command=panelC.destroy)
    button.pack()

#def init():
    #global  root,panelTree,panelA,panelB,ctr_left,ctr_right,center,bindtree,scrollbar,treelist,
root=Tk()
root.title('GridFree')
root.geometry("")

root.option_add('*tearoff',False)

top_frame=Frame(root,width=1000,height=50)
center=Frame(root,width=1000,height=450)
btm_frame=Frame(root,width=1000,height=40)
root.grid_rowconfigure(1,weight=1)

root.grid_rowconfigure(1,weight=1)
root.grid_columnconfigure(0,weight=1)

top_frame.grid(row=0)
center.grid(row=1)
btm_frame.grid(row=2)

ctr_tree=Frame(center,width=250,height=450,padx=5,pady=5)
ctr_left=Frame(center,width=450,height=450)
ctr_right=Frame(center,width=450,height=450)

ctr_tree.pack(side=LEFT)
ctr_left.pack(side=LEFT)
ctr_right.pack(side=LEFT)

panelTree=LabelFrame(ctr_tree,text='Calculaed 2D Layers',padx=5,pady=5)
panelTree.grid(row=0,column=0)
treelist=Listbox(panelTree,width=20,height=15)
treelist.pack(side='left')
bindtree=treelist.bind('<<ListboxSelect>>',treelistop)
scrollbar=Scrollbar(panelTree)
scrollbar.pack(side='right',fill=Y)
treelist.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=treelist.yview)
panelTree.grid_forget()
#for i in range(20):
#    treelist.insert(END,i)




panelWelcome=Text(top_frame,height=3,width=100)
panelWelcome.tag_config("just",justify=CENTER)
panelWelcome.insert(END,"Welcome to use GridFree!\nPlease use the menubar on top to begin your image processing.\n"
                                  "GridFree is a pixel-level label plants in drone images\n","just")


#panelWelcome.grid(row=0,columnspan=3)
#panelWelcome.pack(side="top",padx=10,pady=10)
panelWelcome.configure(state=DISABLED)
panelWelcome.grid(row=0,column=0,padx=10,pady=10)

panelA=Label(ctr_left)
startbutton=Button(panelA,text='Start',command=QGIS_NDVI)
versiondes=Text(panelA)
versiondes.insert(END,'                          Implerment Python version = 3.6.5, QGIS version = 3.4',"just")
versiondes.config(stat=DISABLED)
startbutton.pack()
versiondes.pack(side=RIGHT)
panelA.pack()


menubar=Menu(root)
root.config(menu=menubar)
''' MENU BAR SETTING
filemenu=Menu(menubar)
toolmenu=Menu(menubar)
help_=Menu(menubar)
#panelWelcome.configure(text='')
#panelWelcome.grid(row=0,column=0,padx=10,pady=10)

#filemenu.add_command(label="Open RGB Image(mosaic)",command=select_image)
#filemenu.add_command(label="Open Infrared Image(mosaic)",command=select_inf_image)
filemenu.add_command(label="Open reflectance(wavelength) image",command=QGIS_NDVI)
filemenu.add_command(label="Open Map",command=select_map)
filemenu.add_command(label="Export",command=export_result)
filemenu.add_separator()
filemenu.add_command(label="Exit",command=exit)

toolmenu.add_command(label="Band Calculation",command=bands_calculation)
toolmenu.add_command(label="Rotation",command=rotationpanel)
toolmenu.add_command(label="Classify",command=KMeansPanel)
#toolmenu.add_command(label="Blur",command=blur_panel)
toolmenu.add_separator()
toolmenu.add_command(label="Extract Crops",command=drawboundary)

help_.add_command(label="Instructions",command=instructions)

menubar.add_cascade(menu=filemenu,label="File")
menubar.add_cascade(menu=toolmenu,label="Tools")
menubar.add_cascade(menu=help_,label="Help")

#btn1=Button(root,text="Select an image",command=select_image).grid()
#btn2=Button(root,text="Select a map",command=select_map).grid()
#btn1.pack(side="bottom",fill="both",expand="yes",padx="10",pady="10")
#btn2.pack(side="bottom",fill="both",expand="yes",padx="10",pady="10")
'''

#root.mainloop()
