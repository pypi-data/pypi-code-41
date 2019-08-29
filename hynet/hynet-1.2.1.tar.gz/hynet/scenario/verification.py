"""
Verification of a steady-state scenario.
"""

import warnings

import numpy as np

from hynet.types_ import hynet_eps, BusType, BranchType
from hynet.utilities.graph import get_graph_components


def verify_hybrid_architecture(scr, log_function):
    """
    Return ``True`` if the *hybrid architecture*'s exactness results hold.

    This function is actually part of the ``Scenario`` class. Due to its extent,
    it was moved to a separate module in order to improve code readability.
    """
    def log(message):
        if log_function is not None:
            log_function(message)

    # Topological requirements
    if not scr.has_acyclic_subgrids():
        log("The topological requirements of the hybrid architecture are not "
            "satisfied.")
        return False

    # Prepare for checking the remaining requirements
    requirements_satisfied = True
    warning_exactness = \
        " This can be detrimental to the exactness of the relaxation."

    e_src = scr.e_src.to_numpy()

    z_bar = scr.branch['z_bar'].to_numpy()
    y_src = scr.branch['y_src'].to_numpy()
    y_dst = scr.branch['y_dst'].to_numpy()

    rho = np.multiply(scr.branch['rho_src'].to_numpy().conj(),
                      scr.branch['rho_dst'].to_numpy())
    rho_angle = np.angle(rho) * 180/np.pi

    angle_min = scr.branch['angle_min'].to_numpy()
    angle_max = scr.branch['angle_max'].to_numpy()

    # Electrical requirements

    if np.any(z_bar.real <= 0):
        requirements_satisfied = False
        log("The series resistance of some branches is zero or negative."
            + warning_exactness)

    if np.any(z_bar.imag < 0):
        requirements_satisfied = False
        log("The series reactance of some branches is capacitive."
            + warning_exactness)

    if np.any(y_src.real < 0) or np.any(y_dst.real < 0):
        requirements_satisfied = False
        log("The shunt conductance of some branches is negative."
            + warning_exactness)

    if np.any(np.multiply(np.abs(y_src), np.abs(z_bar)) > 1) or \
            np.any(np.multiply(np.abs(y_dst), np.abs(z_bar)) > 1):
        requirements_satisfied = False
        log("Some branches are not properly insulated."
            + warning_exactness)

    for parallel_branches in scr._get_parallel_branch_indices():
        idx = (e_src[parallel_branches] == e_src[parallel_branches[0]])
        rho_diff = np.concatenate((rho[parallel_branches[idx]],
                                   rho[parallel_branches[~idx]].conj()))
        rho_diff -= rho[parallel_branches[0]]
        if np.any(np.abs(rho_diff) > hynet_eps):
            requirements_satisfied = False
            log("In the group " + str(list(scr.branch.index[parallel_branches]))
                + " of parallel branches the total voltage ratios do not agree."
                + warning_exactness)

    # Constraint requirements

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)  # Ignore NaN warning

        if np.any(angle_min > -rho_angle) or np.any(angle_max < -rho_angle):
            requirements_satisfied = False
            log("Some angle difference constraints do not enclose the negated "
                "total phase shift." + warning_exactness)

    return requirements_satisfied


def verify_scenario(scr, log_function):
    """
    Verify the integrity and validity of the scenario.

    This function is actually part of the ``Scenario`` class. Due to its extent,
    it was moved to a separate module in order to improve code readability.

    Raises
    ------
    ValueError
        In case any kind of integrity or validity violation is detected.
    """
    def log(message):
        if log_function is not None:
            log_function(message)

    e_src = scr.e_src.to_numpy()
    e_dst = scr.e_dst.to_numpy()

    z_bar = scr.branch['z_bar'].to_numpy()
    y_src = scr.branch['y_src'].to_numpy()
    y_dst = scr.branch['y_dst'].to_numpy()

    rho = np.multiply(scr.branch['rho_src'].to_numpy().conj(),
                      scr.branch['rho_dst'].to_numpy())
    rho_angle = np.angle(rho) * 180/np.pi

    base_kv = scr.bus['base_kv'].to_numpy()

    v_min = scr.bus['v_min'].to_numpy()
    v_max = scr.bus['v_max'].to_numpy()

    angle_min = scr.branch['angle_min'].to_numpy()
    angle_max = scr.branch['angle_max'].to_numpy()

    drop_min = scr.branch['drop_min'].to_numpy()
    drop_max = scr.branch['drop_max'].to_numpy()

    if not (scr.base_mva > 0):
        raise ValueError("The MVA base is invalid (positive number expected).")

    if not (scr.loss_price >= 0):
        raise ValueError("The loss price is invalid (nonnegative number expected).")

    # Topological checks

    if scr.num_buses < 1:
        raise ValueError("The grid does not comprise any buses.")

    if scr.num_injectors < 1:
        raise ValueError("There is no injector connected to the grid.")

    if not (scr.branch['src'].isin(scr.bus.index).all() and
            scr.branch['dst'].isin(scr.bus.index).all()):
        raise ValueError("Some branches connect to non-existing buses.")

    if not (scr.converter['src'].isin(scr.bus.index).all() and
            scr.converter['dst'].isin(scr.bus.index).all()):
        raise ValueError("Some converters connect to non-existing buses.")

    if not scr.injector['bus'].isin(scr.bus.index).all():
        raise ValueError("Some injectors connect to non-existing buses.")

    if np.any(np.equal(scr.branch['src'].to_numpy(),
                       scr.branch['dst'].to_numpy())):
        raise ValueError("The grid contains branch-based self-loops.")

    if np.any(np.logical_and(np.not_equal(base_kv[e_src], base_kv[e_dst]),
                             scr.branch['type'].to_numpy() != BranchType.TRANSFORMER)):
        log("Some non-transformer branches connect buses with a different "
            "base voltage.")

    if np.any(np.equal(scr.converter['src'].to_numpy(),
                       scr.converter['dst'].to_numpy())):
        raise ValueError("The grid contains converter-based self-loops.")

    for subgrid in get_graph_components(np.arange(scr.num_buses), (e_src, e_dst)):
        subgrid = np.sort(subgrid)
        num_ref = np.count_nonzero(scr.bus['ref'].iloc[subgrid].to_numpy())
        if num_ref > 1:
            log("Ambiguous references detected. Bus IDs: "
                + str(list(scr.bus.iloc[subgrid].query('ref').index)))
        bus_type = scr.bus['type'].iloc[subgrid]
        is_ac = np.all(bus_type == BusType.AC)
        is_dc = np.all(bus_type == BusType.DC)
        if not (is_ac or is_dc):
            raise ValueError("Inconsistent bus types in the subgrid comprising "
                             "the buses " + str(list(scr.bus.index[subgrid])))
        if is_ac and num_ref < 1:
            # We only require AC subgrids to have a reference bus
            raise ValueError("Reference is missing in the AC subgrid comprising "
                             "the buses " + str(list(scr.bus.index[subgrid])))

    if not scr.has_acyclic_dc_subgrids():
        raise ValueError("The grid contains meshed DC subgrids. hynet only "
                         "supports radial DC subgrids.")

    # Electrical checks

    if np.any(z_bar.real < 0):
        log("The series resistance of some branches is negative.")

    if np.any(np.abs(z_bar) < 1e-6):
        log("Some branches are close to an electrical short. This leads to a "
            "bad conditioning of the OPF problem and may cause numerical "
            "and/or convergence issues.")

    if np.any(y_src.real < 0) or np.any(y_dst.real < 0):
        log("The shunt conductance of some branches is negative.")

    if np.any(np.abs(rho) == 0):
        raise ValueError("Some branches exhibit a total voltage ratio of zero.")

    if np.any(np.abs(rho_angle) > 90):
        raise ValueError("Some branches exhibit a total phase ratio of "
                         "more than 90 degrees.")

    if np.any(scr.converter[['loss_fwd', 'loss_bwd']].to_numpy() < 0) or \
            np.any(scr.converter[['loss_fwd', 'loss_bwd']].to_numpy() >= 100):
        raise ValueError("Some converter loss factors are not within [0,100).")

    # Electrical checks: Restrictions for DC grids

    dc_bus = scr.bus.loc[scr.bus['type'] == BusType.DC]

    if np.any(dc_bus['y_tld'].to_numpy() != 0):
        raise ValueError("Some bus shunts in the DC subgrids are nonzero.")

    if np.any(dc_bus['load'].to_numpy().imag != 0):
        raise ValueError("Some loads in the DC subgrids demand reactive power.")

    dc_branch = scr.branch.loc[
        scr.bus.loc[scr.branch['src'], 'type'].to_numpy() == BusType.DC]

    if np.any(dc_branch['rho_src'].to_numpy() != 1) or \
            np.any(dc_branch['rho_dst'].to_numpy() != 1):
        raise ValueError("Some transformers of the DC branches are non-unity.")

    if np.any(dc_branch['y_src'].to_numpy() != 0) or \
            np.any(dc_branch['y_dst'].to_numpy() != 0):
        raise ValueError("Some shunt admittances of the DC branches are nonzero.")

    if np.any(dc_branch['z_bar'].to_numpy().real <= 0):
        raise ValueError("Some DC branches are lossless or active.")

    if np.any(dc_branch['z_bar'].to_numpy().imag != 0):
        raise ValueError("Some series impedances of the DC branches "
                         "exhibit a nonzero reactance.")

    if np.any(~np.isnan(dc_branch['angle_min'].to_numpy())) or \
            np.any(~np.isnan(dc_branch['angle_max'].to_numpy())):
        log("Some DC branches include angle difference limits.")

    # if np.any(~np.isnan(dc_branch['drop_min'].to_numpy())) or \
    #         np.any(~np.isnan(dc_branch['drop_max'].to_numpy())):
    #     log("Some DC branches include voltage drop limits.")

    dc_converter_src = scr.converter.loc[
        scr.bus.loc[scr.converter['src'], 'type'].to_numpy() == BusType.DC]
    dc_converter_dst = scr.converter.loc[
        scr.bus.loc[scr.converter['dst'], 'type'].to_numpy() == BusType.DC]
    for id_, cap in zip(np.concatenate((dc_converter_src.index.to_numpy(),
                                        dc_converter_dst.index.to_numpy())),
                        np.concatenate((dc_converter_src['cap_src'].to_numpy(),
                                        dc_converter_dst['cap_dst'].to_numpy()))):
        if cap.q_max != 0 or cap.q_min != 0:
            raise ValueError(("Converter {0} offers reactive power on the "
                              "DC side.").format(id_))

    dc_injector = scr.injector.loc[
        scr.bus.loc[scr.injector['bus'], 'type'].to_numpy() == BusType.DC]
    for id_, cap in zip(dc_injector.index.to_numpy(), dc_injector['cap'].to_numpy()):
        if cap.q_max != 0 or cap.q_min != 0:
            raise ValueError(("Injector {0} offers reactive power to a "
                              "DC subgrid.").format(id_))

    # Constraint checks

    if not (np.all(v_min > 0) and np.all(v_max >= v_min)):
        raise ValueError("Some voltage limits are infeasible, zero, or missing.")

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)  # Ignore NaN warning

        if np.any(scr.branch['rating'].to_numpy() <= 0):
            raise ValueError("Some branch ratings are infeasible or zero.")

        if np.any(angle_min < -89) or np.any(angle_max > 89) or \
                np.any(angle_min >= angle_max):
            raise ValueError("Some angle difference limits are infeasible, "
                             "equal, or not within [-89, 89] degrees")

        if np.any(drop_min < -100) or np.any(drop_max <= drop_min):
            raise ValueError("Some voltage drop limits are infeasible, "
                             "equal, or not within [-100, +inf).")

    for n, cap in enumerate(np.concatenate((scr.converter['cap_src'].to_numpy(),
                                            scr.converter['cap_dst'].to_numpy(),
                                            scr.injector['cap'].to_numpy()))):
        # Note that only the box constraint needs to be checked, proper
        # specification of the half-spaces is ensured in CapRegion
        if not (cap.p_max >= cap.p_min and cap.q_max >= cap.q_min):
            raise ValueError(("Some {0:s} capability regions are infeasible "
                              "or incompletely specified.").format(
                             'converter'
                             if n < 2*scr.num_converters else 'injector'))
        if cap.has_polyhedron():
            if cap.p_max == cap.p_min and cap.q_max == cap.q_min != 0:
                log("Singleton capability regions with nonzero reactive power "
                    "and polyhedral constraints are present. This potentially "
                    "causes infeasibility.")
            elif not cap.q_min <= 0 <= cap.q_max:
                log("Capability regions with polyhedral constraints are "
                    "present, where the reactive power limits do not include "
                    "zero. This is not recommended, as the specification "
                    "becomes intricate to understand (and, consequently, "
                    "error-prone).")

    for island in scr.get_islands():
        injectors = scr.injector.loc[scr.injector['bus'].isin(island)]
        if injectors.empty:
            raise ValueError("There's no injector connected to the island "
                             "comprising the buses " + str(list(island)))
        # A simple plausibility check of sufficient injection/load
        # (This can be helpful, e.g., in the simulation of contingencies,
        # where a line/transformer/converter fault can cause load or
        # generation buses to be islanded.)
        total_load = scr.bus.loc[island, 'load'].sum()
        if np.abs(total_load.real) < hynet_eps:
            log("There is no fixed load in the island comprising the buses "
                + str(list(island)))
        if total_load.real > np.sum([x.p_max for x in injectors['cap']]):
            log("The active power load exceeds the injector active power "
                "capacity in the island comprising the buses "
                + str(list(island)))
        if total_load.real < np.sum([x.p_min for x in injectors['cap']]):
            log("The minimum active power injection exceeds the active power "
                "load in the island comprising the buses " + str(list(island)))

    # Objective checks

    for j, (cost_p, cost_q) in enumerate(zip(scr.injector['cost_p'].to_numpy(),
                                             scr.injector['cost_q'].to_numpy())):
        if cost_p is not None:
            if not cost_p.is_convex():
                raise ValueError(("The P-cost function of injector {0} is "
                                  "nonconvex.").format(scr.injector.index[j]))
        if cost_q is not None:
            if not cost_q.is_convex():
                raise ValueError(("The Q-cost function of injector {0} is "
                                  "nonconvex.").format(scr.injector.index[j]))
