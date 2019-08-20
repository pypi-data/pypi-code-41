# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.continuationdlgbox
    ---------------------------------------

    Continuation dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import numpy as np

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
#from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from geophpy.dataset import sensorconfig_getlist

from wumappy.gui.common.cartodlgbox import CartoDlgBox

#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

#SIZE_GRAPH_x = 440

#---------------------------------------------------------------------------#
# Continuation Dialog Box Object                                            #
#---------------------------------------------------------------------------#
class ContinuationDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent,
            sensorconfig='',
            apod=0,
            continuationdist=1.0,
            sensorsep=0.7,
            conversionflag=False):
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
        window.sensorconfig = sensorconfig
        window.continuationdist = continuationdist
        window.sensorsep = sensorsep
        window.conversionflag = conversionflag
        window.valfiltflag = False
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'CONFIG_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 2, 1, 1, 2, 2],
                           ['GroupBox', 'RENDERING_ID', 0, 1, False, None, None, 3, 0, 1, 1, 1],
                           ['GroupBox', 'HISTOGRAM_ID', 1, 1, False, None, None, 4, 0, 1, 1, 1],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Configuration ########################################################
                           ['Label', 'APODISATIONFACTOR_ID', 0, 0, False, None, None, 0],  
                           ['SpinBox', '', 1, 0, True, window.ApodisationFactorInit, window.ApodisationFactorUpdate, 0],  
                           ['Label', 'CONTINUATIONDIST_ID', 2, 0, False, None, None, 0],
                           ['DoubleSpinBox', '', 3, 0, True, window.ContDistanceInit, window.ContDistanceUpdate, 0], 
                           ['Label', 'ALTITUDE_MSG', 4, 0, False, None, None, 0],
##                           ['Label', 'DOWNSENSORALT_ID', 4, 0, False, None, None, 0],
##                           ['DoubleSpinBox', '', 5, 0, True, window.DownSensorAltitudeInit, window.DownSensorAltitudeUpdate, 0],    
##                           ['Label', 'UPSENSORALT_ID', 6, 0, False, None, None, 0],
##                           ['DoubleSpinBox', '', 7, 0, True, window.UpSensorAltitudeInit, window.UpSensorAltitudeUpdate, 0],   
                           ['Label', '', 5, 0, False, None, None, 0],
                           ['CheckBox', 'TOTALFIELDCONV_ID', 6, 0, True, window.TotalfieldConversionFlagInit, window.TotalfieldConversionFlagUpdate, 0],
                           ['Label', 'SENSORSCONFIG_ID', 7, 0, False, window.SensorConfigLabelInit, None, 0],  
                           ['ComboBox', '', 8, 0, True, window.SensorConfigInit, window.SensorConfigUpdate, 0],    
                           ['Label', 'SENSORSSEP_ID', 9, 0, False, window.SensorsSeparationLabeInit, None, 0],
                           ['DoubleSpinBox', '', 10, 0, True, window.SensorsSeparationInit, window.SensorsSeparationUpdate, 0],    
                           ['Label', '', 11, 0, False, None, None, 0],
                           ['Label', 'DISPOPT_ID', 12, 0, False, None, None, 0],
                           ['Label', 'MINIMALVALUE_ID', 13, 0, False, None, None, 0],  
                           ['SpinBox', '', 14, 0, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],    
                           ['Slider', '', 15, 0, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0],   
                           ['Label', 'MAXIMALVALUE_ID', 16, 0, False, None, None, 0],  
                           ['SpinBox', '', 17, 0, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 0],    
                           ['Slider', '', 18, 0, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 0],
                           ['Label', '', 19, 0, False, None, None, 0],
                           ['Label', '', 20, 0, False, None, None, 0],
                           ## Cancel, Update, Valid ################################################
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],   
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],   
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],   
                           ## Histogram ############################################################
                           ['Graphic', '', 0, 0, False, window.HistoImageInit, None, 3],  
                           ## Rendering ############################################################
                           ['Graphic', '', 1, 0, False, window.CartoImageInit, None, 2]]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window

    #--------------------------------------------------------------------------#
    # Configuration TAB                                                        #
    #--------------------------------------------------------------------------#
    def DisplayUpdate(self):
        '''Updates the GUI the change of a filter's parameter.'''

        # Auto updating GUI
        if self.realtimeupdateflag:
            self.CartoImageUpdate()
            self.HistoImageUpdate()

        # Manually updating GUI
        else:
            # Disabling Rendering and Valid to indicate
            # display not yet uptaded.
            # Enabling Update display button.
            self.CartoImageId.setEnabled(False)
            self.HistoImageId.setEnabled(False)
            self.ValidButtonId.setEnabled(False)
            self.DispUpdateButtonId.setEnabled(True)

    def ApodisationFactorInit(self, id=None):
        id.setRange(0, 25)
        id.setSingleStep(5)
        id.setValue(self.apod)
        self.ApodisationFactorId = id
        return id

    def ApodisationFactorUpdate(self):
        self.apod = self.ApodisationFactorId.value()
        self.automaticrangeflag = True
        self.DisplayUpdate()

    def SensorConfigLabelInit(self, id=None):
        id.setEnabled(self.conversionflag)
        self.SensorConfigLabelId = id
        return id

    def SensorConfigInit(self, id=None):
        configlist = sensorconfig_getlist()
        if "TotalField" in configlist:
            configlist.remove("TotalField")
        id.addItems(configlist)
        try:
            index = id.findText(self.sensorconfig)
        except:
            index = 0
        id.setCurrentIndex(index)
        id.setEnabled(self.conversionflag)
        self.SensorConfigId = id
        return id

    def SensorConfigUpdate(self):
        self.sensorconfig = self.SensorConfigId.currentText()
        self.automaticrangeflag = True
        self.DisplayUpdate()
         
    def SensorsSeparationLabeInit(self, id=None):
        id.setEnabled(self.conversionflag)
        self.SensorSeparationLabelId = id
        return id

    def SensorsSeparationInit(self, id=None):
        id.setSingleStep(0.1)
        id.setValue(self.sensorsep)
        id.setEnabled(self.conversionflag)
        self.SensorSeparationId = id
        return id

    def SensorsSeparationUpdate(self):
        self.sensorsep= self.SensorSeparationId.value()
        self.DisplayUpdate()

    def ContDistanceInit(self, id=None):
        id.setSingleStep(0.1)
        id.setRange(-np.inf,np.inf)
        id.setValue(self.continuationdist)
        self.ContDistId = id
        return id

    def ContDistanceUpdate(self):
        self.continuationdist = self.ContDistId.value()
        self.DisplayUpdate()

    def TotalfieldConversionFlagInit(self, id=None):
        id.setChecked(self.conversionflag)
        self.ConversionFlagId = id
        return id

    def TotalfieldConversionFlagUpdate(self):
        self.conversionflag = self.ConversionFlagId.isChecked()

        self.SensorConfigId.setEnabled(self.conversionflag)
        self.SensorConfigLabelId.setEnabled(self.conversionflag)

        self.SensorSeparationId.setEnabled(self.conversionflag)
        self.SensorSeparationLabelId.setEnabled(self.conversionflag)

        self.automaticrangeflag = True
        self.DisplayUpdate()

    def MinimalValuebySpinBoxInit(self, id=None):
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
        self.DisplayUpdate()

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
        self.DisplayUpdate()

    def MaximalValuebySpinBoxInit(self, id=None):
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
        self.DisplayUpdate()

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
        self.DisplayUpdate()

    def HistoImageInit(self, id=None):
        self.HistoImageId = id
        self.histofig = None
        return id

    def HistoImageUpdate(self):
        self.histofig, _ = self.dataset.histo_plot(fig=self.histofig, zmin=self.zmin, zmax=self.zmax)
        self.HistoImageId.update(self.histofig)

        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))   # builds the pixmap from the canvas
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)
        self.HistoImageId.setEnabled(True)
        
    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)                   # Hides button if real time updating activated
        id.setEnabled(False)                                    # disables the button , by default
        return id

    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                                 # updates carto image
        self.HistoImageUpdate()
        
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

            #self.dataset.continuation(self.sensorconfig, self.apod, self.downsensoraltitude, self.upsensoraltitude, self.continuationflag, continuationvalue)
            self.dataset.continuation(apod=self.apod, distance=self.continuationdist, separation=self.sensorsep, totalfieldconversionflag=self.conversionflag)
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

        except Exception as e:
            self.cartofig, cartocmap = None, None
            self.CartoImageId.setEnabled(False)                             # disables the carto image
            self.ValidButtonId.setEnabled(False)
            print(e)
        
        self.firstdisplayflag = False
        self.wid.setCursor(initcursor)                                  # resets the init cursor
