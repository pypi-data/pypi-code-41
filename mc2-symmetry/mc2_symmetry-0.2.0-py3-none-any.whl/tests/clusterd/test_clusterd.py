import unittest

from symmetry.clusterd import DefaultBalancingPolicyService
from symmetry.clusterd.policies import balancing_policy_provider_factory
from symmetry.clusterd.policies.balancing import RoundRobin, Weighted, WeightedProvider


class TestPolicyDiscoveryAndFactory(unittest.TestCase):

    def test_get_available_policies(self):
        service = DefaultBalancingPolicyService()
        policies = service.get_available_policies()

        self.assertTrue(len(policies) > 0)

        self.assertIn('RoundRobin', policies.keys())
        self.assertEqual(RoundRobin, policies['RoundRobin'])

        self.assertIn('Weighted', policies.keys())
        self.assertEqual(Weighted, policies['Weighted'])

    def test_factory(self):
        factory = balancing_policy_provider_factory()
        policy = Weighted()
        policy.weights = {
            'node1': 1,
            'node2': 2
        }

        provider = factory(policy, None, None)
        self.assertIsInstance(provider, WeightedProvider)
        self.assertIs(policy, provider.policy)


if __name__ == '__main__':
    unittest.main()
