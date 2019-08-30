"""
health controller.
"""
from marshmallow import Schema, fields
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import dump_response_data
from microcosm_flask.conventions.registry import response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class PingSchema(Schema):
    status = fields.String()
    name = fields.String()
    ok = fields.Bool()


class SagemakerHealthConvention(Convention):
    def __init__(self, graph):
        super(SagemakerHealthConvention, self).__init__(graph)

    def configure_query(self, ns, definition):
        @self.add_route("/api/health", Operation.Query, ns)
        # Stephens:
        #
        # We need /api/health for AI projects to run on ECS
        # This is a temp solution untill we complete the migration
        #
        # Currently health check exist on /health but not /api/health
        # because we removed /api from route prefix
        #
        # see commands/config.py `build_route_path`
        #
        @response(PingSchema())
        def health_check_query():
            response_data = dict(
                name=self.graph.metadata.name,
                ok=True,
            )
            return dump_response_data(PingSchema(), response_data, 200)


def configure_health(graph):
    ns = Namespace(
        subject="/api/health",
        version=None
    )
    convention = SagemakerHealthConvention(graph)
    convention.configure(ns, query=tuple())
