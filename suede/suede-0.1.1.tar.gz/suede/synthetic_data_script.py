import numpy as np
from synthetic_data import generate_data as gd
from visualization_tools import neuron_hist as nh
from visualization_tools import avg_firing_rates_by_dir as af


if __name__ == "__main__":
    # example of generating desired experiment data based on specific input parameters (these are for a 16-target reach)

    # try altering any of these following input parameters
    num_targets = 16
    base_firing_rate = 23.75
    num_trials = 100
    # time before target onset
    bt = 250
    # time after target onset
    at = 635
    # direction list created with degrees (0 to 360)
    dir_list = np.arange(0, 360, 360 / num_targets)
    # distance to target in cm
    d = 10

    # use the generate_data function to create synthetic training data and test data (replace this with your real data
    # if available)
    data = gd.generate_data(trials_per_dir=num_trials * np.ones(num_targets), d=d,
                            reach_dirs=dir_list, preferred_dirs=dir_list, base_firing_rate=base_firing_rate,
                            scaling_factor=base_firing_rate / 10, bt=bt, at=at)

    # extract values of the resulting structured array using keys
    spike_data = data['spike_data']
    actual_dirs = data['actual_dir']

    # plot histogram of average spike counts over total trial time for neuron 0 for reach tasks at 0 degrees
    nh.neuron_hist(spike_data=spike_data, actual_dirs=actual_dirs, neuron_idx=0, reach_dir=0, bin_width=10,
                   bt=250, at=635)

    # plot the average firing rates of all neurons across all reach tasks at 90 degrees
    af.avg_firing_rates_by_dir(spike_data=spike_data, actual_dirs=actual_dirs, reach_dirs=dir_list,
                               reach_dir=90, plot=True)
