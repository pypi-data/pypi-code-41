# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.ploughfiltdlgbox
    ------------------------------------

    Anti-Plough filtering dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *  # Only used for cursor, really necessary ?
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox
from geophpy.dataset import spectrum_plottype_getlist

#---------------------------------------------------------------------------#
# Anti-Plough Filtering Dialog Box Object                                   #
#---------------------------------------------------------------------------#
class PloughFiltDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, apod=0, angle=90, cutoff=None, width=2):
        '''
        '''
        
        window = cls()
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.zmin = window.parent.zmin
        window.zmax = window.parent.zmax
        zmin, zmax = window.dataset.histo_getlimits()
        if window.zmin is  None:
            window.zmin = zmin
        if window.zmax is None:
            window.zmax = zmax            

        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')

        window.apodfactor = apod
        window.angle = angle
        window.cutoff = cutoff
        window.width = width

        window.items_list = [
            # TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN,[GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
            # GroupBox ---------------------------------------------------------
            ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
            ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 3, 2],
            ['GroupBox', 'RENDERING_ID', 0, 1, False, None, None, 2, 0, 1, 1, 1],
            ['GroupBox', 'RAWSPECTRUM_ID', 0, 1, False, None, None, 2, 0, 1, 1, 1],
            ['GroupBox', 'FILTSPECTRUM_ID', 0, 1, False, None, None, 2, 0, 1, 1, 1],
            ['GroupBox', 'DIRFILTER_ID', 0, 1, False, None, None, 2, 0, 1, 1, 1],
            # Filter options --------------------------------------------------
            ['Label', 'APODISATIONFACTOR_ID', 0, 0, False, None, None, 0],
            ['SpinBox', '', 1, 0, True, window.ApodisationFactorInit, window.ApodisationFactorUpdate, 0],
            ['Label', 'PLOUGHANGLE_ID', 2, 0, False, None, None, 0],
            ['DoubleSpinBox', '', 3, 0, True, window.AnglebySpinBoxInit, window.AnglebySpinBoxUpdate, 0],
            ['Slider', '', 4, 0, True, window.AnglebySliderInit, window.AnglebySliderUpdate, 0],
            ['Label', 'PLOUGHCUTOFF_ID', 5, 0, False, None, None, 0],
            ['DoubleSpinBox', '', 6, 0, True, window.CutOffInit, window.CutOffUpdate, 0],
            ['Label', 'PLOUGHWIDTH_ID', 7, 0, False, None, None, 0],
            ['DoubleSpinBox', '', 8, 0, True, window.WidthInit, window.WidthUpdate, 0],
            ['Label', '', 9, 0, False, None, None, 0],
            # Cancel, Update, Valid --------------------------------------------
            ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],
            ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],
            ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],
            # Rendering --------------------------------------------------------
            ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 2],
            # Spectrum ---------------------------------------------------------
            ['Label', 'PLOTTYPE_ID', 1, 0, False, None, None, 3],
            ['ComboBox', '', 1, 1, True, window.PlotTypeInit, window.PlotTypeUpdate, 3],
            ['Graphic', '', 0, 0, False, window.SpectrumImageInit, None, 3, 1, 2],
            # Filtered Spectrum ------------------------------------------------
            ['Graphic', '', 0, 1, False, window.FiltSpectrumImageInit, None, 4],
            # Directional Filter -----------------------------------------------
            ['Graphic', '', 0, 1, False, window.DirFilterImageInit, None, 5]
            ]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window

    #--------------------------------------------------------------------------#
    # Filter options TAB                                                       #
    #--------------------------------------------------------------------------#
    def DisplayUpdate(self):
        '''Updates the GUI at the change of a filter's parameter.'''

        # Auto updating GUI
        if self.realtimeupdateflag:
            self.CartoImageUpdate()
            #self.SpectrumImageUpdate()
            self.DirFilterImageUpdate()
            self.FiltSpectrumImageUpdate()

        # Manually updating GUI
        else:
            # Disabling Rendering and Valid to indicate
            # display not yet uptaded.
            # Enabling Update display button.
            self.CartoImageId.setEnabled(False)
            self.ValidButtonId.setEnabled(False)
            self.DispUpdateButtonId.setEnabled(True)

    def ApodisationFactorInit(self, id=None):
        if id is not None:
            id.setRange(0, 25)
            id.setSingleStep(5)
            id.setValue(self.apodfactor) 
        self.ApodisationFactorId = id
        return id


    def ApodisationFactorUpdate(self):
        self.apodfactor = self.ApodisationFactorId.value()
        self.DisplayUpdate()
        self.DirFilterImageUpdate()
        #self.FiltSpectrumImageUpdate()
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def AnglebySpinBoxInit(self, id=None):
        if id is not None:
            id.setRange(0, 90)
            id.setValue(self.angle)
        self.AnglebySpinBoxId = id
        return id


    def AnglebySpinBoxUpdate(self):
        self.angle = self.AnglebySpinBoxId.value()
        self.AnglebySliderId.setValue(self.angle)

        self.DirFilterImageUpdate()
        #self.FiltSpectrumImageUpdate()
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def AnglebySliderInit(self, id=None):
        if id is not None:
            id.setOrientation(Qt.Horizontal)
            id.setRange(0, 90)
            id.setValue(self.angle)
        self.AnglebySliderId = id
        self.AnglebySliderId.TickPosition(QSlider.TicksBothSides)
        self.AnglebySliderId.setTickInterval((90-0)*0.25)
        return id


    def AnglebySliderUpdate(self):
        self.angle = self.AnglebySliderId.value()
        self.AnglebySpinBoxId.setValue(self.angle)

        
    def CutOffInit(self, id=None):
        if id is not None:
            id.setRange(0, 10000.0)
            id.setValue(self.cutoff)
            if self.cutoff==0:
                self.cutoff = None
        self.CutOffId = id
        return id


    def CutOffUpdate(self):
        self.cutoff = self.CutOffId.value()
        if self.cutoff==0:
            self.cutoff = None
        
        self.DirFilterImageUpdate()
        #self.FiltSpectrumImageUpdate()
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def WidthInit(self, id=None):
        if id is not None:
            id.setRange(1, 10.0)
            id.setValue(self.width)
        self.WidthId = id
        return id

    def WidthUpdate(self):
        self.width = self.WidthId.value()
        self.DirFilterImageUpdate()
        #self.FiltSpectrumImageUpdate()
        self.DisplayUpdate()

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
        #self.SpectrumImageUpdate()
        self.DirFilterImageUpdate()
        self.FiltSpectrumImageUpdate()


    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id


    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id

    #--------------------------------------------------------------------------#
    # Spectrum TAB                                                             #
    #--------------------------------------------------------------------------#
    def PlotTypeInit(self, id=None):
        plottype_list = spectrum_plottype_getlist()
        plottype_index = 1
        self.plottype = plottype_list[plottype_index]
        
        if id is not None:
            id.addItems(plottype_list)
            id.setCurrentIndex(plottype_index)
        self.PlotTypeId = id
        return id

    def PlotTypeUpdate(self):
        self.plottype = self.PlotTypeId.currentText()
        self.SpectrumImageUpdate()
        self.FiltSpectrumImageUpdate()
        #self.DisplayUpdate()

##    def SpectrumImageInit(self, id=None):
##        self.spectrumfig = None
##        self.SpectrumImageId = id
##        self.SpectrumImageUpdate()
##        return id
##
##    def SpectrumImageUpdate(self):
####        # Directionnel filter direction
####        nx = self.dataset.data.z_image.shape[1]
####        dx = self.dataset.info.x_gridding_delta
####        u = np.fft.fftfreq(nx, d=dx)
####        ymax = np.sin(self.angle*np.pi/180)*u.max()
####        x = [0, u.max()]
####        y = [0, ymax]
####
####        lines = [[x, y]]
##
##        # forcing figure clearing ?
##        if self.spectrumfig is not None:
##            self.spectrumfig.clf()
##        #self.spectrumfig, _ = self.originaldataset.spectral_plotmap(fig=self.spectrumfig, plottype=self.plottype, cmapdisplay=False, lines=lines)
##        self.spectrumfig, _ = self.originaldataset.spectral_plotmap(fig=self.spectrumfig, plottype=self.plottype, cmapdisplay=False)
##
##        #pixmap = QPixmap.grabWidget(self.spectrumfig.canvas)   # builds the pixmap from the canvas
##        pixmap = QPixmap.grabWidget(FigureCanvas(self.spectrumfig))   # builds the pixmap from the canvas
##        pixmap = pixmap.scaledToWidth(SIZE_GRAPH_x)
##        self.SpectrumImageId.setPixmap(pixmap)

    def SpectrumImageInit(self, id=None):
        self.spectrumfig = None
        self.SpectrumImageId = id
        self.SpectrumImageUpdate()
        return id

    def SpectrumImageUpdate(self):
        self.spectrumfig, _ = self.originaldataset.spectral_plotmap(fig=self.spectrumfig, plottype=self.plottype, cmapdisplay=False)
        self.SpectrumImageId.update(self.spectrumfig)

    def FiltSpectrumImageInit(self, id=None):
        self.filtspectrumfig = None
        self.FiltSpectrumImageId = id
        self.FiltSpectrumImageUpdate()
        return id

    def FiltSpectrumImageUpdate(self):
        self.filtspectrumfig, _ = self.dataset.spectral_plotmap(fig=self.filtspectrumfig, plottype=self.plottype, cmapdisplay=False)
        self.FiltSpectrumImageId.update(self.filtspectrumfig)

        #pixmap = QPixmap.grabWidget(self.spectrumfig.canvas)   # builds the pixmap from the canvas
        #pixmap = QPixmap.grabWidget(FigureCanvas(self.filtspectrumfig))   # builds the pixmap from the canvas
        #pixmap = pixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.FiltSpectrumImageId.setPixmap(pixmap)

    #--------------------------------------------------------------------------#
    # Directional Filter TAB                                                   #
    #--------------------------------------------------------------------------#
    def DirFilterImageInit(self, id=None):
        self.dirfiltfig = None
        self.DirFilterImageId = id
        self.DirFilterImageUpdate()
        return id

    def DirFilterImageUpdate(self):
        self.dirfiltfig, _ = self.originaldataset.plot_directional_filter(fig=self.dirfiltfig, cutoff=self.cutoff, azimuth=self.angle, width=self.width)
        self.DirFilterImageId.update(self.dirfiltfig)

        #pixmap = QPixmap.grabWidget(FigureCanvas(self.dirfiltfig))   # builds the pixmap from the canvas
        #pixmap = pixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.DirFilterImageId.setPixmap(pixmap)

    #--------------------------------------------------------------------------#
    # Rendering TAB                                                            #
    #--------------------------------------------------------------------------#
    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        ###
        #self.cartofig = self.CartoImageId.getFigure()
        ###
        self.CartoImageUpdate()
        return id

    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        # processes data set
        self.dataset = self.originaldataset.copy()
        self.dataset.ploughfilt(apod=self.apodfactor, azimuth=self.angle, cutoff=self.cutoff, width=self.width)

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

        self.wid.setCursor(initcursor)                                  # resets the init cursor
        
