import unittest

import falcon.testing
import pymq
from pymq.provider.redis import RedisConfig

import symmetry.webapp.app as webapp
from symmetry.api import NodeInfo, RoutingRecord
from symmetry.clusterd import BalancingPolicyDaemon, RedisClusterInfo
from symmetry.clusterd.policies.balancing import Weighted
from symmetry.webapp.app import DefaultRedisContext
from tests.testutils import RedisResource


class WebAppTestCase(falcon.testing.TestCase):
    redis: RedisResource
    eventbus: pymq.core.EventBus
    app_context: DefaultRedisContext

    @classmethod
    def setUpClass(cls):
        cls.redis = RedisResource()
        cls.redis.setUp()

    @classmethod
    def tearDownClass(cls):
        cls.redis.tearDown()

    def setUp(self):
        super().setUp()
        pymq.init(RedisConfig(self.rds))
        self.app_context = webapp.DefaultRedisContext(self.rds)
        webapp.setup(self.app, self.app_context)

    def tearDown(self):
        pymq.shutdown()
        self.redis.rds.flushall()

    @property
    def rds(self):
        return self.redis.rds


class NodesResourceTest(WebAppTestCase):

    def test_nodes_get(self):
        result = self.simulate_get('/api/nodes')
        self.assertEqual(0, len(result.json))

        self.app_context.node_manager.save_node(NodeInfo('unittest_node', '127.0.0.2'))

        result = self.simulate_get('/api/nodes')
        self.assertEqual(1, len(result.json))

    def test_nodes_post(self):
        self.simulate_post('/api/nodes', json={'node_id': 'added_node', 'host': '127.0.0.3'})

        nodes = self.app_context.node_manager.get_nodes()

        self.assertEqual(1, len(nodes))
        self.assertEqual('added_node', nodes[0].node_id)
        self.assertEqual('127.0.0.3', nodes[0].host)


class NodeResourceTest(WebAppTestCase):

    def test_nodes_get(self):
        expected = NodeInfo('unittest_node', '127.0.0.2', '01:02:03:04:05:06')

        self.app_context.node_manager.save_node(expected)
        result = self.simulate_get('/api/nodes/unittest_node')

        self.assertEqual(expected.node_id, result.json['node_id'])
        self.assertEqual(expected.host, result.json['host'])
        self.assertEqual(expected.mac, result.json['mac'])
        self.assertEqual(int(expected.ssh_port), int(result.json['ssh_port']))

    def test_nodes_get_non_existing_returns_404(self):
        result = self.simulate_get('/api/nodes/non-existing')
        self.assertEqual(falcon.HTTP_404, result.status)

    def test_nodes_delete(self):
        expected = NodeInfo('unittest_node', '127.0.0.2', '01:02:03:04:05:06')
        self.app_context.node_manager.save_node(expected)

        nodes = self.app_context.node_manager.get_nodes()
        self.assertEqual(1, len(nodes))  # making sure it's actually there

        self.simulate_delete('/api/nodes/unittest_node')

        nodes = self.app_context.node_manager.get_nodes()
        self.assertEqual(0, len(nodes), 'Nodes list was not empty: %s' % nodes)

    def test_nodes_delete_non_existing_returns_404(self):
        result = self.simulate_delete('/api/nodes/non-existing')
        self.assertEqual(falcon.HTTP_404, result.status)


class RoutesResourceTest(WebAppTestCase):

    def test_routes_get(self):
        record0 = RoutingRecord('aservice', ['ahost', 'bhost'], [2, 3])
        record1 = RoutingRecord('bservice', ['ahost', 'bhost'], [4, 5])
        self.app_context.rtbl.set_routing(record0)
        self.app_context.rtbl.set_routing(record1)

        result = self.simulate_get('/api/routes')
        result = list(result.json)

        self.assertEqual(2, len(result))
        result.sort(key=lambda d: d['service'])

        self.assertEqual(record0.service, result[0]['service'])
        self.assertEqual(record0.hosts, result[0]['hosts'])
        self.assertEqual(record0.weights, result[0]['weights'])

        self.assertEqual(record1.service, result[1]['service'])
        self.assertEqual(record1.hosts, result[1]['hosts'])
        self.assertEqual(record1.weights, result[1]['weights'])

    def test_routes_post(self):
        doc = {'service': 'cservice', 'hosts': ['ahost', 'bhost'], 'weights': [1, 2]}

        self.assertEqual(0, len(self.app_context.rtbl.get_routes()))

        self.simulate_post('/api/routes', json=doc)

        self.assertEqual(1, len(self.app_context.rtbl.get_routes()))

        record = self.app_context.rtbl.get_routing('cservice')

        self.assertEqual(doc['service'], record.service)
        self.assertEqual(doc['hosts'], record.hosts)
        self.assertEqual(doc['weights'], record.weights)


class RoutesServiceResourceTest(WebAppTestCase):
    def test_routes_service_get(self):
        record0 = RoutingRecord('aservice', ['ahost', 'bhost'], [2, 3])
        record1 = RoutingRecord('bservice', ['ahost', 'bhost'], [4, 5])
        self.app_context.rtbl.set_routing(record0)
        self.app_context.rtbl.set_routing(record1)

        result = self.simulate_get('/api/routes/aservice')

        self.assertEqual(record0.service, result.json['service'])
        self.assertEqual(record0.hosts, result.json['hosts'])
        self.assertEqual(record0.weights, result.json['weights'])

    def test_routes_service_get_non_existing(self):
        result = self.simulate_get('/api/routes/nonexisting')
        self.assertEqual(falcon.HTTP_404, result.status)

    def test_routes_service_delete(self):
        record0 = RoutingRecord('aservice', ['ahost', 'bhost'], [2, 3])
        self.app_context.rtbl.set_routing(record0)

        self.assertEqual(1, len(self.app_context.rtbl.get_routes()))

        self.simulate_delete('/api/routes/aservice')

        self.assertEqual(0, len(self.app_context.rtbl.get_routes()))
        self.assertRaises(ValueError, self.app_context.rtbl.get_routing, 'aservice')


class BalancingPoliciesResourceTest(WebAppTestCase):
    def test_policies_balancing_get(self):
        result = self.simulate_get('/api/policies/balancing')
        self.assertEqual(result.status, falcon.HTTP_OK)

        items = result.json
        self.assertTrue(len(items) > 0)

        self.assertIn('RoundRobin', [item['policy'] for item in items])
        self.assertIn('Weighted', [item['policy'] for item in items])

    def test_policies_balancing_get_single(self):
        result = self.simulate_get('/api/policies/balancing/RoundRobin')
        self.assertEqual(result.status, falcon.HTTP_OK)

        item = result.json
        self.assertEqual('RoundRobin', item['policy'])

    def test_policies_balancing_get_active(self):
        daemon = BalancingPolicyDaemon(RedisClusterInfo(self.app_context.rds), self.app_context.rtbl)
        policy = Weighted({
            'node1': 1,
            'node2': 2
        })
        daemon._policy = policy

        result = self.simulate_get('/api/policies/balancing/active')
        self.assertEqual(result.status, falcon.HTTP_OK)

        item = result.json
        self.assertEqual('Weighted', item['policy'])
        self.assertEqual({'weights': policy.weights}, item['parameters'])


if __name__ == '__main__':
    unittest.main()
