"""
Utilities for the selection of branches for an AC to DC conversion.
"""

import logging

import numpy as np
import pandas as pd

from hynet.types_ import (hynet_id_,
                          hynet_float_,
                          hynet_eps,
                          BranchType)
from hynet.scenario.representation import Scenario
from hynet.utilities.graph import (get_minimum_spanning_tree,
                                   get_graph_components)
from hynet.utilities.worker import workers

_log = logging.getLogger(__name__)


def get_series_resistance_weights(scenario, prefer_transformers=False):
    """
    Return a pandas Series of branch weights based on their series resistance.

    Parameters
    ----------
    scenario : Scenario
        Scenario for which the branch weights shall be created.
    prefer_transformers : bool, optional
        If ``True`` (default ``False``), the weight of transformer branches is
        increased by the maximum series resistance in the system to prefer
        their conversion to DC operation.

    Returns
    -------
    branch_weights : pandas.Series
        Branch weights indexed by the branch ID.

    See Also
    --------
    get_branches_outside_mst
    """
    if scenario.branch.empty:
        return pd.Series([], index=scenario.branch.index, dtype=hynet_float_)

    branch_weights = pd.Series(np.abs(scenario.branch['z_bar'].to_numpy().real),
                               index=scenario.branch.index)
    branch_weights += 100 * hynet_eps  # Avoid zero weights

    for parallel_branches in scenario.get_parallel_branches():
        branch_weights[parallel_branches[0]] = \
            1 / np.sum(1 / branch_weights[parallel_branches].to_numpy())
        branch_weights.drop(parallel_branches[1:], inplace=True)

    if prefer_transformers:
        r_max = branch_weights.abs().max()
        is_transformer = scenario.branch.loc[branch_weights.index, 'type']
        is_transformer = (is_transformer == BranchType.TRANSFORMER)
        branch_weights.loc[is_transformer] += r_max

    return branch_weights


def get_mst_branches(scenario, branch_weights):
    """
    Return an array of branch IDs that are part of the minimum spanning tree.

    The branch weights associate a weight with (selected) branches of the
    scenario and all *corridors* defined by these branches are considered as
    edges of the graph. Please note that converters are not considered, i.e.,
    the function operates on (selected) branches of the subgrids. This function
    returns the IDs of the branches that reside in the corridors of the
    minimum spanning tree.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be considered.
    branch_weights : pandas.Series
        Branch weights indexed by the branch ID.

    Returns
    -------
    index : pandas.Index
        Pandas index with the branch IDs of those branches that reside in the
        corridors of the minimum spanning tree.

    See Also
    --------
    get_series_resistance_weights
    """
    if not np.all(branch_weights > 0):
        raise ValueError("All branch weights must be positive.")

    e_src = scenario.e_src.loc[branch_weights.index]
    e_dst = scenario.e_dst.loc[branch_weights.index]

    edges = get_minimum_spanning_tree((e_src.to_numpy(), e_dst.to_numpy()),
                                      branch_weights.to_numpy())
    return scenario.get_branches_in_corridors(edges)


def get_branches_outside_mst(scenario, branch_weights):
    """
    Return an array of branch IDs that reside outside the minimum spanning tree.

    The branch weights associate a weight with (selected) branches of the
    scenario and all *corridors* defined by these branches are considered as
    edges of the graph. Please note that converters are not considered, i.e.,
    the function operates on (selected) branches of the subgrids. This function
    returns the IDs of the branches that reside *outside* the corridors of the
    minimum spanning tree.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be considered.
    branch_weights : pandas.Series
        Branch weights indexed by the branch ID.

    Returns
    -------
    index : pandas.Index
        Pandas index with the branch IDs of those branches that reside
        *outside* the corridors of the minimum spanning tree.

    See Also
    --------
    get_series_resistance_weights
    """
    return scenario.branch.index.difference(
        get_mst_branches(scenario, branch_weights))


def get_islanding_branches(scenario, show_progress=True):
    """
    Return the branch IDs for all corridors whose removal leads to islanding.

    Branches which are part of *all* spanning trees of (the corridors of) a
    grid are of particular interest, because their congestion can directly lead
    to infeasibility of the optimal power flow as there are no alternative
    power flow routes. This function identifies the corridors that are part of
    all spanning trees and returns the IDs of the branches that reside in these
    corridors.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be evaluated.
    show_progress : bool, optional
        If ``True`` (default), the progress is reported to the standard output.

    Returns
    -------
    pandas.Index
        Index with the ID of all branches that reside in corridors whose
        removal leads to islanding.
    """
    # Identify the branches in some spanning tree to reduce the search space
    branch_weights = get_series_resistance_weights(scenario)
    branches_mst = get_mst_branches(scenario, branch_weights)

    # Check these branches (or, more precisely, their corridors) for islanding
    num_buses = scenario.num_buses
    num_branches = len(branches_mst)
    num_islands = len(scenario.get_islands())
    (e_src, e_dst) = (scenario.e_src, scenario.e_dst)
    (c_src, c_dst) = (scenario.c_src, scenario.c_dst)

    islanding_branches = \
        workers.map(_check_grid_islanding,
                    list(zip(branches_mst,
                             [num_buses] * num_branches,
                             [num_islands] * num_branches,
                             [(e_src, e_dst)] * num_branches,
                             [(c_src, c_dst)] * num_branches)),
                    show_progress=show_progress)

    islanding_branches = \
        pd.Index(data=set(islanding_branches) - set([None]), dtype=hynet_id_)
    return islanding_branches


def _check_grid_islanding(args):
    """
    Check if the branch resides in a corridor whose removal leads to islanding.
    """
    branch_id, num_buses, num_islands, (e_src, e_dst), (c_src, c_dst) = args

    src = e_src.at[branch_id]
    dst = e_dst.at[branch_id]

    idx_corridor = e_src.index[
        ((e_src == src) & (e_dst == dst)) | ((e_dst == src) & (e_src == dst))
    ]

    e_src = e_src.drop(idx_corridor)
    e_dst = e_dst.drop(idx_corridor)

    islands = get_graph_components(np.arange(num_buses),
                                   (np.concatenate((e_src.to_numpy(),
                                                    c_src.to_numpy())),
                                    np.concatenate((e_dst.to_numpy(),
                                                    c_dst.to_numpy()))))

    return branch_id if len(islands) > num_islands else None
