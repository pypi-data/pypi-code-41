import logging
import os
from os import path

import falcon
import redis

from symmetry.api import NodeManager, NodeInfo, ClusterGateway, RoutingTable, RoutingRecord, ServiceMetadataRepository, \
    ServiceManager, BalancingPolicyService
from symmetry.clusterd import DefaultBalancingPolicyService
from symmetry.common.cluster import RedisNodeManager, NodeOperationNotifierDecorator, DefaultClusterGateway
from symmetry.common.typing import json_schema, deep_to_dict
from symmetry.nrg import DefaultServiceManager, RedisServiceMetadataRepository
from symmetry.nrg.web import ServicesResource, ServiceResource, ServiceDeploymentResource
from symmetry.routing import RedisRoutingTable
from symmetry.webapp import ApiResource

logger = logging.getLogger(__name__)


class AppContext:
    rds: redis.Redis
    node_manager: NodeManager
    service_metadata_repository: ServiceMetadataRepository
    service_manager: ServiceManager
    cluster: ClusterGateway
    rtbl: RoutingTable
    balancing_policy_service: BalancingPolicyService


class DefaultRedisContext(AppContext):

    def __init__(self, rds) -> None:
        super().__init__()
        self.rds = rds

        self.node_manager = NodeOperationNotifierDecorator(RedisNodeManager(self.rds))
        self.service_metadata_repository = RedisServiceMetadataRepository(self.rds)
        self.service_manager = DefaultServiceManager(self.service_metadata_repository, self.node_manager)
        self.cluster = DefaultClusterGateway(self.node_manager)
        self.rtbl = RedisRoutingTable(self.rds)
        self.balancing_policy_service = DefaultBalancingPolicyService()


def setup(api, context: AppContext):
    rds = context.rds
    node_manager = context.node_manager
    cluster = context.cluster

    api.add_route('/api', ApiResource(api))

    nodes = NodesResource(node_manager)
    api.add_route('/api/nodes', nodes)
    api.add_route('/api/nodes/{node}', nodes, suffix='single')

    actions = NodeActionResource(cluster)
    api.add_route('/api/nodes/{node}/state', actions, suffix='state')
    api.add_route('/api/nodes/{node}/boot', actions, suffix='boot')
    api.add_route('/api/nodes/{node}/shutdown', actions, suffix='shutdown')
    api.add_route('/api/nodes/{node}/suspend', actions, suffix='suspend')

    api.add_route('/api/cluster/state', ClusterStateResource(cluster))
    api.add_route('/api/cluster/metrics', ClusterMetricsResource(cluster, rds))

    api.add_route('/api/routes', RoutesResource(context.rtbl))
    api.add_route('/api/routes/{service}', RoutesServiceResource(context.rtbl))

    api.add_route('/api/services', ServicesResource(context.service_metadata_repository))
    api.add_route('/api/services/{service_id}', ServiceResource(context.service_metadata_repository))
    api.add_route('/api/services/{service_id}/deployment', ServiceDeploymentResource(context.service_manager))

    resource = BalancingPoliciesResource(context.balancing_policy_service)
    api.add_route('/api/policies/balancing', resource)
    api.add_route('/api/policies/balancing/active', resource, suffix='active')
    api.add_route('/api/policies/balancing/{policy_name}', resource, suffix='single')

    working_dir = os.getcwd()
    api.add_route('/ui/dashboard', HtmlResource(path.join(working_dir, 'symmetry/webapp/web/dashboard.html')))
    api.add_route('/ui/details', HtmlResource(path.join(working_dir, 'symmetry/webapp/web/details.html')))
    api.add_route('/ui/services', HtmlResource(path.join(working_dir, 'symmetry/webapp/web/services.html')))
    api.add_static_route('/ui/static', path.join(working_dir, 'symmetry/webapp/web/static/'))


class NodesResource:
    def __init__(self, node_manager: NodeManager) -> None:
        super().__init__()
        self.node_manager = node_manager

    def on_get(self, req, resp):
        nodes = self.node_manager.get_nodes()
        states = self.node_manager.get_node_states()

        nodes = [node._asdict() for node in nodes]
        for node in nodes:
            node['state'] = states[node['node_id']]

        resp.media = nodes

    def on_post(self, req, resp):
        if not req.content_length:
            raise falcon.HTTPBadRequest()

        doc = req.media
        try:
            node_info = NodeInfo(**doc)
        except Exception as e:
            logger.debug('could not deserialize NodeInfo from document %s: %s', doc, e)
            raise falcon.HTTPBadRequest()

        created = self.node_manager.save_node(node_info)
        logger.info('Saved node info %s', node_info)
        resp.media = bool(created)

    def on_get_single(self, req, resp, node):
        node_id = node

        for node in self.node_manager.get_nodes():
            if node.node_id == node_id:
                resp.media = node._asdict()
                return

        raise falcon.HTTPNotFound()

    def on_delete_single(self, req, resp, node):
        node_id = node
        if not self.node_manager.has_node(node_id):
            raise falcon.HTTPNotFound()

        self.node_manager.remove_node(node_id)


class ClusterAwareResource:
    def __init__(self, cluster: ClusterGateway) -> None:
        super().__init__()
        self.cluster = cluster

    def require_node(self, node_id):
        node_info = self.cluster.node_manager.get_node(node_id)

        if not node_info:
            raise falcon.HTTPNotFound()

        return node_info


class NodeActionResource(ClusterAwareResource):

    def on_get_state(self, req, resp, node):
        node_info = self.require_node(node)
        resp.media = self.cluster.is_up(node_info)

    def on_post_boot(self, req, resp, node):
        self.require_node(node)
        try:
            self.cluster.boot([node])
        except Exception as e:
            logger.exception('error booting node %s', node)
            raise falcon.HTTPInternalServerError(description=str(e))

    def on_post_shutdown(self, req, resp, node):
        self.require_node(node)
        try:
            self.cluster.shutdown([node])
        except Exception as e:
            logger.exception('error shutting down node %s', node)
            raise falcon.HTTPInternalServerError(description=str(e))

    def on_post_suspend(self, req, resp, node):
        self.require_node(node)
        try:
            self.cluster.suspend([node])
        except Exception as e:
            logger.exception('error suspending down node %s', node)
            raise falcon.HTTPInternalServerError(description=str(e))


class ClusterStateResource(ClusterAwareResource):
    def on_get(self, req, resp):
        resp.media = self.cluster.probe_node_states()


class ClusterMetricsResource(ClusterAwareResource):

    def __init__(self, cluster: ClusterGateway, rds) -> None:
        super().__init__(cluster)
        self.rds = rds

    def on_get(self, req, resp):
        rds = self.rds
        metrics = ['freq', 'cpu', 'watt']

        # prepare result dict
        result = {n.node_id: {m: list() for m in metrics} for n in self.cluster.nodes}

        for node in self.cluster.nodes:
            for metric in metrics:
                key = 'metrics:%s:%s' % (node.node_id, metric)
                r = rds.zrange(key, 0, -1)
                for v in r[-60:]:
                    ts, val = v.split(' ')
                    result[node.node_id][metric].append({'timestamp': float(ts), 'value': val})

        resp.media = result


class HtmlResource:

    def __init__(self, fpath) -> None:
        super().__init__()
        self.fpath = fpath

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        with open(self.fpath, 'r') as f:
            resp.body = f.read()


class RoutesResource:
    rtbl: RoutingTable

    def __init__(self, rtbl) -> None:
        super().__init__()
        self.rtbl = rtbl

    def on_get(self, req, resp):
        routes = [route._asdict() for route in self.rtbl.get_routes()]
        resp.media = routes

    def on_post(self, req, resp):
        doc = req.media
        record = RoutingRecord(**doc)
        self.rtbl.set_routing(record)


class RoutesServiceResource:
    rtbl: RoutingTable

    def __init__(self, rtbl) -> None:
        super().__init__()
        self.rtbl = rtbl

    def on_get(self, req, resp, service):
        try:
            record = self.rtbl.get_routing(service)
        except ValueError:
            record = None

        if not record:
            raise falcon.HTTPNotFound()

        resp.media = record._asdict()

    def on_delete(self, req, resp, service):
        self.rtbl.remove_service(service)


class BalancingPoliciesResource:
    policy_service: BalancingPolicyService

    def __init__(self, policy_service) -> None:
        super().__init__()
        self.policy_service = policy_service

    def on_get(self, req, resp):
        policies = self.policy_service.get_available_policies()

        result = [{'policy': name, 'schema': json_schema(cls)} for name, cls in policies.items()]

        resp.media = result

    def on_get_single(self, req, resp, policy_name):
        policy = self.policy_service.get_policy(policy_name)

        if not policy:
            raise falcon.HTTPNotFound()

        cls = policy
        resp.media = {'policy': policy_name, 'schema': json_schema(cls)}

    def on_get_active(self, req, resp):
        policy = self.policy_service.get_active_policy()
        if not policy:
            resp.media = {}
            return

        resp.media = {'policy': policy.name, 'parameters': deep_to_dict(policy)}

    def on_post_active(self, req, resp):
        # self.policy_service.set_active_policy(policy)
        raise NotImplementedError  # TODO: implement set active method


class CORSComponent(object):
    """
    CORS preprocessor from the Falcon documentation.
    """

    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Access-Control-Allow-Origin', '*')

        if (req_succeeded
                and req.method == 'OPTIONS'
                and req.get_header('Access-Control-Request-Method')
        ):
            # NOTE(kgriffs): This is a CORS preflight request. Patch the
            #   response accordingly.

            allow = resp.get_header('Allow')
            resp.delete_header('Allow')

            allow_headers = req.get_header(
                'Access-Control-Request-Headers',
                default='*'
            )

            resp.set_headers((
                ('Access-Control-Allow-Methods', allow),
                ('Access-Control-Allow-Headers', allow_headers),
                ('Access-Control-Max-Age', '86400'),  # 24 hours
            ))
