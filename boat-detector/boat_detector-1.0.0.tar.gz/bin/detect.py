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

import os
import numpy as np
import pandas as pd
import argparse
import datetime
from pint import UnitRegistry
import math
from ketos.utils import detect_peaks
from ketos.data_handling.parsing import str2bool
import src.parsing as pa
from src.parsing import Detector

import matplotlib
viz = os.environ.get('DISABLE_VIZ')
if viz is not None:
    if int(viz) == 1:
        matplotlib.use('Agg')

import matplotlib.pyplot as plt


def extract_time_res(df):
    time_res = math.inf
    for i in range(1,len(df.index)):
        t0 = pa.parse_time(df.index[i-1])
        t1 = pa.parse_time(df.index[i])
        delta = 1E-6 * (t1 - t0).microseconds
        if delta < time_res and delta > 0:
            time_res = delta

    return time_res


def zeros_and_ones(x):
    x = ((-1)*x + 1) / 2
    x = x.astype(int)
    return x


def parse_args():

    # configure parser
    parser = argparse.ArgumentParser(description='Perform outlier- and peak analysis of time-series data.')
    parser.add_argument('-c', '--config_file', type=str, help='path to json configuration file.', default='settings.json')
    parser.add_argument('-i', '--input_file', type=str, help='.csv file containing time-series data to be analyzed.', default='output.csv')
    parser.add_argument('-o', '--output_file', type=str, help='.csv file where analysis report will be outputted.', default='detections.csv')
    parser.add_argument('-S', '--show_graph', action='store_true', help='Show time-series data')

    # parse command-line args
    args = parser.parse_args()
    
    return args


def main():

    # parse command-line args
    args = parse_args()

    config_file = args.config_file
    input_file = args.input_file
    output_file = args.output_file
    show_graph = args.show_graph

    # time table
    i = input_file.rfind('.')
    time_table = input_file[:i] + '_time_table.csv'

    # read input data into pandas dataframe
    df0 = pd.read_csv(input_file)

    assert df0.shape[0] >= 2, "Input data should have at least two rows of data"

    # parse settings.json
    _, _, detector_config_file = pa.parse_settings(config_file)   

    # read configuration file
    data_series, detectors, configs, outlier_fraction, min_sep = pa.parse_detect_config(detector_config_file)

    # extract relevant columns
    data_series.append('time')
    X = df0[data_series]

    # use time column as index
    X = X.set_index('time')

    # dataframe for output data
    df = pd.DataFrame(X.index)
    df = df.set_index('time')


    #=================
    # peak detection #
    #=================

    if Detector.PEAK_FINDING in detectors:
        cfg = configs['peak_finding_config']
        time_res = extract_time_res(X)
        dist = max(1, int(cfg.separation / time_res))
        df['Peak Finding'] = detect_peaks(X, distance=dist, prominence=cfg.size, multiplicity=cfg.multiplicity, height=cfg.height)


    #====================
    # outlier detection #
    #====================

    # Robust covariance
    if Detector.ELLIPTIC_ENVELOPE in detectors:
        from sklearn.covariance import EllipticEnvelope
        ee = EllipticEnvelope(contamination=outlier_fraction)
        ee.fit(X) 
        df['Elliptic Envelope'] = pred = zeros_and_ones(ee.predict(X))

    # Local Outlier Factor
    if Detector.LOCAL_OUTLIER_FACTOR in detectors:
        from sklearn.neighbors import LocalOutlierFactor
        lof = LocalOutlierFactor(contamination=outlier_fraction)
        df['Local Outlier Factor'] = zeros_and_ones(lof.fit_predict(X))

    # Isolation Forest
    if Detector.ISOLATION_FOREST in detectors:
        from sklearn.ensemble import IsolationForest
        isofor = IsolationForest(contamination=outlier_fraction)
        isofor.fit(X) 
        df['Isolation Forest'] = zeros_and_ones(isofor.predict(X))


    #================
    # One-class SVM #
    #================

    if Detector.ONE_CLASS_SVM in detectors:
        from sklearn import svm
        cfg = configs['svm_config']
        clf = svm.OneClassSVM(nu=cfg.nu, kernel=cfg.kernel, degree=cfg.degree, gamma=cfg.gamma)
        df_train = pd.read_csv(cfg.training_data)
        X_train = df_train[data_series]
        X_train = X_train.set_index('time')
        # fit
        clf.fit(X_train)
        # predict
        df['One-class SVM'] = zeros_and_ones(clf.predict(X))


    #===================================================
    # Count time-separated anomalies and create output #
    #===================================================

    # count time-separated anomalies
    s = np.sum(df, axis=1)
    n = s.shape[0]
    sep = 0
    times = list()
    for i in range(0,n):
        tnow = pa.parse_time(df.index[i])
        if i > 0:
            tprev = pa.parse_time(df.index[i-1])
            delta = (tnow - tprev).total_seconds()
            sep += delta
        if (s[i] > 0 and (sep > min_sep or i == 0)):
            sep = 0
            times.append(tnow)

    df_out = pd.DataFrame(columns=['time'])
    df_out['time'] = np.array(times)

    # if time table exists, determine file name and 'local time'
    if time_table != None:
        df_tt = pd.read_csv(time_table)
        df_tt = df_tt.sort_index(ascending=False, axis=0)
        fnames = list()
        times = list()
        for t in df_out['time']:
            for _, row in df_tt.iterrows():
                t0 = pa.parse_time(row['time'])
                f = row['file']
                dt = (t0 - t).total_seconds()
                if (dt < 0):
                    fnames.append(f)
                    times.append(-dt)
                    break
        df_out['file_name'] = np.array(fnames)
        df_out['seconds_from_start_of_file'] = np.array(times)

    # save detections file
    df_out.to_csv(output_file)
    print(' {0} boats detected'.format(len(times)))
    print(' Detection report saved to: {0}'.format(output_file))


    # plot
    if show_graph:
        ax = plt.gca()
        ax.set_xlabel('Time')
        ax.set_ylabel('Signal')
        n = len(X.index.values)
        xticks = [0, int(n/2), n-1]
        X.plot(y=X.columns, xticks=xticks, ax=ax)
        plt.show()


if __name__ == '__main__':
   main()
