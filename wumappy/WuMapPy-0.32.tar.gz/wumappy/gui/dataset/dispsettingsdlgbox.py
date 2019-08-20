# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.dispsettingsdlgbox
    --------------------------------------

    Display settings dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import os
#import numpy as np
import numexpr as ne

from geophpy.dataset import (
    plottype_getlist,
    interpolation_getlist,
    colormap_getlist,
    colormap_icon_getlist,
    colormap_icon_getpath)

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox
import matplotlib.pyplot as plt

#------------------------------------------------------------------------------#
# Display Settings Dialog Box Object                                           #
#------------------------------------------------------------------------------#
class DispSettingsDlgBox:

    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent):
        '''
        '''
        
        window = cls()
        window.title = title
        window.parent = parent
        window.dataset = parent.dataset
        #window.parentid = parent.wid
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')                                                                
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'DISPOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 3, 2],
                           ['GroupBox', 'RENDERING_ID', 0, 2, False, None, None, 2, 0, 1, 1, 1],
                           ['GroupBox', 'HISTOGRAM_ID', 0, 1, False, None, None, 3, 0, 1, 1, 1],
                           #['GroupBox', 'GRIDINGOPT_ID', 0, 0, False, None, None, 4, 0, 1, 1, 0],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Display options TAB ##################################################
                           ['Label', 'PLOTTYPE_ID', 0, 0, False, None, None, 0],
                           ['ComboBox', '', 0, 1, True, window.PlotTypeInit, window.PlotTypeUpdate, 0],
                           ['LineEdit', '', 0, 3, True, window.ContourLvlValueInit, window.ContourLvlValueUpdate, 0],
                           ['Label', 'LEVELS_ID', 0, 2, False, window.ContourLvlTextInit, None, 0],
                           ['Label', 'DISPINTERPOLATION_ID', 1, 0, False, None, None, 0],
                           ['ComboBox', '', 1, 1, True, window.InterpolationInit, window.InterpolationUpdate, 0],
                           ['Label', 'COLORMAP_ID', 2, 0, False, None, None, 0],
                           ['ComboBox', '', 2, 1, True, window.ColorMapInit, window.ColorMapUpdate, 0],
                           ['Label', '', 3, 0, False, None, None, 0],
                           ['CheckBox', 'REVERSEFLAG_ID', 4, 0, True, window.ColorMapReverseInit, window.ColorMapReverseUpdate, 0],
                           ['CheckBox', 'AXISDISPLAYFLAG_ID', 4, 1, True, window.AxisDisplayInit, window.AxisDisplayUpdate, 0],
                           ['CheckBox', 'COLORBARDISPLAYFLAG_ID', 5, 0, True, window.ColorBarDisplayInit, window.ColorBarDisplayUpdate, 0],
                           ['CheckBox', 'COLORBARLOGSCALEFLAG_ID', 5, 1, True, window.ColorBarLogScaleInit, window.ColorBarLogScaleUpdate, 0],
                           ['Label', '', 6, 0, False, None, None, 0],
                           ['Label', 'MINIMALVALUE_ID', 7, 0, False, None, None, 0],
                           ['DoubleSpinBox', '', 7, 3, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],
                           ['Slider', '', 7, 1, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0, 1, 2],
                           ['Label', 'MAXIMALVALUE_ID', 8, 0, False, None, None, 0],
                           ['DoubleSpinBox', '', 8, 3, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 0],
                           ['Slider', '', 8, 1, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 0, 1, 2],
                           ['Label', '', 11, 0, False, None, None, 0],
                           ['Label', '', 12, 0, False, None, None, 0],
                           ['Label', '', 13, 0, False, None, None, 0],
                           ['Label', '', 14, 0, False, None, None, 0],
                           ## Cancel, Update Valid #################################################
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],
                           ## Histogram TAB ########################################################
                           ['CheckBox', 'COLORHIST_ID', 0, 0, True, window.HistoColorDisplayInit, window.HistoColorDisplayUpdate, 3],
                           ['CheckBox', 'COLORBARDISPLAYFLAG_ID', 0, 1, True, window.HistoColorBarDisplayInit, window.HistoColorBarDisplayUpdate, 3],
                           #['Image', '', 2, 0, False, window.HistoImageInit, None, 3, 1, 0],
                           ['Graphic', '', 2, 0, False, window.HistoImageInit, None, 3, 1, 0],
                           ### Rendering TAB #######################################################
                           ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 2]]
                           #['Image', '', 0, 1, False, window.CartoImageInit, None, 2]]

        dlgbox = CartoDlgBox(window.asciiset.getStringValue('DISPLAYSETTINGS_ID'), window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window

    #--------------------------------------------------------------------------#
    # Display settings TAB                                                     #
    #--------------------------------------------------------------------------#
    def PlotTypeInit(self, id=None):
        self.plottype = self.parent.plottype

        # building "plot type" list
        plottype_list = plottype_getlist()
        try:
            plottype_index = plottype_list.index(self.plottype)
        except:
            plottype_index = 0
            
        if id is not None:
            id.addItems(plottype_list)
            id.setCurrentIndex(plottype_index)
        self.PlotTypeId = id
        return id

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

    def PlotTypeUpdate(self):
        self.plottype = self.PlotTypeId.currentText()

        # Enabling/Disabling plot levels
        enabledflag = self.plottype in ['2D-CONTOURF', '2D-CONTOUR']
        self.ContourLvlValueId.setEnabled(enabledflag)
        self.ContourLvlTextId.setEnabled(enabledflag)
        
        self.DisplayUpdate()

    def ContourLvlValueInit(self, id=None):
        if id is not None:
            id.setText(str(100))

        self.ContourLvlValueId = id
        self.levels = 100

        enabledflag = self.plottype in ['2D-CONTOURF', '2D-CONTOUR']
        self.ContourLvlValueId.setEnabled(enabledflag)
        return id

    def ContourLvlValueUpdate(self):
        try:
            lvl = int(ne.evaluate(self.ContourLvlValueId.text()))
            if lvl<=2:
                lvl =2
            self.levels = lvl
            self.ContourLvlValueId.setText(str(self.levels))
        except:
            self.levels = 100
            self.ContourLvlValueId.setText('100')

        self.DisplayUpdate()

    def ContourLvlTextInit(self, id=None):
        enabledflag = self.plottype in ['2D-CONTOURF', '2D-CONTOUR']
        if id is not None:
            id.setEnabled(enabledflag)

        self.ContourLvlTextId = id
        return id

    def InterpolationInit(self, id=None):        
        self.interpolation = self.parent.interpolation

        # Building "interpolation" list
        interpolation_list = interpolation_getlist()
        try:
            interpolation_index = interpolation_list.index(self.interpolation)
        except:
            interpolation_index = 0
            
        if id is not None:
            id.addItems(interpolation_list)
            id.setCurrentIndex(interpolation_index)

        self.InterpolationId = id
        return id
    
    def InterpolationUpdate(self):
        self.interpolation = self.InterpolationId.currentText()
        self.DisplayUpdate()

    def ColorMapInit(self, id=None):
        self.colormap = self.parent.colormap
                                                    # building of the "color map" field to select in a list
        cmap_list = colormap_getlist()
        icon_list = colormap_icon_getlist()
        icon_path = colormap_icon_getpath()

        try:
            cmap_index = cmap_list.index(self.colormap)
        except:
            cmap_index = 0
            
        if id is not None:
            ###ORIGINAL CODE having some flaw:
            ###- color map list of name not really meaning full for fancy colormap (visual help needed).
            ###- should display colormap miniature next to the colormap name to be able to work on values as well as on zimage
            #id.addItems(cmap_list)
            #id.setCurrentIndex(cmap_index)
            ###
            # Color map miniature icon creation
            for i, cmap in enumerate(cmap_list):
                icon_name = os.path.join(icon_path, icon_list[i])

                # reading icon from file
                if os.path.isfile(icon_name):
                    cmapicon = QIcon(icon_name)
                    
                # creating icon directly from colormap
                else:
                    cmapfig = colormap_plot(cmap)
                    cmapicon = QPixmap.grabWidget(FigureCanvas(cmapfig))
                    plt.close(cmapfig)

                # updating colomap list
                id.addItem(cmapicon, cmap)
                iconsize = QSize(100,16)
                id.setIconSize(iconsize)
                # ... TBD ... automatic resizing of the icon?
                #self.dataentrycombo.setMinimumHeight(self.projecttoolbar.height())
                
            id.setCurrentIndex(cmap_index)

        self.ColorMapId = id
        return id

    def ColorMapUpdate(self):
        self.colormap = self.ColorMapId.currentText()
        self.DisplayUpdate()

    def ColorMapReverseInit(self, id=None):
        self.reverseflag = self.parent.reverseflag
        
        if id is not None:
            id.setChecked(self.reverseflag)

        self.ColorMapReverseId = id
        return id

    def ColorMapReverseUpdate(self):
        self.reverseflag = self.ColorMapReverseId.isChecked()
        self.DisplayUpdate()

    def ColorBarDisplayInit(self, id=None):
        self.colorbardisplayflag = self.parent.colorbardisplayflag
        
        if id is not None:
            id.setChecked(self.colorbardisplayflag)

        self.ColorBarDisplayId = id
        return id

    def ColorBarDisplayUpdate(self):
        self.colorbardisplayflag = self.ColorBarDisplayId.isChecked()
        self.DisplayUpdate()

    def AxisDisplayInit(self, id=None):
        self.axisdisplayflag = self.parent.axisdisplayflag

        if id is not None:
            id.setChecked(self.axisdisplayflag)

        self.AxisDisplayId = id
        return id

    def AxisDisplayUpdate(self):
        self.axisdisplayflag = self.AxisDisplayId.isChecked()
        self.DisplayUpdate()

    def ColorBarLogScaleInit(self, id=None):
        self.zmin = self.parent.zmin
        self.zmax = self.parent.zmax
        self.colorbarlogscaleflag = self.parent.colorbarlogscaleflag

        # data limits from  histogram
        zmin, zmax = self.dataset.histo_getlimits()
        
        if self.zmin is None:
            self.zmin = zmin
        if self.zmax is None:
            self.zmax = zmax            

        if id is not None:
            # Logscale impossible
            if (self.zmin <= 0):
                self.colorbarlogscaleflag = False               
                id.setEnabled(False)

            # Logscale possible
            else:
                id.setEnabled(True)

            id.setChecked(self.colorbarlogscaleflag)

        self.ColorBarLogScaleId = id
        return id

    def ColorBarLogScaleUpdate(self):
        self.colorbarlogscaleflag = self.ColorBarLogScaleId.isChecked()
        self.DisplayUpdate()

    def MinimalValuebySpinBoxInit(self, id=None):
        if id is not None:
            # Limits from dataset histogram
            zmin, zmax = self.dataset.histo_getlimits()
            id.setRange(zmin, zmax)
            id.setValue(self.zmin)

        self.MinValuebySpinBoxId = id
        return id

    def MinimalValuebySpinBoxUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySpinBoxId.value()
        
        if self.zmin >= self.zmax:
            self.zmin = zminsaved

        self.MinValuebySpinBoxId.setValue(self.zmin)
        self.MinValuebySliderId.setValue(self.zmin)
        self.DisplayUpdate()

    def MinimalValuebySliderInit(self, id=None):
        if id is not None:
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
        self.DisplayUpdate()

    def MaximalValuebySpinBoxInit(self, id=None):
        if id is not None:
            zmin, zmax = self.dataset.histo_getlimits()
            id.setRange(zmin, zmax)
            id.setValue(self.zmax)
        self.MaxValuebySpinBoxId = id
        return id

    def MaximalValuebySpinBoxUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySpinBoxId.value()
        if self.zmax <= self.zmin:
            self.zmax = zmaxsaved
            self.MaxValuebySpinBoxId.setValue(self.zmax)

        self.MaxValuebySliderId.setValue(self.zmax)
        self.DisplayUpdate()

    def MaximalValuebySliderInit(self, id=None):
        if id is not None:
            zmin, zmax = self.dataset.histo_getlimits()
            id.setOrientation(Qt.Horizontal)
            id.setRange(zmin, zmax)
            id.setValue(self.zmax)
        self.MaxValuebySliderId = id
        return id

    def MaximalValuebySliderUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySliderId.value()
        if self.zmax <= self.zmin:
            self.zmax = zmaxsaved
            self.MaxValuebySliderId.setValue(self.zmax) 

        self.MaxValuebySpinBoxId.setValue(self.zmax)
        self.DisplayUpdate()

    #--------------------------------------------------------------------------#
    # Histogram TAB                                                            #
    #--------------------------------------------------------------------------#
    def HistoColorBarDisplayInit(self, id=None):
        self.histocolorbardisplayflag = True

        if id is not None:
            id.setChecked(self.histocolorbardisplayflag)

        self.HistoColorBarDisplayId = id
        return id

    def HistoColorBarDisplayUpdate(self):
        self.histocolorbardisplayflag = self.HistoColorBarDisplayId.isChecked()
        self.HistoImageUpdate()
        self.DisplayUpdate()

    def HistoColorDisplayInit(self, id=None):
        self.histocolorflag = True

        if id is not None:
            id.setChecked(self.histocolorflag)

        self.HistoColorDisplayId = id
        return id

    def HistoColorDisplayUpdate(self):
        self.histocolorflag = self.HistoColorDisplayId.isChecked()
        self.HistoImageUpdate()
        self.DisplayUpdate()

    def HistoImageInit(self, id=None):
        self.histofig = None
        self.HistoImageId = id
        self.HistoImageUpdate()
##        self.HistoImageId = id
##        self.histofig = self.HistoImageId.getFigure()
##        self.HistoImageUpdate()
        return id

    def HistoImageUpdate(self):
#        self.histofig = self.dataset.histo_plot(fig=self.histofig, zmin=self.zmin, zmax=self.zmax)

        self.histofig, _ = self.dataset.histo_plot(
            zmin=self.zmin, zmax=self.zmax,
            cmapname=self.colormap, creversed=self.reverseflag,
            coloredhisto=self.histocolorflag,
            cmapdisplay=self.histocolorbardisplayflag)

        #self.histofig.patch.set_alpha(0.9)  # transparent figure background
        #self.histofig.patch.set_linewidth(4)
        #self.histofig.patch.set_edgecolor('black')
        self.HistoImageId.update(self.histofig)

        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)
        #self.HistoImageId.draw()
        self.HistoImageId.setEnabled(True)
        
    #--------------------------------------------------------------------------#
    # Cancel, Update, Valid button TAB                                         #
    #--------------------------------------------------------------------------#
    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)       # Hides button if real time updating activated
        id.setEnabled(False)                        # disables the button , by default
        return id

    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                     # updates carto image
        self.HistoImageUpdate()

    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id

    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id

    #--------------------------------------------------------------------------#
    # Rendering TAB                                                            #
    #--------------------------------------------------------------------------#
    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        #self.cartofig = self.CartoImageId.getFigure()
        self.CartoImageUpdate()
        return id

    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor
        
        # plots geophysical image
        self.cartofig, cartocmap = self.dataset.plot(
            plottype=self.plottype, cmapname=self.colormap, creversed=self.reverseflag,
            fig=self.cartofig, interpolation=self.interpolation, cmmin=self.zmin,
            cmmax=self.zmax,
            levels=self.levels,
            cmapdisplay = self.colorbardisplayflag,
            axisdisplay = self.axisdisplayflag, logscale=self.colorbarlogscaleflag)

        #self.cartofig.patch.set_alpha(0.1)  # transparent figure background
        #self.cartofig.patch.set_linewidth(4)
        #self.cartofig.patch.set_edgecolor('black')
        self.CartoImageId.update(self.cartofig)
            
        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)
##        ###
##        self.cartofig.patch.set_linewidth(2)
##        self.cartofig.patch.set_edgecolor('black')
##        self.CartoImageId.draw()
##        ###
        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button
        
        self.wid.setCursor(initcursor)                                  # resets the init cursor
