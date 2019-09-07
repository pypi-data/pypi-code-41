"""
This is a proxy that forwards service requests using the symmetry router. It can be used as a gateway for clients to
hide symmetry.
"""
import falcon
import redis

from symmetry.gateway import Router, ServiceRequest, SymmetryServiceRouter, WeightedRoundRobinBalancer
from symmetry.routing import RedisRoutingTable


class RootResource:
    def on_get(self, req, resp):
        pass


class ServiceProxy:
    router: Router

    def __init__(self, router) -> None:
        super().__init__()
        self.router = router

    def __call__(self, req: falcon.Request, resp):
        segments = req.path.split('/')[1:]

        service = segments[0]
        path = req.path[len(service) + 1:].lstrip('/')

        request = ServiceRequest(service, path, req.method, params=req.params, data=req.stream)
        result = self.router.request(request)

        resp.status = str(result.status_code) + ' ' + result.reason
        resp.content_type = result.headers.get('content-type', 'plain/text')
        resp.body = result.text


api = falcon.API()
api.add_route('/', RootResource())

# FIXME: probably not the best place to create an application context
sink = ServiceProxy(
    SymmetryServiceRouter(WeightedRoundRobinBalancer(RedisRoutingTable(redis.Redis(decode_responses=True)))))
api.add_sink(sink, '/')
