#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:35:21 2017

@author: rieger
"""
import sys
#sys.path.append('/user/awakeop/AWAKE_ANALYSIS_TOOLS/plotting_tools/')
from awakeIMClass import *
import numpy as np
import scipy as sp
import matplotlib as mpl
import pickle
import time
import os

'''
Defining the plots for the GUI
'''

def BI_beamImage(plotax,fig,fixedaxes,japc,vec,awkLBox,maxVal,PixelLengthProfileFit,ProfileParam):
    # fixedaxes beinhaltet x axis calibration value
    try:
        time.sleep(1)#TT41.BTV.412350.STREAK,TT41.BTV.412350.STREAK
        timeVal=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTimeValues')
        vec=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageData')
        vec=vec.reshape(512,672)
    except:
        print('no data available')
    if ProfileParam[0]>ProfileParam[1]:
        ProfileParam=(ProfileParam[1],ProfileParam[0])

    if maxVal <=0:
        # maxVal = 1.1*np.max(vec[:,300:400].sum()/100/512)
        maxVal=1.5*np.mean(vec[:,(int(ProfileParam[0]/672*336)+336):(int(ProfileParam[1]/672*336)+336)])+0.1*np.max(vec[:,(int(ProfileParam[0]/672*336)+336):(int(ProfileParam[1]/672*336)+336)])

    plotax.clear()
    print('before plot')
    plotax.imshow(np.fliplr(vec.T),extent=[timeVal[-1],timeVal[1],fixedaxes[0][150],fixedaxes[0][-150]],vmin=175,vmax=maxVal,aspect='auto',cmap='Blues') 
    print('behind plot')
    plotax.plot((timeVal[-1],timeVal[1]),(ProfileParam[0],ProfileParam[0]),c='k',linestyle='dotted',linewidth=2)
    plotax.plot((timeVal[-1],timeVal[1]),(ProfileParam[1],ProfileParam[1]),c='k',linestyle='dotted',linewidth=2)

    plotax.set_ylabel('Space (px)')
    plotax.set_xlabel('Time (ps)')

    PixelLengthProfileFit=int(PixelLengthProfileFit)
    
    '''
    thickness plot
    '''
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    try:
        startVals= np.arange(10,490,PixelLengthProfileFit)
        endVals= np.arange(10+PixelLengthProfileFit,500,PixelLengthProfileFit)
        startGuess=[3,1/4*np.abs(fixedaxes[0][0]-fixedaxes[0][-1]),fixedaxes[0][345],400]
        import scipy as sp
        slices=[(vec.T[:,l:k].sum(1)/(np.abs(l-k)))/((vec.T[:,l:k].sum()/(np.abs(l-k)))) for l,k in zip(startVals,endVals)]
        fits=[sp.optimize.least_squares(gaussFIT1D,startGuess,args=(fixedaxes[0],k)) for k in slices]

        parentFig=plotax.get_figure()
        if len(parentFig.axes)>3:
            ax2=parentFig.axes[3]
            ax2.clear()

        else:
            ax2=plotax.twinx()

        ax2.scatter(timeVal[endVals-5],[np.abs(k.x[1]) for k in fits],label='Spatial fits (mm)',s=30,marker='d',c='r')
        ax2.set_ylim(0,np.minimum(np.max([np.abs(k.x[1]) for k in fits])*1.1,5))
    except:
        print('no spatial fit!')
    plotax.set_xlim(timeVal[-1],timeVal[1])
    plotax.set_title(str(japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTime')))

def BI_ProfilePlot(plotax,fig,fixedaxes,japc,vec,ProfileParam):
    plotax.clear()
    try:
        time.sleep(0.5)
        timeVal=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTimeValues')
        vec=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageData')-175
    except:
        print('no data recieved!')
        
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    if ProfileParam[0]>ProfileParam[1]:
        ProfileParam=(ProfileParam[1],ProfileParam[0])

    vecP=vec.reshape(512,672)[:,ProfileParam[0]:ProfileParam[1]].mean(1)
    vecP=vecP/np.max(vecP)
    timeVal=np.append(timeVal[1]-timeVal[2],timeVal[1:])
    plobj1=plotax.plot(np.flipud(timeVal),np.flipud(vecP),c='r',linewidth=2,label='temporal Profile')
    
    try:
        parentFig=plotax.get_figure()
        if len(parentFig.axes)>4:
            ax2=parentFig.axes[4]
            ax2.clear()
        else:
            ax2=plotax.twiny()
        import scipy as sp
        vecP2=(vec.reshape(512,672)).mean(0)
        
        plobj2=ax2.plot(fixedaxes[0],vecP2/np.max(vecP2),label='Spatial Profile') #error here?
        print('error in plot?')
        startGuess=[(np.max(vecP2)-np.min(vecP2))/2,2/3*(fixedaxes[0][-1]-fixedaxes[0][0]),fixedaxes[0][335],0]
        optimres=sp.optimize.least_squares(gaussFIT1D,startGuess,args=(fixedaxes[0],vecP2/np.max(vecP2)))
        
        plotobj4=ax2.plot(fixedaxes[0],gaussFIT1D(optimres.x,fixedaxes[0],0),c='k',linestyle='dotted',linewidth=1.5,label='Gauss fit exp(-x**2/(2*sigma**2)): sigma={0:1.2f}'.format(np.abs(optimres.x[1])))

    except:
        print('no standard')
        
    try:
        import scipy as sp
        startGuess=[(np.max(vecP)-np.min(vecP))/2,2/3*(timeVal[-1]-timeVal[0]),timeVal[255],175]
        optimres=sp.optimize.least_squares(gaussFIT1D,startGuess,args=(np.flipud(timeVal),np.flipud(vecP)))
        plobj3=plotax.plot(np.flipud(timeVal),np.flipud(gaussFIT1D(optimres.x,timeVal,0)),c='g',linestyle='dotted',linewidth=1.5,label='Gauss fit: sigma={0:1.2f}'.format(np.abs(optimres.x[1])))
        legendAll=[l.get_label() for l in plobj1+plobj2+plobj3+plotobj4]
        plotax.legend(plobj1+plobj2+plobj3+plotobj4,legendAll)

    except:
        print('no fitplot')
    #plotax.set_ylim(np.min(vec),1.05*np.max(vec))
    plotax.set_ylim(0,1.05)

'''
Starting the GUI application
'''
    
app = QApplication(sys.argv)
aw = AwakeWindow(["TT41.BCTF.412340/Acquisition#totalIntensityPreferred"],BI_beamImage,BI_ProfilePlot,fixedaxes=(np.arange(0,672),),selector="SPS.USER.AWAKE1",name='BI Streak Image',BI_beamImage={'awkLBox':laserboxMPP,'maxVal':-1,'PixelLengthProfileFit':10,'ProfileParam':(300,370)},BI_ProfilePlot={'ProfileParam':(300,370)},reverse=True)
progname='AwakeSTREAK'
aw.setWindowTitle("%s" % progname)
aw.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))
aw.show()
app.exec_()
