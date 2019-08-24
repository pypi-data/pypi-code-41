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
import scipy.special as sps
import scipy.optimize as spo

'''
defining some functions (not really ):) needed for the varaince esstimation
'''
def zeta(x):
    return 2 + x**2 - 0.39269908169872414 * np.exp(-x**2/2) *( (2+x**2)*sps.iv(0,1/4*x**2) + x**2*sps.iv(1,1/4*x**2) )**2

def fpoint(x,mean,var):
    buff= zeta(x)*(1+mean**2/var) -2
    if buff <0:
        return x
    else:
        return x - np.sqrt(buff)

# 0.42920367320510344*estVar ist varianz der rici distribution, verwende das um zu cutten wenn estimated signal =0

def estimateCut(mean,var,nmin=1,nmax=100):
    skipZero=0
    if nmin==0:
        skipZero=1
    estSig=np.zeros(mean[nmin:nmax].shape)
    estNoise=np.zeros(mean[nmin:nmax].shape)

    for k in range(0,estSig.shape[0]):
        try:
            # varianze ist die unabhängige variable, varainz bestimmt den max/min wert für buff
            buff=spo.brentq(fpoint,0,20,args=(mean[k+nmin],var[k+nmin]))
            estNoise[k]=var[k+nmin]/zeta(buff)
            estSig[k]=np.maximum(0,mean[k+nmin]**2 + (1-2/zeta(buff))*var[k+nmin])
        except:
                estNoise[k]=var[k+nmin]*2 # noise fuer signal=0 from wiki
                estSig[k]=0
    rice_mean=np.sqrt(estNoise)*np.sqrt(np.pi/2)*sps.assoc_laguerre(-estSig/estNoise/2,0.5,0)
    # estimated singla, estimated noise, mean_of_dist, variance of dist
    return estSig,estNoise,rice_mean, 0.42920367320510344*estNoise

'''
Defining the plots for the GUI
'''

def XMPP_beamImage(plotax,fig,fixedaxes,japc,vec,awkLBox,maxVal,PixelLengthProfileFit,ProfileParam):
    # fixedaxes beinhaltet x axis calibration value
    #TT41.BTV.412350.STREAK,XMPP-STREAK
    try:
        time.sleep(1)
        timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
        vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData')
        vec=vec.reshape(512,672)
    except:
        print('Failed to retrieve data')
    if ProfileParam[0]>ProfileParam[1]:
        ProfileParam=(ProfileParam[1],ProfileParam[0])
    if maxVal <=0:
        # maxVal = 1.1*np.max(vec[:,300:400].sum()/100/512)
        maxVal=1.5*np.mean(vec[:,(int(ProfileParam[0]/8.75*336)+336):(int(ProfileParam[1]/8.75*336)+336)])+0.1*np.max(vec[:,(int(ProfileParam[0]/8.75*336)+336):(int(ProfileParam[1]/8.5*336)+336)])
    plotax.clear()
    plotax.imshow(np.fliplr(vec.T),extent=[timeVal[-1],timeVal[1],fixedaxes[0][150],fixedaxes[0][-150]],vmin=400,vmax=maxVal,aspect='auto',cmap='Blues')
    
    #plotax.plot((1000,0),(-1.75,-1.75),c='k',linestyle='dotted',linewidth=2)
    #print('Before first plot')
    plotax.plot((timeVal[-1],timeVal[1]),(ProfileParam[0],ProfileParam[0]),c='k',linestyle='dotted',linewidth=2)
    #print('Before second plot')
    plotax.plot((timeVal[-1],timeVal[1]),(ProfileParam[1],ProfileParam[1]),c='k',linestyle='dotted',linewidth=2)
    
    plotax.set_ylabel('Space (mm)')
    plotax.set_xlabel('Time (ps)')

    PixelLengthProfileFit=int(PixelLengthProfileFit)
    currentFineDelay=awkLBox() #get finedelay setting
    fineDelay,pxTpl=awkLBox[japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeRange')]#acess timerange values
    if fineDelay is not None:
        psShift=(fineDelay-currentFineDelay)*1000
        lowerlim=(512-pxTpl[0])/512*(timeVal[-1]-timeVal[1]) + psShift
        upperlim=(512-pxTpl[1])/512*(timeVal[-1]-timeVal[1]) + psShift
        plotax.plot((upperlim,upperlim),(fixedaxes[0][150],fixedaxes[0][-150]),c='y',linestyle='dotted',linewidth=4)
        plotax.plot((lowerlim,lowerlim),(fixedaxes[0][150],fixedaxes[0][-150]),c='y',linestyle='dotted',linewidth=4,label='LASER BOX')
    
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
    plotax.set_title(str(japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')))
  
def XMPP_PlotFFT(plotax,fig,fixedaxes,japc,vec,historyList,profileParam,historyBKG):
    time.sleep(0.5)
    if profileParam[0]>profileParam[1]:
        profileParam=(profileParam[1],profileParam[0])
    plotax.clear()
    ''' streak image data'''
    try:
        timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
        vec,header=japc.getParam('XMPP-STREAK/StreakImage#streakImageData',getHeader=True,unixtime=True)
        vec=vec.reshape(512,672)-400 # to get roughly rid of offset
    except:
        print('Failed to retrieve data')
        
    ''' laser emeter to distinguish from bkg shots'''

    LaserPower=japc.getParam('EMETER04/Acq#value') #in J


    ''' reshape data and normalise, use hanning window and no roll, hanning window mainly to get rid of ringing into the noise and decoherence of low frequency components'''

    
    profile=(vec[:,(int(profileParam[0]/8.75*336)+336):(int(profileParam[1]/8.75*336)+336)]).mean(1) #profile
    profile=(profile-np.mean(profile))*np.hanning(512) #subtract meanto get rid of offset ringings
    FFT_PRF=np.abs(np.fft.fft(profile))/(np.abs(np.fft.fft(profile))[100:256]).sum() #far away from any measureable frequency
    F=1/(timeVal[-1]-timeVal[1])*1e3
    FFT_TIME=np.arange(0,512*F,F)
    
    
    plobj1=plotax.plot(FFT_TIME,FFT_PRF,linewidth=2.5,label='current FFT')
    axmax=np.minimum(320,np.maximum(320,40*F))
    xticks=np.arange(0,axmax,20)
    plotax.xaxis.set_ticks(xticks)
    plotax.set_xlim(0,axmax)
    plotax.set_ylim(0,np.max(FFT_PRF[3:40])*1.45)
    plotax.set_xlabel('Frequency (GHz)')
    
    ''' check if histoyBKG or historyList has to be appended'''
    data=FFT_PRF
    if LaserPower < 0.005:
        historyBKG.append(FFT_PRF)
        #data=np.array(historyBKG).mean(0)
        if len(historyBKG)>15:
            del(historyBKG[0])
            
    else:
        historyList.append(FFT_PRF)
        #data=np.array(historyList).mean(0)
        if len(historyList)>20:
            del(historyList[0])
    
    
    try:
        parentFig=plotax.get_figure()
        if len(parentFig.axes)>4:
            ax2=parentFig.axes[4]
            ax2.clear()
        else:
            ax2=plotax.twinx()

        
        try:
            ''' estimate a decision line'''
            if len(historyBKG)>1:
                mean_bkg=np.array(historyBKG).mean(0)
                var_bkg=np.array(historyBKG).var(0)
            else:
                raise AWAKException('HistoryBKG is not long enough')
                #mean_bkg=np.array(historyList).mean(0)
                #var_bkg=np.array(historyList).mean(0)/2 # dummy to not get nan
            ''' some start and end bins to make it easier'''
    
            Aout1,Aout2,meanCut,varianceCut=estimateCut(mean_bkg,var_bkg,binS,binE) #binS and binE from outside
            ''' fit variance as variance estimation is !extremely! slow converging, >1k samples for halfway acceptables errors (like 50%), general problem'''
            fitpoly=sp.polyfit(FFT_TIME[binS:binE],np.sqrt(varianceCut),1) #order 1 polynom is ok
            sigma=sp.polyval(fitpoly,FFT_TIME[binS:binE])
    
            detFreq=0
            maxArg=0
            if (FFT_PRF[binS+buffarg].flatten()-(meanCut[buffarg]+pref*sigma[buffarg]))>0:
                    detFreq=FFT_TIME[buffarg+binS]
                    maxArg=binS+buffarg
            print('noFail_profile_fit_and_detection_true') 
            plotax.plot(FFT_TIME[binS:binE],pref*sigma+meanCut,c='k')
        except:
            print('no distinction plot')
        ''' plot history'''
        historyData=np.zeros(FFT_TIME.shape)
        for k in historyList:
            historyData=historyData+k
        historyData=historyData/np.maximum(len(historyList),1)
        plobj2=ax2.plot(FFT_TIME,historyData,label='FFT History (20 shots)',c='r',linestyle='dotted')
        plobj3=ax2.plot((0,1),(0,1),linestyle='None',label='profileParam is independent of other Plots!\n USE PLOT BELOW TO ADJUST XMPP_PlotFFT/profileParam accordingly!!')
        ax2.set_xlim(0,axmax)
        ax2.set_ylim(0,np.max(data[3:40])*1.25)
        ax2.xaxis.set_ticks(xticks)
        ''' plot selection criterion'''

        
        legendAll=[l.get_label() for l in plobj1+plobj2+plobj3]
        plotax.legend(plobj1+plobj2+plobj3,legendAll)
        
    except:
        detFreq=0
        print('no fft history')
        
    my_gui_vals = japc.getParam('TSG41.AWAKE-XMPP-FFTFREQ/ValueAcquisition#floatValue')
    FFT_MAX_IND = np.argmax(FFT_PRF[3:40]) + 3
    FFT_MAX_VAL = np.max(FFT_PRF[3:40])
    FFT_MAX_FRQ = FFT_TIME[FFT_MAX_IND]
    
    if 'detFreq' in locals():
        AVG_MAX_IND = maxArg
        AVG_MAX_VAL = np.max(data[3:40])
        AVG_MAX_FRQ = detFreq#FFT_TIME[AVG_MAX_IND]
    else:
        AVG_MAX_VAL = my_gui_vals[4]
        AVG_MAX_FRQ = my_gui_vals[3]
    
    
    my_gui_vals[0] = header['acqStamp']
    my_gui_vals[1] = FFT_MAX_FRQ
    my_gui_vals[2] = FFT_MAX_VAL
    my_gui_vals[3] = AVG_MAX_FRQ
    my_gui_vals[4] = AVG_MAX_VAL
    japc.setParam('TSG41.AWAKE-XMPP-FFTFREQ/ValueSettings#floatValue',my_gui_vals)
    
''' profile plot function'''
    
def XMPP_ProfilePlot(plotax,fig,fixedaxes,japc,vec,profileParam):
    plotax.clear()
    try:
        time.sleep(0.5)
        timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
        vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData')
        vec=vec.reshape(512,672)-400
    except:
        print('Failed to retrieve data')
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    if profileParam[0]>profileParam[1]:
        profileParam=(profileParam[1],profileParam[0])    
    vecP=vec[:,int(profileParam[0]/8.75*336)+336:int(profileParam[1]/8.75*336)+336].sum(1)/(int(profileParam[1]/8.75*336)-int(profileParam[0]/8.75*336))
    vecP=vecP/np.max(vecP)
    timeVal=np.append(timeVal[1],timeVal[1:])
    plobj1=plotax.plot(np.flipud(timeVal),np.flipud(vecP),c='r',linewidth=2,label='temporal Profile')
    try:
        parentFig=plotax.get_figure()
        if len(parentFig.axes)>5:
            ax2=parentFig.axes[5]
            ax2.clear()
        else:
            ax2=plotax.twiny()
            ax2.clear()
            
        import scipy as sp
        
        vecP2=vec.reshape(512,672).sum(0)/(512)
        plobj2=ax2.plot(fixedaxes[0],vecP2/np.max(vecP2),label='Spatial Profile')
        startGuess=[(np.max(vecP2)-np.min(vecP2))/2,2/3*(fixedaxes[0][-1]-fixedaxes[0][0]),fixedaxes[0][335],400]
        optimres=sp.optimize.least_squares(gaussFIT1D,startGuess,args=(fixedaxes[0],vecP2/np.max(vecP2)))
        plotobj4=ax2.plot(fixedaxes[0],gaussFIT1D(optimres.x,fixedaxes[0],0),c='k',linestyle='dotted',linewidth=1.5,label='Gauss fit exp(-x**2/(2*sigma**2)): sigma={0:1.2f}'.format(np.abs(optimres.x[1])))
        ''' plot lines to show profile selected'''
        ax2.plot((profileParam[0],profileParam[0]),(0,1.5),c='k',linestyle='dotted')
        ax2.plot((profileParam[1],profileParam[1]),(0,1.5),c='k',linestyle='dotted')
        
    except:
        print('no standard')
        
    try:
        import scipy as sp
        startGuess=[(np.max(vecP)-np.min(vecP))/2,2/3*(timeVal[-1]-timeVal[0]),timeVal[255],400]
        optimres=spo.least_squares(gaussFIT1D,startGuess,args=(np.flipud(timeVal),np.flipud(vecP)))
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

''' parameters for freq estimation and detection'''
binS=5
binE=45
total_p=0.01
p_single=1-(1-total_p)**(1/(binE-binS))
''' sigma * sqrt(-2log(1-F)) : prefactor sqrt() - rayleigh distribution'''
pref=np.sqrt(-2*np.log(1-(1-p_single)))

app = QApplication(sys.argv)
aw = AwakeWindow(["TT41.BCTF.412340/Acquisition#totalIntensityPreferred"],XMPP_beamImage,XMPP_PlotFFT,XMPP_ProfilePlot,fixedaxes=(np.linspace(-8.75,8.75,672),),selector="SPS.USER.AWAKE1",name='AwakeLaserBox Image',XMPP_beamImage={'awkLBox':laserboxMPP,'maxVal':-1,'PixelLengthProfileFit':10,'ProfileParam':(-1.5,1.5)},XMPP_PlotFFT={'historyList':[],'profileParam':(-1,1),'historyBKG':[]},XMPP_ProfilePlot={'profileParam':(-2,2)},reverse=True)
progname='XMPP AwakeSTREAK'
aw.setWindowTitle("%s" % progname)
aw.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))
aw.show()
app.exec_()
