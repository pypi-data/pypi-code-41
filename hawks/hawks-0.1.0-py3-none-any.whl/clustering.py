import functools
from datetime import datetime
from pathlib import Path
from itertools import zip_longest
import warnings
import inspect
# from inspect import getfullargspec

import numpy as np
import pandas as pd
import sklearn.cluster
import sklearn.mixture
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score

import hawks.problem_features

def define_cluster_algs(seed):
    cluster_algs = {
        "K-Means++": {
            "class": getattr(sklearn.cluster, "KMeans"),
            "kwargs": {
                "n_clusters": None,
                "random_state": seed
            }
        },
        "Single-Linkage": {
            "class": getattr(sklearn.cluster, "AgglomerativeClustering"),
            "kwargs": {
                "n_clusters": None,
                "linkage": "single"
            }
        },
        "Average-Linkage": {
            "class": getattr(sklearn.cluster, "AgglomerativeClustering"),
            "kwargs": {
                "linkage": "average",
                "n_clusters": None
            }
        },
        "Single-Linkage (Double)": {
            "class": getattr(sklearn.cluster, "AgglomerativeClustering"),
            "kwargs": {
                "linkage": "single",
                "n_clusters": 2.0
            }
        },
        "Average-Linkage (Double)": {
            "class": getattr(sklearn.cluster, "AgglomerativeClustering"),
            "kwargs": {
                "linkage": "average",
                "n_clusters": 2.0
            }
        },
        "GMM": {
            "class": getattr(sklearn.mixture, "GaussianMixture"),
            "kwargs": {
                "n_components": None,
                "random_state": seed
            }
        }
    }
    return cluster_algs

def run_clustering(datasets=None, label_sets=None, generator=None, subset=None, save=True, seed=None, df=None, source="hawks", problem_features=False):
    # Something needs to be given
    if generator is None and datasets is None:
        raise ValueError(f"No generator or datasets have been given - there's nothing to evaluate!")
    # If save is true but no generator, need to set a save location
    if generator is None and save is True:
        base_folder = Path.cwd() / "hawks_experiments" / f"clustering_{datetime.today().strftime('%Y_%m_%d-%H%M%S')}"
        base_folder.mkdir(parents=True)
        # No folder, so create one in similar way to animate?
    elif generator is not None and (save is True or generator.any_saving):
        base_folder = self.base_folder
    # If the labels are in the data, set flag
    if label_sets == "data":
        labels_in_data = True
        label_sets = [] # To allow len and iteration calls
    else:
        labels_in_data = False
    # Check if any corresponding labels are missing
    if not labels_in_data and (len(datasets) > len(label_sets)):
        warnings.warn(
            message=f"More datasets have been provided than labels, so ARI etc. results may be incomplete",
            category=UserWarning
        )
    # Get the problem feature functions if needed
    if problem_features:
            feature_funcs = dict(
            inspect.getmembers(hawks.problem_features, inspect.isfunction)
        )
    # Set the seed used for stochastic algs
    # Provided seed has priority, then seed from generator
    if seed is None and generator is not None:
        seed = generator.global_seed
    # Otherwise random seed, but raise warning due to unreliable reproducibility
    elif seed is None and generator is None:
        seed = np.random.randint(100)
        warnings.warn(
            message=f"No seed was provided, using {seed} instead",
            category=UserWarning
        )
    # Get the defined clustering algs
    cluster_algs = define_cluster_algs(seed)
    # If a subset of algorithms is given, then select only those
    if subset is not None:
        alg_dict = {}
        for alg_name in subset:
            try:
                alg_dict[alg_name] = cluster_algs[alg_name]
            except KeyError as e:
                raise Exception(f"{alg_name} cannot be found, must be in: {cluster_algs.keys()}") from e
    # Otherwise we are running all defined algs
    else:
        alg_dict = cluster_algs
    # If not dataframe is given, create a new one
    if df is None:
        # Initialize the dataframe
        df = pd.DataFrame()
    # Loop over the datasets
    for dataset_num, (data, labels) in enumerate(zip_longest(datasets, label_sets)):
        # If the data is actually a path to the data, then load it in
        if isinstance(data, (str, Path)):
            # Read in the data
            data = np.genfromtxt(
                data,
                delimiter=","
            )
            # Extract the labels
            if labels_in_data:
                # Separate the data and labels
                labels = data[:, -1]
                data = data[:, :-1]
        # If the labels are a path, extract them
        if isinstance(labels, (str, Path)):
            # Read in the labels
            labels = np.genfromtxt(
                labels,
                delimiter=","
            )
            ### Might need to do some reshaping here? ###
        if problem_features:
            problem_feature_vals = calc_problem_features(data, feature_funcs)
        # Loop over the dict of clustering algorithms
        for name, d in alg_dict.items():
            # Add in the number of clusters
            d["kwargs"] = determine_num_clusters(name, d["kwargs"], labels)
            # Pass the kwargs to the relevant algorithm class
            alg = d["class"](**d["kwargs"])
            # Run the algorithm
            alg.fit(data)
            # Predict labels and compare if we have the truth
            if labels is not None:
                # Obtain labels for this algorithm on this dataset
                if hasattr(alg, "labels_"):
                    labels_pred = alg.labels_.astype(np.int)
                else:
                    labels_pred = alg.predict(data)
                ari_score = adjusted_rand_score(labels, labels_pred)
                ami_score = adjusted_mutual_info_score(labels, labels_pred)
            # No labels, so just set scores to NaN
            else:
                ari_score = np.nan
                ami_score = np.nan
            # Store the specific info for this dataset, for this algorithm
            d = {
                "source": source,
                "dataset": dataset_num,
                "cluster_alg": name,
                "ari": ari_score,
                "ami": ami_score
            }
            # Add the problem feature values if needed
            if problem_features:
                d.update(problem_feature_vals)
            # Calculate evaluation metrics and add to df
            df = df.append(
                d,
                ignore_index=True
            )
    # Save the results if specified
    if save:
        df.to_csv(
            base_folder / "cluster_results.csv",
            sep=",",
            index=False
        )
    return df

def determine_num_clusters(col_name, alg_kwargs, labels):
    # Fix annoying inconsistency with sklearn arg names
    if col_name == "GMM":
        arg = "n_components"
    else:
        arg = "n_clusters"
    # Check that this alg takes arg as input
    if arg in alg_kwargs:
        # Calc the actual number of clusters
        num_clusts = np.unique(labels).shape[0]
        # Set this as the target
        if alg_kwargs[arg] is None:
            alg_kwargs[arg] = num_clusts
        # Use a multiplier if given
        elif isinstance(alg_kwargs[arg], float):
            multiplier = alg_kwargs[arg]
            alg_kwargs[arg] = num_clusts * multiplier
    return alg_kwargs

def calc_problem_features(data, feature_funcs):
    problem_feature_vals = {}
    # Calculate the feature values for this problem/data
    for name, func in feature_funcs:
        problem_feature_vals[f"f_{name}"] = func(data)
    return problem_feature_vals