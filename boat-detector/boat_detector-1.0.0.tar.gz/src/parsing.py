# ================================================================================ #
#   Authors: Oliver Kirsebom                                                       #
#   Contact: oliver.kirsebom@dal.ca                                                #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: boat_detector                                                         #
#   Project goal: Command-line tool for processing hydrophone data and searching   # 
#   for the acoustic signature of motorized vessels.                               #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

import datetime
import numpy as np
import pandas as pd
import os
import json
import math
import ketos.data_handling.parsing as pa
import ketos.audio_processing.spectrogram_filters as sf
from ketos.utils import get_member
from pint import UnitRegistry
from enum import Enum
from collections import namedtuple


ureg = UnitRegistry() 


PeakFindingConfig = namedtuple('PeakFindingConfig', 'separation size multiplicity height')
PeakFindingConfig.__new__.__defaults__ = (60, 3.0, 1, 0)
PeakFindingConfig.__doc__ = '''\
Configuration of peak finding algorithm

separation - Minimum temporal separation between neighboring peaks in seconds
size - Minimum peak height relative to baseline given in multiples of the signal standard devitation (float)
multiplicity - Minimum number of data series in which peak occurs
height - minimum absolute height of peak'''

SVMConfig = namedtuple('SVMConfig', 'nu kernel gamma degree training_data')
SVMConfig.__new__.__defaults__ = (0.01, "poly", 0.001, 2, "None")
SVMConfig.__doc__ = '''\
Configuration of One-class SVM model

See: http://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html
'''


class Detector(Enum):
    PEAK_FINDING = 1
    ELLIPTIC_ENVELOPE = 2
    LOCAL_OUTLIER_FACTOR = 3
    ISOLATION_FOREST = 4
    ONE_CLASS_SVM = 5


def parse_settings(path):

    # default values
    fmt = '*HMS_%H_%M_%S__DMY_%d_%m_%y*'
    batch_size = 5E6
    detector = ['FAV', 'OBI'][0]

    with open(path, "r") as read_file:

        # load json file
        data = json.load(read_file)

        # date-time format
        fmt = data['date_time_format']        
        if fmt[0] != '*':
            fmt = '*' + fmt
        if fmt[-1] != '*':
            fmt = fmt + '*'

        # max batch size
        batch_size = int(float(data['batch_size']))

        # detector 
        detector = data['detector']
        
    return fmt, batch_size, detector


def parse_preproc_config(path):

    with open(path, "r") as read_file:
        data = json.load(read_file)

        # filters
        filters = list()
        if data.get('filters') is not None:
            for x in data['filters']:
                if x == 'FREQUENCY':
                    bands, names = parse_frequency_config(data)
                    f = sf.FrequencyFilter(bands=bands, names=names)
                    filters.append(f)
                elif x == 'MEDIAN':
                    window_size, step_size = parse_window_config(data, 'median_config')
                    f = sf.WindowFilter(window_size=window_size, step_size=step_size, filter_func=np.ma.median)
                    filters.append(f)
                elif x == 'MEDIAN_SUBTRACTION':
                    window_size, _ = parse_window_config(data, 'median_subtraction_config')
                    f = sf.WindowSubtractionFilter(window_size=window_size, filter_func=np.ma.median)
                    filters.append(f)
                elif x == 'AVERAGE':
                    window_size, step_size = parse_window_config(data, 'average_config')
                    f = sf.WindowFilter(window_size=window_size, step_size=step_size, filter_func=np.ma.average)
                    filters.append(f)
                elif x == 'AVERAGE_SUBTRACTION':
                    window_size, _ = parse_window_config(data, 'average_subtraction_config')
                    f = sf.WindowSubtractionFilter(window_size=window_size, filter_func=np.ma.average)
                    filters.append(f)
                elif x == 'CROPPING':
                    flow, fhigh = parse_cropping_config(data)
                    f = sf.CroppingFilter(flow=flow, fhigh=fhigh)
                    filters.append(f)
                elif x == 'HARMONIC':
                    f = sf.HarmonicFilter()
                    filters.append(f)
                elif x == 'FAV':
                    f = sf.FAVFilter()
                    filters.append(f)
                elif x == 'FAV_THRESHOLD':
                    threshold = 3.0
                    if data.get('fav_config') is not None:
                        threshold = float(data['fav_config'].get('threshold'))
                    f = sf.FAVThresholdFilter(threshold=threshold)
                    filters.append(f)
                else:
                    print('Warning: Unknown filter {0} will be ignored'.format(x))

        # spectrogram
        spectr_config = pa.parse_spectrogram_configuration(data['spectrogram'])

        return spectr_config, filters


def parse_frequency_config(data):
    bands, names = list(), None
    if data.get('frequency_config') is not None:
        names, bands = pa.parse_frequency_bands(data['frequency_config'])
    return bands, names


def parse_window_config(data, name):
    window_size = math.inf
    step_size = None

    if data.get(name) is not None:

        d = data[name]
        Q = ureg.Quantity

        if d.get('window_size') is not None:
            window_size = Q(d['window_size'])
            window_size = window_size.m_as("s")

        if d.get('step_size') is not None:
            step_size = Q(d['step_size'])
            step_size = step_size.m_as("s")

    return window_size, step_size


def parse_cropping_config(data):
    flow, fhigh = None, None

    if data.get('crop_config') is not None:

        d = data['crop_config']
        Q = ureg.Quantity

        if d.get('min_frequency') is not None:
            flow = Q(d['min_frequency'])
            flow = flow.m_as("Hz")

        if d.get('max_frequency') is not None:
            fhigh = Q(d['max_frequency'])
            fhigh = fhigh.m_as("Hz")

    return flow, fhigh


def parse_harmonic_config(data):
    fsep = None

    if data.get('harmonic_config') is not None:

        d = data['harmonic_config']
        Q = ureg.Quantity

        if d.get('frequency_separation') is not None:
            fsep = Q(d['frequency_separation'])
            fsep = fsep.m_as("Hz")

    return fsep


def parse_detect_config(path):

    with open(path, "r") as read_file:

        # data series
        data = json.load(read_file)['detect_config']
        data_series = data['data_series']

        # detectors
        det_names = data['detectors'] # strings
        detectors = list() # enums
        for det_name in det_names:
            detectors.append(get_member(Detector, det_name))
                
        # configs
        configs = {}
        name, cfg = parse_peak_finding_config(data)
        configs[name] = cfg
        name, cfg = parse_svm_config(data)
        configs[name] = cfg

        # outlier fraction
        outlier_fraction = 0.1
        if data.get('outlier_fraction') is not None:
            outlier_fraction = float(data['outlier_fraction'])

        # minimum outlier separation in seconds
        min_sep = 1
        if data.get('anomaly_separation') is not None:
            Q = ureg.Quantity
            min_sep = Q(data['anomaly_separation'])
            min_sep = min_sep.m_as("s")

        return data_series, detectors, configs, outlier_fraction, min_sep


def parse_peak_finding_config(data):
    s = 'peak_finding_config'
    default = PeakFindingConfig()
    separation = default.separation
    size = default.size
    multiplicity = default.multiplicity
    height = default.height
    if data.get(s) is not None:
        d = data[s]
        if d.get('separation') is not None:
            Q = ureg.Quantity
            separation = Q(d['separation'])
            separation = separation.m_as("s")
        if d.get('prominence') is not None:
            size = float(d['prominence'])
        if d.get('multiplicity') is not None:
            multiplicity = int(d['multiplicity'])
        if d.get('height') is not None:
            height = float(d['height'])

    res = PeakFindingConfig(separation=separation, size=size, multiplicity=multiplicity, height=height)
    return s, res


def parse_svm_config(data):
    s = 'svm_config'
    default = SVMConfig()
    nu = default.nu
    kernel = default.kernel
    gamma = default.gamma
    degree = default.degree
    training_data = default.training_data
    if data.get(s) is not None:
        d = data[s]
        if d['nu'] is not None:
            nu = float(d['nu'])
        if d['kernel'] is not None:
            kernel = d['kernel']
        if d['gamma'] is not None:
            gamma = float(d['gamma'])
        if d['degree'] is not None:
            degree = int(d['degree'])
        if d['training_data'] is not None:
            training_data = d['training_data']

    res = SVMConfig(nu=nu, kernel=kernel, gamma=gamma, degree=degree, training_data=training_data)
    return s, res


def parse_time(s):
    fmt = "%Y-%m-%d %H:%M:%S"
    nofrag = s
    frag = None
    if s.find('.') >= 0:
        nofrag, frag = s.split('.')

    dt = datetime.datetime.strptime(nofrag, fmt)
    if frag is not None:
        dt = dt.replace(microsecond=int(1E3*int(frag)))

    return dt
