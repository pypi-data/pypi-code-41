#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 13:10:15 2018

@author: sgess
"""
import numpy as np
import pyjapc

import os
import sys
os.environ['AAT'] = '/user/awakeop/AWAKE_ANALYSIS_TOOLS/'
#os.environ['AAT'] = '/afs/cern.ch/user/s/sgess/AWAKE_ANALYSIS_TOOLS/'
sys.path.append(os.environ['AAT']+'analyses/')
import frame_analysis as fa

''' Class for AWAKE Camera Properties '''
class AwakeCamera():
    def __init__(self,device,name,system,mode,japc):
        self.device = device
        self.name = name
        self.system = system
        self.mode = mode
        self.japc = japc
        self.run_ana = True
        self.fit_gauss = False
        self.median_filter = False
        self.fillCamHandles()
        self.initCam()
        
    def fillCamHandles(self):
        
        if self.system == 'PXI':
            
            self.settings_prop = 'PublishedSettings'
            self.exposure_field = 'exposureTime'
            self.delay_field = 'delayTime'
            self.height_str = 'height'
            self.width_str = 'width'
            self.pixel_str = 'pixelSize'
            self.x_ax_str = ''
            self.y_ax_str = ''
            self.timestamp_str = 'imageTimeStamp'
            
            if self.mode == 'EXT':
                self.image_prop = 'ExtractionImage'
                self.image_str = 'imageRawData'
                self.timingSelector = 'SPS.USER.AWAKE1'
            elif self.mode == 'LASER':
                self.image_prop = 'CameraImage'
                self.image_str = 'image'
                self.timingSelector = 'SPS.USER.ALL'
            else:
                print('GTFOH')
                return
            
            self.acq_string = self.device + '/' + self.image_prop
            self.sys_string = self.device + '/' + self.settings_prop
            
        elif self.system == 'BTV':
            
            self.image_prop = 'Image'
            self.settings_prop = ''
            self.image_str = 'imageSet'
            self.height_str = 'nbPtsInSet1'
            self.width_str = 'nbPtsInSet2'
            self.pixel_str = ''
            self.x_ax_str = 'imagePositionSet1'
            self.y_ax_str = 'imagePositionSet2'
            self.timestamp_str = ''
            
            if self.mode == 'EXT':
                self.timingSelector = 'SPS.USER.AWAKE1'
            elif self.mode == 'LASER':
                self.device = self.device + '.LASER'
                self.timingSelector = 'SPS.USER.ALL'
            else:
                print('GTFOH')
                return
            
            self.acq_string = self.device + '/' + self.image_prop
            
        else:
            print('GTFOH')
            return
        
    def initCam(self):
        
        if self.system == 'PXI':
            self.initPXI()
            self.getSystem()
        elif self.system == 'BTV':
            self.initBTV()
        else:
            print('GTFOH')
            return
        
        if self.run_ana:
            self.analyze()
            
    def initPXI(self):
        
        camData = self.async_get(self.acq_string)
        
        if self.mode == 'EXT':
            self.px_sz = camData[self.pixel_str]
        elif self.mode == 'LASER':
            self.px_sz = 5.0*camData[self.pixel_str]
        else:
            print('GTFOH')
            return
        
        self.image = camData[self.image_str]
        self.width = camData[self.width_str]
        self.height = camData[self.height_str]
        x_ax = self.px_sz*np.arange(self.width)
        self.x_ax = x_ax - np.mean(x_ax)
        y_ax = self.px_sz*np.arange(self.height)
        self.y_ax = y_ax - np.mean(y_ax)
        self.roi = [self.x_ax[0],self.x_ax[-1],self.y_ax[0],self.y_ax[-1]]
        
    def initBTV(self):
        
        camData = self.async_get(self.acq_string)
        
        im_vec = camData[self.image_str]
        self.width = camData[self.width_str]
        self.height = camData[self.height_str]
        self.image = np.reshape(im_vec,(self.width,self.height))
        self.x_ax = camData[self.x_ax_str]
        self.y_ax = camData[self.y_ax_str]
        self.px_sz = self.x_ax[1] - self.x_ax[0]
        self.roi = [self.x_ax[0],self.x_ax[-1],self.y_ax[0],self.y_ax[-1]]
            
    def getSystem(self):
        
        sysData = self.async_get(self.sys_string)
        self.exp_time = sysData[self.exposure_field]
        self.del_time = sysData[self.delay_field]
        
    def updateImage(self):
        
        if self.system == 'PXI':
            self.image = self.async_get(self.acq_string+'#'+self.image_str)
            
        elif self.system == 'BTV':
            im_vec = self.async_get(self.acq_string+'#'+self.image_str)
            self.image = np.reshape(im_vec,(self.width,self.height))
            
        else:
            print('GTFOH')
            return
        
        if self.run_ana:
            self.analyze()
        
    def analyze(self):
        self.frame_ana = fa.FrameAna(self.image,self.x_ax,self.y_ax,self.roi)
        self.frame_ana.fit_gauss = self.fit_gauss
        self.frame_ana.median_filter = self.median_filter
        self.frame_ana.analyze_frame()
    
    def async_get(self,param):
        
        return self.japc.getParam(param,timingSelectorOverride=self.timingSelector)
    
    def subCallback(self,name,image):
        
        if self.system == 'PXI':
            self.image = image
            
        elif self.system == 'BTV':
            self.image = np.reshape(image,(self.width,self.height))
            
        else:
            print('GTFOH')
            return
        
        if self.run_ana:
            self.analyze()
    
    def start_sub(self):
        
        self.japc.subscribeParam(self.acq_string+'#'+self.image_str,self.subCallback)
        self.sub_state = True
        self.japc.startSubscriptions()
        
    def start_ExtSub(self,extFunc):
        
        self.japc.subscribeParam(self.acq_string+'#'+self.image_str,extFunc)
        self.sub_state = True
        self.japc.startSubscriptions()
        
    def stop_sub(self):
        #print('out dis bitch')
        self.japc.stopSubscriptions()
        self.japc.clearSubscriptions()
        self.sub_state = False
