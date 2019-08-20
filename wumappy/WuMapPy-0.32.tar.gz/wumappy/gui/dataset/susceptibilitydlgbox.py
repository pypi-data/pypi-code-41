# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.susceptibilitydlgbox
    ----------------------------------------

    Equivalent stratum of magnetic susceptibility dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import absolute_import

from geophpy.dataset import sensorconfig_getlist

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *  # Only used for cursor, really necessary ?
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox

#---------------------------------------------------------------------------#
# Susceptibility Dialog Box Object                                          #
#---------------------------------------------------------------------------#
class SusceptibilityDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, sensorconfig, apod=0, downsensoraltitude=0.3, upsensoraltitude=1.0, calcdepthvalue=0.0, stratumthicknessvalue=1.0, inclineangle=65, alphaangle=0):
        '''
        '''
        
        window = cls()
        window.firstdisplayflag = True             # True if first display of dialog box, False in the others cases 
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.zmin = window.parent.zmin
        window.zmax = window.parent.zmax
        zmin, zmax = window.dataset.histo_getlimits()
        if window.zmin is None:
            window.zmin = zmin
        if window.zmax is None:
            window.zmax = zmax
        window.automaticrangeflag = True
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.apod = apod
        window.inclineangle = inclineangle
        window.alphaangle = alphaangle
        window.sensorconfig = sensorconfig
        window.downsensoraltitude = downsensoraltitude
        window.upsensoraltitude = upsensoraltitude
        window.calcdepthvalue = calcdepthvalue
        window.stratumthicknessvalue = stratumthicknessvalue
        window.items_list = [
            # TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN,[GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
            # GroupBox ---------------------------------------------------------
            ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
            ['GroupBox', 'CONFIG_ID', 1, 0, False, None, None, 1, 1, 1, 1, 0],
            ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 2, 1, 1, 2, 2],
            ['GroupBox', 'RENDERING_ID', 0, 1, False, None, None, 3, 0, 1, 1, 1],
            ['GroupBox', 'HISTOGRAM_ID', 1, 1, False, None, None, 4, 0, 1, 1, 1],
            # Filter options --------------------------------------------------
            ['Label', 'APODISATIONFACTOR_ID', 0, 0, False, None, None, 0],  
            ['SpinBox', '', 1, 0, True, window.ApodisationFactorInit, window.ApodisationFactorUpdate, 0],    
            ['Label', 'APODISATIONFACTOR_MSG', 2, 0, False, None, None, 0],
            ['ComboBox', '', 1, 1, True, window.SensorConfigInit, window.SensorConfigUpdate, 1],    
            ['Label', 'INCLINEANGLE_ID', 3, 0, False, None, None, 0],  
            ['DoubleSpinBox', '', 4, 0, True, window.InclineAngleInit, window.InclineAngleUpdate, 0],    
            ['Label', 'ALPHAANGLE_ID', 5, 0, False, None, None, 0],  
            ['DoubleSpinBox', '', 6, 0, True, window.AlphaAngleInit, window.AlphaAngleUpdate, 0],    
            ['DoubleSpinBox', '', 8, 0, True, window.CalcDepthValueInit, window.CalcDepthValueUpdate, 0],   
            ['Label', 'CALCDEPTH_ID', 7, 0, False, None, None, 0],   
            ['Label', 'MINIMALVALUE_ID', 9, 0, False, None, None, 0],  
            ['DoubleSpinBox', '', 10, 0, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],    
            ['Slider', '', 11, 0, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0],  
            # Configuration ----------------------------------------------------
            ['Label', 'EQSTRATTHICKNESS_ID', 7, 1, False, None, None, 1],
            ['Label', 'PROSPTECH_ID', 0, 1, False, None, None, 1],  
            ['Label', 'DOWNSENSORALT_ID', 3, 1, False, None, None, 1],
            ['DoubleSpinBox', '', 4, 1, True, window.DownSensorAltitudeInit, window.DownSensorAltitudeUpdate, 1],    
            ['Label', 'UPSENSORALT_ID', 5, 1, False, None, None, 1],
            ['DoubleSpinBox', '', 6, 1, True, window.UpSensorAltitudeInit, window.UpSensorAltitudeUpdate, 1],    
            ['Label', 'ALTITUDE_MSG', 2, 1, False, None, None, 1],  
            ['DoubleSpinBox', '', 8, 1, True, window.StratumThicknessValueInit, window.StratumThicknessValueUpdate, 1],  
            ['Label', 'MAXIMALVALUE_ID', 9, 1, False, None, None, 1],  
            ['DoubleSpinBox', '', 10, 1, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 1],    
            ['Slider', '', 11, 1, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 1],  
            # Cancel, Update, Valid --------------------------------------------
            ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 2],   
            ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 2],   
            ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 2],   
            # Histogram --------------------------------------------------------
            ['Graphic', '', 12, 1, False, window.HistoImageInit, None, 4], 
            # Rendering --------------------------------------------------------
            ['Graphic', '', 0, 2, False, window.CartoImageInit, None, 3]
            ]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    def ApodisationFactorInit(self, id=None):
        if (id != None):
            id.setRange(0, 25)
            id.setSingleStep(5)
            id.setValue(self.apod)
        self.ApodisationFactorId = id
        return id


    def ApodisationFactorUpdate(self):
        self.apod = self.ApodisationFactorId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def InclineAngleInit(self, id=None):
        if (id != None):
            id.setRange(0.1, 90)
            id.setValue(self.inclineangle)
        self.InclineAngleId = id
        return id


    def InclineAngleUpdate(self):
        self.inclineangle = self.InclineAngleId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def AlphaAngleInit(self, id=None):
        if (id != None):
            id.setRange(0, 360)
            id.setValue(self.alphaangle)
        self.AlphaAngleId = id
        return id


    def AlphaAngleUpdate(self):
        self.alphaangle = self.AlphaAngleId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def SensorConfigInit(self, id=None):
        list = sensorconfig_getlist()
        id.addItems(list)
        try:
            index = id.findText(self.sensorconfig)
        except:
            index = 0
        id.setCurrentIndex(index)
        self.SensorConfigId = id
        return id
        
        

    def SensorConfigUpdate(self):
        self.sensorconfig = self.SensorConfigId.currentText()
        self.automaticrangeflag = True
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button
        

    def DownSensorAltitudeInit(self, id=None):
        id.setSingleStep(0.1)
        id.setValue(self.downsensoraltitude)
        self.DownSensorAltId = id
        return id


    def DownSensorAltitudeUpdate(self):
        self.downsensoraltitude = self.DownSensorAltId.value()
        self.UpSensorAltId.setRange(self.downsensoraltitude + 0.1, 99)
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button
        
        
    def UpSensorAltitudeInit(self, id=None):
        id.setSingleStep(0.1)
        id.setRange(self.downsensoraltitude + 0.1, 99)
        if (self.upsensoraltitude < self.downsensoraltitude):   # if wrong upsensor altitude
            self.upsensoraltitude = self.downsensoraltitude + 1.# set the up-sensor altitude equal to just more than down-sensor altitude 
        id.setValue(self.upsensoraltitude)
        self.DownSensorAltId.setRange(0, self.upsensoraltitude - 0.1)
        self.UpSensorAltId = id
        return id


    def UpSensorAltitudeUpdate(self):
        self.upsensoraltitude = self.UpSensorAltId.value()
        self.DownSensorAltId.setRange(0, self.upsensoraltitude - 0.1)
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def CalcDepthValueInit(self, id=None):
        id.setSingleStep(0.1)
        id.setValue(self.calcdepthvalue)
        self.CalcDepthValueId = id
        return id


    def CalcDepthValueUpdate(self):
        self.calcdepthvalue = self.CalcDepthValueId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button

        
    def StratumThicknessValueInit(self, id=None):
        id.setSingleStep(0.1)
        id.setValue(self.stratumthicknessvalue)
        self.StratumThicknessValueId = id
        return id


    def StratumThicknessValueUpdate(self):
        self.stratumthicknessvalue = self.StratumThicknessValueId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button

        
    def MinimalValuebySpinBoxInit(self, id=None):
        id.setSingleStep(0.1)
        self.MinValuebySpinBoxId = id
        return id


    def MinimalValuebySpinBoxReset(self):
        self.MinValuebySpinBoxId.setRange(self.zmin, self.zmax)
        self.MinValuebySpinBoxId.setValue(self.zmin)


    def MinimalValuebySpinBoxUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySpinBoxId.value()
        if (self.zmin >= self.zmax):
            self.zmin = zminsaved
        self.MinValuebySpinBoxId.setValue(self.zmin)    

        self.MinValuebySliderId.setValue(self.zmin)
        if (self.realtimeupdateflag):                       
            if (self.firstdisplayflag != True) :
                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
                self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySliderInit(self, id=None):
        id.setOrientation(Qt.Horizontal)
        self.MinValuebySliderId = id
        return id


    def MinimalValuebySliderReset(self):
        self.MinValuebySliderId.setRange(self.zmin, self.zmax)
        self.MinValuebySliderId.setValue(self.zmin)


    def MinimalValuebySliderUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySliderId.value()
        if (self.zmin >= self.zmax):
            self.zmin = zminsaved
            self.MinValuebySliderId.setValue(self.zmin)    

        self.MinValuebySpinBoxId.setValue(self.zmin)
        if (self.realtimeupdateflag):                       
            if (self.firstdisplayflag != True) :
                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
                self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySpinBoxInit(self, id=None):
        id.setSingleStep(0.1)
        self.MaxValuebySpinBoxId = id
        return id


    def MaximalValuebySpinBoxReset(self):
        self.MaxValuebySpinBoxId.setRange(self.zmin, self.zmax)
        self.MaxValuebySpinBoxId.setValue(self.zmax)


    def MaximalValuebySpinBoxUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySpinBoxId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved
            self.MaxValuebySpinBoxId.setValue(self.zmax)    
            
        self.MaxValuebySliderId.setValue(self.zmax)
        if (self.realtimeupdateflag):                       
            if (self.firstdisplayflag != True) :
                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
                self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySliderInit(self, id=None):
        id.setOrientation(Qt.Horizontal)
        self.MaxValuebySliderId = id
        return id


    def MaximalValuebySliderReset(self):
        self.MaxValuebySliderId.setRange(self.zmin, self.zmax)
        self.MaxValuebySliderId.setValue(self.zmax)
        return id


    def MaximalValuebySliderUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySliderId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved
            self.MaxValuebySliderId.setValue(self.zmax)    
            
        self.MaxValuebySpinBoxId.setValue(self.zmax)
        if (self.realtimeupdateflag):                       
            if (self.firstdisplayflag != True) :
                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
                self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def HistoImageInit(self, id=None):
        self.HistoImageId = id
        return id


    def HistoImageUpdate(self):
        self.histofig, _ = self.dataset.histo_plot(zmin=self.zmin, zmax=self.zmax, cmapname=self.parent.colormap)
        self.HistoImageId.update(self.histofig)

        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))   # builds the pixmap from the canvas
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)
        

    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)                   # Hides button if real time updating activated
        id.setEnabled(False)                                    # disables the button , by default
        return id


    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                                 # updates carto image
        

    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id


    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id


    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        self.CartoImageUpdate()
        self.HistoImageUpdate()
        return id


    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        try:
            # processes data set
            self.dataset = self.originaldataset.copy()
            self.dataset.susceptibility(self.sensorconfig, self.apod, self.downsensoraltitude, self.upsensoraltitude, self.calcdepthvalue, self.stratumthicknessvalue, self.inclineangle, self.alphaangle)
            if (self.automaticrangeflag):
                self.automaticrangeflag = False
                self.zmin, self.zmax = self.dataset.histo_getlimits()
                self.MinimalValuebySpinBoxReset()
                self.MinimalValuebySliderReset()
                self.MaximalValuebySpinBoxReset()
                self.MaximalValuebySliderReset()

            # plots geophysical image
            self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.cartofig, interpolation=self.parent.interpolation, cmmin=self.zmin, cmmax=self.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)        
            self.CartoImageId.update(self.cartofig)

            #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
            #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))    # builds the pixmap from the canvas
            #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
            #self.CartoImageId.setPixmap(cartopixmap)

            self.CartoImageId.setEnabled(True)                              # enables the carto image
            self.ValidButtonId.setEnabled(True)                             # enables the valid button
            self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button
        except:
            self.cartofig, cartocmap = None, None
            self.CartoImageId.setEnabled(False)                             # disables the carto image
            self.ValidButtonId.setEnabled(False)
        
        self.firstdisplayflag = False
        self.wid.setCursor(initcursor)                                  # resets the init cursor
