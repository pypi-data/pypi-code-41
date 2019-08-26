from jaeger_client.constants import TRACE_ID_HEADER
from opentracing import Format
from opentracing import Reference
from opentracing import ReferenceType

from py_jaeger_tracing.global_variables import TracingEnvironment


class TracingStringExtractor:
    def __init__(self, operation='child'):
        self._operation = operation

    def _extract(self, carrier):
        span_ctx = TracingEnvironment.tracer.extract(
            format=Format.TEXT_MAP,
            carrier={
                TRACE_ID_HEADER: carrier
            }
        )

        references = [Reference(ReferenceType.FOLLOWS_FROM, span_ctx)]
        if len(TracingEnvironment.spans) > 0:
            references += [Reference(ReferenceType.FOLLOWS_FROM, TracingEnvironment.spans[-1])]

        span = TracingEnvironment.tracer.start_span(
            operation_name=self._operation,
            references=references
        )

        TracingEnvironment.spans.append(span)
        span.finish()

    def extract(self, carrier):
        if TracingEnvironment.tracer:
            self._extract(carrier)
