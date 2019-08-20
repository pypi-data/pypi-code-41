"""Manage flooding to ports on VLANs."""

# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2015 Brad Cowie, Christopher Lorier and Joe Stringer.
# Copyright (C) 2015 Research and Education Advanced Network New Zealand Ltd.
# Copyright (C) 2015--2019 The Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict

from faucet import valve_of
from faucet import valve_packet
from faucet.valve_manager_base import ValveManagerBase


class ValveFloodManager(ValveManagerBase):
    """Implement dataplane based flooding for standalone dataplanes."""

    # Enumerate possible eth_dst flood destinations.
    # First bool says whether to flood this destination if the VLAN
    # has unicast flooding enabled (if unicast flooding is enabled,
    # then we flood all destination eth_dsts).
    FLOOD_DSTS = (
        (True, None, None),
        (False, valve_packet.BRIDGE_GROUP_ADDRESS, valve_packet.mac_byte_mask(3)), # 802.x
        (False, '01:00:5E:00:00:00', valve_packet.mac_byte_mask(3)), # IPv4 multicast
        (False, '33:33:00:00:00:00', valve_packet.mac_byte_mask(2)), # IPv6 multicast
        (False, valve_of.mac.BROADCAST_STR, valve_packet.mac_byte_mask(6)), # eth broadcasts
    )

    def __init__(self, logger, flood_table, pipeline,
                 use_group_table, groups, combinatorial_port_flood,
                 canonical_port_order):
        self.logger = logger
        self.flood_table = flood_table
        self.pipeline = pipeline
        self.use_group_table = use_group_table
        self.groups = groups
        self.combinatorial_port_flood = combinatorial_port_flood
        self.bypass_priority = self._FILTER_PRIORITY
        self.flood_priority = self._MATCH_PRIORITY
        self.classification_offset = 0x100
        self.canonical_port_order = canonical_port_order

    def initialise_tables(self):
        """Initialise the flood table with filtering flows."""
        ofmsgs = []
        for eth_dst, eth_dst_mask in (
                (valve_packet.CISCO_CDP_VTP_UDLD_ADDRESS, valve_packet.mac_byte_mask(6)),
                (valve_packet.CISCO_SPANNING_GROUP_ADDRESS, valve_packet.mac_byte_mask(6)),
                (valve_packet.BRIDGE_GROUP_ADDRESS, valve_packet.BRIDGE_GROUP_MASK)):
            ofmsgs.append(self.flood_table.flowdrop(
                self.flood_table.match(eth_dst=eth_dst, eth_dst_mask=eth_dst_mask),
                priority=self._mask_flood_priority(eth_dst_mask)))
        return ofmsgs

    def _mask_flood_priority(self, eth_dst_mask):
        return self.flood_priority + valve_packet.mac_mask_bits(eth_dst_mask)

    @staticmethod
    def _vlan_all_ports(vlan, exclude_unicast):
        """Return list of all ports that should be flooded to on a VLAN."""
        return list(vlan.flood_ports(vlan.get_ports(), exclude_unicast))

    def _build_flood_local_rule_actions(self, vlan, exclude_unicast, in_port, exclude_all_external):
        """Return a list of flood actions to flood packets from a port."""
        external_ports = self.canonical_port_order(vlan.loop_protect_external_ports_up())
        exclude_ports = vlan.exclude_same_lag_member_ports(in_port)
        exclude_ports.update(vlan.exclude_native_if_dot1x())
        if exclude_all_external or (in_port is not None and in_port.loop_protect_external):
            exclude_ports.update(set(external_ports))
        else:
            exclude_ports.update(set(external_ports[1:]))
        return valve_of.flood_port_outputs(
            vlan.tagged_flood_ports(exclude_unicast),
            vlan.untagged_flood_ports(exclude_unicast),
            in_port=in_port,
            exclude_ports=exclude_ports)

    def _build_flood_rule_actions(self, vlan, exclude_unicast, in_port, exclude_all_external=False):
        actions = []
        if vlan.loop_protect_external_ports() and vlan.tagged_flood_ports(exclude_unicast):
            actions.append(self.flood_table.set_external_forwarding_requested())
        actions.extend(self._build_flood_local_rule_actions(
            vlan, exclude_unicast, in_port, exclude_all_external))
        return actions

    def _build_flood_rule(self, match, command, flood_acts, flood_priority):
        return self.flood_table.flowmod(
            match=match,
            command=command,
            inst=[valve_of.apply_actions(flood_acts)],
            priority=flood_priority)

    def _vlan_flood_priority(self, eth_dst_mask):
        return self._mask_flood_priority(eth_dst_mask)

    def _build_flood_rule_for_vlan(self, vlan, eth_dst, eth_dst_mask, # pylint: disable=too-many-arguments
                                   exclude_unicast, command):
        flood_priority = self._vlan_flood_priority(eth_dst_mask)
        match = self.flood_table.match(
            vlan=vlan, eth_dst=eth_dst, eth_dst_mask=eth_dst_mask)
        flood_acts = self._build_flood_rule_actions(
            vlan, exclude_unicast, None)
        return (self._build_flood_rule(match, command, flood_acts, flood_priority), flood_acts)

    @staticmethod
    def _output_non_output_actions(flood_acts):
        output_ports = set()
        all_nonoutput_actions = set()
        deduped_acts = []
        # avoid dedupe_ofmsgs() here, as it's expensive - most of the time we are comparing
        # port numbers as integers which is much cheaper.
        for act in flood_acts:
            if valve_of.is_output(act):
                if act.port in output_ports:
                    continue
                output_ports.add(act.port)
            else:
                str_act = str(act)
                if str_act in all_nonoutput_actions:
                    continue
                all_nonoutput_actions.add(str_act)
            deduped_acts.append(act)
        nonoutput_actions = all_nonoutput_actions - set([str(valve_of.pop_vlan())])
        return (deduped_acts, output_ports, nonoutput_actions)

    def _build_flood_acts_for_port(self, vlan, exclude_unicast, port,
                                   exclude_all_external=False):
        flood_acts = []
        port_output_ports = []
        port_non_output_acts = []
        if port.dyn_phys_up:
            flood_acts = self._build_flood_rule_actions(
                vlan, exclude_unicast, port, exclude_all_external)
            flood_acts, port_output_ports, port_non_output_acts = self._output_non_output_actions(
                flood_acts)
            if not port_output_ports:
                flood_acts = []
                port_non_output_acts = []
        return (flood_acts, port_output_ports, port_non_output_acts)

    def _build_flood_match_priority(self, port, vlan, eth_dst, eth_dst_mask, add_match):
        flood_priority = self._vlan_flood_priority(eth_dst_mask) + 1
        if add_match is None:
            add_match = {}
        match = self.flood_table.match(
            vlan=vlan, in_port=port.number,
            eth_dst=eth_dst, eth_dst_mask=eth_dst_mask,
            **add_match)
        return (flood_priority, match)

    def _build_flood_rule_for_port(self, vlan, eth_dst, eth_dst_mask, # pylint: disable=too-many-arguments
                                   command, port, flood_acts, add_match=None):
        flood_priority, match = self._build_flood_match_priority(
            port, vlan, eth_dst, eth_dst_mask, add_match)
        return self._build_flood_rule(match, command, flood_acts, flood_priority)

    def _build_mask_flood_rules(self, vlan, eth_dst, eth_dst_mask, # pylint: disable=too-many-arguments
                                exclude_unicast, command):
        ofmsgs = []
        if self.combinatorial_port_flood:
            for port in self._vlan_all_ports(vlan, exclude_unicast):
                flood_acts, _, _ = self._build_flood_acts_for_port(
                    vlan, exclude_unicast, port)
                if flood_acts:
                    ofmsgs.append(self._build_flood_rule_for_port(
                        vlan, eth_dst, eth_dst_mask, command, port, flood_acts))
        else:
            vlan_flood_ofmsg, vlan_flood_acts = self._build_flood_rule_for_vlan(
                vlan, eth_dst, eth_dst_mask, exclude_unicast, command)
            if not self.use_group_table:
                ofmsgs.append(vlan_flood_ofmsg)
            flood_acts, vlan_output_ports, vlan_non_output_acts = self._output_non_output_actions(
                vlan_flood_acts)
            for port in self._vlan_all_ports(vlan, exclude_unicast):
                (flood_acts,
                 port_output_ports,
                 port_non_output_acts) = self._build_flood_acts_for_port(
                     vlan, exclude_unicast, port)
                if not flood_acts:
                    continue
                if (vlan_output_ports - set([port.number]) == port_output_ports
                        and vlan_non_output_acts == port_non_output_acts):
                    # Delete a potentially existing port specific flow
                    # TODO: optimize, avoid generating delete for port if no existing flow.
                    flood_priority, match = self._build_flood_match_priority(
                        port, vlan, eth_dst, eth_dst_mask, add_match=None)
                    ofmsgs.append(self.flood_table.flowdel(
                        match=match, priority=flood_priority))
                else:
                    ofmsgs.append(self._build_flood_rule_for_port(
                        vlan, eth_dst, eth_dst_mask, command, port, flood_acts))
        return ofmsgs

    def _build_multiout_flood_rules(self, vlan, command):
        """Build flooding rules for a VLAN without using groups."""
        ofmsgs = []
        for unicast_eth_dst, eth_dst, eth_dst_mask in self.FLOOD_DSTS:
            if unicast_eth_dst and not vlan.unicast_flood:
                continue
            ofmsgs.extend(self._build_mask_flood_rules(
                vlan, eth_dst, eth_dst_mask,
                unicast_eth_dst, command))
        return ofmsgs

    def _build_group_flood_rules(self, vlan, modify, command):
        """Build flooding rules for a VLAN using groups."""
        ofmsgs = []
        groups_by_unicast_eth = {}

        _, vlan_flood_acts = self._build_flood_rule_for_vlan(
            vlan, None, None, False, command)

        group_id = vlan.vid
        group = self.groups.get_entry(
            group_id, valve_of.build_group_flood_buckets(vlan_flood_acts))
        groups_by_unicast_eth[False] = group
        groups_by_unicast_eth[True] = group

        # Only configure unicast flooding group if has different output
        # actions to non unicast flooding.
        _, unicast_eth_vlan_flood_acts = self._build_flood_rule_for_vlan(
            vlan, None, None, True, command)
        unicast_eth_vlan_flood_acts, unicast_output_ports, _ = self._output_non_output_actions(
            unicast_eth_vlan_flood_acts)
        vlan_flood_acts, vlan_output_ports, _ = self._output_non_output_actions(vlan_flood_acts)
        if unicast_output_ports != vlan_output_ports:
            group_id += valve_of.VLAN_GROUP_OFFSET
            group = self.groups.get_entry(
                group_id, valve_of.build_group_flood_buckets(unicast_eth_vlan_flood_acts))
            groups_by_unicast_eth[True] = group

        for group in groups_by_unicast_eth.values():
            if modify:
                ofmsgs.append(group.modify())
            else:
                ofmsgs.extend(group.add())

        for unicast_eth_dst, eth_dst, eth_dst_mask in self.FLOOD_DSTS:
            if unicast_eth_dst and not vlan.unicast_flood:
                continue
            group = groups_by_unicast_eth[unicast_eth_dst]
            match = self.flood_table.match(
                vlan=vlan, eth_dst=eth_dst, eth_dst_mask=eth_dst_mask)
            flood_priority = self._mask_flood_priority(eth_dst_mask)
            ofmsgs.append(self.flood_table.flowmod(
                match=match,
                command=command,
                inst=[valve_of.apply_actions([valve_of.group_act(group.group_id)])],
                priority=flood_priority))
        return ofmsgs

    def add_vlan(self, vlan):
        return self.build_flood_rules(vlan)

    def del_vlan(self, vlan):
        return [self.flood_table.flowdel(self.flood_table.match(vlan=vlan.vid))]

    def update_vlan(self, vlan):
        return self.build_flood_rules(vlan, modify=True)

    def build_flood_rules(self, vlan, modify=False):
        """Add flows to flood packets to unknown destinations on a VLAN."""
        command = valve_of.ofp.OFPFC_ADD
        if modify:
            command = valve_of.ofp.OFPFC_MODIFY_STRICT
        ofmsgs = self._build_multiout_flood_rules(vlan, command)
        if self.use_group_table:
            ofmsgs.extend(self._build_group_flood_rules(vlan, modify, command))
        return ofmsgs

    @staticmethod
    def update_stack_topo(event, dp, port=None): # pylint: disable=unused-argument,invalid-name
        """Update the stack topology. It has nothing to do for non-stacking DPs."""
        return

    @staticmethod
    def edge_learn_port(_other_valves, pkt_meta):
        """Possibly learn a host on a port.

        Args:
            other_valves (list): All Valves other than this one.
            pkt_meta (PacketMeta): PacketMeta instance for packet received.
        Returns:
            port to learn host on.
        """
        return pkt_meta.port


class ValveFloodStackManager(ValveFloodManager):
    """Implement dataplane based flooding for stacked dataplanes."""

    def __init__(self, logger, flood_table, pipeline, # pylint: disable=too-many-arguments
                 use_group_table, groups,
                 combinatorial_port_flood, canonical_port_order,
                 stack_ports, has_externals,
                 dp_shortest_path_to_root, shortest_path_port,
                 longest_path_to_root_len, is_stack_root,
                 is_stack_root_candidate, graph):
        super(ValveFloodStackManager, self).__init__(
            logger, flood_table, pipeline,
            use_group_table, groups,
            combinatorial_port_flood,
            canonical_port_order)
        self.stack_ports = stack_ports
        self.canonical_port_order = canonical_port_order
        self.externals = has_externals
        self.shortest_path_port = shortest_path_port
        self.dp_shortest_path_to_root = dp_shortest_path_to_root
        self.longest_path_to_root_len = longest_path_to_root_len
        self.is_stack_root = is_stack_root
        self.is_stack_root_candidate = is_stack_root_candidate
        self.graph = graph
        stack_size = self.longest_path_to_root_len()
        if stack_size is not None and stack_size > 2:
            self.logger.info('stack size %u' % stack_size)
            self._flood_actions_func = self._flood_actions
        else:
            self.logger.info('stack size <= 2, using non root-reflection stacking')
            self._flood_actions_func = self._flood_actions_size2
        self._set_ext_port_flag = []
        self._set_nonext_port_flag = []
        self.external_root_only = False
        if self.externals:
            self.logger.info('external ports present, using loop protection')
            self._set_ext_port_flag = [self.flood_table.set_external_forwarding_requested()]
            self._set_nonext_port_flag = [self.flood_table.set_no_external_forwarding_requested()]
            if not self.is_stack_root() and self.is_stack_root_candidate():
                self.logger.info('external flooding on root only')
                self.external_root_only = True
        self._reset_peer_distances()

    def _reset_peer_distances(self):
        """Reset distances to/from root for this DP."""
        self.all_towards_root_stack_ports = set()
        self.towards_root_stack_ports = set()
        self.away_from_root_stack_ports = set()
        all_peer_ports = {port for port in self._canonical_stack_up_ports(self.stack_ports)}

        if self.is_stack_root():
            self.away_from_root_stack_ports = all_peer_ports
        else:
            port_peer_distances = {
                port: len(port.stack['dp'].shortest_path_to_root()) for port in all_peer_ports}
            shortest_peer_distance = None
            for port, port_peer_distance in port_peer_distances.items():
                if shortest_peer_distance is None:
                    shortest_peer_distance = port_peer_distance
                    continue
                shortest_peer_distance = min(shortest_peer_distance, port_peer_distance)
            self.all_towards_root_stack_ports = {
                port for port, port_peer_distance in port_peer_distances.items()
                if port_peer_distance == shortest_peer_distance}
            if self.all_towards_root_stack_ports:
                first_peer_dp = list(self.all_towards_root_stack_ports)[0].stack['dp']
                self.towards_root_stack_ports = {
                    port for port in self.all_towards_root_stack_ports
                    if port.stack['dp'] == first_peer_dp}
            self.away_from_root_stack_ports = all_peer_ports - self.all_towards_root_stack_ports

        if not self.is_stack_root():
            if self.towards_root_stack_ports:
                self.logger.info(
                    'shortest path to root is via %s' % self.towards_root_stack_ports)
            else:
                self.logger.info('no path available to root')

    def _flood_actions_size2(self, in_port, external_ports,
                             away_flood_actions, toward_flood_actions, local_flood_actions):
        if not in_port or in_port in self.stack_ports:
            flood_prefix = []
        else:
            if external_ports:
                flood_prefix = self._set_nonext_port_flag
            else:
                flood_prefix = self._set_ext_port_flag

        # Special case for stack with maximum distance 2 - we don't need to reflect off of the root.
        if self.is_stack_root():
            flood_actions = (
                flood_prefix + away_flood_actions + local_flood_actions)
        else:
            # Default strategy is flood locally and then to the root.
            flood_actions = (
                flood_prefix + toward_flood_actions + local_flood_actions)

            # If packet came from the root, flood it locally.
            if in_port in self.all_towards_root_stack_ports:
                flood_actions = (flood_prefix + local_flood_actions)

        return flood_actions

    def _flood_actions(self, in_port, external_ports,
                       away_flood_actions, toward_flood_actions, local_flood_actions):
        # General case for stack with maximum distance > 2
        if self.is_stack_root():
            if external_ports:
                flood_prefix = self._set_nonext_port_flag
            else:
                flood_prefix = self._set_ext_port_flag
            flood_actions = (away_flood_actions + local_flood_actions)

            if in_port and in_port in self.away_from_root_stack_ports:
                # Packet from a non-root switch, flood locally and to all non-root switches
                # (reflect it).
                flood_actions = (
                    away_flood_actions + [valve_of.output_in_port()] + local_flood_actions)

            flood_actions = flood_prefix + flood_actions
        else:
            # Default non-root strategy is flood towards root.
            if external_ports:
                flood_actions = self._set_nonext_port_flag + toward_flood_actions
            else:
                flood_actions = self._set_ext_port_flag + toward_flood_actions

            if in_port:
                # Packet from switch further away, flood it to the root.
                if in_port in self.away_from_root_stack_ports:
                    flood_actions = toward_flood_actions
                # Packet from the root.
                elif in_port in self.all_towards_root_stack_ports:
                    # If we have external ports, and packet hasn't already been flooded
                    # externally, flood it externally before passing it to further away switches,
                    # and mark it flooded.
                    if external_ports:
                        flood_actions = (
                            self._set_nonext_port_flag + away_flood_actions + local_flood_actions)
                    else:
                        flood_actions = (
                            away_flood_actions + self._set_nonext_port_flag + local_flood_actions)
                # Packet from external port, locally. Mark it already flooded externally and
                # flood to root (it came from an external switch so keep it within the stack).
                elif in_port.loop_protect_external:
                    flood_actions = self._set_nonext_port_flag + toward_flood_actions
                else:
                    flood_actions = self._set_ext_port_flag + toward_flood_actions

        return flood_actions

    def _build_flood_rule_actions(self, vlan, exclude_unicast, in_port, exclude_all_external=False):
        """Calculate flooding destinations based on this DP's position.

        If a standalone switch, then flood to local VLAN ports.

        If a distributed switch where all switches are directly
        connected to the root (star topology), edge switches flood locally
        and to the root, and the root floods to the other edges.

        If a non-star distributed switch topologies, use selective
        flooding (see the following example).

                               Hosts
                               ||||
                               ||||
                 +----+       +----+       +----+
              ---+1   |       |1234|       |   1+---
        Hosts ---+2   |       |    |       |   2+--- Hosts
              ---+3   |       |    |       |   3+---
              ---+4  5+-------+5  6+-------+5  4+---
                 +----+       +----+       +----+

                 Root DP

        Non-root switches flood only to the root. The root switch
        reflects incoming floods back out. Non-root switches
        flood packets from the root locally and further away.
        Flooding is entirely implemented in the dataplane.

        A host connected to a non-root switch can receive a copy
        of its own flooded packet (because the non-root switch
        does not know it has seen the packet already).

        A host connected to the root switch does not have this problem
        (because flooding is always away from the root). Therefore,
        connections to other non-FAUCET stacking networks should only
        be made to the root.

        On the root switch (left), flood destinations are:

        1: 2 3 4 5(s)
        2: 1 3 4 5(s)
        3: 1 2 4 5(s)
        4: 1 2 3 5(s)
        5: 1 2 3 4 5(s, note reflection)

        On the middle switch:

        1: 5(s)
        2: 5(s)
        3: 5(s)
        4: 5(s)
        5: 1 2 3 4 6(s)
        6: 5(s)

        On the rightmost switch:

        1: 5(s)
        2: 5(s)
        3: 5(s)
        4: 5(s)
        5: 1 2 3 4
        """
        exclude_ports = []
        external_ports = vlan.loop_protect_external_ports()

        if in_port and in_port in self.stack_ports:
            in_port_peer_dp = in_port.stack['dp']
            exclude_ports = [
                port for port in self.stack_ports
                if port.stack['dp'] == in_port_peer_dp]
        local_flood_actions = self._build_flood_local_rule_actions(
            vlan, exclude_unicast, in_port, exclude_all_external)
        away_flood_actions = valve_of.flood_tagged_port_outputs(
            self.away_from_root_stack_ports, in_port, exclude_ports=exclude_ports)
        toward_flood_actions = valve_of.flood_tagged_port_outputs(
            self.towards_root_stack_ports, in_port)
        flood_acts = self._flood_actions_func(
            in_port, external_ports, away_flood_actions,
            toward_flood_actions, local_flood_actions)
        return flood_acts

    def _canonical_stack_up_ports(self, ports):
        return self.canonical_port_order([port for port in ports if port.is_stack_up()])

    def _build_mask_flood_rules(self, vlan, eth_dst, eth_dst_mask, # pylint: disable=too-many-arguments
                                exclude_unicast, command):
        # Stack ports aren't in VLANs, so need special rules to cause flooding from them.
        ofmsgs = super(ValveFloodStackManager, self)._build_mask_flood_rules(
            vlan, eth_dst, eth_dst_mask, exclude_unicast, command)
        towards_up_ports = self._canonical_stack_up_ports(self.towards_root_stack_ports)
        away_up_ports_by_dp = defaultdict(list)
        for port in self._canonical_stack_up_ports(self.away_from_root_stack_ports):
            away_up_ports_by_dp[port.stack['dp']].append(port)
        towards_up_port = None
        if towards_up_ports:
            towards_up_port = towards_up_ports[0]
        replace_priority_offset = (
            self.classification_offset - (
                self.pipeline.filter_priority - self.pipeline.select_priority))

        for port in self.stack_ports:
            prune = False
            if self.is_stack_root():
                # On the root switch, only flood from one port where multiply connected to a DP.
                away_up_port = None
                remote_dp = port.stack['dp']
                if away_up_ports_by_dp[remote_dp]:
                    away_up_port = away_up_ports_by_dp[remote_dp][0]
                prune = port in self.away_from_root_stack_ports and port != away_up_port
            else:
                # On a non root switch, only flood from one of the ports
                # connected towards the root.
                prune = port in self.all_towards_root_stack_ports and port != towards_up_port
            flood_acts = []

            match = {'in_port': port.number, 'vlan': vlan}
            if eth_dst is not None:
                match.update({'eth_dst': eth_dst, 'eth_dst_mask': eth_dst_mask})

            priority_offset = replace_priority_offset
            if eth_dst is None:
                priority_offset -= 1
            if prune:
                # Allow the prune rule to be replaced with OF strict matching if
                # this port is unpruned later.
                ofmsgs.extend(self.pipeline.filter_packets(
                    match, priority_offset=priority_offset))
            else:
                ofmsgs.extend(self.pipeline.remove_filter(
                    match, priority_offset=priority_offset))
                # Non-root switches don't need to learn hosts that only
                # broadcast, to save resources.
                if not self.is_stack_root():
                    if eth_dst is not None:
                        ofmsgs.extend(self.pipeline.select_packets(
                            self.flood_table, match,
                            priority_offset=self.classification_offset))

            if self.externals:
                # If external flag is set, flood to external ports, otherwise exclude them.
                for ext_port_flag, exclude_all_external in (
                        (valve_of.PCP_NONEXT_PORT_FLAG, True),
                        (valve_of.PCP_EXT_PORT_FLAG, False)):
                    if self.external_root_only:
                        exclude_all_external = True
                    if not prune:
                        flood_acts, _, _ = self._build_flood_acts_for_port(
                            vlan, exclude_unicast, port, exclude_all_external=exclude_all_external)
                    port_flood_ofmsg = self._build_flood_rule_for_port(
                        vlan, eth_dst, eth_dst_mask, command, port, flood_acts,
                        add_match={valve_of.EXTERNAL_FORWARDING_FIELD: ext_port_flag})
                    ofmsgs.append(port_flood_ofmsg)
            else:
                if not prune:
                    flood_acts, _, _ = self._build_flood_acts_for_port(
                        vlan, exclude_unicast, port)
                port_flood_ofmsg = self._build_flood_rule_for_port(
                    vlan, eth_dst, eth_dst_mask, command, port, flood_acts)
                ofmsgs.append(port_flood_ofmsg)

        return ofmsgs

    def _edge_dp_for_host(self, other_valves, pkt_meta):
        """Simple distributed unicast learning.

        Args:
            other_valves (list): All Valves other than this one.
            pkt_meta (PacketMeta): PacketMeta instance for packet received.
        Returns:
            Valve instance or None (of edge datapath where packet received)
        """
        # TODO: simplest possible unicast learning.
        # We find just one port that is the shortest unicast path to
        # the destination. We could use other factors (eg we could
        # load balance over multiple ports based on destination MAC).
        # TODO: edge DPs could use a different forwarding algorithm
        # (for example, just default switch to a neighbor).
        # Find port that forwards closer to destination DP that
        # has already learned this host (if any).
        if pkt_meta.port.stack:
            peer_dp = pkt_meta.port.stack['dp']
            if peer_dp.is_stack_edge() or peer_dp.is_stack_root():
                return peer_dp
        stacked_valves = [valve for valve in other_valves if valve.dp.stack is not None]
        eth_src = pkt_meta.eth_src
        vlan_vid = pkt_meta.vlan.vid
        for other_valve in stacked_valves:
            if vlan_vid in other_valve.dp.vlans:
                other_dp_vlan = other_valve.dp.vlans[vlan_vid]
                entry = other_dp_vlan.cached_host(eth_src)
                if entry and not entry.port.stack:
                    return other_valve.dp
        return None

    def update_stack_topo(self, event, dp, port=None):
        """Update the stack topo according to the event."""

        if self.graph is None:
            return

        def _stack_topo_up_dp(_dp): # pylint: disable=invalid-name
            for port in [port for port in _dp.stack_ports]:
                if port.is_stack_up():
                    _stack_topo_up_port(_dp, port)
                else:
                    _stack_topo_down_port(_dp, port)

        def _stack_topo_down_dp(_dp): # pylint: disable=invalid-name
            for port in [port for port in _dp.stack_ports]:
                _stack_topo_down_port(_dp, port)

        def _stack_topo_up_port(_dp, _port): # pylint: disable=invalid-name
            _dp.add_stack_link(self.graph, _dp, _port)

        def _stack_topo_down_port(_dp, _port): # pylint: disable=invalid-name
            _dp.remove_stack_link(self.graph, _dp, _port)

        if port:
            if event:
                _stack_topo_up_port(dp, port)
            else:
                _stack_topo_down_port(dp, port)
        else:
            if event:
                _stack_topo_up_dp(dp)
            else:
                _stack_topo_down_dp(dp)

        self._reset_peer_distances()

    def edge_learn_port(self, other_valves, pkt_meta):
        """
        Find a port towards the edge DP where the packet originated from

        Args:
            other_valves (list): All Valves other than this one.
            pkt_meta (PacketMeta): PacketMeta instance for packet received.
        Returns:
            port to learn host on, or None.
        """
        if pkt_meta.port.stack:
            edge_dp = self._edge_dp_for_host(other_valves, pkt_meta)
            # No edge DP may have learned this host yet.
            if edge_dp is None:
                return None
            return self.shortest_path_port(edge_dp.name)
        return super(ValveFloodStackManager, self).edge_learn_port(
            other_valves, pkt_meta)
