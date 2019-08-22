# -*- coding: utf-8 -*-

# pyrsr, A package providing relative spectral response functions for remote sensing instruments.
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Sensor specifications needed by pyrsr."""

from pandas import DataFrame
import numpy as np

sensors = {
    'AVNIR-2': {
        'satellite': 'ALOS',
        'sensor': 'AVNIR-2',
        'LBA': ['1', '2', '3', '4'],
    },

    'AST_full': {
        'satellite': 'Terra',
        'sensor': 'ASTER',
        'LBA': ['1', '2', '3N', '3B', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'],
    },

    'AST_V1': {
        'satellite': 'Terra',
        'sensor': 'ASTER',
        'subsystem': 'VNIR1',
        'LBA': ['1', '2', '3N'],
    },

    'AST_V2': {
        'satellite': 'Terra',
        'sensor': 'ASTER',
        'subsystem': 'VNIR2',
        'LBA': ['3B'],
    },

    'AST_S': {
        'satellite': 'Terra',
        'sensor': 'ASTER',
        'subsystem': 'SWIR',
        'LBA': ['4', '5', '6', '7', '8', '9'],
    },

    'AST_T': {
        'satellite': 'Terra',
        'sensor': 'ASTER',
        'subsystem': 'TIR',
        'LBA': ['10', '11', '12', '13', '14'],
        'thermal': ['10', '11', '12', '13', '14']
    },

    'TM4': {
        'satellite': 'Landsat-4',
        'sensor': 'TM',
        'subsystem': 'SAM',
        'LBA': ['1', '2', '3', '4', '5', '6', '7'],
        'LBA_sorted': ['1', '2', '3', '4', '5', '7', '6'],
        'thermal': ['6']
    },

    'TM5': {
        'satellite': 'Landsat-5',
        'sensor': 'TM',
        'subsystem': 'SAM',
        'LBA': ['1', '2', '3', '4', '5', '6', '7'],
        'LBA_sorted': ['1', '2', '3', '4', '5', '7', '6'],
        'thermal': ['6']
    },

    'TM7': {
        'satellite': 'Landsat-7',
        'sensor': 'ETM+',
        'subsystem': 'SAM',
        'LBA': ['1', '2', '3', '4', '5', '6L', '6H', '7', '8'],
        'LBA_sorted': ['1', '2', '3', '8', '4', '5', '7', '6L', '6H'],
        'pan': ['8'],
        'thermal': ['6L', '6H']
    },

    'LDCM': {
        'satellite': 'Landsat-8',
        'sensor': 'LDCM',
        'LBA': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        'LBA_sorted': ['1', '2', '3', '4', '5', '9', '6', '7', '8', '10', '11'],
        'LBA_after_AC': ['1', '2', '3', '4', '5', '6', '7'],
        'pan': ['8'],
        'thermal': ['10', '11']
    },

    'OLI_TIRS': {
        'satellite': 'Landsat-8',
        'sensor': 'OLI_TIRS',
        'LBA': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        'LBA_sorted': ['1', '2', '3', '4', '5', '9', '6', '7', '8', '10', '11'],
        'LBA_after_AC': ['1', '2', '3', '4', '5', '6', '7'],
        'pan': ['8'],
        'thermal': ['10', '11']
    },

    'OLI': {
        'satellite': 'Landsat-8',
        'sensor': 'OLI',
        'LBA': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'LBA_sorted': ['1', '2', '3', '4', '5', '9', '6', '7', '8'],
        'LBA_after_AC': ['1', '2', '3', '4', '5', '6', '7'],
        'pan': ['8']
    },

    'TIRS': {
        'satellite': 'Landsat-8',
        'sensor': 'TIRS',
        'LBA': ['10', '11'],
        'thermal': ['10', '11']
    },

    'SPOT1a': {
        'satellite': 'SPOT-1',
        'sensor': 'HRV1',
        'LBA': ['1', '2', '3', '4'],
        'pan': ['4'],
    },

    'SPOT2a': {
        'satellite': 'SPOT-2',
        'sensor': 'HRV1',
        'LBA': ['1', '2', '3', '4'],
        'pan': ['4'],
    },

    'SPOT3a': {
        'satellite': 'SPOT-3',
        'sensor': 'HRV1',
        'LBA': ['1', '2', '3', '4'],
        'pan': ['4'],
    },

    'SPOT4a': {
        'satellite': 'SPOT-4',
        'sensor': 'HRVIR1',
        'LBA': ['1', '2', '3', '4', '5'],
        'pan': ['5']
    },

    'SPOT5a': {
        'satellite': 'SPOT-5',
        'sensor': 'HRG1',
        'LBA': ['1', '2', '3', '4', '5'],
        'pan': ['5']
    },

    'SPOT1b': {
        'satellite': 'SPOT-1',
        'sensor': 'HRV2',
        'LBA': ['1', '2', '3', '4'],
        'pan': ['4'],
    },

    'SPOT2b': {
        'satellite': 'SPOT-2',
        'sensor': 'HRV2',
        'LBA': ['1', '2', '3', '4'],
        'pan': ['4'],
    },

    'SPOT3b': {
        'satellite': 'SPOT-3',
        'sensor': 'HRV2',
        'LBA': ['1', '2', '3', '4'],
        'pan': ['4'],
    },

    'SPOT4b': {
        'satellite': 'SPOT-4',
        'sensor': 'HRVIR2',
        'LBA': ['1', '2', '3', '4', '5'],
        'pan': ['5']
    },

    'SPOT5b': {
        'satellite': 'SPOT-5',
        'sensor': 'HRG2',
        'LBA': ['1', '2', '3', '4', '5'],
        'pan': ['5']
    },

    'RE1': {
        'satellite': 'RapidEye-1',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5'],
    },

    'RE2': {
        'satellite': 'RapidEye-2',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5'],
    },

    'RE3': {
        'satellite': 'RapidEye-3',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5'],
    },

    'RE4': {
        'satellite': 'RapidEye-4',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5'],
    },

    'RE5': {
        'satellite': 'RapidEye-5',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5'],
    },

    'S2A_full': {
        'satellite': 'Sentinel-2A',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '9', '10', '11', '12'],
        'LBA_after_AC': ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '11', '12'],
    },

    'S2B_full': {
        'satellite': 'Sentinel-2B',
        'sensor': 'MSI',
        'LBA': ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '9', '10', '11', '12'],
        'LBA_after_AC': ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '11', '12'],
    },

    'S2A10': {
        'satellite': 'Sentinel-2A',
        'sensor': 'MSI',
        'subsystem': 'S2A10',
        'LBA': ['2', '3', '4', '8'],
    },

    'S2A20': {
        'satellite': 'Sentinel-2A',
        'sensor': 'MSI',
        'subsystem': 'S2A20',
        'LBA': ['5', '6', '7', '8A', '11', '12'],
    },

    'S2A60': {
        'satellite': 'Sentinel-2A',
        'sensor': 'MSI',
        'subsystem': 'S2A60',
        'LBA': ['1', '9', '10'],
        'LBA_after_AC': ['1'],
    },

    'S2B10': {
        'satellite': 'Sentinel-2B',
        'sensor': 'MSI',
        'subsystem': 'S2A10',
        'LBA': ['2', '3', '4', '8'],
    },

    'S2B20': {
        'satellite': 'Sentinel-2B',
        'sensor': 'MSI',
        'subsystem': 'S2A20',
        'LBA': ['5', '6', '7', '8A', '11', '12'],
    },

    'S2B60': {
        'satellite': 'Sentinel-2B',
        'sensor': 'MSI',
        'subsystem': 'S2A60',
        'LBA': ['1', '9', '10'],
        'LBA_after_AC': ['1'],
    },

}

df_sensors = \
    DataFrame\
    .from_dict(sensors, orient='index')\
    .loc[:, ['satellite', 'sensor', 'subsystem', 'LBA', 'LBA_sorted', 'LBA_after_AC', 'pan', 'thermal']]


# class SensorSpecs(DataFrame):
#     def __init__(self, satellite, sensor, subsystem='', **kwargs):
#         super(SensorSpecs, self).__init__()
#
#         self.satellite =


def get_sensorspecs(satellite, sensor, subsystem=''):
    if (satellite, sensor) in [('Landsat-4', 'TM'), ('Landsat-5', 'TM'), ('Landsat-7', 'ETM+')] and not subsystem:
        subsystem = 'SAM'

    if satellite.startswith('RapidEye'):
        satellite = 'RapidEye-5'

    sub = df_sensors[(df_sensors.satellite == satellite) &
                     (df_sensors.sensor == sensor) &
                     ((df_sensors.subsystem == subsystem) if subsystem else df_sensors.subsystem.isnull())].copy()

    if len(sub.index) == 0:
        raise ValueError("No sensor specifications for combination '%s' '%s' '%s' found."
                         % (satellite, sensor, subsystem))

    elif len(sub.index) > 1:
        raise ValueError("Multiple sensor specifications found for combination '%s' '%s' '%s': \n %s"
                         % (satellite, sensor, subsystem, sub))

    specs = sub.to_dict(orient='records')[0]
    specs = dict(zip(specs.keys(), [v if v is not np.nan else None for v in specs.values()]))

    return specs


def get_LayerBandsAssignment(satellite, sensor, subsystem='', no_thermal=False, no_pan=False, after_ac=False,
                             sort_by_cwl=False):
    specs = get_sensorspecs(satellite, sensor, subsystem)
    LBA = specs['LBA']

    if sort_by_cwl and specs['LBA_sorted']:
        LBA = specs['LBA_sorted']

    if no_thermal and specs['thermal']:
        LBA = [i for i in LBA if i not in specs['thermal']]

    if no_pan and specs['pan']:
        LBA = [i for i in LBA if i not in specs['pan']]

    if after_ac and specs['LBA_after_AC']:
        LBA = [i for i in LBA if i in specs['LBA_after_AC']]

    return LBA
