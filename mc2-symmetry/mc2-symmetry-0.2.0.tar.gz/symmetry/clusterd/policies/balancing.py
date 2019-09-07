import logging
import time
from collections import defaultdict
from typing import Dict, List

import pymq

from symmetry.api import ClusterInfo, RoutingTable, NodeActivatedEvent, NodeDisconnectedEvent, RoutingRecord, \
    BalancingPolicy
from symmetry.telemetry.recorder import TelemetrySubscriber

logger = logging.getLogger(__name__)


class RoundRobin(BalancingPolicy):
    name = 'RoundRobin'


class Weighted(BalancingPolicy):
    name = 'Weighted'
    weights: Dict[str, float] = dict()

    def __init__(self, weights=None) -> None:
        super().__init__()
        if weights:
            self.weights = weights


class ReactiveAutoscaling(BalancingPolicy):
    name = 'ReactiveAutoscaling'

    metric: str = 'cpu'
    th_up: float = 80
    th_down: float = 25
    cooldown: float = 20
    window_length: int = 10


class BalancingPolicyProvider:
    policy: BalancingPolicy
    cluster: ClusterInfo
    rtbl: RoutingTable

    def __init__(self, policy, cluster, rtbl) -> None:
        super().__init__()
        self.policy = policy
        self.cluster: ClusterInfo = cluster
        self.rtbl: RoutingTable = rtbl

        pymq.subscribe(self._on_node_activated)
        pymq.subscribe(self._on_node_disconnected)

    # TODO: events for service added/removed/deployment changed

    def _on_node_activated(self, event: NodeActivatedEvent):
        pass

    def _on_node_disconnected(self, event: NodeDisconnectedEvent):
        pass

    def run(self):
        raise NotImplementedError

    def close(self):
        logger.debug('closing %s', self.__class__.__name__)
        pymq.unsubscribe(self._on_node_activated)
        pymq.unsubscribe(self._on_node_disconnected)


class RoundRobinProvider(BalancingPolicyProvider):
    policy: RoundRobin

    def _on_node_disconnected(self, event: NodeDisconnectedEvent):
        nodes = self.cluster.active_nodes
        nodes.remove(event.node_id)  # active_nodes may not be in the correct state yet

        self.update_weights(self.cluster.services, nodes)

    def _on_node_activated(self, event: NodeActivatedEvent):
        nodes = self.cluster.active_nodes
        if event.node_id not in nodes:
            nodes.append(event.node_id)

        self.update_weights(self.cluster.services, nodes)

    def run(self):
        self.update_weights(self.cluster.services, self.cluster.active_nodes)

    def update_weights(self, services, active_nodes):
        rtbl = self.rtbl

        for service in services:
            # TODO: we make an assumption that all services are replicated on all nodes, which is implicitly the case
            #  now, but this piece of code should use nrg to resolve node--service availability
            nodes = active_nodes
            weights = [1] * len(nodes)

            record = RoutingRecord(service, nodes, weights)
            logger.debug('%s setting routing record %s', self.__class__.__name__, record)
            rtbl.set_routing(record)


class WeightedProvider(BalancingPolicyProvider):
    policy: Weighted

    def _on_node_disconnected(self, event: NodeDisconnectedEvent):
        nodes = self.cluster.active_nodes
        nodes.remove(event.node_id)  # active_nodes may not be in the correct state yet

        self.update_weights(self.cluster.services, nodes)

    def _on_node_activated(self, event: NodeActivatedEvent):
        nodes = self.cluster.active_nodes
        if event.node_id not in nodes:
            nodes.append(event.node_id)

        self.update_weights(self.cluster.services, nodes)

    def run(self):
        self.update_weights(self.cluster.services, self.cluster.active_nodes)

    def update_weights(self, services, nodes):
        weights = self.get_weights(nodes)

        for service in services:
            record = RoutingRecord(service, nodes, weights)
            logger.debug('%s setting routing record %s', self.__class__.__name__, record)
            self.rtbl.set_routing(record)

    def get_weights(self, nodes) -> List[float]:
        weights = self.policy.weights
        return [weights.get(node_id, 0) for node_id in nodes]


class ReactiveAutoscalingProvider(BalancingPolicyProvider):
    policy: ReactiveAutoscaling

    def __init__(self, policy: ReactiveAutoscaling, cluster, rtbl) -> None:
        super().__init__(policy, cluster, rtbl)
        # FIXME: seems things are unnecessary complicated if there's on good way of injecting arbitrary application
        #  dependencies
        self._subscriber = TelemetrySubscriber(cluster.rds, pattern='telemetry:%s:*' % policy.metric)

        self._windows = defaultdict(list)
        self._last_scale = 0
        self._used_nodes = set()

    def scaled_recently(self):
        return (self._last_scale + self.policy.cooldown) > time.time()

    def _on_node_disconnected(self, event: NodeDisconnectedEvent):
        if event.node_id not in self._used_nodes:
            return

        # TODO: would probably be more effective to immediately search for alternative node to add instead
        self._used_nodes.remove(event.node_id)
        self._update_records()

    def _on_node_activated(self, event: NodeActivatedEvent):
        if not self._used_nodes:
            self._used_nodes.add(event.node_id)
            self._update_records()

    def run(self):
        policy = self.policy

        logger.debug(
            'starting reactive autoscaling policy {metric=%s, th_up=%s, th_down=%s, window_length=%s, cooldown=%s}"',
            policy.metric, policy.th_up, policy.th_down, policy.window_length, policy.cooldown)

        windows = self._windows
        th_up = policy.th_up
        th_down = policy.th_down
        metric = policy.metric
        used_nodes = self._used_nodes

        used_nodes.add(self.cluster.active_nodes[0])
        self._update_records()

        logger.debug('initiating balancer with nodes %s from %s', used_nodes, self.cluster.active_nodes)

        for t, _, node, value in self._subscriber.run():
            if node not in used_nodes:
                continue

            window = windows[node]
            window.append((float(t), float(value)))

            if self.scaled_recently():
                continue  # FIXME: busy waiting

            avg = self._evaluate_window(window)
            logger.debug('current average value of %s on %s is %s', metric, node, avg)
            if avg > th_up:
                self.scale_up()
                self._last_scale = time.time()
            elif avg < th_down:
                self.scale_down()
                self._last_scale = time.time()

    def scale_up(self):
        # pick the first active node not in use
        next_node = None
        for node in self.cluster.active_nodes:
            if node not in self._used_nodes:
                next_node = node
                break

        if not next_node:
            logger.debug('cannot scale up further, no additional nodes')
            # no additional nodes to scale to. guess the cluster is exploding.
            return False

        logger.debug('scaling up %s', next_node)
        self._used_nodes.add(next_node)
        self._update_records()

        return True

    def scale_down(self):
        if len(self._used_nodes) <= 1:
            # need at least one active node
            return False

        # scaling down is as easy as removing one of the used nodes and re-setting the weights
        node = self._used_nodes.pop()
        logger.debug('scaling down %s', node)
        self._update_records()
        return True

    def _update_records(self):
        nodes = list(self._used_nodes)
        weights = [1] * len(nodes)

        for service in self.cluster.services:
            record = RoutingRecord(service, nodes, weights)
            logger.debug('%s setting routing record %s', self.__class__.__name__, record)
            self.rtbl.set_routing(record)

    def close(self):
        self._subscriber.close()
        super().close()

    def _evaluate_window(self, window):
        t_n, _ = window[-1]
        boundary = t_n - self.policy.window_length

        # trim window
        window = [(t, v) for t, v in window if (t >= boundary)]

        values = [v for _, v in window]
        return round(sum(values) / len(values))
