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
import argparse
import time
from ketos.data_handling.parsing import WinFun
import src.parsing as pa
from ketos.audio_processing.audio import AudioSignal, TimeStampedAudioSignal
from ketos.audio_processing.spectrogram import MagSpectrogram
from ketos.data_handling.data_handling import AudioSequenceReader


batch_no = 0


def make_spec(signal, config):

    hamming = False
    if config.window_function == WinFun.HAMMING:
        hamming = True

    # make spectrogram
    spec = MagSpectrogram(audio_signal=signal, winlen=config.window_size, winstep=config.step_size,\
            hamming=hamming, timestamp=signal.begin(), decibel=True)

    return spec


def apply_filters(spec, filters):

    # apply filters
    for f in filters:
        #print('  -',f.name)
        f.apply(spec)

    # dataframe for output data
    t = spec.time_labels()
    f = spec.frequency_labels()
    df = pd.DataFrame({'time': t})
    for i in range(len(f)):
        df[f[i]] = spec.image[:,i]

    # use date-time column as index
    df = df.set_index('time')
    df = df.sort_index(ascending=True)

    return df


def process(signal, config, filters):

    global batch_no
    batch_no += 1

    # make spectrogram
    spec = make_spec(signal=signal, config=config)

    # apply filters
    filtered_data = apply_filters(spec=spec, filters=filters)

    return filtered_data


def parse_args():

    # configure parser
    parser = argparse.ArgumentParser(description='Split audio signal into frequency bands and produce a time series of the noise magnitude in each band.')
    parser.add_argument('-c', '--config_file', type=str, help='path to json configuration file.', default='settings.json')
    parser.add_argument('-i', '--input', type=str, help='path to the wav file to be analyzed or directory containing multiple wav files.', default='./')
    parser.add_argument('-o', '--output_file', type=str, help='path to output csv file', default='output.csv')
    parser.add_argument('-r', '--recursive_search', action='store_true', help='Include subdirectories in search for wav files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print progress updates during processing')

    # parse command-line args
    args = parser.parse_args()

    return args


def main():

    start_time = time.time()

    # parse command-line args
    args = parse_args()
    config_file = args.config_file
    input_dir = args.input
    output_file = args.output_file
    recursive = args.recursive_search
    verbose = args.verbose

    # parse settings.json
    fmt, batch_size, detector_config_file = pa.parse_settings(config_file)

    # parse detector configuration file
    spectr_config, filters = pa.parse_preproc_config(detector_config_file)

    # create reader 
    reader = AudioSequenceReader(source=input_dir, recursive_search=recursive, rate=spectr_config.rate, datetime_fmt=fmt, verbose=verbose)

    if verbose:
        print(" Found {0} files".format(len(reader.files)))

    # loop over batches
    outputs = list()
    filtered_data = None
    while not reader.finished():

        if verbose:
            global batch_no
            print(" Processing batch #{0} ...".format(batch_no+1))

        batch = reader.next(size=batch_size) # read next chunk of data
        o = process(batch, spectr_config, filters) # process data
        outputs.append(o) # collect output

        # log of file names and times
        time_table = reader.log()

        # concatenate
        if filtered_data is None:
            filtered_data = pd.concat(outputs, ignore_index=False)
        else:
            filtered_data = pd.concat([filtered_data, outputs[-1]], ignore_index=False)

        # save to csv files
        rounded = filtered_data.round(3)
        rounded.to_csv(output_file)
        tt_file = output_file[:output_file.rfind('.')] + '_time_table.csv'
        time_table.to_csv(tt_file)

    print(" Processed data saved to: {0}".format(output_file))
    print(" Time table saved to: {0}".format(tt_file))

    # end script
    elapsed_time = time.time() - start_time
    print(time.strftime(" Elapsed time: %H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == '__main__':
   main()
