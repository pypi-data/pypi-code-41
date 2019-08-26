from jaeger_client.constants import TRACE_ID_HEADER
from opentracing import Format

from py_jaeger_tracing.global_variables import TracingEnvironment


class TracingStringInjector:
    def __init__(self, operation='child'):
        self._operation = operation

    def _inject(self):
        carrier = {}
        if len(TracingEnvironment.spans) > 0:
            span = TracingEnvironment.tracer.start_span(self._operation, child_of=TracingEnvironment.spans[-1])
        else:
            span = TracingEnvironment.tracer.start_span(self._operation)

        TracingEnvironment.tracer.inject(
            span_context=span.context,
            format=Format.TEXT_MAP,
            carrier=carrier
        )
        span.finish()

        return carrier[TRACE_ID_HEADER]

    def inject(self):
        if TracingEnvironment.tracer:
            return self._inject()
        else:
            return ''
