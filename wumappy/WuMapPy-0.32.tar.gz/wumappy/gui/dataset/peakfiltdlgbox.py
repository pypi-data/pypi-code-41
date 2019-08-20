# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.peakfiltdlgbox
    ----------------------------------

    Peak filtering dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import absolute_import

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
#from Qt import __binding__
from Qt.QtCore import *  # Only used for cursor, really necessary ?
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox

#from geophpy.dataset import *


#---------------------------------------------------------------------------#
# Peak Filtering Dialog Box Object                                        #
#---------------------------------------------------------------------------#
class PeakFiltDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, minmaxreplacedflag=False, nanreplacedflag=False, medianreplacedflag=False):
        '''
        '''
        
        window = cls()
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.colormap = parent.dataset.info.cmapname
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

        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.minmaxreplacedflag = minmaxreplacedflag
        window.nanreplacedflag = nanreplacedflag
        window.medianreplacedflag = medianreplacedflag
        window.histofig = None
        window.items_list = [
            # TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN,[GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
            # GroupBox ---------------------------------------------------------
            ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
            ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 4, 2],
            ['GroupBox', 'RENDERING_ID', 0, 2, False, None, None, 2, 0, 1, 1, 1],
            ['GroupBox', 'HISTOGRAM_ID', 0, 1, False, None, None, 3, 0, 1, 1, 1],
            # Filter options --------------------------------------------------
            ['Label', 'MINIMALVALUE_ID', 0, 0, False, None, None, 0],
            ['DoubleSpinBox', '', 1, 0, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],    
            ['Slider', '', 2, 0, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0],  
            ['Label', 'MAXIMALVALUE_ID', 3, 0, False, None, None, 0],  
            ['DoubleSpinBox', '', 4, 0, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 0],    
            ['Slider', '', 5, 0, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 0], 
            ['CheckBox', 'MINMAXREPLACEDFLAG_ID', 7, 0, True, window.MinMaxReplacedValuesInit, window.MinMaxReplacedValuesUpdate, 0],  
            ['CheckBox', 'NANREPLACEDFLAG_ID', 8, 0, True, window.NanReplacedValuesInit, window.NanReplacedValuesUpdate, 0],  
            ['CheckBox', 'MEDIANREPLACEDFLAG_ID', 9, 0, True, window.MedianReplacedValuesInit, window.MedianReplacedValuesUpdate, 0],  
            ['Label', '', 10, 0, False, None, None, 0],
            ['Label', '', 11, 0, False, None, None, 0],
            ['Label', '', 12, 0, False, None, None, 0],
            ['Label', '', 13, 0, False, None, None, 0],
            ['Label', '', 14, 0, False, None, None, 0],
            # Cancel, Update, Valid --------------------------------------------
            ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],   
            ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],   
            ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],   
            # Histogram --------------------------------------------------------
            ['Graphic', '', 6, 0, False, window.HistoImageInit, None, 3],  
            # Rendering --------------------------------------------------------
            ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 2]
            ]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    def MinimalValuebySpinBoxInit(self, id=None):
        if (id != None):
                                                    # gets the limits of the histogram of the data set
            zmin, zmax = self.dataset.histo_getlimits()
            id.setRange(zmin, zmax)
            id.setValue(self.zmin)
        self.MinValuebySpinBoxId = id
        return id


    def MinimalValuebySpinBoxUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySpinBoxId.value()
        if (self.zmin >= self.zmax):
            self.zmin = zminsaved
        self.MinValuebySpinBoxId.setValue(self.zmin)    

        self.MinValuebySliderId.setValue(self.zmin)
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySliderInit(self, id=None):
        if (id != None):
            zmin, zmax = self.dataset.histo_getlimits()
            id.setOrientation(Qt.Horizontal)
            id.setRange(zmin, zmax)
            id.setValue(self.zmin)
        self.MinValuebySliderId = id
        return id


    def MinimalValuebySliderUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySliderId.value()
        if (self.zmin >= self.zmax):
            self.zmin = zminsaved
            self.MinValuebySliderId.setValue(self.zmin)    

        self.MinValuebySpinBoxId.setValue(self.zmin)
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySpinBoxInit(self, id=None):
        if (id != None):
            zmin, zmax = self.dataset.histo_getlimits()
            id.setRange(zmin, zmax)
            id.setValue(self.zmax)
        self.MaxValuebySpinBoxId = id
        return id


    def MaximalValuebySpinBoxUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySpinBoxId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved
            self.MaxValuebySpinBoxId.setValue(self.zmax)    
            
        self.MaxValuebySliderId.setValue(self.zmax)
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySliderInit(self, id=None):
        if (id != None):
            zmin, zmax = self.dataset.histo_getlimits()
            id.setOrientation(Qt.Horizontal)
            id.setRange(zmin, zmax)
            id.setValue(self.zmax)
        self.MaxValuebySliderId = id
        return id


    def MaximalValuebySliderUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySliderId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved
            self.MaxValuebySliderId.setValue(self.zmax)    
            
        self.MaxValuebySpinBoxId.setValue(self.zmax)
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            self.HistoImageUpdate()
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def HistoImageInit(self, id=None):
        self.HistoImageId = id
        self.HistoImageUpdate()
        return id


    def HistoImageUpdate(self):
#        self.histofig = self.dataset.histo_plot(fig=self.histofig, zmin=self.zmin, zmax=self.zmax)
        self.histofig, _ = self.dataset.histo_plot(zmin=self.zmin, zmax=self.zmax, cmapname=self.dataset.info.cmapname)
        self.HistoImageId.update(self.histofig)

        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))   # builds the pixmap from the canvas
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)
        

    def MinMaxReplacedValuesInit(self, id=None):
        if (id != None):
            id.setChecked(self.minmaxreplacedflag)
        self.MinMaxReplacedValuesId = id
        return id
    
    def MinMaxReplacedValuesUpdate(self):
        self.minmaxreplacedflag = self.MinMaxReplacedValuesId.isChecked()
        
        # Unchecking the other boxes
        if self.minmaxreplacedflag:
            self.NanReplacedValuesId.setChecked(False)
            self.MedianReplacedValuesId.setChecked(False)
        
        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            HistoImageUpdate()                                  # updates histo only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)  


    def NanReplacedValuesInit(self, id=None):
        if (id != None):
            id.setChecked(self.nanreplacedflag)
        self.NanReplacedValuesId = id
        return id

    def NanReplacedValuesUpdate(self):
        self.nanreplacedflag = self.NanReplacedValuesId.isChecked()

        # Unchecking the other boxes
        if self.nanreplacedflag:
            self.MinMaxReplacedValuesId.setChecked(False)
            self.MedianReplacedValuesId.setChecked(False)
        
        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            HistoImageUpdate()                                  # updates histo only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button
        

    def MedianReplacedValuesInit(self, id=None):
        if (id != None):
            id.setChecked(self.medianreplacedflag)
        self.MedianReplacedValuesId = id
        return id


    def MedianReplacedValuesUpdate(self):
        self.medianreplacedflag = self.MedianReplacedValuesId.isChecked()

        # Unchecking the other boxes
        if self.medianreplacedflag:
            self.MinMaxReplacedValuesId.setChecked(False)
            self.NanReplacedValuesId.setChecked(False)

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
            HistoImageUpdate()                                  # updates histo only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button
        

    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)       # Hides button if real time updating activated
        id.setEnabled(False)                        # disables the button , by default
        return id


    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                     # updates carto image
        self.HistoImageUpdate()                                  # updates histo graph
        

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
        return id


    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        self.dataset = self.originaldataset.copy()

        # Replacement by Min&Max, NaN or median
        if any([self.minmaxreplacedflag, self.medianreplacedflag, self.nanreplacedflag]):
            self.dataset.peakfilt(self.zmin, self.zmax, self.medianreplacedflag, self.nanreplacedflag)
        # No replacement
        else:
            self.dataset.peakfilt(None, None, self.medianreplacedflag, self.nanreplacedflag)

        # plots geophysical image
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.cartofig, interpolation=self.parent.interpolation, cmmin=None, cmmax=None, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.CartoImageId.update(self.cartofig)

        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))  # builds the pixmap from the canvas
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)

        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button

        self.wid.setCursor(initcursor)                                  # resets the init cursor
