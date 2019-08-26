# This is a script to produce a Gaussian process surrogate from
# Numerical relativity waveform data.


import click
import matplotlib.pyplot as plt

import astropy
from astropy.table import Table
from heron import data, regression, corner, priors, sampling
import os
import heron
from glob import glob
import numpy as np


## Loading data



@click.command()
@click.option("--table",
              default='/home/daniel/data/gravitational-waves/gt-new/training_waveforms.txt',
              help="The parameter table for the waveforms.")
@click.option("--training", default="/home/daniel/data/gravitational-waves/gt-old/",
              help="The location of the data files. This location will be searched recursively for data files.")
@click.option("--test", default="/home/daniel/data-nosync/GW_Waveforms-master/Waveform_txtFiles/GT/")
@click.option("--label", default=None, help="The label for this data set. If no label is provided one will be generated at random.")
@click.option("--inspiral", default=50, help="The number of data points to keep for the inspiral.")
@click.option("--ringdown", default=50, help="The number of data points to keep for the post-merger.")
@click.option("--decimate", default=10, help="The factor by which to reduce the number of datapoints.")
def cli(table, training, test, label, inspiral, ringdown, decimate):
    """
    This script generates the BBH training data from the data files.
    """

    from awesome_codename import generate_codename
    if not label: label = generate_codename()

    inspiral = -1 * inspiral
    columns = ['t', '$q$', '$a_{1x}$', '$a_{1y}$', '$a_{1z}$',
               '$a_{2x}$', '$a_{2y}$', '$a_{2z}$',
               '$L_x$', '$L_y$', '$L_z$']
    headers = ['Index', 'Name', 'tag',
               '$q$',
               '$a_{1x}$', '$a_{1y}$', '$a_{1z}$',
               '$a_{2x}$', '$a_{2y}$', '$a_{2z}$',
               '$L_x$', '$L_y$', '$L_z$',
               'mf', 'af', 'mW']
    
    def find_data(tag, path = training, suffix="asc"):
        """
        Find the data files which contain the NR data for a given tag.
        """
        result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*{}*.{}'.format(tag, suffix)))]
        return result

    t = Table.read(table, format="ascii", names=headers)

    test_waveforms = []
    test_parameters = []
    training_x = []
    training_y = []
    training_waveforms = []
    training_parameters = []
    testing_x = []
    testing_y = []
    waveformsinc = 0
    waveform_table = []
    

    for j,row in enumerate(t):
        # Use the tag to find the data file.
        filetype = "train"
        waveform_file = find_data(row['tag'])
        # Some files are missing from the training set and can be added to the test set, or skipped.
        if len(waveform_file)!=1:
            try:
                waveform_file = find_data(row['tag'], test, "txt")
                if len(waveform_file)!=1: continue
                filetype = "test"
            except IOError:
                continue

        data = np.loadtxt(waveform_file[0])
        # Align the waveforms to the maximum value
        data[:,0] = data[:,0] - data[np.argmax(data[:,1]),0]
        # Decimate the waveforms
        data = data[::decimate] # This is a bit hacky.
        times = data[:,0]
        if len(times)==0: continue

        ix_selection = (times>=inspiral) & (times<=ringdown)
        times = times[ix_selection]

        rowdata = np.zeros((len(columns), len(times)))
        for i, col in enumerate(columns):
            if i == 0: 
                rowdata[i,:] = data[:,0][ix_selection]
            else:
                rowdata[i,:] = np.tile(row[col], len(times))
        if filetype == "train":
            training_parameters.append(rowdata.T[0])
            training_y.append(data[:,1][ix_selection])
            training_x.append(np.atleast_2d(rowdata))
        else:
            test_parameters.append(rowdata.T[0])
            testing_y.append(data[:,2][ix_selection])
            testing_x.append(np.atleast_2d(rowdata))


    training_y = np.hstack(training_y)
    training_x = np.hstack(training_x)
    testing_y = np.hstack(testing_y)
    testing_x = np.hstack(testing_x)
    np.savetxt("training_x.dat", training_x)
    np.savetxt("training_y.dat", training_y)
    np.savetxt("testing_x.dat", testing_x)
    np.savetxt("testing_y.dat", testing_y)
