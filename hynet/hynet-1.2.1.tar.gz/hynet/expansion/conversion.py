"""
Utilities for the conversion of AC lines and transformers to DC operation.
"""

import logging
from collections import namedtuple

import numpy as np

from hynet.types_ import (hynet_id_,
                          hynet_float_,
                          hynet_complex_,
                          BusType,
                          BranchType)
from hynet.scenario.representation import Scenario
from hynet.scenario.capability import ConverterCapRegion
from hynet.utilities.graph import is_acyclic_component

_log = logging.getLogger(__name__)


def convert_transformer_to_b2b_converter(scenario, branch_id, loss_dyn,
                                         q_to_p_ratio, capacity_factor=1.0,
                                         amalgamate=True,
                                         annotation_separator=', '):
    """
    Replace the specified transformer (or AC branch) by an AC/AC converter.

    This function models the conversion of a transformer to DC operation by
    replacing the branch with an AC/AC (back-to-back) converter. Please note
    that this is a simplified representation of such a conversion process for
    use in system-level studies.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be modified.
    branch_id : .hynet_id_
        ID of the branch that shall be converted.
    loss_dyn : float
        Loss factor in percent for the forward and backward conversion losses
        of the introduced converter.
    q_to_p_ratio : float
        Ratio of the Q-capability of the introduced converter w.r.t. its
        P-capability.
    capacity_factor : float, optional
        Capacity factor for the conversion (default ``1.0``): The P-capability
        is set to the branch rating times the capacity factor.
    amalgamate : bool, optional
        If ``True`` (default) and there exists an AC/AC converter between the
        source and destination bus of the branch, this converter is uprated
        accordingly. Otherwise, always a new converter is added.
    annotation_separator : str, optional
        If not ``None`` (default ``', '``), the branch annotation is copied
        to the converter annotation and, if the latter is not empty, this
        separator string is employed to separate the annotations.

    Returns
    -------
    converter_id : .hynet_id_
        ID of the AC/AC converter that replaces the branch.
    amalgamated : bool
        ``True`` if amalgamated and ``False`` otherwise.
    """
    branch = scenario.branch.loc[branch_id]

    if not (branch['rating'] > 0):
        raise ValueError("'The branch must feature a (positive) rating.")

    src = branch['src']
    dst = branch['dst']

    if (scenario.bus.loc[(src, dst), 'type'] != BusType.AC).any():
        raise ValueError("The branch must connect AC buses.")

    p_max = capacity_factor * branch['rating']
    q_max = q_to_p_ratio * p_max

    amalgamated = False
    if amalgamate:
        converters = scenario.converter.loc[
            ((scenario.converter['src'] == src) & (scenario.converter['dst'] == dst)) |
            ((scenario.converter['dst'] == src) & (scenario.converter['src'] == dst))
        ]
        converters = converters.loc[
            (converters[['loss_fwd', 'loss_bwd']] == loss_dyn).all(axis='columns')
        ]

        if not converters.empty:
            # There is already an appropriate AC/DC converter, so upgrade it
            converter_id = converters.index[0]

            for cap in [scenario.converter.loc[converter_id, 'cap_src'],
                        scenario.converter.loc[converter_id, 'cap_dst']]:
                cap.p_max += p_max
                cap.p_min -= p_max
                cap.q_max += q_max
                cap.q_min -= q_max

            amalgamated = True

    if not amalgamated:
        converter_id = scenario.add_converter(
            src=src,
            dst=dst,
            cap_src=ConverterCapRegion(p_bnd=[-p_max, p_max],
                                       q_bnd=[-q_max, q_max]),
            cap_dst=ConverterCapRegion(p_bnd=[-p_max, p_max],
                                       q_bnd=[-q_max, q_max]),
            loss_fwd=loss_dyn,
            loss_bwd=loss_dyn
        )

    # Copy branch annotation if present
    if annotation_separator is not None and branch['annotation']:
        annotation = scenario.converter.at[converter_id, 'annotation']
        if annotation:
            annotation += annotation_separator
        annotation += branch['annotation']
        scenario.converter.at[converter_id, 'annotation'] = annotation

    # Remove the transformer
    scenario.branch = scenario.branch.drop(branch_id)

    return converter_id, amalgamated


def convert_ac_line_to_hvdc_system(scenario, branch_id, loss_fwd, loss_bwd,
                                   q_to_p_ratio, base_kv_map=None,
                                   capacity_factor=np.nan, amalgamate=True):
    """
    Convert the specified AC line to an HVDC system.

    This function models the conversion of an AC line to DC operation by
    introducing AC/DC converters at the line's terminals and updating the
    branch parameters. If ``amalgamate`` is ``True`` (default) and there is
    already an (appropriate) HVDC system connected to either or both terminals
    of the line, the converted line is connected to this DC subgrid (to reduce
    the number of converters). Otherwise, always a point-to-point HVDC system
    is implemented. The branch parameters are updated by retaining only the
    series resistance and line rating, where both are updated according to the
    change of the base voltage. For the latter, the uprating may also be
    specified explicitly via ``capacity_factor``. The introduced DC buses
    inherit the voltage limits (in p.u.) and zone from the respective AC bus.
    Please note that this is a simplified representation of such a conversion
    process for use in system-level studies, while the actual conversion of
    an AC line to DC operation involves extensive and case-specific
    considerations dependent on the present line configuration, see e.g. [1]_
    for more details.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be modified.
    branch_id : .hynet_id_
        ID of the branch that shall be converted.
    loss_fwd : float
        Loss factor in percent for the *forward* flow of active power of the
        introduced converters.
    loss_bwd : float
        Loss factor in percent for the *backward* flow of active power of the
        introduced converters.
    q_to_p_ratio : float
        Ratio of the Q-capability of the introduced converters w.r.t. their
        P-capability.
    base_kv_map : dict[.hynet_float_, .hynet_float_,], optional
        Dictionary that maps the AC base voltage (in kV) to the DC base
        voltage (in kV). By default, a mapping ``x -> floor(sqrt(2) * x)`` is
        used.
    capacity_factor : float, optional
        Capacity factor for the conversion, i.e., the branch rating and the
        converter P-capability is set to the current branch rating times the
        capacity factor. By default, the capacity factor is set to the uprating
        due to the change of the base voltage.
    amalgamate : bool, optional
        If ``True`` (default), the converted line is amalgamated with an
        adjacent HVDC system if possible. Otherwise, always a point-to-point
        HVDC system is implemented. By convention, only AC/DC converters with
        the source terminal at the AC side are considered in the detection of
        and amalgamation with adjacent HVDC systems. The converters introduced
        by this function adhere to this convention.

    Returns
    -------
    converter_id_src : .hynet_id_
        ID of the AC/DC converter at the source terminal of the converted line.
    converter_id_dst : .hynet_id_
        ID of the AC/DC converter at the destination terminal of the converted
        line.
    amalgamated : tuple(bool, bool)
        Named tuple ``('src', 'dst')`` with a Boolean flag for the source and
        destination terminal of the line that is ``True`` if that terminal was
        amalgamated with an existing HVDC system and ``False`` otherwise.

    References
    ----------
    .. [1] CIGRE Working Group B2.41, "Guide to the Conversion of Existing AC
           Lines to DC Operation," CIGRE Brochure 583, May 2014.
    """
    branch = scenario.branch.loc[branch_id].copy()

    if not (branch['rating'] > 0):
        raise ValueError("'The branch must feature a (positive) rating.")

    if (branch[['rho_src', 'rho_dst']] != 1).any():
        raise ValueError("The branch must not model a phase shifter.")

    if branch['z_bar'].real <= 0:
        raise ValueError("The branch must feature a positive series resistance.")

    src = branch['src']
    dst = branch['dst']

    if (scenario.bus.loc[(src, dst), 'type'] != BusType.AC).any():
        raise ValueError("The branch must connect AC buses.")

    ac_base_voltage = scenario.bus.at[src, 'base_kv']

    if scenario.bus.at[dst, 'base_kv'] != ac_base_voltage:
        _log.warning("The branch exhibits different base voltages at its "
                     "terminals. Considering the source bus base voltage.")

    if not (ac_base_voltage > 0):
        raise ValueError("The AC base voltage must be positive.")

    if base_kv_map is None:
        dc_base_voltage = np.floor(np.sqrt(2) * ac_base_voltage)
    else:
        if ac_base_voltage not in base_kv_map:
            raise ValueError("The base voltage mapping has no entry for a "
                             "{:g}kV AC base voltage.".format(ac_base_voltage))
        dc_base_voltage = base_kv_map[ac_base_voltage]

    if not (dc_base_voltage > 0):
        raise ValueError("The DC base voltage must be positive.")

    if np.isnan(capacity_factor):
        capacity_factor = dc_base_voltage / ac_base_voltage

    if not (capacity_factor > 0):
        raise ValueError("The capacity factor must be positive.")

    converter_p_cap = capacity_factor * branch['rating']
    converter_q_cap = q_to_p_ratio * converter_p_cap

    def find_acdc_converter(bus_id):
        """
        Find all AC/DC converters connected to the specified bus.

        This function only considers AC/DC converters that have their source
        bus at the AC side, for which the loss factors as well as the base
        voltage on the DC side match the specification.
        """
        # 1) The source bus must be connected to the specified AC bus
        converters = scenario.converter.loc[scenario.converter['src'] == bus_id]

        # 2) The destination bus must be DC and match the DC base voltage
        bus_dst = scenario.bus.loc[converters['dst'].to_numpy()]
        converters = converters.loc[
            (bus_dst['type'].to_numpy() == BusType.DC) &
            (bus_dst['base_kv'].to_numpy() == dc_base_voltage)
        ]

        # 3) The loss factors must match the specification
        converters = converters.loc[
            (converters['loss_fwd'] == loss_fwd) &
            (converters['loss_bwd'] == loss_bwd)
        ]
        return converters

    def upgrade_converter(converter_id):
        """
        Upgrade the specified converter.

        This function assumes that the source bus of the AC/DC converters is at
        the AC side. The capability is upgraded according to the specification.
        """
        cap_src = scenario.converter.loc[converter_id, 'cap_src']
        cap_src.p_max += converter_p_cap
        cap_src.p_min -= converter_p_cap
        cap_src.q_max += converter_q_cap
        cap_src.q_min -= converter_q_cap

        cap_dst = scenario.converter.loc[converter_id, 'cap_dst']
        cap_dst.p_max += converter_p_cap
        cap_dst.p_min -= converter_p_cap

    def add_converter(ac_bus_id):
        """
        Add and AC/DC converter to the specified bus.

        This function creates a new DC bus and an AC/DC converter with its
        source bus at the AC side. The converter is configured according to the
        specification and the DC voltage limits are inherited from the AC bus.
        """
        dc_bus_id = scenario.add_bus(
            type_=BusType.DC,
            base_kv=dc_base_voltage,
            v_min=scenario.bus.at[ac_bus_id, 'v_min'],
            v_max=scenario.bus.at[ac_bus_id, 'v_max'],
            zone=scenario.bus.at[ac_bus_id, 'zone']
        )
        converter_id = scenario.add_converter(
            src=ac_bus_id,
            dst=dc_bus_id,
            cap_src=ConverterCapRegion(p_bnd=[-converter_p_cap, converter_p_cap],
                                       q_bnd=[-converter_q_cap, converter_q_cap]),
            cap_dst=ConverterCapRegion(p_bnd=[-converter_p_cap, converter_p_cap],
                                       q_bnd=None),
            loss_fwd=loss_fwd,
            loss_bwd=loss_bwd
        )
        return converter_id

    converter_id_src = None
    converter_id_dst = None

    if amalgamate:
        converters_src = find_acdc_converter(src)
        converters_dst = find_acdc_converter(dst)

        if not converters_src.empty and not converters_dst.empty:
            def find_acyclic_amalgamation():
                """
                Find a converter combination for which the additionally
                introduced DC line does not lead to a meshed DC subgrid.
                """
                e_src = scenario.e_src
                e_dst = scenario.e_dst
                nodes = np.arange(scenario.num_buses)
                for id_src in converters_src.index:
                    bus_idx_src = scenario.get_bus_index(
                        hynet_id_(converters_src.at[id_src, 'dst'])
                    )
                    e_src.at[branch_id] = bus_idx_src
                    for id_dst in converters_dst.index:
                        e_dst.at[branch_id] = scenario.get_bus_index(
                            hynet_id_(converters_dst.at[id_dst, 'dst'])
                        )
                        edges = (e_src.to_numpy(), e_dst.to_numpy())
                        if is_acyclic_component(nodes, edges, root=bus_idx_src):
                            return id_src, id_dst
                # All source *and* destination amalgamations lead to loops, so
                # only amalgamate at one of the terminals
                return converters_src.index[0], None
            converter_id_src, converter_id_dst = find_acyclic_amalgamation()
        elif not converters_src.empty:
            converter_id_src = converters_src.index[0]
        elif not converters_dst.empty:
            converter_id_dst = converters_dst.index[0]

    amalgamated = namedtuple('Amalgamation', ['src', 'dst'])\
        (converter_id_src is not None, converter_id_dst is not None)

    if converter_id_src is None:
        converter_id_src = add_converter(src)
    else:
        upgrade_converter(converter_id_src)

    if converter_id_dst is None:
        converter_id_dst = add_converter(dst)
    else:
        upgrade_converter(converter_id_dst)

    # Update the series resistance according to the change in the base voltages
    # (See, e.g., the book "Power Systems Analysis" by Bergen and Vittal)
    line_resistance = branch['z_bar'].real
    line_resistance *= (ac_base_voltage / dc_base_voltage) ** 2

    scenario.branch.at[branch_id, 'type'] = BranchType.LINE
    scenario.branch.at[branch_id, 'src'] = \
        scenario.converter.at[converter_id_src, 'dst']  # Dst. is the DC side
    scenario.branch.at[branch_id, 'dst'] = \
        scenario.converter.at[converter_id_dst, 'dst']  # Dst. is the DC side
    scenario.branch.at[branch_id, 'z_bar'] = hynet_complex_(line_resistance)
    scenario.branch.at[branch_id, 'y_src'] = hynet_complex_(0)
    scenario.branch.at[branch_id, 'y_dst'] = hynet_complex_(0)
    scenario.branch.at[branch_id, 'rating'] *= capacity_factor
    scenario.branch.at[branch_id, 'angle_min'] = hynet_float_(np.nan)
    scenario.branch.at[branch_id, 'angle_max'] = hynet_float_(np.nan)
    scenario.branch.at[branch_id, 'drop_min'] = hynet_float_(np.nan)
    scenario.branch.at[branch_id, 'drop_max'] = hynet_float_(np.nan)

    return converter_id_src, converter_id_dst, amalgamated
