from __future__ import division

import logging
import math
import os
import shutil
import time
import warnings
from builtins import zip
from datetime import datetime

import cloudpickle
import numpy as np
import pandas as pd

from featuretools.computational_backends.feature_set import FeatureSet
from featuretools.computational_backends.feature_set_calculator import (
    FeatureSetCalculator
)
from featuretools.computational_backends.utils import (
    bin_cutoff_times,
    create_client_and_cluster,
    gather_approximate_features,
    gen_empty_approx_features_df,
    save_csv_decorator
)
from featuretools.entityset.relationship import RelationshipPath
from featuretools.feature_base import AggregationFeature, FeatureBase
from featuretools.utils import Trie
from featuretools.utils.gen_utils import make_tqdm_iterator
from featuretools.utils.wrangle import _check_time_type
from featuretools.variable_types import (
    DatetimeTimeIndex,
    NumericTimeIndex,
    PandasTypes
)

logger = logging.getLogger('featuretools.computational_backend')

PBAR_FORMAT = "Elapsed: {elapsed} | Progress: {l_bar}{bar}"
PBAR_FORMAT_REMAINING = PBAR_FORMAT + "| Remaining: {remaining}"


def calculate_feature_matrix(features, entityset=None, cutoff_time=None, instance_ids=None,
                             entities=None, relationships=None,
                             cutoff_time_in_index=False,
                             training_window=None, approximate=None,
                             save_progress=None, verbose=False,
                             chunk_size=None, n_jobs=1, dask_kwargs=None):
    """Calculates a matrix for a given set of instance ids and calculation times.

    Args:
        features (list[:class:`.FeatureBase`]): Feature definitions to be calculated.

        entityset (EntitySet): An already initialized entityset. Required if `entities` and `relationships`
            not provided

        cutoff_time (pd.DataFrame or Datetime): Specifies at which time to calculate
            the features for each instance. The resulting feature matrix will use data
            up to and including the cutoff_time. Can either be a DataFrame with
            'instance_id' and 'time' columns, DataFrame with the name of the
            index variable in the target entity and a time column, or a single
            value to calculate for all instances. If the dataframe has more than two columns, any additional
            columns will be added to the resulting feature matrix.

        instance_ids (list): List of instances to calculate features on. Only
            used if cutoff_time is a single datetime.

        entities (dict[str -> tuple(pd.DataFrame, str, str)]): dictionary of
            entities. Entries take the format
            {entity id: (dataframe, id column, (time_column))}.

        relationships (list[(str, str, str, str)]): list of relationships
            between entities. List items are a tuple with the format
            (parent entity id, parent variable, child entity id, child variable).

        cutoff_time_in_index (bool): If True, return a DataFrame with a MultiIndex
            where the second index is the cutoff time (first is instance id).
            DataFrame will be sorted by (time, instance_id).

        training_window (Timedelta or str, optional):
            Window defining how much time before the cutoff time data
            can be used when calculating features. If ``None``, all data before cutoff time is used.
            Defaults to ``None``.

        approximate (Timedelta or str): Frequency to group instances with similar
            cutoff times by for features with costly calculations. For example,
            if bucket is 24 hours, all instances with cutoff times on the same
            day will use the same calculation for expensive features.

        verbose (bool, optional): Print progress info. The time granularity is
            per chunk.

        chunk_size (int or float or None): maximum number of rows of
            output feature matrix to calculate at time. If passed an integer
            greater than 0, will try to use that many rows per chunk. If passed
            a float value between 0 and 1 sets the chunk size to that
            percentage of all rows. if None, and n_jobs > 1 it will be set to 1/n_jobs

        n_jobs (int, optional): number of parallel processes to use when
            calculating feature matrix.

        dask_kwargs (dict, optional): Dictionary of keyword arguments to be
            passed when creating the dask client and scheduler. Even if n_jobs
            is not set, using `dask_kwargs` will enable multiprocessing.
            Main parameters:

            cluster (str or dask.distributed.LocalCluster):
                cluster or address of cluster to send tasks to. If unspecified,
                a cluster will be created.
            diagnostics port (int):
                port number to use for web dashboard.  If left unspecified, web
                interface will not be enabled.

            Valid keyword arguments for LocalCluster will also be accepted.

        save_progress (str, optional): path to save intermediate computational results.
    """
    assert (isinstance(features, list) and features != [] and
            all([isinstance(feature, FeatureBase) for feature in features])), \
        "features must be a non-empty list of features"

    # handle loading entityset
    from featuretools.entityset.entityset import EntitySet
    if not isinstance(entityset, EntitySet):
        if entities is not None and relationships is not None:
            entityset = EntitySet("entityset", entities, relationships)

    target_entity = entityset[features[0].entity.id]
    pass_columns = []

    if not isinstance(cutoff_time, pd.DataFrame):
        if isinstance(cutoff_time, list):
            raise TypeError("cutoff_time must be a single value or DataFrame")

        if cutoff_time is None:
            if entityset.time_type == NumericTimeIndex:
                cutoff_time = np.inf
            else:
                cutoff_time = datetime.now()

        if instance_ids is None:
            index_var = target_entity.index
            df = target_entity._handle_time(target_entity.df,
                                            time_last=cutoff_time,
                                            training_window=training_window)
            instance_ids = df[index_var].tolist()

        cutoff_time = [cutoff_time] * len(instance_ids)
        map_args = [(id, time) for id, time in zip(instance_ids, cutoff_time)]
        cutoff_time = pd.DataFrame(map_args, columns=['instance_id', 'time'])

    cutoff_time = cutoff_time.reset_index(drop=True)
    # handle how columns are names in cutoff_time
    # maybe add _check_time_dtype helper function
    if "instance_id" not in cutoff_time.columns:
        if target_entity.index not in cutoff_time.columns:
            raise AttributeError('Name of the index variable in the target entity'
                                 ' or "instance_id" must be present in cutoff_time')
        # rename to instance_id
        cutoff_time.rename(columns={target_entity.index: "instance_id"}, inplace=True)

    if "time" not in cutoff_time.columns:
        # take the first column that isn't instance_id and assume it is time
        not_instance_id = [c for c in cutoff_time.columns if c != "instance_id"]
        cutoff_time.rename(columns={not_instance_id[0]: "time"}, inplace=True)

    # Check that cutoff_time time type matches entityset time type
    if entityset.time_type == NumericTimeIndex:
        if cutoff_time['time'].dtype.name not in PandasTypes._pandas_numerics:
            raise TypeError("cutoff_time times must be numeric: try casting "
                            "via pd.to_numeric(cutoff_time['time'])")
    elif entityset.time_type == DatetimeTimeIndex:
        if cutoff_time['time'].dtype.name not in PandasTypes._pandas_datetimes:
            raise TypeError("cutoff_time times must be datetime type: try casting via pd.to_datetime(cutoff_time['time'])")
    assert (cutoff_time[['instance_id', 'time']].duplicated().sum() == 0), \
        "Duplicated rows in cutoff time dataframe."
    pass_columns = [column_name for column_name in cutoff_time.columns[2:]]

    if _check_time_type(cutoff_time['time'].iloc[0]) is None:
        raise ValueError("cutoff_time time values must be datetime or numeric")

    # make sure dtype of instance_id in cutoff time
    # is same as column it references
    target_entity = features[0].entity
    dtype = entityset[target_entity.id].df[target_entity.index].dtype
    cutoff_time["instance_id"] = cutoff_time["instance_id"].astype(dtype)

    feature_set = FeatureSet(features)

    # Get features to approximate
    if approximate is not None:
        approximate_feature_trie = gather_approximate_features(feature_set)
        # Make a new FeatureSet that ignores approximated features
        feature_set = FeatureSet(features, approximate_feature_trie=approximate_feature_trie)

    # Check if there are any non-approximated aggregation features
    no_unapproximated_aggs = True
    for feature in features:
        if isinstance(feature, AggregationFeature):
            # do not need to check if feature is in to_approximate since
            # only base features of direct features can be in to_approximate
            no_unapproximated_aggs = False
            break

        if approximate is not None:
            all_approx_features = {f for _, feats in feature_set.approximate_feature_trie
                                   for f in feats}
        else:
            all_approx_features = set()
        deps = feature.get_dependencies(deep=True, ignored=all_approx_features)
        for dependency in deps:
            if isinstance(dependency, AggregationFeature):
                no_unapproximated_aggs = False
                break

    cutoff_df_time_var = 'time'
    target_time = '_original_time'

    if approximate is not None:
        # If there are approximated aggs, bin times
        binned_cutoff_time = bin_cutoff_times(cutoff_time.copy(), approximate)

        # Think about collisions: what if original time is a feature
        binned_cutoff_time[target_time] = cutoff_time[cutoff_df_time_var]

        cutoff_time_to_pass = binned_cutoff_time

    else:
        cutoff_time_to_pass = cutoff_time

    chunk_size = _handle_chunk_size(chunk_size, cutoff_time.shape[0])

    # make total 5% higher to allot time for wrapping up at end
    progress_bar = make_tqdm_iterator(
        total=cutoff_time.shape[0] / .95,
        smoothing=.05,  # arbitrary selection close to 0, which would be no smoothing
        bar_format=PBAR_FORMAT,
        disable=(not verbose)
    )

    if n_jobs != 1 or dask_kwargs is not None:
        feature_matrix = parallel_calculate_chunks(cutoff_time=cutoff_time_to_pass,
                                                   chunk_size=chunk_size,
                                                   feature_set=feature_set,
                                                   approximate=approximate,
                                                   training_window=training_window,
                                                   save_progress=save_progress,
                                                   entityset=entityset,
                                                   n_jobs=n_jobs,
                                                   no_unapproximated_aggs=no_unapproximated_aggs,
                                                   cutoff_df_time_var=cutoff_df_time_var,
                                                   target_time=target_time,
                                                   pass_columns=pass_columns,
                                                   progress_bar=progress_bar,
                                                   dask_kwargs=dask_kwargs or {})
    else:
        feature_matrix = calculate_chunk(cutoff_time=cutoff_time_to_pass,
                                         chunk_size=chunk_size,
                                         feature_set=feature_set,
                                         approximate=approximate,
                                         training_window=training_window,
                                         save_progress=save_progress,
                                         entityset=entityset,
                                         no_unapproximated_aggs=no_unapproximated_aggs,
                                         cutoff_df_time_var=cutoff_df_time_var,
                                         target_time=target_time,
                                         pass_columns=pass_columns,
                                         progress_bar=progress_bar)

    feature_matrix.sort_index(level='time', kind='mergesort', inplace=True)
    if not cutoff_time_in_index:
        feature_matrix.reset_index(level='time', drop=True, inplace=True)

    if save_progress and os.path.exists(os.path.join(save_progress, 'temp')):
        shutil.rmtree(os.path.join(save_progress, 'temp'))

    # force to 100% since we saved last 5 percent
    progress_bar.update(progress_bar.total - progress_bar.n)
    progress_bar.refresh()
    progress_bar.close()

    return feature_matrix


def calculate_chunk(cutoff_time, chunk_size, feature_set, entityset, approximate, training_window,
                    save_progress, no_unapproximated_aggs, cutoff_df_time_var, target_time,
                    pass_columns, progress_bar=None):
    if not isinstance(feature_set, FeatureSet):
        feature_set = cloudpickle.loads(feature_set)

    feature_matrix = []
    if no_unapproximated_aggs and approximate is not None:
        if entityset.time_type == NumericTimeIndex:
            group_time = np.inf
        else:
            group_time = datetime.now()

    for _, group in cutoff_time.groupby(cutoff_df_time_var):
        # if approximating, calculate the approximate features
        if approximate is not None:
            precalculated_features_trie = approximate_features(
                feature_set,
                group,
                window=approximate,
                entityset=entityset,
                training_window=training_window,
            )
        else:
            precalculated_features_trie = None

        @save_csv_decorator(save_progress)
        def calc_results(time_last, ids, precalculated_features=None, training_window=None):

            progress_callback = None

            if progress_bar is not None:
                def progress_callback(done):
                    progress_bar.update(done * group.shape[0])

            calculator = FeatureSetCalculator(entityset,
                                              feature_set,
                                              time_last,
                                              training_window=training_window,
                                              precalculated_features=precalculated_features)

            matrix = calculator.run(ids, progress_callback=progress_callback)
            return matrix

        # if all aggregations have been approximated, can calculate all together
        if no_unapproximated_aggs and approximate is not None:
            inner_grouped = [[group_time, group]]
        else:
            # if approximated features, set cutoff_time to unbinned time
            if precalculated_features_trie is not None:
                group[cutoff_df_time_var] = group[target_time]

            inner_grouped = group.groupby(cutoff_df_time_var, sort=True)

        if chunk_size is not None:
            inner_grouped = _chunk_dataframe_groups(inner_grouped, chunk_size)

        for time_last, group in inner_grouped:
            if len(feature_matrix) == 1:
                progress_bar.bar_format = PBAR_FORMAT_REMAINING
                progress_bar.refresh()

            # sort group by instance id
            ids = group['instance_id'].sort_values().values
            if no_unapproximated_aggs and approximate is not None:
                window = None
            else:
                window = training_window

            # calculate values for those instances at time time_last
            _feature_matrix = calc_results(time_last,
                                           ids,
                                           precalculated_features=precalculated_features_trie,
                                           training_window=window)

            id_name = _feature_matrix.index.name

            # if approximate, merge feature matrix with group frame to get original
            # cutoff times and passed columns
            if approximate:
                indexer = group[['instance_id', target_time] + pass_columns]
                _feature_matrix = indexer.merge(_feature_matrix,
                                                left_on=['instance_id'],
                                                right_index=True,
                                                how='left')
                _feature_matrix.set_index(['instance_id', target_time], inplace=True)
                _feature_matrix.index.set_names([id_name, 'time'], inplace=True)
                _feature_matrix.sort_index(level=1, kind='mergesort', inplace=True)
            else:
                # all rows have same cutoff time. set time and add passed columns
                num_rows = _feature_matrix.shape[0]
                time_index = pd.Index([time_last] * num_rows, name='time')
                _feature_matrix.set_index(time_index, append=True, inplace=True)
                if len(pass_columns) > 0:
                    pass_through = group[['instance_id', cutoff_df_time_var] + pass_columns]
                    pass_through.rename(columns={'instance_id': id_name,
                                                 cutoff_df_time_var: 'time'},
                                        inplace=True)
                    pass_through.set_index([id_name, 'time'], inplace=True)
                    for col in pass_columns:
                        _feature_matrix[col] = pass_through[col]
            feature_matrix.append(_feature_matrix)

    feature_matrix = pd.concat(feature_matrix)

    return feature_matrix


def approximate_features(feature_set, cutoff_time, window, entityset,
                         training_window=None):
    '''Given a set of features and cutoff_times to be passed to
    calculate_feature_matrix, calculates approximate values of some features
    to speed up calculations.  Cutoff times are sorted into
    window-sized buckets and the approximate feature values are only calculated
    at one cutoff time for each bucket.


    ..note:: this only approximates DirectFeatures of AggregationFeatures, on
        the target entity. In future versions, it may also be possible to
        approximate these features on other top-level entities

    Args:
        cutoff_time (pd.DataFrame): specifies what time to calculate
            the features for each instance at. The resulting feature matrix will use data
            up to and including the cutoff_time. A DataFrame with
            'instance_id' and 'time' columns.

        window (Timedelta or str): frequency to group instances with similar
            cutoff times by for features with costly calculations. For example,
            if bucket is 24 hours, all instances with cutoff times on the same
            day will use the same calculation for expensive features.

        entityset (:class:`.EntitySet`): An already initialized entityset.

        feature_set (:class:`.FeatureSet`): The features to be calculated.

        training_window (`Timedelta`, optional):
            Window defining how much older than the cutoff time data
            can be to be included when calculating the feature. If None, all older data is used.

        save_progress (str, optional): path to save intermediate computational results
    '''
    approx_fms_trie = Trie(path_constructor=RelationshipPath)

    target_time_colname = 'target_time'
    cutoff_time[target_time_colname] = cutoff_time['time']
    approx_cutoffs = bin_cutoff_times(cutoff_time.copy(), window)
    cutoff_df_time_var = 'time'
    cutoff_df_instance_var = 'instance_id'
    # should this order be by dependencies so that calculate_feature_matrix
    # doesn't skip approximating something?
    for relationship_path, approx_feature_names in feature_set.approximate_feature_trie:
        if not approx_feature_names:
            continue

        cutoffs_with_approx_e_ids, new_approx_entity_index_var = \
            _add_approx_entity_index_var(entityset, feature_set.target_eid,
                                         approx_cutoffs.copy(), relationship_path)

        # Select only columns we care about
        columns_we_want = [new_approx_entity_index_var,
                           cutoff_df_time_var,
                           target_time_colname]

        cutoffs_with_approx_e_ids = cutoffs_with_approx_e_ids[columns_we_want]
        cutoffs_with_approx_e_ids = cutoffs_with_approx_e_ids.drop_duplicates()
        cutoffs_with_approx_e_ids.dropna(subset=[new_approx_entity_index_var],
                                         inplace=True)

        approx_features = [feature_set.features_by_name[name]
                           for name in approx_feature_names]
        if cutoffs_with_approx_e_ids.empty:
            approx_fm = gen_empty_approx_features_df(approx_features)
        else:
            cutoffs_with_approx_e_ids.sort_values([cutoff_df_time_var,
                                                   new_approx_entity_index_var], inplace=True)
            # CFM assumes specific column names for cutoff_time argument
            rename = {new_approx_entity_index_var: cutoff_df_instance_var}
            cutoff_time_to_pass = cutoffs_with_approx_e_ids.rename(columns=rename)
            cutoff_time_to_pass = cutoff_time_to_pass[[cutoff_df_instance_var, cutoff_df_time_var]]

            cutoff_time_to_pass.drop_duplicates(inplace=True)
            approx_fm = calculate_feature_matrix(approx_features,
                                                 entityset,
                                                 cutoff_time=cutoff_time_to_pass,
                                                 training_window=training_window,
                                                 approximate=None,
                                                 cutoff_time_in_index=False,
                                                 chunk_size=cutoff_time_to_pass.shape[0])

        approx_fms_trie.get_node(relationship_path).value = approx_fm

    return approx_fms_trie


def scatter_warning(num_scattered_workers, num_workers):
    if num_scattered_workers != num_workers:
        scatter_warning = "EntitySet was only scattered to {} out of {} workers"
        warnings.warn(scatter_warning.format(num_scattered_workers, num_workers))


def parallel_calculate_chunks(cutoff_time, chunk_size, feature_set, approximate, training_window,
                              save_progress, entityset, n_jobs, no_unapproximated_aggs,
                              cutoff_df_time_var, target_time, pass_columns,
                              progress_bar, dask_kwargs=None):
    from distributed import as_completed, Future
    from dask.base import tokenize

    progress_bar.bar_format = PBAR_FORMAT_REMAINING
    progress_bar.refresh()

    client = None
    cluster = None
    try:
        client, cluster = create_client_and_cluster(n_jobs=n_jobs,
                                                    dask_kwargs=dask_kwargs,
                                                    entityset_size=entityset.__sizeof__())
        # scatter the entityset
        # denote future with leading underscore
        start = time.time()
        es_token = "EntitySet-{}".format(tokenize(entityset))
        if es_token in client.list_datasets():
            msg = "Using EntitySet persisted on the cluster as dataset {}"
            progress_bar.write(msg.format(es_token))
            _es = client.get_dataset(es_token)
        else:
            _es = client.scatter([entityset])[0]
            client.publish_dataset(**{_es.key: _es})

        # save features to a tempfile and scatter it
        pickled_feats = cloudpickle.dumps(feature_set)
        _saved_features = client.scatter(pickled_feats)
        client.replicate([_es, _saved_features])
        num_scattered_workers = len(client.who_has([Future(es_token)]).get(es_token, []))
        num_workers = len(client.scheduler_info()['workers'].values())

        chunks = cutoff_time.groupby(cutoff_df_time_var)

        if not chunk_size:
            chunk_size = _handle_chunk_size(1.0 / num_workers, cutoff_time.shape[0])

        chunks = _chunk_dataframe_groups(chunks, chunk_size)

        chunks = [df for _, df in chunks]

        if len(chunks) < num_workers:
            chunk_warning = "Fewer chunks ({}), than workers ({}) consider reducing the chunk size"
            warning_string = chunk_warning.format(len(chunks), num_workers)
            progress_bar.write(warning_string)

        scatter_warning(num_scattered_workers, num_workers)
        end = time.time()
        scatter_time = round(end - start)

        # if enabled, reset timer after scatter for better time remaining estimates
        if not progress_bar.disable:
            progress_bar.reset()

        scatter_string = "EntitySet scattered to {} workers in {} seconds"
        progress_bar.write(scatter_string.format(num_scattered_workers, scatter_time))
        # map chunks
        # TODO: consider handling task submission dask kwargs
        _chunks = client.map(calculate_chunk,
                             chunks,
                             feature_set=_saved_features,
                             chunk_size=None,
                             entityset=_es,
                             approximate=approximate,
                             training_window=training_window,
                             save_progress=save_progress,
                             no_unapproximated_aggs=no_unapproximated_aggs,
                             cutoff_df_time_var=cutoff_df_time_var,
                             target_time=target_time,
                             pass_columns=pass_columns,
                             progress_bar=None)

        feature_matrix = []
        iterator = as_completed(_chunks).batches()
        for batch in iterator:
            results = client.gather(batch)
            for result in results:
                feature_matrix.append(result)
                progress_bar.update(result.shape[0])

    except Exception:
        raise
    finally:
        if 'cluster' not in dask_kwargs and cluster is not None:
            cluster.close()

        if client is not None:
            client.close()

    feature_matrix = pd.concat(feature_matrix)

    return feature_matrix


def _add_approx_entity_index_var(es, target_entity_id, cutoffs, path):
    """
    Add a variable to the cutoff df linking it to the entity at the end of the
    path.

    Return the updated cutoff df and the name of this variable. The name will
    consist of the variables which were joined through.
    """
    last_child_var = 'instance_id'
    last_parent_var = es[target_entity_id].index

    for _, relationship in path:
        child_vars = [last_parent_var, relationship.child_variable.id]
        child_df = es[relationship.child_entity.id].df[child_vars]

        # Rename relationship.child_variable to include the variables we have
        # joined through.
        new_var_name = '%s.%s' % (last_child_var, relationship.child_variable.id)
        to_rename = {relationship.child_variable.id: new_var_name}
        child_df = child_df.rename(columns=to_rename)

        cutoffs = cutoffs.merge(child_df,
                                left_on=last_child_var,
                                right_on=last_parent_var)

        # These will be used in the next iteration.
        last_child_var = new_var_name
        last_parent_var = relationship.parent_variable.id

    return cutoffs, new_var_name


def _chunk_dataframe_groups(grouped, chunk_size):
    """chunks a grouped dataframe into groups no larger than chunk_size"""
    for group_key, group_df in grouped:
        for i in range(0, len(group_df), chunk_size):
            yield group_key, group_df.iloc[i:i + chunk_size]


def _handle_chunk_size(chunk_size, total_size):
    if chunk_size is not None:
        assert chunk_size > 0, "Chunk size must be greater than 0"

        if chunk_size < 1:
            chunk_size = math.ceil(chunk_size * total_size)

        chunk_size = int(chunk_size)

    return chunk_size
