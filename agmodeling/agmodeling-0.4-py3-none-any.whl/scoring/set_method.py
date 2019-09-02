# -*- coding: utf-8 -*-
u'''
Created on 29 nov. 2018

@author: guill


implements a part of the SET method for comparing
sensor output as described by :

An Evaluation Tool Kit of Air Quality 1 Micro-Sensing Units 

(Barak Fishbain1,Uri Lerner, Nuria Castell-Balaguer)


Inspired by the R code :
https://fishbain.net.technion.ac.il/home-page/projects-software/


get_IPI_score(df['REF',df['CANDIDATE]):
 Match     : RMSE      : Pearson   : Kendall   : Spearma   : LFE        :: IPI       
 0.687539  : 0.102816  : 0.747821  : 0.524258  : 0.695786  : 0.980072   :: 0.756295  

0.756295
'''
from __future__ import print_function




import pandas as pd
import numpy as np
from scipy import fftpack
import math


u'''
get the global IPI score, a mean of differtens parameters

R piece of code
# Integrated Performance Index (IPI) calculation
  for (device in 1:(devices-1)) {    
    result[device,10]<-mean(c(result[device,2],result[device,4:9],exp(-result[device,3])))
  }
'''
def get_IPI_score(ref,candidate):
    work = pd.DataFrame()
    work[u'REF'] = ref
    work[u'CANDIDATE'] = candidate
    rmse = get_rmse(work[u'REF'] ,work[u'CANDIDATE'])
    rmseTo1 = 1 - rmse
    cor_pearson = get_pearson_correl(work[u'REF'] ,work[u'CANDIDATE'])
    cor_kendall = get_kendall_correl(work[u'REF'] ,work[u'CANDIDATE'])
    cor_spearman = get_spearman_correl(work[u'REF'] ,work[u'CANDIDATE'])
    match_score = compute_match_score_multiple(work[u'REF'],work[u'CANDIDATE'],10)
    energy_balance =get_energy_balance(work[u'REF'])
    
    scorefinal=np.array([match_score,cor_pearson,
           cor_kendall,cor_spearman,
           energy_balance,rmseTo1])
    IPI=scorefinal.mean()
    
    header = u" %-10s: %-10s: %-10s: %-10s: %-10s: %-10s :: %-10s" \
           % (u"Match",u'RMSE',u'Pearson',u'Kendall', \
              u'Spearman',u'LFE',u'IPI')
    values = u" %-10.6f: %-10.6f: %-10.6f: %-10.6f: %-10.6f: %-10.6f :: %-10.6f" \
           % (match_score,rmse,cor_pearson,cor_kendall, \
              cor_spearman,energy_balance,IPI)
           
     
    print(header)
    print(values)
    return IPI


u'''
2.1 Root Mean Squared Error and Correlation Coefficients

'''
def get_rmse(ref,data) :
    # enfait calcul de Normalized root mean square error (NRMSE)
    diff= ref-data
    refMean= ref.mean()
    rmse = np.sqrt(np.mean(diff*diff))
 #   print "rmse=%.1f rangeDynamicMean=%.1f" % (rmse,rangeDynamicMean)
    returnv = rmse/refMean
    #print standardDev
    return returnv

def get_pearson_correl(ref,data):
    #method : {‘pearson’, ‘kendall’, ‘spearman’}
    return ref.corr(data,method=u'pearson')

def get_kendall_correl(ref,data):
    #method : {‘pearson’, ‘kendall’, ‘spearman’}
    return ref.corr(data,method=u'kendall')
def get_spearman_correl(ref,data):
    #method : {‘pearson’, ‘kendall’, ‘spearman’}
    return ref.corr(data,method=u'spearman')

u'''
2.4 Match Score
 
'''

def compute_match_score_multiple(ref,data,D) :
    work = pd.DataFrame()
    work[u'REF'] = ref
    work[u'CANDIDATE'] = data
    count = 0.0
    dataLen = len(work)
    for i in range(1,D+1) :
        count = count + compute_score_unique(work,i)
    return count / (D*dataLen)

# SCORE
# 
u'''
R code
ighLowAnalysis <- function(param,deviceID,Q){
  
  # Creating new paramter file per device, without missing data (device and AQM)
  paramNetData<-param[param[,deviceID]>=0 & param[,devices]>=0,]
  
  #initial settings
  samples<-dim(paramNetData)[1];
  devices<-dim(paramNetData)[2]-3;
  qLevel<-matrix(0, nrow=samples, ncol=2);
  matchLevel<-vector(mode="numeric", length=samples);
  
  #segmentation and labeling - each sample is regarded as "segment 1", "segment 2"...
  qLevel[,1]<-round(((Q-1)*((paramNetData[,devices])-min(paramNetData[,devices])))/(max(paramNetData[,devices])-min(paramNetData[,devices]))); # AQM
  qLevel[,2]<-round(((Q-1)*((paramNetData[,deviceID])-min(paramNetData[,deviceID])))/(max(paramNetData[,deviceID])-min(paramNetData[,deviceID]))); # Device
  
   
  #match analysis - for each sample, does the micro unit and the AQM are similarly segmented (both are on the same relative segment)
  matchLevel<-(qLevel[,1]==qLevel[,2]);
  
  
  #data aggregation - averging match level (percentage of similarily segmented samples)
  result <- sum(matchLevel)/samples
  return(result)
}

'''
def compute_score_unique(work, d) :
    refRange = [work[u'REF'].min(), work[u'REF'].max()]
    candidateRange = [work[u'CANDIDATE'].min(), work[u'CANDIDATE'].max()]
    binsCandidate=get_bins_score(candidateRange[0]-1,candidateRange[1]+1,d)
    binsRef=get_bins_score(refRange[0]-1,refRange[1]+1,d)
    
    tmp=pd.DataFrame()
    tmp['BINS_CANDIDATE']=pd.cut(work[u'CANDIDATE'],binsCandidate, labels =[x for x in range(0,d)])
    tmp['BINS_REF']=pd.cut(work[u'REF'],binsRef, labels =[x for x in range(0,d)])
    return len(tmp[tmp[u'BINS_CANDIDATE'] == tmp[u'BINS_REF']])



def get_bins_score(mmin,mmax,n) :
    delta = (mmax-mmin)/(n)
    return [mmin+i*delta for i in range(n+1) ]


u'''
2.5 Lower Frequencies Energy (LFE)


R code
energyBalance <- function(deviceData) {
  
  samplesNetData<-length(deviceData)
  # Transformation of signal to the frequency domain
  Sp_a<-dct(deviceData,variant = 2, inverted=FALSE)
  
  
  squaredSp_a=Sp_a*Sp_a
  # Calculation
  l<-length(Sp_a)
  nrg<-(l-1)*(sum(Sp_a*Sp_a))
  mojo<- t
  roro <- c(0:(l-1))
  
  glagla <- c(0:(l-1))*t((Sp_a*Sp_a))
  results<-1 - sum(c(0:(l-1))*t((Sp_a*Sp_a)))/nrg
  
  
  return(results)
}
'''
def get_energy_balance (dataserie) :
    # get the dct
    dct = fftpack.dct(dataserie)
    # compute nrg total () from the R code
    squared = dct*dct
    nrjTot= squared.sum() * (len (dct)-1)
    # create a vector [0,1,2,3,4...,len(dct ) -1]
    vector = np.arange(len (dct))
    # Energie haute frequence 
    aa=vector*squared
    nrjHi = aa.sum()
    return 1 - nrjHi/nrjTot




