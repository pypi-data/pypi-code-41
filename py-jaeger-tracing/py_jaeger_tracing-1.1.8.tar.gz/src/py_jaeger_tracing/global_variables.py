import os
import typing

from jaeger_client import Span
from jaeger_client import Tracer


class MpTracingEnvironment:
    parent_span = None


class TracingEnvironment:
    host = os.environ.get('JAEGER_AGENT_HOST', 'localhost')
    port = int(os.environ.get('JAEGER_AGENT_PORT', '16686'))
    service_name = None
    config = None
    logger = None
    patches = None
    tracer: Tracer = None
    spans: typing.List[Span] = []

    is_tracer_enabled = True
