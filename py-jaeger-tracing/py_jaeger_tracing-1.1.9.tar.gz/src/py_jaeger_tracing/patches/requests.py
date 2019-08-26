import copy

from jaeger_client import Span
from opentracing import Format
from opentracing import tags


def patch_requests():
    import requests

    from py_jaeger_tracing.global_variables import TracingEnvironment
    from py_jaeger_tracing.utils.context import tracing_context

    real_impl = requests.request

    def fake_impl(method, url, **kwargs):
        kwargs = copy.deepcopy(kwargs)

        with tracing_context('request'):
            if len(TracingEnvironment.spans) > 0:
                span: Span = TracingEnvironment.spans[-1]
                span.set_tag(tags.HTTP_METHOD, method.upper())
                span.set_tag(tags.HTTP_URL, url)
                span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)

                kwargs['headers'] = kwargs.get('headers', {})
                TracingEnvironment.tracer.inject(span, Format.HTTP_HEADERS, kwargs['headers'])

            return real_impl(method, url, **kwargs)

    requests.api.request = fake_impl
