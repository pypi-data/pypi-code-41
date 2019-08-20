# -*- coding: utf-8 -*-
'''
    wumappy.gui.opendatasetdlgbox
    -----------------------------

    Opening dataset dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import os
import numpy as np

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
#from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox
#import inspect

from geophpy.dataset import (DataSet,
    festooncorrelation_getlist,
    getlinesfrom_file,
    fileformat_getlist,
    griddinginterpolation_getlist,
    colormap_getlist,
    colormap_icon_getlist,
    colormap_icon_getpath)

import geophpy.misc.utils as geoutils

#---------------------------------------------------------------------------#
# Opening Dataset Dialog Box Object                                         #
#---------------------------------------------------------------------------#
class OpenDatasetDlgBox(object):
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title,
            # File -------------------------------
            filenames,
            parent=None,
            xcolnum=1,
            ycolnum=2,
            zcolnum=3,
            delimiter='\t',
            fileformat='ascii',
            delimitersasuniqueflag=True,
            skiprows=1,
            fieldsrow=0,
            # Gridding ---------------------------
            interpgridding='none',
            stepxgridding=None,
            stepygridding=None,
            autogriddingflag=True,
            dispdatapointflag=False,
            # Display settigns -------------------
            colormap="Greys",
            reverseflag=False,
            coloredhistoflag=True,
            thresholdflag=False,
            minmaxreplacedflag=False,
            nanreplacedflag=False,
            medianreplacedflag=False,
            # Filtering --------------------------
            zeromeanfiltflag=False,
            zeromeanfiltvar='median',
            festoonfiltflag=False,
            festoonfiltmethod='Crosscorr',
            festoonfiltshift=0,
            festoonfiltcorrmin=0.4,
            festoonfiltuniformshift=False,
            medianfiltflag=False,
            nxsize=3,
            nysize=3,
            percent=0,
            gap=0):
        '''
        '''
      
        # Configuration
        window = cls()
        window.title = title
        window.parent = parent
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon

        # Dataset
        window.valfiltflag = False
        window.dataset = None
        window.zmin = None
        window.zmax = None
        window.xmin = None
        window.xmax = None
        window.ymin = None
        window.ymax = None

        # Ascii file
        window.filenames = filenames
        window.delimiter = delimiter
        window.fileformat = fileformat
        window.delimitersasuniqueflag = delimitersasuniqueflag

        window.x_colnum = xcolnum
        window.y_colnum = ycolnum
        window.z_colnum = zcolnum
        window.skiprows = skiprows
        window.fieldsrow = fieldsrow

        # Gridding
        window.stepxgridding = stepxgridding
        window.stepygridding = stepygridding
        window.interpgridding = interpgridding
        window.imsize = '0'
        window.imsizeunit = 'o'
        window.stepxgridding_firstime = True
        window.stepygridding_firstime = True
        window.cache_stepygridding = 0.25
        
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.autogriddingflag = autogriddingflag
        window.dispdatapointflag = dispdatapointflag

        # Filters
        window.zeromeanfiltflag = zeromeanfiltflag
        window.zeromeanfiltvar = zeromeanfiltvar

        window.festoonfiltflag = festoonfiltflag
        window.festoonfiltmethod = festoonfiltmethod
        window.festoonfiltshift = festoonfiltshift
        window.festoonfiltcorrmin = festoonfiltcorrmin
        window.festoonfiltuniformshift = festoonfiltuniformshift

        window.medianfiltflag = medianfiltflag
        window.nxsize = nxsize
        window.nysize = nysize
        window.percent = percent
        window.gap = gap

        # Display settings
        window.colormap = colormap
        window.reverseflag = reverseflag
        window.colorbarlogscaleflag = False
        window.automaticrangeflag = True

        window.thresholdflag = thresholdflag
        window.minmaxreplacedflag = minmaxreplacedflag
        window.nanreplacedflag = nanreplacedflag
        window.medianreplacedflag = medianreplacedflag

        # Histogram
        window.histofig = None
        window.coloredhistoflag = coloredhistoflag
        window.colorbardisplayflag = True
        
        # Data map
        window.cartofig = None
                
        # GROUPBOX must be defined first
        window.items_list = [
            # TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN,[GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
            # GroupBox ---------------------------------------------------------
            ['GroupBox', 'FILEFORMATOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
            ['GroupBox', 'DISPOPT_ID', 0, 1, False, None, None, 2, 0, 1, 1, 0],
            ['GroupBox', 'GRIDINGOPT_ID', 0, 2, False, None, None, 1, 0, 1, 1, 0],
            #['GroupBox', 'DISPOPT_ID', 1, 0, False, None, None, 2, 0, 1, 1, 0],
            ['GroupBox', 'FILTOPT_ID', 0, 3, False, None, None, 3, 0, 1, 1, 0],
            ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 4, 1, 1, 3, 2],
            ['GroupBox', 'RENDERING_ID', 0, 1, False, None, None, 5, 0, 1, 1, 1],
            ['GroupBox', 'HISTOGRAM_ID', 1, 2, False, None, None, 6, 0, 1, 1, 1],
            # File format options TAB ------------------------------------------
            ['Label', 'FILEFORMAT_ID', 0, 0, False, None, None, 0],
            ['ComboBox', '', 0, 1, True, window.FileFormatInit, window.FileFormatUpdate, 0],
            ['Label', 'DELIMITER_ID', 1, 0, False, None, None, 0],
            ['ComboBox', '', 1, 1, True, window.DelimiterInit, window.DelimiterUpdate, 0],
            ['Label', 'SKIPROWS_ID', 0, 2, False, None, None, 0],
            ['SpinBox', '', 0, 3, True, window.SkipRowsNumberInit, window.SkipRowsNumberUpdate, 0],
            ['Label', 'FIELDSROW_ID', 1, 2, False, window.FieldsRowLabelInit, None, 0],
            ['SpinBox', '', 1, 3, True, window.FieldsRowIndexInit, window.FieldsRowIndexUpdate, 0],
            ['CheckBox', 'DELIMITERSASUNIQUEFLAG_ID', 2, 0, False, window.SeveralsDelimitersAsUniqueInit, window.SeveralsDelimitersAsUniqueUpdate, 0, 1, 2],
##            ['Label', '', 3, 0, False, None, None, 0],
            ['Label', 'XCOLNUM_ID', 4, 0, False, None, None, 0],
            ['SpinBox', '', 5, 0, True, window.XColumnInit, window.XColumnUpdate, 0],
            ['Label', 'YCOLNUM_ID', 4, 1, False, None, None, 0],
            ['SpinBox', '', 5, 1, True, window.YColumnInit, window.YColumnUpdate, 0],
            ['Label', 'ZCOLNUM_ID', 4, 2, False, None, None, 0],
            ['SpinBox', '', 5, 2, True, window.ZColumnInit, window.ZColumnUpdate, 0],
            ['Label', 'FILEPREVIEW_ID', 7, 0, False, None, None, 0],
            ['Table', '', 8, 0, False, window.FilePreviewInit, None, 0, 1, 0],
            ['Label', '', 9, 0, False, None, None, 0],
            # Display options TAB ----------------------------------------------
            ['Label', 'COLORMAP_ID', 0, 0, False, None, None, 1],   
            ['ComboBox', '', 0, 1, True, window.ColorMapInit, window.ColorMapUpdate, 1, 1, 2], 
            ['CheckBox', 'REVERSEFLAG_ID', 1, 1, True, window.ColorMapReverseInit, window.ColorMapReverseUpdate, 1],  
            ['CheckBox', 'COLORBARLOGSCALEFLAG_ID', 1, 2, True, window.ColorBarLogScaleInit, window.ColorBarLogScaleUpdate, 1],   
            #['Label', '', 2, 0, False, None, None, 1],
            ['Label', 'MINIMALVALUE_ID', 3, 0, False, None, None, 1],  
            ['Slider', '', 3, 1, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 1, 1 ,2],  
            ['SpinBox', '', 3, 3, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 1],    
            ['Label', 'MAXIMALVALUE_ID', 4, 0, False, None, None, 1],
            ['Slider', '', 4, 1, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 1, 1 ,2], 
            ['SpinBox', '', 4, 3, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 1],    
##            ['Label', '', 5, 0, False, None, None, 1],
            ['Label', 'HISTOGRAM_ID', 5, 0, False, None, None, 1],
            ['CheckBox', 'COLORHIST_ID', 5, 1, True, window.ColoredHistInit, window.ColoredHistUpdate, 1],
            ['CheckBox', 'COLORBARDISPLAYFLAG_ID', 5, 2, True, window.ColorBarDisplayInit, window.ColorBarDisplayUpdate, 1],
##            #['Image', '', 9, 0, False, window.HistoImageInit, None, 1, 1, 4],
##            ['Graphic', '', 9, 0, False, window.HistoImageInit, None, 1, 1, 4],
##            ['Label', '', 11, 0, False, None, None, 1],
##            #['CheckBox', 'PEAKFILT_ID', 8, 0, True, window.PeakFiltInit, window.PeakFiltUpdate, 1],
##            #['Label', 'LABEL_NANREPLACEDFLAG_ID', 9, 0, False, None, None, 1],
##            #['CheckBox', 'MINMAXREPLACEDFLAG_ID', 9, 1, True, window.MinMaxReplacedValuesInit, window.MinMaxReplacedValuesUpdate, 1],  
##            #['CheckBox', 'NANREPLACEDFLAG_ID', 10, 1, True, window.NanReplacedValuesInit, window.NanReplacedValuesUpdate, 1],  
##            #['CheckBox', 'MEDIANREPLACEDFLAG_ID', 11, 1, True, window.MedianReplacedValuesInit, window.MedianReplacedValuesUpdate, 1],  
##            ['Label', '', 12, 0, False, None, None, 1],
            # Gridding options TAB ---------------------------------------------
            ['Label', 'STEPXGRIDDING_ID', 0, 0, False, window.GriddingXStepLabelInit, None, 2],
            ['DoubleSpinBox', '', 0, 1, True, window.GriddingXStepInit, window.GriddingXStepUpdate, 2],
            ['Label', 'STEPYGRIDDING_ID', 1, 0, False, window.GriddingYStepLabelInit, None, 2],
            ['DoubleSpinBox', '', 1, 1, True, window.GriddingYStepInit, window.GriddingYStepUpdate, 2],
            ['Label', '', 2, 1, False, window.GriddingSizeInit, None, 2],
            ['CheckBox', 'SQUARE_PIXEL', 3, 1, True, window.GriddingSquareInit, window.GriddingSquareUpdate, 2],
            ['CheckBox', 'AUTOGRIDDINGFLAG_ID', 4, 1, True, window.GriddingAutoInit, window.GriddingAutoUpdate, 2],
            ['CheckBox', 'DATAPOINTSFLAG_ID', 5, 1, True, window.DataPointsDisplayInit, window.DataPointsDisplayUpdate, 2],
            #['CheckBox', 'DISPGRIDDINGFLAG_ID', 5, 1, True, window.GriddingPointsDisplayInit, window.GriddingPointsDisplayUpdate, 2],
##            ['Label', '', 6, 0, False, None, None, 2],
            ['Label', 'INTERPOLATION_ID', 7, 0, False, None, None, 2],
            ['ComboBox', '', 7, 1, True, window.GriddingInterpolationInit, window.GriddingInterpolationUpdate, 2],
##            ['Label', '', 8, 0, False, None, None, 2],
##            ['Label', '', 9, 0, False, None, None, 2],
##            ['Label', '', 10, 0, False, None, None, 2],
##            ['Label', '', 11, 0, False, None, None, 2],
##            ['Label', '', 12, 0, False, None, None, 2],
##            ['Label', '', 13, 0, False, None, None, 2],
            # Filters options TAB ----------------------------------------------
            # Median filter
            ['CheckBox', 'MEDIANFILT_ID', 0, 0, True, window.MedianFiltInit, window.MedianFiltUpdate, 3],
            ['Label', 'FILTERNXSIZE_ID', 1, 0, False, window.NxSizeLabelInit, None, 3],
            ['SpinBox', '', 1, 1, True, window.NxSizeInit, window.NxSizeUpdate, 3],
            ['Label', 'FILTERNYSIZE_ID', 2, 0, False, window.NySizeLabelInit, None, 3],
            ['SpinBox', '', 2, 1, True, window.NySizeInit, window.NySizeUpdate, 3],
            ['Label', 'MEDIANFILTERPERCENT_ID', 3, 0, False, window.PercentLabelInit, None, 3],
            ['SpinBox', '', 3, 1, True, window.PercentInit, window.PercentUpdate, 3],
            ['Label', 'MEDIANFILTERGAP_ID', 4, 0, False, window.GapLabelInit, None, 3],
            ['SpinBox', '', 4, 1, True, window.GapInit, window.GapUpdate, 3],
            ['Label', '', 5, 0, False, None, None, 3],
            # Zero Mean filter
            ['Radio', 'ZEROMEAN_ID', 7, 0, True, window.ZeroMeanInit, window.ZeroMeanMedianUpdate, 3],
            ['Radio', 'ZEROMEDIAN_ID', 7, 1, True, window.ZeroMedianInit, window.ZeroMeanMedianUpdate, 3],
            ['CheckBox', 'ZEROMEANFILT_ID', 6, 0, True, window.ZeroMeanFiltInit, window.ZeroMeanFiltUpdate, 3],
            ['Label', '', 8, 0, False, None, None, 3],
            # Festoon filter
            ['CheckBox', 'FESTOONFILT_ID', 9, 0, True, window.FestoonFiltInit, window.FestoonFiltUpdate, 3],
            ['Label', 'FESTOONFILTMETHOD_ID', 10, 0, False, window.FestoonMethodLabelInit, None, 3],
            ['ComboBox', '', 10, 1, True, window.FestoonMethodInit, window.FestoonMethodUpdate, 3],
            ['CheckBox', 'FESTOONFILTSHIFT_ID', 11, 0, True, window.FestoonUniformShiftInit, window.FestoonUniformShiftUpdate, 3],
            #['Label', 'FESTOONFILTSHIFT_ID', 9, 0, False, window.FestoonShiftLabelInit, None, 3],
            ['SpinBox', '', 11, 1, True, window.FestoonShiftInit, window.FestoonShiftUpdate, 3],
            ['Label', 'FESTOONFILTMINCORR_ID', 12, 0, False, window.FestoonCorrMinLabelInit, None, 3],
            ['DoubleSpinBox', '', 12, 1, True, window.FestoonCorrMinInit, window.FestoonCorrMinUpdate, 3],
#            ['Label', '', 13, 0, False, None, None, 3],
            # Tthresholding
            ['CheckBox', 'THRESHOLD_ID', 14, 0, True, window.ThresholdInit, window.ThresholdUpdate, 3],
            ['Label', 'LABEL_NANREPLACEDFLAG_ID', 15, 0, False, None, None, 3],
            ['CheckBox', 'MINMAXREPLACEDFLAG_ID', 15, 1, True, window.MinMaxReplacedValuesInit, window.MinMaxReplacedValuesUpdate, 3],
            ['CheckBox', 'NANREPLACEDFLAG_ID', 16, 1, True, window.NanReplacedValuesInit, window.NanReplacedValuesUpdate, 3],
            ['CheckBox', 'MEDIANREPLACEDFLAG_ID', 17, 1, True, window.MedianReplacedValuesInit, window.MedianReplacedValuesUpdate, 3],
##            ['Label', '', 18, 0, False, None, None, 3],
##            #['Label', '', 19, 0, False, None, None, 3],
##            #['Label', '', 20, 0, False, None, None, 3],
            # Cancel, Update, Valid --------------------------------------------
            ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 4],
            ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 4],   \
            ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 4],   \
            # Histogram TAB ----------------------------------------------------
            ['Graphic', '', 0, 0, False, window.HistoImageInit, None, 6],   
            ## Rendering TAB ---------------------------------------------------
            ['Graphic', '', 1, 0, False, window.CartoImageInit, None, 5]
            ]
        
        dlgbox = CartoDlgBox("Open dataset - " + window.filenames[0], window, window.items_list)  # self.wid is built in CartoDlgBox
        ##dlgbox.resize(dlgbox.minimumSizeHint())
        dlgbox.exec()

        return dlgbox.result(), window

    #--------------------------------------------------------------------------#
    # File format options TAB                                                  #
    #--------------------------------------------------------------------------#
    def DisplayUpdate(self):
        ''' Updates the GUI at the change of a filter's parameter. '''
        
        # Auto Update
        if self.realtimeupdateflag:                       
            self.CartoImageUpdate()
            self.HistoImageUpdate()

        # Manual Update
        else:
            self.CartoImageId.setEnabled(False)  # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)  # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)  # enables the display update button


    # File format ##############################################################
    def FileNamesInit(self, id=None):
        filenames=""
        n = len(self.filenames)
        for i in range(n):
            filenames = filenames + self.filenames[i]
            if (i<(n-1)):
                filenames = filenames + '\n'
        id.setText(filenames)
        return id

    def FileFormatInit(self, id=None):
        formatlist = fileformat_getlist()
        id.addItems(formatlist)
        index = id.findText(self.fileformat)
        id.setCurrentIndex(index)
        self.FileFormatId = id
        return id

    def FileFormatUpdate(self):
        self.fileformat = self.FileFormatId.currentText()

        self.DisplayUpdate()
        self.automaticrangeflag = True

    def DelimiterInit(self, id=None):
        id.addItems(['.', ',', ';', 'space', 'tab', '|', '-'])
        if (self.delimiter == ' '):
            delimiter = 'space'
        elif (self.delimiter == '\t'):
            delimiter = 'tab'
        else:
            delimiter = self.delimiter
        index = id.findText(delimiter)
        id.setCurrentIndex(index)
        self.DelimiterId = id
        return id

    def DelimiterUpdate(self):
        self.delimiter = self.DelimiterId.currentText()
        if (self.delimiter == 'space'):
            self.delimiter = ' '
        elif (self.delimiter == 'tab'):
            self.delimiter = '\t'

        self.DisplayUpdate()
        self.automaticrangeflag = True
        self.FilePreviewUpdate()

    def SeveralsDelimitersAsUniqueInit(self, id=None):
        id.setChecked(self.delimitersasuniqueflag)
        self.SeveralsDelimiterAsUniqueId = id
        return id

    def SeveralsDelimitersAsUniqueUpdate(self):
        self.delimitersasuniqueflag = self.SeveralsDelimiterAsUniqueId.isChecked()
        self.FilePreviewUpdate()
        
        self.DisplayUpdate()

    def SkipRowsNumberInit(self, id=None):
        id.setValue(self.skiprows)
        self.SkipRowsNumberId = id

        return id

    def SkipRowsNumberUpdate(self):
        self.skiprows = self.SkipRowsNumberId.value()

        # Enabling/Disabling Fields Row if header
        self.FieldsRowIndexId.setEnabled(self.skiprows!=0)
        self.FieldsRowLabelId.setEnabled(self.skiprows!=0 and self.fieldsrow!=0)

        # Decreasing Fields Row if necessary
        if self.fieldsrow>self.skiprows:
            self.FieldsRowIndexId.setValue(self.skiprows)
            self.FieldsRowIndexUpdate()

        self.FilePreviewUpdate()

        self.DisplayUpdate()
        self.automaticrangeflag = True

    def FieldsRowLabelInit(self, id=None):
        id.setEnabled(self.skiprows!=0)
        self.FieldsRowLabelId = id
        return id

    def FieldsRowIndexInit(self, id=None):
        # Enabling/Disabling if header
        id.setValue(self.fieldsrow)
        id.setMinimum(0)
        id.setEnabled(self.skiprows!=0)
        self.FieldsRowLabelId.setEnabled(self.fieldsrow!=0)

        self.FieldsRowIndexId = id
        return id    

    def FieldsRowIndexUpdate(self):
        self.fieldsrow = self.FieldsRowIndexId.value()
        self.FieldsRowLabelId.setEnabled(self.fieldsrow!=0)

        # Increasing Skip Rows if necessary
        if self.fieldsrow>self.skiprows:
            self.SkipRowsNumberId.setValue(self.fieldsrow)
            self.SkipRowsNumberUpdate()

        self.FilePreviewUpdate()
        self.DisplayUpdate()
        self.automaticrangeflag = True
  
    def XColumnInit(self, id=None):
        id.setValue(self.x_colnum)
        self.XColumnId = id
        return id
    
    def XColumnUpdate(self):
        self.x_colnum = self.XColumnId.value()
        self.FilePreviewUpdate()
        
        self.DisplayUpdate()
        self.automaticrangeflag = True
    
    def YColumnInit(self, id=None):
        id.setValue(self.y_colnum)
        self.YColumnId = id
        return id
    
    def YColumnUpdate(self):
        self.y_colnum = self.YColumnId.value()
        self.FilePreviewUpdate()
        
        self.DisplayUpdate()
        self.automaticrangeflag = True
    
    def ZColumnInit(self, id=None):
        id.setValue(self.z_colnum)
        self.ZColumnId = id
        return id

    def ZColumnUpdate(self):
        self.z_colnum = self.ZColumnId.value()
        self.automaticrangeflag = True
        self.FilePreviewUpdate()
        
        self.DisplayUpdate()

    def FilePreviewInit(self, id=None):     
        self.FilePreviewId = id
        self.FilePreviewUpdate()
        return id

    # File preview #############################################################
    def FilePreviewUpdate(self):
        # Text colors
        steelblueColor = QColor(70, 130, 180)
        grayColor = QColor(169, 169, 169)

        # Number of row for preview
        rowsnb = 10
        if self.skiprows > rowsnb:
            rowsnb = self.skiprows + 1

        colsnb, rows = getlinesfrom_file(self.filenames[0],
                                         fileformat=self.fileformat,
                                         delimiter=self.delimiter,
                                         skipinitialspace=self.delimitersasuniqueflag,
                                         skiprowsnb=0,
                                         rowsnb=rowsnb)

        # Initializing table
        self.FilePreviewId.clear()
        
        self.FilePreviewId.setRowCount(rowsnb)
        self.FilePreviewId.setColumnCount(colsnb)

        idx = self.XColumnId.value()-1
        idy = self.YColumnId.value()-1
        idz = self.ZColumnId.value()-1
        
        # Updating table content
        for line, row in enumerate(rows):
            for col in range(colsnb):
                item = QTableWidgetItem(row[col])
                self.FilePreviewId.setItem(line, col, item)
                self.FilePreviewId.item(line ,col).setFlags(Qt.ItemIsEnabled)  # Read Only

                # File  header lines (in gray)
                if self.skiprows>0:
                    color = QBrush(grayColor)
                    if line in range(self.skiprows) and col in range(colsnb):
                        self.FilePreviewId.item(line, col).setForeground(color)

                # Unused column  (in gray)
                if col not in [idx, idy, idz]:
                    color = QBrush(grayColor)
                    self.FilePreviewId.item(line, col).setForeground(color)

        # Updating Fields headers    
        if self.fieldsrow!=0:
            # Fields row in blue
            color = QBrush(steelblueColor)
            labels = rows[self.fieldsrow-1]
            self.FilePreviewId.setHorizontalHeaderLabels(labels)
            for col in [idx, idy, idz]:
                # Testing fot None prevents error
                ## if a bad delimiter is selected
                item = self.FilePreviewId.item(self.fieldsrow-1,col)
                if item is not None:
                    item.setForeground(color)
                    
                # Table Header in blue
                item = self.FilePreviewId.horizontalHeaderItem(col)
                if item is not None:
                    item.setForeground(color)

        else:
            color = QBrush(steelblueColor)
            
            LabelX = 'X'
            LabelY = 'Y'
            LabelZ = 'Z'

            itemX = QTableWidgetItem(LabelX)
            itemY = QTableWidgetItem(LabelY)
            itemZ = QTableWidgetItem(LabelZ)

            self.FilePreviewId.setHorizontalHeaderItem(idx, itemX)
            self.FilePreviewId.setHorizontalHeaderItem(idy, itemY)
            self.FilePreviewId.setHorizontalHeaderItem(idz, itemZ)
            
            # Table Header in blue
            for col in [idx, idy, idz]:
                # Testing fot None prevents error
                ## if a bad delimiter is selected
                item = self.FilePreviewId.horizontalHeaderItem(col)
                if item is not None:
                    item.setForeground(color)

        # Updating Vertical Headers
        if self.skiprows>0:
            color = QBrush(grayColor)
            # Headers
            for line in range(self.skiprows):
                itemHd = QTableWidgetItem(''.join(['HD', str(line+1)]))
                self.FilePreviewId.setVerticalHeaderItem(line, itemHd)

            # Field
            if self.fieldsrow!=0:
                color = QBrush(steelblueColor)
                self.FilePreviewId.verticalHeaderItem(self.fieldsrow-1).setForeground(color)

    #--------------------------------------------------------------------------#
    # Gridding options TAB                                                     #
    #--------------------------------------------------------------------------#
    def GriddingSquareInit(self, id=None):
        if id is not None:
            id.setChecked(False)
            self.square_pixelId = id
            self.GriddingYStepId.setEnabled(not id.isChecked() and not self.autogriddingflag)
        return id

    def GriddingSquareUpdate(self):
        if self.square_pixelId.isChecked():
          self.cache_stepygridding = self.GriddingYStepId.value()
          self.stepygridding = self.GriddingXStepId.value()

        else:
          self.stepygridding = self.cache_stepygridding

        self.GriddingYStepLabelId.setEnabled(not self.square_pixelId.isChecked())
        self.GriddingYStepId.setEnabled(not self.square_pixelId.isChecked())

        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate() 

    def GriddingAutoInit(self, id=None):
        if id is not None:
            id.setChecked(self.autogriddingflag)
            if (self.autogriddingflag == True):
               self.stepxgridding = None
               self.stepygridding = None
               Enabled = False
            else:
               Enabled = True
        self.GriddingAutoId = id
        return id

    def GriddingAutoUpdate(self):
        self.stepxgridding = None
        self.stepygridding = None
        self.autogriddingflag = self.GriddingAutoId.isChecked()

        # Auto-gridding
        if self.autogriddingflag:
           self.stepxgridding = None
           self.stepygridding = None
           Enabled = False

        # Manual gridding
        else:
           Enabled = True

        self.GriddingXStepLabelId.setEnabled(Enabled)
        self.GriddingXStepId.setEnabled(Enabled)
        self.GriddingYStepLabelId.setEnabled(Enabled)
        self.square_pixelId.setEnabled(Enabled) 
        self.square_pixelId.setChecked(False)
        self.GriddingYStepId.setEnabled(Enabled)

        self.GriddingXStepUpdate()
        self.GriddingYStepUpdate()
        self.GridSizeEstimationUpdate()
        self.GriddingSizeUpdate()
        self.DisplayUpdate()

    def DataPointsDisplayInit(self, id=None):
        self.DataPointsDisplayId = id
        if id is not None:
            id.setChecked(self.dispdatapointflag)
        return id

    def DataPointsDisplayUpdate(self):
        self.dispdatapointflag = self.DataPointsDisplayId.isChecked()
        self.DisplayUpdate()

    def GriddingXStepLabelInit(self, id=None):
        id.setEnabled(not self.autogriddingflag)
        self.GriddingXStepLabelId = id
        return id

    def GriddingXStepInit(self, id=None):
        id.setSingleStep(0.25)
        id.setEnabled(not self.autogriddingflag)
        self.GriddingXStepId = id

        try:
            x = self.dataset.get_xvalues()
            xmin = x.min()
            xmax = x.max()
            stepmax = np.abs(xmax-xmin)
            self.GriddingXStepId.setMaximum(stepmax)
        except:
            self.GriddingXStepId.setMaximum(np.inf)

        return id

    def GriddingXStepUpdate(self):
        if self.square_pixelId.isChecked():
            self.stepygridding = self.GriddingXStepId.value()
        self.stepxgridding = self.GriddingXStepId.value()
        if not self.stepxgridding_firstime:
            self.DisplayUpdate()

        else:
            self.stepxgridding_firstime = False

        self.GridSizeEstimationUpdate()
        self.GriddingSizeUpdate()

    def GriddingYStepLabelInit(self, id=None):
        id.setEnabled(not self.autogriddingflag)
        self.GriddingYStepLabelId = id
        return id
    
    def GriddingYStepInit(self, id=None):
        id.setSingleStep(0.25)
        id.setEnabled(not self.autogriddingflag)
        self.GriddingYStepId = id

        try:
            y = self.dataset.get_yvalues
            ymin = y.min()
            ymax = y.max()
            stepmax = np.abs(ymax-ymin)
            self.GriddingYStepId.setMaximum(stepmax)
        except:
            self.GriddingYStepId.setMaximum(np.inf)

        return id

    def GriddingYStepUpdate(self):
        self.stepygridding = self.GriddingYStepId.value()
        if (self.stepygridding_firstime == False):
            self.DisplayUpdate()
        else:
            self.stepygridding_firstime = False

        self.GridSizeEstimationUpdate()
        self.GriddingSizeUpdate()

    def GridSizeEstimationUpdate(self):
        bytesnb = getattr(self, 'bytesnb', 8)
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        if self.stepxgridding is not None and self.stepygridding is not None:
            x_step = self.stepxgridding
            y_step = self.stepygridding
        elif self.dataset is not None:
            x_step = self.dataset.get_median_xstep()
            y_step = self.dataset.get_median_ystep()
        else:
            x_step = 1
            y_step = 1

        if xmin is not None and xmax is not None and ymin is not None and ymax is not None:
            nx = int(np.around((xmax - xmin)/x_step) + 1)
            ny = int(np.around((ymax - ymin)/y_step) + 1)
        else:
            nx = 0
            ny = 0

        self.rowsnb = ny
        self.colsnb = nx
        imsize = nx*ny*bytesnb
        decim = 1

        if np.floor(imsize/1e9)>=1:
            imsize = np.round(imsize/1e9,decimals=decim)
            unit = 'Go'

        elif np.floor(imsize/1e6)>=1:
            imsize = np.round(imsize/1e6,decimals=decim)
            unit = 'Mo'

        elif np.floor(imsize/1e3)>=1:
            imsize = np.round(imsize/1e3,decimals=decim)
            unit = 'ko'

        else:
            imsize = np.round(imsize,decimals=decim)
            unit = 'o'

        self.imsize = imsize
        self.imsizeunit = unit

    def GriddingSizeInit(self, id=None):
        self.GriddingSizeId = id
        return id

    def GriddingSizeUpdate(self):
        ny, nx, imsize, imsizeunit = self.rowsnb, self.colsnb, self.imsize, self.imsizeunit

        factor_selector = {"o": 1,
                           "ko": 1e3,
                           "Mo": 1e6,
                           "Go": 1e9
                           }

        factor = factor_selector[imsizeunit]

        if self.imsize*factor>=.7e9:
            text = "%s (%s * %s) [~%s %s] MIGHT TOO LARGE TO BE COMPUTED"%(self.asciiset.getStringValue('SIZEGRIDDING_ID'), ny, nx, imsize, imsizeunit)

        else:
            text = "%s (%s * %s) [~%s %s]"%(self.asciiset.getStringValue('SIZEGRIDDING_ID'), ny, nx, imsize, imsizeunit)

        self.GriddingSizeId.setText(text)

    def GriddingInterpolationInit(self, id=None):
                                                                    # building of the "interpolation" field to select in a list
        interpolation_list = griddinginterpolation_getlist()
        try:
            interpolation_index = interpolation_list.index(self.interpgridding)
        except:
            interpolation_index = 0

        if id is not None:
            id.addItems(interpolation_list)
            id.setCurrentIndex(interpolation_index)
        self.GriddingInterpolationId = id
        return id

    def GriddingInterpolationUpdate(self):        
        self.interpgridding = self.GriddingInterpolationId.currentText()
        self.DisplayUpdate()

    #--------------------------------------------------------------------------#
    # Display options TAB                                                      #
    #--------------------------------------------------------------------------#
    # Color map ################################################################
    def ColorMapInit(self, id=None):
        ''' Build the colormap list for selection. '''

        # Geophpy's colormap and icon list
        cmap_list = colormap_getlist()
        icon_list = colormap_icon_getlist()
        icon_path = colormap_icon_getpath()

        ###
        ##
        # Not working yet
        ##
        #### Sorting icon list following cmap list
##        icon_list_sort = []
##        for cmname in icon_list:
##            if cmname in icon_list:
##                idx = icon_list.index(cmname)
##                icon_list_sort.append(icon_list[idx])

        try:
            cmap_index = cmap_list.index(self.colormap)
        except:
            cmap_index = 0

        if id is not None:
            for i, cmap in enumerate(cmap_list):
                #print(i)
                #print(i, cmap)
                try:
                    icon_name = os.path.join(icon_path, icon_list[i])
                except:
                    icon_name = ['']

                # reading icon from file
                if os.path.isfile(icon_name):
                    cmapicon = QIcon(icon_name)
                    
                # or creating icon file directly from colormap
                else:
                    colormap_make_icon(cmap, path=icon_path)
                    icon_name = os.path.join(icon_path, 'CMAP_', cmap,'.png')
                    cmapicon = QIcon(icon_name)

                    #cmapfig = colormap_plot(cmap)
                    #cmapicon = QPixmap.grabWidget(FigureCanvas(cmapfig))
                    #plt.close(cmapfig)

                # updating colomap list
                id.addItem(cmapicon, cmap)
                iconsize = QSize(100,16)
                id.setIconSize(iconsize)
            
            id.setCurrentIndex(cmap_index)
        self.ColorMapId = id
        return id

    def ColorMapUpdate(self):
        self.colormap = self.ColorMapId.currentText()
        self.DisplayUpdate()

    def ColorMapReverseInit(self, id=None):
        if id is not None:
            id.setChecked(self.reverseflag)
        self.ColorMapReverseId = id
        return id

    def ColorMapReverseUpdate(self):
        self.reverseflag = self.ColorMapReverseId.isChecked()
        self.DisplayUpdate()

    def ColorBarLogScaleInit(self, id=None):
        self.ColorBarLogScaleId = id
        return id

    def ColorBarLogScaleReset(self):
        zmin, zmax = self.dataset.histo_getlimits()
        if (zmin <= 0):                                 # if data values are below or equal to zero
            self.colorbarlogscaleflag = False               
            self.ColorBarLogScaleId.setEnabled(False)   # the data can not be log scaled
        else:
            self.ColorBarLogScaleId.setEnabled(True)            
        self.ColorBarLogScaleId.setChecked(self.colorbarlogscaleflag)

    def ColorBarLogScaleUpdate(self):
        self.colorbarlogscaleflag = self.ColorBarLogScaleId.isChecked()
        self.DisplayUpdate()

    # Min/Max values ###########################################################
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

    #--------------------------------------------------------------------------#
    # Filters options TAB                                                      #
    #--------------------------------------------------------------------------#
    # Median filter ############################################################
    def MedianFiltInit(self, id=None):
        if id is not None:
            id.setChecked(self.medianfiltflag)
        self.MedianFiltId = id
        return id

    def MedianFiltUpdate(self):
        self.medianfiltflag = self.MedianFiltId.isChecked()
        
        self.NxSizeLabelId.setEnabled(self.medianfiltflag)
        self.NxSizeId.setEnabled(self.medianfiltflag)

        self.NySizeLabelId.setEnabled(self.medianfiltflag)
        self.NySizeId.setEnabled(self.medianfiltflag)

        self.PercentId.setEnabled(self.medianfiltflag)
        self.PercentLabelId.setEnabled(self.medianfiltflag)

        self.GapId.setEnabled(self.medianfiltflag)
        self.GapLabelId.setEnabled(self.medianfiltflag)
        
        self.DisplayUpdate()

    def NxSizeLabelInit(self, id=None):
        if id is not None:                                                    
            id.setEnabled(self.medianfiltflag)
        self.NxSizeLabelId = id
        return id

    def NxSizeInit(self, id=None):
        if id is not None:
            id.setEnabled(self.medianfiltflag)
            id.setRange(0, 100)
            id.setValue(self.nxsize)
        self.NxSizeId = id
        return id

    def NxSizeUpdate(self):
        self.nxsize = self.NxSizeId.value()
        self.DisplayUpdate()

    def NySizeLabelInit(self, id=None):
        if id is not None:                                                    
            id.setEnabled(self.medianfiltflag)
        self.NySizeLabelId = id
        return id

    def NySizeInit(self, id=None):
        if id is not None:
            id.setEnabled(self.medianfiltflag)
            id.setRange(0, 100)
            id.setValue(self.nysize)
        self.NySizeId = id
        return id

    def NySizeUpdate(self):
        self.nysize = self.NySizeId.value()
        self.DisplayUpdate()

    def PercentLabelInit(self, id=None):
        if id is not None:                                                    
            id.setEnabled(self.medianfiltflag)
        self.PercentLabelId = id
        return id

    def PercentInit(self, id=None):
        if id is not None:
            id.setEnabled(self.medianfiltflag)
            id.setRange(0, 100)
            id.setValue(self.percent)
        self.PercentId = id
        return id

    def PercentUpdate(self):
        self.percent = self.PercentId.value()
        self.DisplayUpdate()

    def GapLabelInit(self, id=None):
        if id is not None:                                                    
            id.setEnabled(self.medianfiltflag)
        self.GapLabelId = id
        return id

    def GapInit(self, id=None):
        if id is not None:
            id.setEnabled(self.medianfiltflag)
            id.setRange(0, 100)
            id.setValue(self.gap)
        self.GapId = id
        return id

    def GapUpdate(self):
        self.gap = self.GapId.value()
        self.DisplayUpdate()

    # Zero Mean/Median filter ##################################################
    def ZeroMeanInit(self, id=None):
        if id is not None:
            id.setChecked(self.zeromeanfiltvar=='mean')
        self.ZeroMeanId = id
        return id  

    def ZeroMedianInit(self, id=None):
        if id is not None:
            id.setChecked(self.zeromeanfiltvar=='median')
        self.ZeroMedianId = id
        return id

    def ZeroMeanMedianSelector(self):
        if self.ZeroMeanId.isChecked():
            self.zeromeanfiltvar = 'mean'

        elif self.ZeroMedianId.isChecked():
            self.zeromeanfiltvar = 'median'

    def ZeroMeanMedianUpdate(self):
        self.ZeroMeanMedianSelector()
        self.DisplayUpdate()

    def ZeroMeanFiltInit(self, id=None):
        if id is not None:
            id.setChecked(self.zeromeanfiltflag)
        self.ZeroMeanFiltId = id
        self.ZeroMeanId.setEnabled(self.zeromeanfiltflag)
        self.ZeroMedianId.setEnabled(self.zeromeanfiltflag)
        return id

    def ZeroMeanFiltUpdate(self):
        # Enabling/Disabling filter
        self.ZeroMeanId.setEnabled(self.ZeroMeanFiltId.isChecked())
        self.ZeroMedianId.setEnabled(self.ZeroMeanFiltId.isChecked())
        self.zeromeanfiltflag = self.ZeroMeanFiltId.isChecked()
        self.DisplayUpdate()

    # Festoon filter ###########################################################
    def FestoonUniformShiftInit(self, id=None):
        if id is not None:
            id.setChecked(self.festoonfiltuniformshift)
            id.setEnabled(self.festoonfiltflag)
        self.FestoonUniformShiftId = id
        return id

    def FestoonUniformShiftUpdate(self):
        self.festoonfiltuniformshift = self.FestoonUniformShiftId.isChecked()
        #self.FestoonShiftLabelId.setEnabled(self.festoonfiltuniformshift)
        self.FestoonShiftId.setEnabled(self.festoonfiltuniformshift)
        self.DisplayUpdate()

    def FestoonFiltInit(self, id=None):
        if id is not None:
            id.setChecked(self.festoonfiltflag)
        self.FestoonFiltId = id
        return id

    def FestoonFiltUpdate(self):
        self.festoonfiltflag = self.FestoonFiltId.isChecked()
        
        self.FestoonMethodLabelId.setEnabled(self.festoonfiltflag)
        self.FestoonMethodId.setEnabled(self.festoonfiltflag)
        
        self.FestoonUniformShiftId.setEnabled(self.festoonfiltflag)
        
        self.FestoonCorrMinLabelId.setEnabled(self.festoonfiltflag)
        self.FestoonCorrMinId.setEnabled(self.festoonfiltflag)
        
        self.FestoonUniformShiftUpdate()
        if not self.festoonfiltflag:
            self.FestoonShiftId.setEnabled(self.festoonfiltflag)
            #self.FestoonShiftLabelId.setEnabled(self.festoonfiltflag)
        
        self.DisplayUpdate()

    def FestoonMethodLabelInit(self, id=None):
        id.setEnabled(self.festoonfiltflag)
        self.FestoonMethodLabelId = id
        return id

    def FestoonMethodInit(self, id=None):
        method_list = festooncorrelation_getlist()
        try:
            method_index = method_list.index(self.festoonfiltmethod)
        except:
            method_index = 0
            
        if id is not None:
            id.addItems(method_list)
            id.setCurrentIndex(method_index)
            id.setEnabled(self.festoonfiltflag)
        self.FestoonMethodId = id
        return id


    def FestoonMethodUpdate(self):
        self.festoonfiltmethod = self.FestoonMethodId.currentText()
        self.DisplayUpdate()

    def FestoonShiftInit(self, id=None):
        if id is not None:                                                    
            range = 400 # TEMP
            id.setRange(-range, +range)
            id.setValue(self.festoonfiltshift)
            id.setEnabled(self.festoonfiltuniformshift)
        self.FestoonShiftId = id
        return id


    def FestoonShiftUpdate(self):
        self.festoonfiltshift = self.FestoonShiftId.value()
        self.DisplayUpdate()

    def FestoonCorrMinLabelInit(self, id=None):
        if id is not None:                                                    
            id.setEnabled(self.festoonfiltuniformshift)
        self.FestoonCorrMinLabelId = id
        return id
    
    def FestoonCorrMinInit(self, id=None):
        if id is not None:
            id.setRange(0, 1.0)
            id.setSingleStep(0.1)
            id.setValue(self.festoonfiltcorrmin)
            id.setEnabled(self.festoonfiltflag)
        self.FestoonCorrMinId = id
        return id

    def FestoonCorrMinUpdate(self, id=None):
        self.festoonfiltcorrmin = self.FestoonCorrMinId.value()
        self.DisplayUpdate()

    # Thresholding #############################################################
    def ThresholdInit(self, id=None):
        if id is not None:
            id.setChecked(self.thresholdflag)
        self.ThresholdId = id
        return id

    def ThresholdUpdate(self):
        self.thresholdflag = self.ThresholdId.isChecked()

        # Enables/disable other checkboxes
        self.MinMaxReplacedValuesId.setEnabled(self.thresholdflag)
        self.NanReplacedValuesId.setEnabled(self.thresholdflag)
        self.MedianReplacedValuesId.setEnabled(self.thresholdflag)

        # Uchecking all boxes if disabled
        if ~self.thresholdflag:
            self.MinMaxReplacedValuesId.setChecked(False)
            self.NanReplacedValuesId.setChecked(False)
            self.MedianReplacedValuesId.setChecked(False)            
        
        self.DisplayUpdate()


    # Peak Filter ##############################################################
    def PeakFiltInit(self, id=None):
        if id is not None:
            id.setChecked(self.peakfiltflag)
        self.PeakFiltId = id
        return id

    def PeakFiltUpdate(self):
        self.peakfiltflag = self.PeakFiltId.isChecked()

        # Enables/diable other checkboxes
        self.MinMaxReplacedValuesId.setEnabled(self.peakfiltflag)
        self.NanReplacedValuesId.setEnabled(self.peakfiltflag)
        self.MedianReplacedValuesId.setEnabled(self.peakfiltflag)

        # Uchecking all boxes if diabled
        if ~self.peakfiltflag:
            self.MinMaxReplacedValuesId.setChecked(False)
            self.NanReplacedValuesId.setChecked(False)
            self.MedianReplacedValuesId.setChecked(False)            
        
        self.DisplayUpdate()

    def MinMaxReplacedValuesInit(self, id=None):
        if id is not None:
            id.setEnabled(self.thresholdflag)
            id.setChecked(self.minmaxreplacedflag)
        self.MinMaxReplacedValuesId = id
        return id

    def MinMaxReplacedValuesUpdate(self):
        self.minmaxreplacedflag = self.MinMaxReplacedValuesId.isChecked()
        
        # Unchecking the other boxes
        if self.minmaxreplacedflag:
            self.NanReplacedValuesId.setChecked(False)
            self.MedianReplacedValuesId.setChecked(False)
        
        self.DisplayUpdate()

    def NanReplacedValuesInit(self, id=None):
        if id is not None:
            id.setEnabled(self.thresholdflag)
            id.setChecked(self.nanreplacedflag)
        self.NanReplacedValuesId = id
        return id

    def NanReplacedValuesUpdate(self):
        self.nanreplacedflag = self.NanReplacedValuesId.isChecked()

        # Unchecking the other boxes
        if self.nanreplacedflag:
            self.MinMaxReplacedValuesId.setChecked(False)
            self.MedianReplacedValuesId.setChecked(False)

        self.DisplayUpdate()

    def MedianReplacedValuesInit(self, id=None):
        if id is not None:
            id.setEnabled(self.thresholdflag)
            id.setChecked(self.medianreplacedflag)
        self.MedianReplacedValuesId = id
        return id

    def MedianReplacedValuesUpdate(self):
        self.medianreplacedflag = self.MedianReplacedValuesId.isChecked()

        # Unchecking the other boxes
        if self.medianreplacedflag:
            self.MinMaxReplacedValuesId.setChecked(False)
            self.NanReplacedValuesId.setChecked(False)
            
        self.DisplayUpdate()

    #--------------------------------------------------------------------------#
    # Cancel, Update, Valid button TAB                                         #
    #--------------------------------------------------------------------------#
    def DispUpdateButtonInit(self, id=None):
        id.setEnabled(False)                        # disables the button , by default
        if self.realtimeupdateflag is True:
            id.setHidden(self.realtimeupdateflag)   # Hides button if real time updating activated
        self.DispUpdateButtonId = id
        return id

    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                     # updates carto image

    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id

    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id

    #--------------------------------------------------------------------------#
    # Histogram TAB                                                            #
    #--------------------------------------------------------------------------#
    def ColorBarDisplayInit(self, id=None):
        self.colorbardisplayflag = self.colorbardisplayflag

        if id is not None:
            id.setChecked(self.colorbardisplayflag)

        self.ColorBarDisplayId = id
        return id

    def ColoredHistInit(self, id=None):
        id.setChecked(self.coloredhistoflag)
        self.ColoredHistId = id
        return id

    def ColoredHistUpdate(self):
        self.coloredhistoflag = self.ColoredHistId.isChecked()
        self.HistoImageUpdate()

    def HistoImageInit(self, id=None):
        self.HistoImageId = id
        return id

    def HistoImageUpdate(self):
        self.histofig, _ = self.dataset.histo_plot(fig=self.histofig,
                                                zmin=self.zmin,
                                                zmax=self.zmax,
                                                cmapname=self.colormap,
                                                coloredhisto=self.coloredhistoflag,
                                                creversed=self.reverseflag,
                                                cmapdisplay=self.colorbardisplayflag)
        #self.histofig.patch.set_alpha(0.1)  # transparent figure background
        #self.histofig.patch.set_linewidth(4)
        #self.histofig.patch.set_edgecolor('black')
        self.HistoImageId.update(self.histofig)
        
        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)


    def ColorBarDisplayUpdate(self):
        self.colorbardisplayflag = self.ColorBarDisplayId.isChecked()
        self.HistoImageUpdate()

        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button

    #--------------------------------------------------------------------------#
    # Rendering TAB                                                            #
    #--------------------------------------------------------------------------#
    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        self.CartoImageUpdate()
        self.HistoImageUpdate()
        return id

    def CartoImageUpdate(self):
        first = True
        initcursor = self.wid.cursor()              # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)    # sets the wait cursor

        # Updating file preview
        self.FilePreviewUpdate()
        for n in range(len(self.filenames)):
            # treats data values
            colsnb = getlinesfrom_file(self.filenames[n],
                                       self.fileformat,
                                       self.delimiter,
                                       self.delimitersasuniqueflag,
                                       self.skiprows, 10)[0]

            if first is True:
                datacolsnb = colsnb
            else:
                if (colsnb != datacolsnb):
                    datacolsnb = 0

        if (datacolsnb >= 3) :
            self.XColumnId.setRange(1, datacolsnb)
            self.YColumnId.setRange(1, datacolsnb)
            self.ZColumnId.setRange(1, datacolsnb)

        # Reading dataset from files #######################################
        try:
            # Reading dataset
            success, self.dataset = DataSet.from_file(self.filenames,
                                                      fileformat=self.fileformat,
                                                      delimiter=self.delimiter,
                                                      x_colnum=self.x_colnum,
                                                      y_colnum=self.y_colnum,
                                                      z_colnum=self.z_colnum,
                                                      skipinitialspace=self.delimitersasuniqueflag,
                                                      skip_rows=self.skiprows,
                                                      fields_row=self.fieldsrow)
            plottype = '2D-SCATTER'  # ensure a plot if the interpolated image size is too big

            # Spatial domain from scatter values
            self.zmin, self.zmax = self.dataset.histo_getlimits(valfilt=True)  # Histogram from raw values
            self.xmin = min(self.dataset.get_xvalues())
            self.xmax = max(self.dataset.get_xvalues())
            self.ymin = min(self.dataset.get_yvalues())
            self.ymax = max(self.dataset.get_yvalues())

            # Median spatial stepsize
            x_step, y_step = self.stepxgridding, self.stepygridding
            if x_step is None:
                x_step  = self.dataset.get_median_xstep()
                x_decimal = 2
            else:
                x_decimal = geoutils.getdecimalsnb(x_step)

            if y_step is None:
                y_step  = self.dataset.get_median_ystep()
                y_decimal = 2
            else:
                y_decimal = geoutils.getdecimalsnb(y_step)

            # Future image size
            xmin = round(self.xmin, x_decimal)
            xmax = round(self.xmax, x_decimal)
            ymin = round(self.ymin, y_decimal)
            ymax = round(self.ymax, y_decimal)

            nx = int(np.around((xmax - xmin)/x_step) + 1)
            ny = int(np.around((ymax - ymin)/y_step) + 1)

            self.colsnb = nx
            self.rowsnb = ny
            self.bytesnb =  ymax.itemsize # number bytes from raw values
            
            self.GridSizeEstimationUpdate()
            self.GriddingSizeUpdate()
            

            # Updating maximum possible grid step
            x_stepmax = np.abs(xmax-xmin)
            y_stepmax = np.abs(ymax-ymin)

            self.GriddingXStepId.setMaximum(x_stepmax)
            self.GriddingYStepId.setMaximum(y_stepmax)

            # Gridding and processing dataset #######################################
            # Error might happen if the data grid is too large (memory Error)
            try:
                self.dataset.interpolate(interpolation=self.interpgridding,
                                         x_step=self.stepxgridding,
                                         y_step=self.stepygridding,
                                         x_frame_factor=0.,
                                         y_frame_factor=0.)

                self.zmin, self.zmax = self.dataset.histo_getlimits()  # Histogram from raw grid
                self.xmin = self.dataset.info.x_min
                self.xmax = self.dataset.info.x_max
                self.ymin = self.dataset.info.y_min
                self.ymax = self.dataset.info.y_max

                self.colsnb = len(self.dataset.data.z_image)  # number of cols from raw grid
                self.rowsnb = len(self.dataset.data.z_image[0])  # number of rows from raw grid
                self.bytesnb = self.ymax.itemsize # number bytes from raw values

                plottype = '2D-SURFACE'

            except Exception as e:
                print(e)
                pass

            self.GridSizeEstimationUpdate()
            self.GriddingSizeUpdate()

            # Dataset processing ###############################################
            # Thresholding
            if (self.thresholdflag):
                self.dataset.threshold(self.zmin, self.zmax, setmed=self.medianreplacedflag, setnan=self.nanreplacedflag, valfilt=self.valfiltflag)

##            # Processes peak filtering if flag enabled
##            if (self.peakfiltflag):
##                self, method='hampel', halfwidth=5, threshold=3, mode='relative', setnan=False, valfilt=False
##                self.dataset.peakfilt(method=self.peakmethod, halfwidth=self.peakhalfwidth, threshold=self.peakthreshold, mode=self.peakmode, setnan=self.nanreplacedflag, valfilt=self.valfiltflag)

            # processes zero-mean filtering if flag enabled
            if self.zeromeanfiltflag:
                self.dataset.zeromeanprofile(setvar=self.zeromeanfiltvar, valfilt=self.valfiltflag)
                #zeromeanprofile(setvar='mean')

            # processes festoon filtering if flag enabled
            if self.festoonfiltflag:
                self.dataset.festoonfilt(method=self.festoonfiltmethod,
                                         shift=self.festoonfiltshift,
                                         corrmin=self.festoonfiltcorrmin,
                                         uniformshift=self.festoonfiltuniformshift,
                                         valfilt=self.valfiltflag)

            # processes median filtering if flag enabled
            if self.medianfiltflag:
                self.dataset.medianfilt(self.nxsize, self.nysize, self.percent, self.gap, self.valfiltflag)

            # Ploting geophysical map ##########################################
            # resets limits of input parameters
            if self.automaticrangeflag:
                self.automaticrangeflag = False
                self.zmin, self.zmax = self.dataset.histo_getlimits()
                self.ColorBarLogScaleReset()
                self.MaximalValuebySpinBoxReset()
                self.MaximalValuebySliderReset()
                self.MinimalValuebySpinBoxReset()
                self.MinimalValuebySliderReset()
                
            # Min & Max colors
            if self.thresholdflag:     # displays all values to verify peak filtering effects
                cmmin = None            
                cmmax = None
            else:                       # display filtering only
                cmmin = self.zmin
                cmmax = self.zmax

            # Actual plot creation
            #self.cartofig, cartocmap = self.dataset.plot(self.dataset.info.plottype, self.colormap, cmmin=cmmin, cmmax=cmmax, fig=self.cartofig, interpolation='none', creversed=self.reverseflag, logscale=self.colorbarlogscaleflag, pointsdisplay=self.dispdatapointflag)
            self.cartofig, cartocmap = self.dataset.plot(plottype,
                                                         self.colormap,
                                                         cmmin=cmmin,
                                                         cmmax=cmmax,
                                                         fig=self.cartofig,
                                                         interpolation='none',
                                                         creversed=self.reverseflag,
                                                         logscale=self.colorbarlogscaleflag,
                                                         pointsdisplay=self.dispdatapointflag)
            #self.cartofig.patch.set_alpha(0.1)  # transparent figure background
            #self.cartofig.patch.set_linewidth(4)
            #self.cartofig.patch.set_edgecolor('black')
            self.CartoImageId.update(self.cartofig)

            self.GriddingXStepId.setValue(self.dataset.info.x_gridding_delta)
            self.dataset.info.x_gridding_delta = self.GriddingXStepId.value()    # to be sure than the value in the dialog box is not the real value arounded
            self.GriddingYStepId.setValue(self.dataset.info.y_gridding_delta)
            self.dataset.info.y_gridding_delta = self.GriddingYStepId.value()    # to be sure than the value in the dialog box is not the real value arounded
            self.interpgridding = self.dataset.info.gridding_interpolation
            self.stepxgridding = self.dataset.info.x_gridding_delta
            self.stepygridding = self.dataset.info.y_gridding_delta

            #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
            #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))

            #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x) #AB# TAILLE EN FONCTION DE SIZE X ET SIZE Y
            #self.CartoImageId.setPixmap(cartopixmap)
            #self.CartoImageId.setPixmap(cartopixmap)
            #self.CartoImageId.setPixmap(cartopixmap)

            self.CartoImageId.setEnabled(True)                              # enables the carto image
            self.ValidButtonId.setEnabled(True)

        # Unable to read dataset from file
        except Exception as e:
            print(e)
            self.cartofig, cartocmap = None, None
            self.CartoImageId.setEnabled(False)                             # disables the carto image
            self.ValidButtonId.setEnabled(False)
           

        self.DispUpdateButtonId.setEnabled(False)                           # disables the display update button

        self.wid.setCursor(initcursor)                                          # resets the init cursor

        if not self.realtimeupdateflag: #Permet de debug le probleme du non refresh de l'histogramme quand realtime n'est pas definit
          self.HistoImageUpdate()
