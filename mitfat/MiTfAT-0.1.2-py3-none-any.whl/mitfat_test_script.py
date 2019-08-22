# %% __main__
if __name__ == "__main__":
    import os
    # %% flags
    if_save_eps = False  # if save plots in .eps format. All are saved in .png format by default.
                        # if setting it to True casues some warning messages, just ignore them.

    if_plot_basics = True  # plot normalised time-series, or raw if you do not normalise the data
    if_plot_lin_reg = True  # plots of linearised siganls, separately for each time-degment.
    if_plot_raw = True  #  plot raw time-series

    if_cluster = True  # if cluster and then dave plots for [2, ..., 9] clusters.
    if_cluster_hiararchical = True  # if hierarchical cluster and then save.

    if_detrend = True  # if detrend and save

    # %% have a copy of the config file in your current working directory
    #   for future references
    # this config file includes info on what data to load and from where
    from mitfat.file_io import print_info
    print_info('sample_info_file.txt')

    # %% there is a info_file and sample dataset accompanying the code
    # the rest of this example file is based on that dataset
    import mitfat
    from mitfat.file_io import read_data
    import pkg_resources
    info_file = pkg_resources.resource_filename('mitfat', 'sample_info_file.txt')
    DATA_PATH = pkg_resources.resource_filename('mitfat', 'datasets/')
    dataset1 = read_data(info_file)
    print(dataset1.description)

    # Basic plots
    if if_plot_basics:
       dataset1.plot_basics()

    if if_plot_lin_reg:
       dataset1.plot_basics('lin_reg')

    if if_plot_raw:
       dataset1.plot_basics('raw')

    if if_cluster:
        ###
        X_train = dataset1.data_normalised
        X_train_label = 'RAW_Normalised'  # just used in plot titles and folder names
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [2, 3, 4, 5,]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = \
                dataset1.cluster(X_train, num_clusters)
            dataset1.save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1.plot_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
        ###
        X_train = dataset1.data_mean
        X_train_label = 'Mean_Normalised'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [3, 4, 5, 6,]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = \
                dataset1.cluster(X_train, num_clusters)
            dataset1.save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1.plot_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
        ###
        X_train = dataset1.line_reg_slopes
        X_train_label = 'Lin_regression_slopes_per_segments'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [5, 6, 7, 8,]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = \
                dataset1.cluster(X_train, num_clusters)
            dataset1.save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1.plot_clusters(X_train, X_train_label,
                                    cluster_labels,
                                    cluster_centroid, if_slopes=True)
        ###
        X_train = dataset1.mean_segments
        X_train_label = 'Mean_Segments'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [2, 3, 4, 5,]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = dataset1.cluster(X_train, num_clusters)
            dataset1.save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1.plot_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)

    if if_cluster_hiararchical:
        signal = 'raw'
        dataset1.cluster_hierarchial(signal, if_save_plot=True)

    if if_detrend:
        dataset1.detrend()
