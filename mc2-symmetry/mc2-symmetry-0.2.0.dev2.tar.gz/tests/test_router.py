import unittest

import symmetry.gateway
from symmetry.gateway import StaticRouter, ServiceRequest, StaticLocalhostBalancer, SymmetryHostRouter, \
    SymmetryServiceRouter


class TestRouterUrlCreation(unittest.TestCase):
    def test_static_router(self):
        router = StaticRouter('http://localhost')
        url = router._get_url(ServiceRequest('foobar', '/some/service'))
        self.assertEqual('http://localhost/some/service', url)

    def test_symmetry_host_router(self):
        balancer = StaticLocalhostBalancer()
        router = SymmetryHostRouter(balancer)

        url = router._get_url(ServiceRequest('foobar', '/some/service'))
        self.assertEqual('http://localhost/some/service', url)

    def test_symmetry_service_router(self):
        balancer = StaticLocalhostBalancer()
        router = SymmetryServiceRouter(balancer)

        url = router._get_url(ServiceRequest('foobar', '/some/service'))
        self.assertEqual('http://localhost/foobar/some/service', url)

    def test_request_basic(self):
        """
        Whitebox test to check whether requests is called correctly by the router
        """

        class MockResponse:
            method = 'get'
            status_code = 200
            args: dict
            kwargs: dict

        def mocked_request(*args, **kwargs):
            response = MockResponse()
            response.args = args
            response.kwargs = kwargs
            return response

        symmetry.gateway.requests.request = mocked_request
        router = StaticRouter('http://localhost')
        response = router.request(ServiceRequest('foobar', '/some/service'))

        self.assertEqual('get', response.args[0])
        self.assertEqual('http://localhost/some/service', response.args[1])


if __name__ == '__main__':
    unittest.main()
