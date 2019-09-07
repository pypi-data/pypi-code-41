import threading
import unittest
from unittest import mock

import pymq
from timeout_decorator import timeout_decorator

from symmetry.api import ClusterInfo, RoutingRecord, NodeDisconnectedEvent, NodeActivatedEvent, \
    BalancingPolicyService
from symmetry.clusterd import BalancingPolicyDaemon, DefaultBalancingPolicyService
from symmetry.clusterd.policies.balancing import RoundRobin, Weighted
from symmetry.routing import RedisRoutingTable
from tests import testutils


class PolicyIntegrationTest(testutils.AppTestCase):
    rtbl: RedisRoutingTable
    cluster: ClusterInfo
    service: BalancingPolicyService

    @mock.patch('symmetry.api.ClusterInfo')
    def setUp(self, mock_cluster) -> None:
        super().setUp()
        self.rtbl = RedisRoutingTable(self.redis.rds)
        self.cluster: ClusterInfo = mock_cluster

        self.cluster.services = ['aservice']
        self.cluster.nodes = ['node1', 'node2', 'node3']
        self.cluster.active_nodes = ['node1', 'node2']

        self.service = DefaultBalancingPolicyService()


class RoundRobinPolicyIntegrationTest(PolicyIntegrationTest):

    @timeout_decorator.timeout(3)
    def test_update_round_robin_policy(self):
        daemon = BalancingPolicyDaemon(self.cluster, self.rtbl)

        t = threading.Thread(target=daemon.run)
        t.start()

        try:
            self.assertIsNone(daemon.get_active_policy(), 'Policy should be none if not yet set')

            self.service.set_active_policy(RoundRobin())

            policy = testutils.poll(daemon.get_active_policy, timeout=1)
            routes = testutils.poll(self.rtbl.get_routes, timeout=1)

            self.assertEqual('RoundRobin', policy.name)
            self.assertEqual(1, len(routes), 'expected one route to be set, was %s' % routes)

            record: RoutingRecord = routes[0]
            self.assertEqual('aservice', record.service)
            self.assertIn('node1', record.hosts)
            self.assertIn('node2', record.hosts)
            self.assertNotIn('node3', record.hosts, 'non-active node should not be set in provider')

            self.assertEqual(1, record.weights[0])
            self.assertEqual(1, record.weights[1])
        finally:
            daemon.close()

        t.join()

    @timeout_decorator.timeout(3)
    def test_round_robin_updates_removed_node_correctly(self):
        daemon = BalancingPolicyDaemon(self.cluster, self.rtbl)

        t = threading.Thread(target=daemon.run)
        t.start()

        try:
            self.service.set_active_policy(RoundRobin())

            records = testutils.poll(self.rtbl.get_routes, timeout=1)
            self.assertIn('node2', records[0].hosts)

            pymq.publish(NodeDisconnectedEvent('node2'))

            try:
                testutils.poll(lambda: 'node2' not in self.rtbl.get_routing('aservice').hosts, timeout=1)
            except TimeoutError:
                self.fail('Expected RoundRobinPolicy to remove disconnected node from: %s' % self.rtbl.get_routes())

            self.assertNotIn('node2', self.rtbl.get_routing('aservice').hosts)
        finally:
            daemon.close()

        t.join()

    @timeout_decorator.timeout(3)
    def test_round_robin_updates_activated_node_correctly(self):
        daemon = BalancingPolicyDaemon(self.cluster, self.rtbl)

        t = threading.Thread(target=daemon.run)
        t.start()

        try:
            self.service.set_active_policy(RoundRobin())

            records = testutils.poll(self.rtbl.get_routes, timeout=1)
            self.assertNotIn('node3', records[0].hosts)

            self.cluster.active_nodes.append('node3')
            pymq.publish(NodeActivatedEvent('node3'))

            try:
                testutils.poll(lambda: 'node3' in self.rtbl.get_routing('aservice').hosts, timeout=1)
            except TimeoutError:
                self.fail('Expected RoundRobinPolicy to add activated node to: %s' % self.rtbl.get_routes())

            self.assertIn('node3', self.rtbl.get_routing('aservice').hosts)
        finally:
            daemon.close()

        t.join()


class WeightedPolicyIntegrationTest(PolicyIntegrationTest):

    @timeout_decorator.timeout(3)
    def test_update_weighted_random_policy(self):
        daemon = BalancingPolicyDaemon(self.cluster, self.rtbl)

        t = threading.Thread(target=daemon.run)
        t.start()

        try:
            self.assertIsNone(daemon.get_active_policy(), 'Policy should be none if not yet set')

            policy = Weighted()
            policy.weights = {
                'node1': 1,
                'node2': 2,
                'node3': 3,
            }
            self.service.set_active_policy(policy)

            policy = testutils.poll(daemon.get_active_policy, timeout=1)
            routes = testutils.poll(self.rtbl.get_routes, timeout=1)

            self.assertEqual('Weighted', policy.name)
            self.assertEqual(1, len(routes), 'expected one route to be set, was %s' % routes)

            record: RoutingRecord = routes[0]
            self.assertEqual('aservice', record.service)
            self.assertIn('node1', record.hosts)
            self.assertIn('node2', record.hosts)
            self.assertNotIn('node3', record.hosts, 'non-active node should not be set in provider')

            self.assertEqual(1, record.weights[0])
            self.assertEqual(2, record.weights[1])
        finally:
            daemon.close()

        t.join()


if __name__ == '__main__':
    unittest.main()
