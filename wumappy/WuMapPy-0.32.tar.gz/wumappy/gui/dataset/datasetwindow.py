# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.datasetwindow
    ---------------------------------

    Data set window management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import os
#import sys

from geophpy.dataset import (
    pictureformat_getlist,
    rasterformat_getlist,
    gridformat_getlist,
    gridtype_getlist)

from geophpy.geoposset import format_chooser as gpos_format_chooser

#-----------------------------------------------------------------------------#
# Trying to handle both PySide (Qt4) and PySide2 (Qt5)                        #
#-----------------------------------------------------------------------------#
#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
if __binding__ in ('PyQt5', 'PySide2'):
    is_qt5 = True
    is_qt4 = not is_qt5
elif __binding__ in ('PyQt4', 'PySide'):
    is_qt4 = True
    is_qt5 = not is_qt4

#-----------------------------------------------------------------------------#
# Matplotlib's import                                                         #
#-----------------------------------------------------------------------------#
if is_qt4:
    from matplotlib.backends.backend_qt4agg import (
        #NavigationToolbar2QT as NavigationToolbar,
        FigureCanvasQTAgg as FigureCanvas)
else:
    from matplotlib.backends.backend_qt5agg import (
#        NavigationToolbar2QT as NavigationToolbar,
        FigureCanvasQTAgg as FigureCanvas)
#from matplotlib.figure import Figure
#import matplotlib.cm as cm

#-----------------------------------------------------------------------------#
# WuMapPy's import                                                            #
#-----------------------------------------------------------------------------#
#from wumappy.gui.common.cartodlgbox import CartoDlgBox
from wumappy.gui.common.menubar import MenuBar

from wumappy.gui.guisettingsdlgbox import GuiSettingsDlgBox
from wumappy.gui.languagedlgbox import LanguageDlgBox
from wumappy.gui.opengeopossetdlgbox import OpenGeopossetDlgBox

from wumappy.gui.dataset.georefdlgbox import GeorefDlgBox
from wumappy.gui.dataset.dispsettingsdlgbox import DispSettingsDlgBox
from wumappy.gui.dataset.datasettransformdlgbox import DatasetTransformDlgBox
#from wumappy.gui.dataset.peakfiltdlgbox import PeakfiltDlgBox
from wumappy.gui.dataset.thresholddlgbox import ThresholdDlgBox
from wumappy.gui.dataset.zeromeanfiltdlgbox import ZeroMeanFiltDlgBox
from wumappy.gui.dataset.medianfiltdlgbox import MedianFiltDlgBox
from wumappy.gui.dataset.festoonfiltdlgbox import FestoonFiltDlgBox
from wumappy.gui.dataset.regtrendfiltdlgbox import RegTrendFiltDlgBox
from wumappy.gui.dataset.wallisfiltdlgbox import WallisFiltDlgBox
from wumappy.gui.dataset.ploughfiltdlgbox import PloughFiltDlgBox
from wumappy.gui.dataset.constdestripdlgbox import ConstDestripDlgBox
from wumappy.gui.dataset.cubicdestripdlgbox import CubicDestripDlgBox
from wumappy.gui.dataset.logtransformdlgbox import LogTransformDlgBox
from wumappy.gui.dataset.polereductiondlgbox import PoleReductionDlgBox
from wumappy.gui.dataset.continuationdlgbox import ContinuationDlgBox
from wumappy.gui.dataset.eulerdeconvolutiondlgbox import EulerDeconvolutionDlgBox
from wumappy.gui.dataset.datasetinformationsdlgbox import DatasetInformationsDlgBox
from wumappy.gui.dataset.analyticsignaldlgbox import AnalyticSignalDlgBox
from wumappy.gui.dataset.susceptibilitydlgbox import SusceptibilityDlgBox
from wumappy.gui.dataset.gradmagfieldconversiondlgbox import GradMagFieldConversionDlgBox

from wumappy.gui.geoposset.geopossetwindow import GeopossetWindow

#-----------------------------------------------------------------------------#
# Data set Window Object                                                      #
#-----------------------------------------------------------------------------#
# MENUS
ITEM_FILES = 1
ITEM_SETTINGS = 2
ITEM_OPERATION = 3
ITEM_PROCESSING = 4
ITEM_MAGPROCESSING = 5
ITEM_INFORMATIONS = 6
ITEM_GEOREFERENCING = 7
# ITEM FILES MENU
ITEM_CLOSE = 10
ITEM_PRINT = 11
ITEM_EXPORT = 12
ITEM_EXPORT_PICTURE = 13
ITEM_EXPORT_KML = 14
ITEM_EXPORT_RASTER = 15
ITEM_EXPORT_GRD = 16
ITEM_SAVE = 17
# ITEM OPERATION MENU
ITEM_INFO = 20
ITEM_TRANSFORM = 21
ITEM_DATSETOPER = 22
ITEM_CLIP = 23
ITEM_DIGITIZE = 24
ITEM_GRID = 25
# ITEM PROCESSING MENU
ITEM_THRESHOLD = 30
ITEM_ZEROMEANFILT = 31
ITEM_MEDIANFILT = 32
ITEM_FESTOONFILT = 33
ITEM_CONSTDESTRIP = 34
ITEM_CUBICDESTRIP = 35
ITEM_REGTRENDFILT = 36
ITEM_WALLISFILT = 37
ITEM_PLOUGHFILT = 38
# ITEM MAGPROCESSING MENU
ITEM_LOGTRANSFORM = 40
ITEM_POLEREDUCTION = 41
ITEM_EQUATORREDUCTION = 42
ITEM_CONTINUATION = 43
ITEM_EULERDECONVOLUTION = 44
ITEM_ANALYTICSIGNAL = 45
ITEM_SUSCEPTIBILITY = 46
ITEM_GRADMAGFIELDCONV = 47
# ITEM GEOREFERENCING MENU
ITEM_LOADGCP = 48
# ITEM MISCSETTINGS MENU
ITEM_MISCSETTINGS = 50

class DatasetWindow(QWidget):
    def __init__(self):
        self.wid = None                  # window id
        self.dataset = None
        self.plottype = None
        self.colormap = None
        self.reverseflag = False
        self.interpolation = 'bilinear'
        self.dpi = None
        self.axisdisplayflag = False
        self.cbardisplay = False
        self.zmin = None
        self.zmax = None
        self.fig = None
        self.menubarid = None
        self.parent = None
        self.title = ''
        self.geopossetwindowslist = []
        self.colorbardisplayflag = False
        self.colorbarlogscaleflag = False
        self.colorbarlogscaleflag = False
        self.configset = None
        self.icon = None
        self.asciiset = None
        self.menubar = None
        self.canvas = None
        self.ItemList =  []
        ###
        self.statusbar = None
        ###
        self.layoutid = None


    @classmethod
    def new(cls, parent, title, dataset, geopossetwindowslist, plottype,
            colormap, interpolation='bilinear', dpi=600, axisdisplayflag=False,
            colorbardisplayflag=False, zmin=None, zmax=None,
            colorbarlogscaleflag=False, reverseflag=False):
        '''
        creates data window associated at a data set
        '''

        window = cls()

        window.parent = parent
        window.wid = QWidget()                    # builds the windows to insert the canvas
        window.layoutid = QVBoxLayout(window.wid) # implements Layout to display canvas inside
##        ### Adding a status bar
##        window.statusbar = QStatusBar()
##        window.statusbar.showMessage("Ready")
##        ###
        window.title = title
        window.dataset = dataset
        window.geopossetwindowslist = geopossetwindowslist
        window.plottype = plottype
        window.colormap = colormap
        window.interpolation = interpolation
        window.dpi = dpi
        window.axisdisplayflag = axisdisplayflag
        window.colorbardisplayflag = colorbardisplayflag
        window.reverseflag = reverseflag
        window.zmin = zmin
        window.zmax = zmax
        window.colorbarlogscaleflag = colorbarlogscaleflag
        window.configset = parent.configset
        window.icon = parent.icon
        window.asciiset = parent.asciiset
        window.ItemList = [
            # item num, item name, "Menu", function or None, tooltip, parent num, isEnabled
            ## Files menu -----------------------------------------------------
            [ITEM_FILES, 'FILES_ID', "Menu", "", None, True],
            [ITEM_SAVE, 'SAVE_ID', window.save, "Saves the data set", ITEM_FILES, True],
            [ITEM_CLOSE, 'CLOSE_ID', window.close, "Closes the data set", ITEM_FILES, True],
            [ITEM_EXPORT, 'EXPORT_ID', "Menu", "", ITEM_FILES, True],
            [ITEM_EXPORT_PICTURE, 'EXPORTIMAGE_ID', window.exportPictureFile, "Exports the data set image in an image format file", ITEM_EXPORT, True],
            [ITEM_EXPORT_KML, 'EXPORTKML_ID', window.exportKmlFile, "Exports the data set picture in a kmz file to open it in google-earth", ITEM_EXPORT, window.isDatasetGeoreferenced],
            [ITEM_EXPORT_RASTER, 'EXPORTRASTER_ID', window.exportRasterFile, "Exports the data set picture in a raster file (picture file + worldfile) to open it in a SIG software", ITEM_EXPORT, window.isDatasetGeoreferenced],
            [ITEM_EXPORT_GRD, 'EXPORTGRID_ID', window.exportGridFile, "Exports the data set picture as a GRD Surfer Grid File", ITEM_EXPORT, True],
            ## Dislay settings menu -------------------------------------------
            [ITEM_SETTINGS, 'DISPLAYSETTINGS_ID', window.displaySettings, "", None, True],
            ## Operation menu -------------------------------------------------
            [ITEM_OPERATION, 'OPERATION_ID', "Menu", "", None, True],
            [ITEM_INFO, 'INFO_ID', window.infoDataset, "Show informations about data set", ITEM_OPERATION, True],
            [ITEM_TRANSFORM, 'TRANSFORM_ID', window.transformDataset, "", ITEM_OPERATION, True],
            [ITEM_DATSETOPER, 'MATH_ID', window.infoDataset, "", ITEM_OPERATION, False],
            [ITEM_CLIP, 'CLIP_ID', window.infoDataset, "", ITEM_OPERATION, False],
            [ITEM_DIGITIZE, 'DIGITIZE_ID', window.infoDataset, "", ITEM_OPERATION, False],
            [ITEM_DIGITIZE, 'GRID_ID', window.infoDataset, "", ITEM_OPERATION, False],
            ## Processing menu -----------------------------------------------
            [ITEM_PROCESSING, 'PROCESSING_ID', "Menu", "", None, True],
            [ITEM_THRESHOLD, 'THRESHOLD_ID', window.thresholdFiltering, "", ITEM_PROCESSING, True],
            [ITEM_ZEROMEANFILT, 'ZEROMEANFILT_ID', window.zeromeanFiltering, "", ITEM_PROCESSING, True],
            [ITEM_MEDIANFILT, 'MEDIANFILT_ID', window.medianFiltering, "", ITEM_PROCESSING, True],
            [ITEM_FESTOONFILT, 'FESTOONFILT_ID', window.festoonFiltering, "", ITEM_PROCESSING, True],
            [ITEM_REGTRENDFILT, 'REGTRENDFILT_ID', window.regtrendFiltering, "", ITEM_PROCESSING, True],
            [ITEM_WALLISFILT, 'WALLISFILT_ID', window.wallisFiltering, "", ITEM_PROCESSING, True],
            [ITEM_PLOUGHFILT, 'PLOUGHFILT_ID', window.ploughFiltering, "", ITEM_PROCESSING, True],
            [ITEM_CONSTDESTRIP, 'CONSTDESTRIP_ID', window.constDestriping, "", ITEM_PROCESSING, True],
            [ITEM_CUBICDESTRIP, 'CUBICDESTRIP_ID', window.cubicDestriping, "", ITEM_PROCESSING, False],
            ## Magnetic processing menu ---------------------------------------
            [ITEM_MAGPROCESSING, 'MAGPROCESSING_ID', "Menu", "", None, True],
            [ITEM_LOGTRANSFORM, 'LOGTRANSFORM_ID', window.logTransform, "", ITEM_MAGPROCESSING, True],
            [ITEM_POLEREDUCTION, 'POLEREDUCTION_ID', window.poleReduction, "", ITEM_MAGPROCESSING, True],
            [ITEM_CONTINUATION, 'CONTINUATION_ID', window.continuation, "", ITEM_MAGPROCESSING, True],
            [ITEM_ANALYTICSIGNAL, 'ANALYTICSIGNAL_ID', window.analyticSignal, "", ITEM_MAGPROCESSING, True],
            [ITEM_SUSCEPTIBILITY, 'SUSCEPTIBILITY_ID', window.susceptibility, "", ITEM_MAGPROCESSING, False],
            [ITEM_GRADMAGFIELDCONV, 'GRADMAGFIELDCONV_ID', window.gradMagFieldConversion, "", ITEM_MAGPROCESSING, False],
            [ITEM_EULERDECONVOLUTION, 'EULERDECONV_ID', window.eulerDeconvolution, "", ITEM_MAGPROCESSING, True],
            ## Georeferencing menu --------------------------------------------
            [ITEM_GEOREFERENCING, 'GEOREFERENCING_ID', "Menu", "", None, True],
            [ITEM_LOADGCP, 'LOADGCP_ID', window.loadGCPs, "Load Ground Control Points", ITEM_GEOREFERENCING, True],
            [ITEM_GEOREFERENCING, 'DATASETGEOREFERENCING_ID', window.georeferenceDataSet, "Dataset georeferencing", ITEM_GEOREFERENCING, window.isGeoreferencingAvailable],
            ## Miscellaneous settings menu ------------------------------------
            [ITEM_MISCSETTINGS, 'MISCSETTINGS_ID', window.settings, "", None, True]
            ]

        # build window's menubar
        window.menubar = MenuBar.from_list(window.ItemList, window)
        window.wid.setMinimumSize(window.wid.geometry().size())

        window.layoutid.setMenuBar(window.menubar.id)   # layout under menu bar

        window.wid.setWindowTitle(title)                # windows's title
        window.wid.setWindowIcon(window.icon)           # window's icon

        # Window position under the parent window position
        parentGeometry = parent.wid.geometry()
        windowGeometry = window.wid.geometry()
        windowGeometry.setRect(parentGeometry.x(),
                               parentGeometry.y(),
                               windowGeometry.width(),
                               windowGeometry.height()
                               )
        window.wid.setGeometry(windowGeometry)

        #AB# Rajout de la fonction UpdateDisplay une premiere fois pour eviter
        #de rajouter tout le temps une barre supp
        window.fig, _ = window.dataset.plot(window.plottype,
                                            window.colormap,
                                            window.reverseflag,
                                            fig=window.fig,
                                            interpolation=window.interpolation,
                                            dpi=window.dpi,
                                            axisdisplay=window.axisdisplayflag,
                                            cmapdisplay=window.colorbardisplayflag,
                                            cmmin=window.zmin,
                                            cmmax=window.zmax,
                                            logscale=window.colorbarlogscaleflag
                                            )

##        # Tools bar
##        window.mpl_toolbar = NavigationToolbar(window.fig.canvas, window.wid) #AB# Création de la toolbar
##
##        window.layoutid.addWidget(window.mpl_toolbar)                       #AB# Ajout de la toolbar
##        window.layoutid.addWidget(window.fig.canvas)        # adds the canvas in the layout

        window.canvas = FigureCanvas(window.fig)
        window.canvas.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        # Plot resizing behavior
##        window.wid.setFixedSize(window.wid.size())  # preventing windows from resizing for now
        ## by default 'equal' in geophpy
        # window.fig.axes[0].set_aspect('equal')

        window.layoutid.addWidget(window.canvas)

        #FigureCanvas.setSizePolicy(window, QSizePolicy.Expanding, QSizePolicy.Expanding)
        ## #Adding a status bar to layout
        #window.layoutid.addWidget(window.statusbar)
        ###

        ###
        # Resize handle
        window.layoutid.addWidget(QSizeGrip(window.wid),
                                  Qt.AlignBottom,
                                  Qt.AlignRight)
        ###

        return window

    def updateDisplay(self):
        self.fig, _ = self.dataset.plot(self.plottype, self.colormap, self.reverseflag, fig=self.fig, interpolation=self.interpolation, dpi=self.dpi, axisdisplay=self.axisdisplayflag, cmapdisplay=self.colorbardisplayflag, cmmin=self.zmin, cmmax=self.zmax, logscale=self.colorbarlogscaleflag)
        self.layoutid.addWidget(self.fig.canvas)        # adds the canvas in the layout

    def view(self):
        self.wid.show()

    def close(self):
        ''' Close the dataset window. '''

        self.parent.datasetwindowslist.remove(self)
        self.wid.close()

    def save(self):
        ''' Save the dataset. '''

        success = True
        savedir = self.configset.get('DIRECTORIES', 'savefiledir')

        initcursor = self.wid.cursor()   # save init cursor type
        self.wid.setCursor(Qt.WaitCursor)  # set wait cursor

        #filename, selectedfilter = QFileDialog.getSaveFileName(self.wid, 'Save dataset', dir=savedir, filter="*.nc")
        ## PyQt5's getOpenFileNames has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getOpenFileNames(parent, title, directory, initialFilter, options)
        filename, _ = QFileDialog.getSaveFileName(self.wid,
                                                  'Save dataset',
                                                  savedir,
                                                  "*.nc"
                                                  )

##        qfiledlg = QFileDialog(self.wid, directory = savedirdir, filter = "*.nc")
##                qfiledlg.setFont(self.asciiset.font)
##                qfiledlg.setGeometry(self.wid.geometry().left(), self.wid.geometry().top(), qfiledlg.geometry().width(), qfiledlg.geometry().height())
##                qfiledlg.setAcceptMode(QFileDialog.AcceptSave)
##                qfiledlg.show()
##                qfiledlg.exec()
##        if (qfiledlg.result() == QDialog.Accepted):
##            fullfilename = qfiledlg.selectedFiles()
##            self.configset.set('DIRECTORIES', 'savefiledir', os.path.dirname(fullfilename[0]))
##            self.dataset.to_file(fullfilename[0], fileformat='netcdf')
##        else:
##            success = False

        # File selected (empty (False) if cancel is clicked)
        if filename:
            self.configset.set('DIRECTORIES', 'savefiledir', os.path.dirname(filename))
            self.dataset.to_file(filename, fileformat='netcdf')
        else:
            success = False

        self.wid.setCursor(initcursor)   # reset the init cursor

        return success

    def print(self):
        '''
        Prints the data set graphic representation
        '''
        success = False
#        printer = QPrinter()
#        printDlg = QPrintDialog(printer)
#        if printDlg.exec_() == QDialog.Accepted:
#            document = QTextDocument(self.title)
#            document.addRessource(QTextDocument.ImageResource,
#            document.print_(printer)
#            success = True

        return success

    def exportPictureFile(self):
        ''' Export dataset as a picture file. '''

        # Creating available raster format filters
        lst = pictureformat_getlist()
        filt = "Image Files ("

        for frmt in lst:
            filt = filt + " *" + frmt
        filt = filt + ")"

        success = True

        # Export dialogbox
        export_dir = self.configset.get('DIRECTORIES', 'exportimagedir')
        DefaultSaveName = os.path.join(export_dir, 'export.png')
        #fullfilename = QFileDialog.getSaveFileName(dir=DefaultSaveName, filter=filt)
        ## PyQt5's getSaveFileName has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getSaveFileName(parent, caption, directory, initialFilter, selectedFilet, options)
        fullfilename = QFileDialog.getSaveFileName(self.wid,
                                                   'Export dataset',
                                                   DefaultSaveName,
                                                   filt
                                                   )
        file_ext = os.path.splitext(fullfilename[0])[1]

        # Checking selected filter
        initcursor = self.wid.cursor()  # save init cursor type
        self.wid.setCursor(Qt.WaitCursor)  # set wait cursor

        if file_ext in lst:
            self.configset.set('DIRECTORIES',
                               'exportimagedir',
                               os.path.dirname(fullfilename[0])
                               )
            self.dataset.plot(self.plottype,
                              self.colormap,
                              self.reverseflag,
                              fig=None,
                              filename=fullfilename[0],
                              interpolation=self.interpolation,
                              dpi=self.dpi,
                              axisdisplay=self.axisdisplayflag,
                              cmapdisplay=self.colorbardisplayflag,
                              cmmin=self.zmin,
                              cmmax=self.zmax
                              )
        else:
            success = False

        self.wid.setCursor(initcursor)  # reset init cursor

        return success

    def exportKmlFile(self):
        ''' Export dataset as a kmz file. '''

        success = True
        # Export dialogbox
        export_dir = self.configset.get('DIRECTORIES', 'exportkmldir')
        DefaultSaveName = os.path.join(export_dir, 'export.kml')

        #kmlfilename = QFileDialog.getSaveFileName(dir=dir, filter = "*.kml")
        ## PyQt5's getSaveFileName has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getSaveFileName(parent, caption, directory, initialFilter, selectedFilet, options)
        kmlfilename = QFileDialog.getSaveFileName(self.wid,
                                                  'Export dataset',
                                                  DefaultSaveName,
                                                  "*.kml"
                                                  )
        filename = os.path.splitext(kmlfilename[0])[0]
        picturefilename = filename + ".png"

        self.configset.set('DIRECTORIES',
                           'exportkmldir',
                           os.path.dirname(kmlfilename[0])
                           )
        self.dataset.to_kml(self.plottype,
                            self.colormap,
                            kmlfilename[0],
                            self.reverseflag,
                            picturefilename,
                            cmmin=self.zmin,
                            cmmax=self.zmax,
                            interpolation=self.interpolation,
                            dpi=self.dpi
                            )

        return success

    def exportRasterFile(self):
        ''' Export dataset as a georeferenced raster file.

        (.png + .pgw, .jpg + .jgw, .tif + .tfw)

        '''

        # Creating available raster format filters
        lists = rasterformat_getlist()
        filters = "Image Files ("

        for frmt in lists:
            filters = filters + " *" + frmt
        filters = filters + ")"

        success = True

        # Export dialogbox
        export_dir = self.configset.get('DIRECTORIES', 'exportrasterdir')
        DefaultSaveName = os.path.join(export_dir, 'export.png')
        #fullfilename = QFileDialog.getSaveFileName(dir=DefaultSaveName, filter=filters)
        ## PyQt5's getSaveFileName has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getSaveFileName(parent, caption, directory, initialFilter, selectedFilet, options)
        fullfilename = QFileDialog.getSaveFileName(self.wid,
                                                   'Export dataset',
                                                   DefaultSaveName,
                                                   filters
                                                   )
        file_ext = os.path.splitext(fullfilename[0])[1]

        # Checking selected filter
        if file_ext in lists:
            self.configset.set('DIRECTORIES',
                               'exportrasterdir',
                               os.path.dirname(fullfilename[0])
                               )
            self.dataset.to_raster(self.plottype,
                                   self.colormap,
                                   fullfilename[0],
                                   self.reverseflag,
                                   cmmin=self.zmin,
                                   cmmax=self.zmax,
                                   interpolation=self.interpolation,
                                   dpi=self.dpi
                                   )
        else:
            success = False

        return success

    def exportGridFile(self):
        ''' Export to GRD Surfer Grid File (.grd). '''

        # Creating available grid format filters
        formatlist = gridformat_getlist()
        typelist = gridtype_getlist()

        filters = []
        for filt in formatlist:
            filters.append(filt + " (*.grd)")
        filters = ';;'.join(filters)

        success = False

        # Export dialogbox
        export_dir = self.configset.get('DIRECTORIES', 'exportgriddir')
        DefaultSaveName = os.path.join(export_dir, 'export.grd')

        #fullfilename, selectedfilter = QFileDialog.getSaveFileName(dir=DefaultSaveName, filter=filters)
        ## PyQt5's getSaveFileName has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getSaveFileName(parent, caption, directory, initialFilter, selectedFilet, options)
        fullfilename, selectedfilter = QFileDialog.getSaveFileName(self.wid,
                                                                   'Export dataset',
                                                                   DefaultSaveName,
                                                                   filters
                                                                   )
        filename = os.path.splitext(fullfilename)[0]

        # Checking selected filter
        match = [frmt in selectedfilter for frmt in formatlist]
        if any(match):
            idxTrue = [idx for idx, val in enumerate(match) if val][0]
            gridtype = typelist[idxTrue]

            success = self.dataset.to_file(filename+'.grd',
                                           fileformat='surfer',
                                           gridtype=gridtype
                                           )
            self.configset.set('DIRECTORIES',
                               'exportgriddir',
                               os.path.dirname(fullfilename)
                               )

            # Georeferenced dataset
            if self.isDatasetGeoreferenced:
                pass
                # ... TBD... propose and extra wolrd File ?

        return success

    #-------------------------------------------------------------------------#
    # Display settings MENU                                                   #
    #-------------------------------------------------------------------------#
    def displaySettings(self):
        '''
        Adjusts the display settings
        '''
        r, dialogbox = DispSettingsDlgBox.new("Display Settings", self)
        if r == QDialog.Accepted:
            self.axisdisplayflag = dialogbox.axisdisplayflag
            self.colorbardisplayflag = dialogbox.colorbardisplayflag
            self.reverseflag = dialogbox.reverseflag
            self.interpolation = dialogbox.interpolation
            self.plottype = dialogbox.plottype
            self.colormap = dialogbox.colormap
            self.zmin = dialogbox.zmin
            self.zmax = dialogbox.zmax
            self.colorbarlogscaleflag = dialogbox.colorbarlogscaleflag
            self.updateDisplay()
                            # updates config file
            self.configset.set('DISPSETTINGS',
                               'plottype',
                               self.plottype
                               )
            self.configset.set('DISPSETTINGS',
                               'interpolation',
                               self.interpolation
                               )
            self.configset.set('DISPSETTINGS',
                               'colormap',
                               self.colormap
                               )
            self.configset.set('DISPSETTINGS',
                               'reverseflag',
                               str(self.reverseflag)
                               )
            self.configset.set('DISPSETTINGS',
                               'colorbardisplayflag',
                               str(self.colorbardisplayflag)
                               )
            self.configset.set('DISPSETTINGS',
                               'colorbarlogscaleflag',
                               str(self.colorbarlogscaleflag)
                               )
            self.configset.set('DISPSETTINGS',
                               'axisdisplayflag',
                               str(self.axisdisplayflag)
                               )
            self.configset.set('DISPSETTINGS',
                               'dpi',
                               str(self.dpi)
                               )

    #-------------------------------------------------------------------------#
    # Operations MENU                                                         #
    #-------------------------------------------------------------------------#
    def infoDataset(self):
        ''' Data set informations. '''

        DatasetInformationsDlgBox.new("Informations", self)

    def transformDataset(self):
        ''' Dataset transforamtion dialog box. '''

        dlg_label = self.asciiset.getStringValue('TRANSFORM_ID')
        r, dialogbox = DatasetTransformDlgBox.new(dlg_label, self)

        if r == QDialog.Accepted:
            # Updating display
            self.dataset = dialogbox.dataset
            self.updateDisplay()

    #-------------------------------------------------------------------------#
    # Processing MENU                                                         #
    #-------------------------------------------------------------------------#
    def thresholdFiltering(self):
        ''' Data thresholding dialog box. '''

        minmaxreplacedflag = self.configset.getboolean('PROCESSING',
                                                       'thresholdminmaxreplacedflag'
                                                       )
        nanreplacedflag = self.configset.getboolean('PROCESSING',
                                                    'thresholdnanreplacedflag'
                                                    )
        medianreplacedflag = self.configset.getboolean('PROCESSING',
                                                       'thresholdmedianreplacedflag'
                                                       )

        dlg_label = self.asciiset.getStringValue('THRESHOLD_ID')
        r, dialogbox = ThresholdDlgBox.new(dlg_label,
                                           self,
                                           minmaxreplacedflag,
                                           nanreplacedflag,
                                           medianreplacedflag
                                           )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()
                            # updates config file
            self.configset.set('PROCESSING',
                               'thresholdnanreplacedflag',
                               str(dialogbox.nanreplacedflag)
                               )
            self.configset.set('PROCESSING',
                               'thresholdmedianreplacedflag',
                               str(dialogbox.medianreplacedflag)
                               )
            self.configset.set('PROCESSING',
                               'thresholdminmaxreplacedflag',
                               str(dialogbox.minmaxreplacedflag)
                               )

    def zeromeanFiltering(self):
        ''' Zero-mean traverse filtering dialog box. '''

        zeromeanfiltvar = self.configset.get('PROCESSING', 'zeromeanfiltvar')

        dlg_label = self.asciiset.getStringValue('ZEROMEANFILT_ID')
        r, dialogbox = ZeroMeanFiltDlgBox.new(dlg_label,
                                              self,
                                              zeromeanfiltvar
                                              )

        if r == QDialog.Accepted:
            # Updating display
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # Updating configuration file
            self.configset.set('PROCESSING',
                               'zeromeanfiltvar',
                               str(dialogbox.zeromeanfiltvar)
                               )

    def medianFiltering(self):
        ''' Median filter dialog box. '''

        nxsize = self.configset.getint('PROCESSING',
                                       'medianfiltnxsize'
                                       )
        nysize = self.configset.getint('PROCESSING',
                                       'medianfiltnysize'
                                       )
        percent = self.configset.getint('PROCESSING',
                                        'medianfiltpercent'
                                        )
        gap = self.configset.getint('PROCESSING',
                                    'medianfiltgap'
                                    )

        dlg_label = self.asciiset.getStringValue('MEDIANFILT_ID')
        r, dialogbox = MedianFiltDlgBox.new(dlg_label,
                                            self,
                                            nxsize,
                                            nysize,
                                            percent,
                                            gap
                                            )
        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()
                            # updates config file
            self.configset.set('PROCESSING',
                               'medianfiltnxsize',
                               str(dialogbox.nxsize)
                               )
            self.configset.set('PROCESSING',
                               'medianfiltnysize',
                               str(dialogbox.nysize)
                               )
            self.configset.set('PROCESSING',
                               'medianfiltpercent',
                               str(dialogbox.percent)
                               )
            self.configset.set('PROCESSING',
                               'medianfiltgap',
                               str(dialogbox.gap)
                               )

    def festoonFiltering(self):
        ''' Festoon/destaggering filter dialog box. '''

        # using configuration file values
        method = self.configset.get('PROCESSING',
                                    'festoonfiltmethod'
                                    )
        shift = self.configset.getint('PROCESSING',
                                      'festoonfiltshift'
                                      )
        corrmin = self.configset.getfloat('PROCESSING',
                                          'festoonfiltcorrmin'
                                          )
        uniformshift = self.configset.getboolean('PROCESSING',
                                                 'festoonfiltuniformshift'
                                                 )
        dlg_label = self.asciiset.getStringValue('FESTOONFILT_ID')
        r, dialogbox = FestoonFiltDlgBox.new(dlg_label,
                                             self,
                                             method=method,
                                             shift=shift,
                                             corrmin=corrmin,
                                             uniformshift=uniformshift
                                             )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'festoonfiltmethod',
                               dialogbox.method
                               )
            self.configset.set('PROCESSING',
                               'festoonfiltshift',
                               str(dialogbox.shift)
                               )
            self.configset.set('PROCESSING',
                               'festoonfiltcorrmin',
                               str(dialogbox.corrmin)
                               )
            self.configset.set('PROCESSING',
                               'festoonfiltuniformshift',
                               str(dialogbox.uniformshift)
                               )

    def wallisFiltering(self):
        ''' Processes Wallis contrast filter dialog box. '''

        nxsize = self.configset.getint('PROCESSING',
                                       'wallisfiltnxsize'
                                       )
        nysize = self.configset.getint('PROCESSING',
                                       'wallisfiltnysize'
                                       )
        targmean = self.configset.getfloat('PROCESSING',
                                           'wallisfilttargmean'
                                           )
        targstdev = self.configset.getfloat('PROCESSING',
                                            'wallisfilttargstdev'
                                            )
        setgain = self.configset.getfloat('PROCESSING',
                                          'wallisfiltsetgain'
                                          )
        limitstdev = self.configset.getfloat('PROCESSING',
                                             'wallisfiltlimitstdev'
                                             )
        edgefactor = self.configset.getfloat('PROCESSING',
                                             'wallisfiltedgefactor'
                                             )

        dlg_label = self.asciiset.getStringValue('WALLISFILT_ID')
        r, dialogbox = WallisFiltDlgBox.new(dlg_label,
                                            self,
                                            nxsize,
                                            nysize,
                                            targmean,
                                            targstdev,
                                            setgain,
                                            limitstdev,
                                            edgefactor
                                            )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'wallisfiltnxsize',
                               str(dialogbox.nxsize)
                               )
            self.configset.set('PROCESSING',
                               'wallisfiltnysize',
                               str(dialogbox.nysize)
                               )
            self.configset.set('PROCESSING',
                               'wallisfilttargmean',
                               str(dialogbox.targmean)
                               )
            self.configset.set('PROCESSING',
                               'wallisfilttargstdev',
                               str(dialogbox.targstdev)
                               )
            self.configset.set('PROCESSING',
                               'wallisfiltsetgain',
                               str(dialogbox.setgain)
                               )
            self.configset.set('PROCESSING',
                               'wallisfiltlimitstdev',
                               str(dialogbox.limitstdev)
                               )
            self.configset.set('PROCESSING',
                               'wallisfiltedgefactor',
                               str(dialogbox.edgefactor)
                               )

    def ploughFiltering(self):
        ''' Anti-plough filter dialog box.'''

        apod = self.configset.getfloat('PROCESSING',
                                       'apodisationfactor'
                                       )
        angle = self.configset.getfloat('PROCESSING',
                                        'ploughangle'
                                        )
        width = self.configset.getfloat('PROCESSING',
                                        'ploughwidth'
                                        )
        cutoff = self.configset.get('PROCESSING',
                                    'ploughcutoff'
                                    )
        if cutoff == 'none':
            cutoff = 0
        else:
            cutoff = float(cutoff)

        dlg_label = self.asciiset.getStringValue('PLOUGHFILT_ID')
        r, dialogbox = PloughFiltDlgBox.new(dlg_label,
                                            self,
                                            apod=apod,
                                            angle=angle,
                                            cutoff=cutoff,
                                            width=width
                                            )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'apodisationfactor',
                               str(dialogbox.apodfactor)
                               )
            self.configset.set('PROCESSING',
                               'ploughangle',
                               str(dialogbox.angle)
                               )
            self.configset.set('PROCESSING',
                               'ploughwidth',
                               str(dialogbox.width)
                               )

            if dialogbox.cutoff == 0:
                self.configset.set('PROCESSING',
                                   'ploughcutoff',
                                   'none'
                                   )

            else:
                self.configset.set('PROCESSING',
                                   'ploughcutoff',
                                   str(dialogbox.cutoff)
                                   )

    def constDestriping(self):
        ''' Constant destriping dialog box. '''

        # read config file
        method = self.configset.get('PROCESSING',
                                    'destripingmethod'
                                    )
        config = self.configset.get('PROCESSING',
                                    'destripingconfig'
                                    )
        reference = self.configset.get('PROCESSING',
                                       'destripingreference'
                                       )
        nprof = self.configset.getint('PROCESSING',
                                      'destripingprofilesnb'
                                      )

        # filter dlgbox
        dlg_label = self.asciiset.getStringValue('CONSTDESTRIP_ID')
        r, dialogbox = ConstDestripDlgBox.new(dlg_label,
                                              self,
                                              nprof,
                                              method,
                                              reference,
                                              config
                                              )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'destripingmethod',
                               dialogbox.method
                               )
            self.configset.set('PROCESSING',
                               'destripingconfig',
                               dialogbox.config
                               )
            self.configset.set('PROCESSING',
                               'destripingreference',
                               dialogbox.reference
                               )
            self.configset.set('PROCESSING',
                               'destripingprofilesnb',
                               str(dialogbox.nprof)
                               )

    def cubicDestriping(self):
        ''' Cubic destriping dialog box. '''

        # read config file
        ndeg = self.configset.getint('PROCESSING',
                                     'destripingdegreesnb'
                                     )
        nprof = self.configset.getint('PROCESSING',
                                      'destripingprofilesnb'
                                      )

        # filter dlgbox
        dlg_label = self.asciiset.getStringValue('CUBICDESTRIP_ID')
        r, dialogbox = CubicDestripDlgBox.new(dlg_label,
                                              self,
                                              nprof,
                                              ndeg
                                              )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'destripingdegreesnb',
                               str(dialogbox.ndeg)
                               )
            self.configset.set('PROCESSING',
                               'destripingprofilesnb',
                               str(dialogbox.nprof)
                               )

    def regtrendFiltering(self):
        ''' Regional trend filter dialog box. '''

        # read config file
        nxsize = self.configset.getint('PROCESSING',
                                       'regtrendfiltnxsize'
                                       )
        nysize = self.configset.getint('PROCESSING',
                                       'regtrendfiltnysize'
                                       )
        method = self.configset.get('PROCESSING',
                                    'regtrendmethod'
                                    )
        component = self.configset.get('PROCESSING',
                                       'regtrendcomponent'
                                       )

        # filter dlgbox
        dlg_label = self.asciiset.getStringValue('REGTRENDFILT_ID')
        r, dialogbox = RegTrendFiltDlgBox.new(dlg_label,
                                              self,
                                              nxsize,
                                              nysize,
                                              method,
                                              component
                                              )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'medianfiltnxsize',
                               str(dialogbox.nxsize)
                               )
            self.configset.set('PROCESSING',
                               'medianfiltnysize',
                               str(dialogbox.nysize)
                               )
            self.configset.set('PROCESSING',
                               'regtrendmethod',
                               dialogbox.method
                               )
            self.configset.set('PROCESSING',
                               'regtrendcomponent',
                               dialogbox.component
                               )

    #--------------------------------------------------------------------------#
    # Mgnetic processing MENU                                                  #
    #--------------------------------------------------------------------------#
    def logTransform(self):
        ''' Logarithmic  transformation dialog box. '''

        # read config file
        multfactor = self.configset.getint('PROCESSING',
                                           'multfactor'
                                           )

        # filter dlgbox
        dlg_label = self.asciiset.getStringValue('LOGTRANSFORM_ID')
        r, dialogbox = LogTransformDlgBox.new(dlg_label,
                                              self,
                                              multfactor
                                              )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # updates config file
            self.configset.set('PROCESSING',
                               'multfactor',
                               str(dialogbox.multfactor)
                               )

    def poleReduction(self):
        ''' Redution to the magnetic pole dialog box. '''

        # read config file
        apod = self.configset.getint('PROCESSING',
                                     'apodisationfactor'
                                     )
        inclineangle = self.configset.getfloat('PROCESSING',
                                               'maginclineangle'
                                               )
        alphaangle = self.configset.getfloat('PROCESSING',
                                             'magalphaangle'
                                             )

        # filter dlgbox
        dlg_label = self.asciiset.getStringValue('POLEREDUCTION_ID')
        r, dialogbox = PoleReductionDlgBox.new(dlg_label,
                                               self,
                                               apod,
                                               inclineangle,
                                               alphaangle
                                               )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'apodisationfactor',
                               str(dialogbox.apod)
                               )
            self.configset.set('PROCESSING',
                               'maginclineangle',
                               str(dialogbox.inclineangle)
                               )
            self.configset.set('PROCESSING',
                               'magalphaangle',
                               str(dialogbox.alphaangle)
                               )

    def continuation(self):
        ''' Magnetic continuation dialog box. '''

        # read config file
        apod = self.configset.getint('PROCESSING',
                                     'apodisationfactor'
                                     )
        sensorconfig = self.configset.get('PROCESSING',
                                          'sensorconfig'
                                          )
        sensorsep = self.configset.getfloat('PROCESSING',
                                            'sensorsep'
                                            )
        continuationdist = self.configset.getfloat('PROCESSING',
                                                   'continuationdist'
                                                   )
        conversionflag = self.configset.getboolean('PROCESSING',
                                                   'totalfieldconversionflag'
                                                   )

        # filter dlgbox
        dlg_label = self.asciiset.getStringValue('CONTINUATION_ID')
        r, dialogbox = ContinuationDlgBox.new(dlg_label,
                                              self,
                                              sensorconfig=sensorconfig,
                                              apod=apod,
                                              continuationdist=continuationdist,
                                              sensorsep=sensorsep,
                                              conversionflag=conversionflag
                                              )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'apodisationfactor',
                               str(dialogbox.apod)
                               )
            self.configset.set('PROCESSING',
                               'sensorconfig',
                               dialogbox.sensorconfig
                               )
            self.configset.set('PROCESSING',
                               'sensorsep',
                               str(dialogbox.sensorsep)
                               )
            self.configset.set('PROCESSING',
                               'continuationdist',
                               str(dialogbox.continuationdist)
                               )
            self.configset.set('PROCESSING',
                               'totalfieldconversionflag',
                               str(dialogbox.conversionflag)
                               )

    def analyticSignal(self):
        ''' Analytic signal dialog box. '''

        apod = self.configset.getint('PROCESSING',
                                     'apodisationfactor'
                                     )

        dlg_label = self.asciiset.getStringValue('ANALYTICSIGNAL_ID')
        r, dialogbox = AnalyticSignalDlgBox.new(dlg_label,
                                                self,
                                                apod
                                                )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.zmin = dialogbox.zmin
            self.zmax = dialogbox.zmax
            self.updateDisplay()

            # updates config file
            self.configset.set('PROCESSING',
                               'apodisationfactor',
                               str(dialogbox.apod)
                               )

    def susceptibility(self):
        ''' Equivalent stratum in magnetic susceptibility dialog box. '''

        apod = self.configset.getint('PROCESSING',
                                     'apodisationfactor'
                                     )
        prosptech = self.configset.get('PROCESSING',
                                       'prosptech'
                                       )
        downsensoraltitude = self.configset.getfloat('PROCESSING',
                                                     'downsensoraltitude'
                                                     )
        upsensoraltitude = self.configset.getfloat('PROCESSING',
                                                   'upsensoraltitude'
                                                   )
        calcdepthvalue = self.configset.getfloat('PROCESSING',
                                                 'calcdepth'
                                                 )
        stratumthicknessvalue = self.configset.getfloat('PROCESSING',
                                                        'stratumthickness'
                                                        )
        inclineangle = self.configset.getfloat('PROCESSING',
                                               'maginclineangle'
                                               )
        alphaangle = self.configset.getfloat('PROCESSING',
                                             'magalphaangle'
                                             )

        dlg_label = self.asciiset.getStringValue('SUSCEPTIBILITY_ID')
        r, dialogbox = SusceptibilityDlgBox.new(dlg_label,
                                                self,
                                                prosptech,
                                                apod,
                                                downsensoraltitude,
                                                upsensoraltitude,
                                                calcdepthvalue,
                                                stratumthicknessvalue,
                                                inclineangle,
                                                alphaangle
                                                )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'apodisationfactor',
                               str(dialogbox.apod)
                               )
            self.configset.set('PROCESSING',
                               'prosptech',
                               dialogbox.prosptech
                               )
            self.configset.set('PROCESSING',
                               'downsensoraltitude',
                               str(dialogbox.downsensoraltitude)
                               )
            self.configset.set('PROCESSING',
                               'upsensoraltitude',
                               str(dialogbox.upsensoraltitude)
                               )
            self.configset.set('PROCESSING',
                               'calcdepth',
                               str(dialogbox.calcdepthvalue)
                               )
            self.configset.set('PROCESSING',
                               'stratumthickness',
                               str(dialogbox.stratumthicknessvalue)
                               )
            self.configset.set('PROCESSING',
                               'maginclineangle',
                               str(dialogbox.inclineangle)
                               )
            self.configset.set('PROCESSING',
                               'magalphaangle',
                               str(dialogbox.alphaangle)
                               )

    def gradMagFieldConversion(self):
        ''' Conversion between sensors configurations dialog box. '''

        apod = self.configset.getint('PROCESSING',
                                     'apodisationfactor')
        prosptechused = self.configset.get('PROCESSING',
                                           'prosptech'
                                           )
        downsensoraltused = self.configset.getfloat('PROCESSING',
                                                    'downsensoraltitude'
                                                    )
        upsensoraltused = self.configset.getfloat('PROCESSING',
                                                  'upsensoraltitude'
                                                  )
        prosptechsim = self.configset.get('PROCESSING',
                                          'prosptech'
                                          )
        downsensoraltsim = self.configset.getfloat('PROCESSING',
                                                   'downsensoraltitude'
                                                   )
        upsensoraltsim = self.configset.getfloat('PROCESSING',
                                                 'upsensoraltitude'
                                                 )
        inclineangle = self.configset.getfloat('PROCESSING',
                                               'maginclineangle'
                                               )
        alphaangle = self.configset.getfloat('PROCESSING',
                                             'magalphaangle'
                                             )

        dlg_label = self.asciiset.getStringValue('GRADMAGFIELDCONV_ID')
        r, dialogbox = GradMagFieldConversionDlgBox.new(dlg_label,
                                                        self,
                                                        prosptechused,
                                                        prosptechsim,
                                                        apod,
                                                        downsensoraltused,
                                                        upsensoraltused,
                                                        downsensoraltsim,
                                                        upsensoraltsim,
                                                        inclineangle,
                                                        alphaangle
                                                        )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

            # update config file
            self.configset.set('PROCESSING',
                               'apodisationfactor',
                               str(dialogbox.apod)
                               )
            self.configset.set('PROCESSING',
                               'prosptech',
                               dialogbox.prosptechused
                               )
            self.configset.set('PROCESSING',
                               'downsensoraltitude',
                               str(dialogbox.downsensoraltused)
                               )
            self.configset.set('PROCESSING',
                               'upsensoraltitude',
                               str(dialogbox.upsensoraltused)
                               )
            self.configset.set('PROCESSING',
                               'maginclineangle',
                               str(dialogbox.inclineangle)
                               )
            self.configset.set('PROCESSING',
                               'magalphaangle',
                               str(dialogbox.alphaangle)
                               )

    def eulerDeconvolution(self):
        ''' Euler deconvolution dialog box. '''

        apod = self.configset.getint('PROCESSING',
                                     'apodisationfactor'
                                     )
        #nflag = self.configset.getboolean('PROCESSING', 'eulerstructindexflag')
        structind = self.configset.getint('PROCESSING',
                                          'eulerstructindexvalue'
                                          )

        dlg_label = self.asciiset.getStringValue('EULERDECONV_ID')
        r, dialogbox = EulerDeconvolutionDlgBox.new(dlg_label,
                                                    self,
                                                    apod,
                                                    structind
                                                    )

        if r == QDialog.Accepted:
            self.dataset = dialogbox.dataset
            self.updateDisplay()

                            # updates config file
##            self.configset.set('PROCESSING', 'apodisationfactor', str(dialogbox.apod))
##            self.configset.set('PROCESSING', 'eulerstructindexflag', str(dialogbox.inclineangle))
##            self.configset.set('PROCESSING', 'eulerstructindexvalue', str(dialogbox.alphaangle))

    def loadGCPs(self):
        ''' Load dataset Ground Control Points. '''

        title = "Load " + self.title + "'s GCPs"
        directory = self.configset.get('DIRECTORIES',
                                       'opengeopossetfiledir'
                                       )
        filters = ('ASCII file (*.csv *.txt *.dat)'
                   ';;'
                   'shapefile (*.shp)')

        filename, _ = QFileDialog.getOpenFileName(None,
                                                  'Open file',
                                                  directory,
                                                  filters)

        # Wait cursor
        initcursor = self.wid.cursor()
        self.wid.setCursor(Qt.WaitCursor)

        if filename:
            # Conversion to list
            if isinstance(filename, str):
                filename = [filename]

            dirname = os.path.dirname(os.path.realpath(filename[0]))
            self.configset.set('DIRECTORIES',
                               'opengeopossetfiledir',
                               dirname
                               )

            refsystem = self.configset.get('GEOPOSITIONING',
                                           'refsystem'
                                           )
            utm_letter = self.configset.get('GEOPOSITIONING',
                                            'utm_letter'
                                            )
            utm_number = self.configset.getint('GEOPOSITIONING',
                                               'utm_number'
                                               )

            # Choosing file format (ASCII/Shape
            file_ext = os.path.splitext(filename[0])[1]
            filetype = gpos_format_chooser[file_ext]

            try:
                dlg_label = "Open Geographic Positions Set From " + filetype
                r, openfiles = OpenGeopossetDlgBox.new(dlg_label,
                                                       filetype,
                                                       filename,
                                                       refsystem,
                                                       utm_number,
                                                       utm_letter,
                                                       self
                                                       )

                if r == QDialog.Accepted:
                    geoposset = openfiles.geoposset
                    gset_idx = str(self.parent.currentgeopossetwindowsindex)
                    title = "GeoPosSet" + gset_idx
                    self.parent.currentgeopossetwindowsindex += 1
                    window = GeopossetWindow.new(self,
                                                 title,
                                                 geoposset,
                                                 None)
                    self.parent.geopossetwindowslist.append(window)
                    #self.geopossetwindowslist.append(window)
                    print(self.geopossetwindowslist)
                    window.view()

                    # update config file
                    self.configset.set('GEOPOSITIONING',
                                       'refsystem',
                                       str(openfiles.geoposset.refsystem)
                                       )
                    self.configset.set('GEOPOSITIONING',
                                       'utm_letter',
                                       str(openfiles.geoposset.utm_letter)
                                       )
                    self.configset.set('GEOPOSITIONING',
                                       'utm_number',
                                       str(openfiles.geoposset.utm_number)
                                       )

                    # update all dataset windows's menu
                    for datasetwindow in self.parent.datasetwindowslist:
                        datasetwindow.menubar.update()

            except:
                QErrorMessage()

        # Init cursor
        self.wid.setCursor(initcursor)

    def georeferenceDataSet(self):
        ''' Georeferences the data set. '''

        title = "Georeferencing " + self.title
        r, dlgbox = GeorefDlgBox.new(title,
                                     self,
                                     self.geopossetwindowslist
                                     )

        if r == QDialog.Accepted:
            self.dataset.setgeoref(dlgbox.geoposset.refsystem,
                                   dlgbox.selectedpoints_list,
                                   dlgbox.geoposset.utm_letter,
                                   dlgbox.geoposset.utm_number
                                   )
            self.geopossetwindowslist[dlgbox.geopossetindex].geoposset = dlgbox.geoposset
            self.menubar.update()       # updates bar menu with enabled or disabled items

    def isGeoreferencingAvailable(self):
        ''' True if a georeferencing system is available. '''

        return len(self.geopossetwindowslist) > 0

    def isDatasetGeoreferenced(self):
        ''' True if dataset is georeferenced. '''

        return self.dataset.georef.active

    def settings(self):
        ''' Edit GUI Settings. '''

        r, guisettings = GuiSettingsDlgBox.new("User Interface Settings",
                                               self)

        if r == QDialog.Accepted:
            # update config file
            self.configset.set('MISC',
                               'realtimeupdateflag',
                               str(guisettings.realtimeupdateflag)
                               )
            self.configset.set('MISC',
                               'changeresolutionflag',
                               str(guisettings.changeresolutionflag)
                               )

    def language(self):
        ''' Edit language Settings. '''

        r, language = LanguageDlgBox.new("Language Settings",
                                         self)

        if r == QDialog.Accepted:
            # new ascii set language and font
            self.asciiset = language.asciiset
            # update configuration file
            self.configset.set('ASCII',
                               'language',
                               self.asciiset.lnglist[self.asciiset.lngindex].name
                               )
            # update menu bar with new language or font
            self.menubar.update()

            # update all dataset windows
            for datasetwindow in self.datasetwindowslist:
                datasetwindow.menubar.update()

            # update all geoposset windows
            for geopossetwindow in self.geopossetwindowslist:
                geopossetwindow.menubar.update()

    def font(self):
        ''' Edit Font Settings. '''

        qfontdlg = QFontDialog(self.asciiset.font, self.wid)
        qfontdlg.setFont(self.asciiset.font)
        qfontdlg.setGeometry(self.geometry().left(),
                             self.geometry().top(),
                             qfontdlg.geometry().width(),
                             qfontdlg.geometry().height()
                             )

        qfontdlg.show()
        qfontdlg.exec()
        font = qfontdlg.selectedFont()

        if qfontdlg.result() == QDialog.Accepted:
            self.asciiset.font = font
            self.asciiset.fontname = font.family()
            self.asciiset.fontsize = font.pointSize()
            self.wid.setFont(font)  # set font before updating menu bar

            # update configuration file
            self.configset.set('ASCII',
                               'fontname',
                               self.asciiset.fontname
                               )
            self.configset.set('ASCII',
                               'fontsize',
                               str(self.asciiset.fontsize)
                               )
            # update menu bar with new language or font
            self.menubar.update()
            # updates all data set windows
            self.fillingwindow()

            # update all dataset windows
            for datasetwindow in self.datasetwindowslist:
                datasetwindow.menubar.update()

            # update all geoposset windows
            for geopossetwindow in self.geopossetwindowslist:
                geopossetwindow.menubar.update()
