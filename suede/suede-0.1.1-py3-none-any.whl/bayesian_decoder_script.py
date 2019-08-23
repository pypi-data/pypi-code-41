import matplotlib.pyplot as plt
import numpy as np
from suede.bayesian.bayesian_decoder import bayesian_decoder
from suede.synthetic_data.generate_data import generate_data
from suede.visualization_tools.calc_accuracy import calc_accuracy


# example of how to run the bayesian decoder with 16-target reach data
if __name__ == "__main__":

    # try altering any of these following input parameters
    num_targets = 16
    base_firing_rate = 23.75
    num_trials_train = 100
    num_trials_test = 10
    # time before target onset
    bt = 250
    # time after target onset
    at = 635
    # direction list created with degrees (0 to 360)
    dir_list = np.arange(0, 360, 360 / num_targets)
    # distance to target in cm
    d = 10

    # use the generate_data function to create synthetic training data and test data (replace these with your real data
    # if available)
    train_data = generate_data(trials_per_dir=num_trials_train * np.ones(num_targets), d=d,
                               reach_dirs=dir_list, preferred_dirs=dir_list, base_firing_rate=base_firing_rate,
                               scaling_factor=base_firing_rate / 10, bt=bt, at=at)
    test_data = generate_data(trials_per_dir=num_trials_test * np.ones(num_targets), d=d,
                              reach_dirs=dir_list, preferred_dirs=dir_list, base_firing_rate=base_firing_rate,
                              scaling_factor=base_firing_rate / 10, bt=bt, at=at)

    # extract values of the resulting structured array using keys
    train_spike_data = train_data['spike_data']
    train_dirs = train_data['actual_dir']

    test_spike_data = test_data['spike_data']
    test_dirs = test_data['actual_dir']

    # the scalar 0.2 value was chosen due to the assumption that some of the time post-target appearance should not be
    # considered in the integration time due to the subject's reaction time 0.6 was arbitrarily chosen to be greater
    # than 0.2 and less than 1
    predictions = bayesian_decoder(train_spike_data, train_dirs, test_spike_data, dir_list,
                                   tint_start=0.2*at, tint_end=0.6*at, bt=bt)

    # calculate the accuracy for a single implementation of the decoder
    accuracy = calc_accuracy(predictions, test_dirs)

    # plot accuracies for a number of different predictions
    # in this example, each prediction is a result of varying the length of t_int with the following parameters:
    step_size = 10

    # the scalar 0.2 value was chosen due to the assumption that some of the time post-target appearance should not be
    # considered in the integration time due to the subject's reaction time
    # 0.3 and 0.6 were arbitrarily chosen at two values greater than 0.2 and less than 1
    tint_start = 0.2 * at
    first_tint_end = int(0.3 * at)
    last_tint_end = int(0.6 * at)
    tint_ends = np.arange(first_tint_end, last_tint_end, step_size)

    # matrix of total predictions takes the shape of # of different sets of predictions and # of trials per
    # prediction set
    num_predictions = len(tint_ends)
    num_trials = len(predictions)
    all_predictions = np.zeros((num_predictions, num_trials))

    # get the set of the predictions via the bayesian_decoder function for each set of inputs
    for i in range(num_predictions):
        all_predictions[i] = bayesian_decoder(train_spike_data, train_dirs, test_spike_data, dir_list,
                                              tint_start, tint_ends[i], bt=bt)

    # activate the "many" variable in calc_accuracy to calculate the accuracies of your sets of predictions
    accuracies = calc_accuracy(predicted=all_predictions, expected=test_dirs, many=True)

    # plot against the length of tint (which is what was varied in this example)
    with plt.style.context('ggplot'):
        plt.plot(tint_ends - tint_start, accuracies)
        plt.title("Bayesian Decoder Accuracy vs. Length of T-int")
        plt.xlabel("Length of T-int (ms)"), plt.ylabel("Accuracy (%)")
        plt.show()

