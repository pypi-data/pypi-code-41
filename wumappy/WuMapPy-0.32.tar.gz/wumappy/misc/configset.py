# -*- coding: utf-8 -*-
'''
    wumappy.misc.configset
    ----------------------

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

import os
from os.path import expanduser
import configparser
import platform

#import glob                             # for managing severals files thanks to "*." extension
#import csv 
#import numpy as np

#------------------------------------------------------------------------------#
# GUI configuration                                                            #
#------------------------------------------------------------------------------#
settings_dir = "/settings"              # resources directory
export_dir = "/export"                  # export directory
temp_dir = "/temp"                      # temporary directory
config_filename = "/config.ini"
file_dir = "."                          # default files directory

config_array = [   \
    # section,   option,   default
    ['ASCII', 'language', 'english'],
    ['ASCII', 'fontname', 'MS Shell Dlg 2'],
    ['ASCII', 'fontsize', '10'],
    ['FILES', 'fileformat', 'ascii'],
    ['FILES', 'delimiter',  'space'],
    ['FILES', 'delimitersasuniqueflag', 'True'],
    ['FILES', 'skiprows', '1'],
    ['FILES', 'fieldsrow', '0'],
    ['GENSETTINGS', 'autogriddingflag', 'True'],
    ['GENSETTINGS', 'dispdatapointflag', 'False'],
    ['GENSETTINGS', 'stepxgridding', '1.0'],
    ['GENSETTINGS', 'stepygridding', '1.0'],
    ['GENSETTINGS', 'interpgridding', 'linear'],
    ['GENSETTINGS', 'xcolnum', '1'],
    ['GENSETTINGS', 'ycolnum', '2'],
    ['GENSETTINGS', 'zcolnum', '3'],
    ['DISPSETTINGS', 'plottype', '2D-SURFACE'],
    ['DISPSETTINGS', 'interpolation', 'bilinear'],
    ['DISPSETTINGS', 'colormap', 'Greys'],
    ['DISPSETTINGS', 'reverseflag', 'False'],
    ['DISPSETTINGS', 'colorbardisplayflag', 'True'],
    ['DISPSETTINGS', 'colorbarlogscaleflag','False'],
    ['DISPSETTINGS', 'coloredhistoflag','True'],
    ['DISPSETTINGS', 'axisdisplayflag', 'False'],
    ['DISPSETTINGS', 'dpi', '600'],
    ['DIRECTORIES', 'savefiledir', file_dir],
    ['DIRECTORIES', 'exportimagedir', export_dir],
    ['DIRECTORIES', 'exportrasterdir', export_dir],
    ['DIRECTORIES', 'exportkmldir', export_dir],
    ['DIRECTORIES', 'exportgriddir', export_dir],
    ['DIRECTORIES', 'openfiledir', file_dir],
    ['DIRECTORIES', 'importfiledir', file_dir],
    ['DIRECTORIES', 'opengeopossetfiledir', file_dir],
    ['DIRECTORIES', 'eulerfiledir', file_dir],
    ['PROCESSING', 'thresholdminmaxreplacedflag', 'False'],
    ['PROCESSING', 'thresholdnanreplacedflag', 'False'],
    ['PROCESSING', 'thresholdmedianreplacedflag', 'False'],
    ['PROCESSING', 'medianfiltnxsize', '3'],
    ['PROCESSING', 'medianfiltnysize', '3'],
    ['PROCESSING', 'medianfiltpercent', '0'],
    ['PROCESSING', 'medianfiltgap', '0'],
    ['PROCESSING', 'zeromeanfiltflag', 'False'],
    ['PROCESSING', 'zeromeanfiltvar', 'median'],
    ['PROCESSING', 'festoonfiltflag', 'False'],
    ['PROCESSING', 'festoonfiltmethod', 'Crosscorr'],
    ['PROCESSING', 'festoonfiltshift', '0'],
    ['PROCESSING', 'festoonfiltcorrmin', '0.4'],
    ['PROCESSING', 'festoonfiltuniformshift', 'False'],
    ['PROCESSING', 'apodisationfactor', '0'],
    ['PROCESSING', 'maginclineangle', '65'],
    ['PROCESSING', 'magalphaangle', '0'],
    ['PROCESSING', 'multfactor', '5'],
    ['PROCESSING', 'prosptech', ''],
    ['PROCESSING', 'sensorconfig', ''],
    ['PROCESSING', 'sensorsep', '0.7'],
    ['PROCESSING', 'totalfieldconversionflag', 'False'],
    ['PROCESSING', 'downsensoraltitude', '0.30'],
    ['PROCESSING', 'upsensoraltitude', '1.00'],
    ['PROCESSING', 'continuationflag', 'False'],
    ['PROCESSING', 'continuationvalue', '0.00'],
    ['PROCESSING', 'continuationdist', '0.50'],
    ['PROCESSING', 'continuationsoilsurfaceaboveflag', 'False'],
    ['PROCESSING', 'destripingmethod', 'additive'],
    ['PROCESSING', 'destripingconfig', 'mono'],
    ['PROCESSING', 'destripingreference', 'median'],
    ['PROCESSING', 'destripingprofilesnb', '0'],
    ['PROCESSING', 'destripingdegreesnb', '3'],
    ['PROCESSING', 'regtrendfiltnxsize', '11'],
    ['PROCESSING', 'regtrendfiltnysize', '11'],
    ['PROCESSING', 'regtrendmethod', 'absolute'],
    ['PROCESSING', 'regtrendcomponent', 'local'],
    ['PROCESSING', 'ploughangle', '90'],
    ['PROCESSING', 'ploughcutoff', '100'],
    ['PROCESSING', 'ploughwidth', '3'],
    ['PROCESSING', 'wallisfiltnxsize', '11'],
    ['PROCESSING', 'wallisfiltnysize', '11'],
    ['PROCESSING', 'wallisfilttargmean', '125'],
    ['PROCESSING', 'wallisfilttargstdev', '50'],
    ['PROCESSING', 'wallisfiltsetgain', '8'],
    ['PROCESSING', 'wallisfiltlimitstdev', '25'],
    ['PROCESSING', 'wallisfiltedgefactor', '0.1'],
    ['PROCESSING', 'calcdepth', '0.'],
    ['PROCESSING', 'stratumthickness', '1.'],
    ['GEOPOSITIONING', 'refsystem', 'WGS84'],
    ['GEOPOSITIONING', 'utm_letter', 'E'],
    ['GEOPOSITIONING', 'utm_number', '1'],
    ['MISC', 'html_viewer', 'none'],
    ['MISC', 'pdf_viewer', 'none'],
    ['MISC', 'realtimeupdateflag', 'False'],
    ['MISC', 'changeresolutionflag', 'True']] # GroupBox display
        

class ConfigSet(object):    
    def __init__(self):
        self.dict = configparser.ConfigParser()
                        # gets the configuration settings
                        # create the ressource directory if necessary
        if (platform.system() == 'Windows'):
            self.main_dir = expanduser("~") + "/wumappy"
        else:           # Linux, Mac OS, ...
            self.main_dir = expanduser("~") + "/.wumappy"
        os.makedirs(self.main_dir + settings_dir, exist_ok=True)
        os.makedirs(self.main_dir + export_dir, exist_ok=True)
        os.makedirs(self.main_dir + export_dir, exist_ok=True)
        os.makedirs(self.main_dir + temp_dir, exist_ok=True)
        self.temp_dir = self.main_dir + temp_dir
        full_config_filename = self.main_dir + settings_dir + config_filename
        self.dict = configparser.ConfigParser(allow_no_value = False)
        self.dict.read(full_config_filename)

        for line in config_array:
            section = line[0]
            option = line[1]
            default = line[2]
            
            if not self.dict.has_section(section):          # if section doesn't exist, creates it
                self.dict.add_section(section)

            if not self.dict.has_option(section, option):
                self.dict.set(section, option, default)


    def get(self, section, option):
        try :
            value = self.dict.get(section, option)
        except:
            value = ""
        return(value)


    def getint(self, section, option):
        try:
            value = self.dict.getint(section, option)
        except:
            value = -1
        return(value)


    def getfloat(self, section, option):
        try:
            value = self.dict.getfloat(section, option)
        except:
            value = -1.0
        return(value)


    def getboolean(self, section, option):
        try:
            value = self.dict.getboolean(section, option)
        except:
            value = False
        return(value)


    def set(self, section, option, value):
        self.dict.set(section, option, value)


    def save(self):
        full_config_filename = self.main_dir + settings_dir + config_filename
        file = open(full_config_filename, 'w')
        self.dict.write(file)
        file.close()
        
