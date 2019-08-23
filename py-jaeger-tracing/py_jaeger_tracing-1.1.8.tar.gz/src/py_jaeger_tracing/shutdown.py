import time

from py_jaeger_tracing.global_variables import MpTracingEnvironment
from py_jaeger_tracing.global_variables import TracingEnvironment

FINISH_TIMEOUT = 2  # require for clean buffer


def on_shutdown():
    if MpTracingEnvironment.parent_span is None:
        for span in TracingEnvironment.spans:
            span.finish()
    else:
        for span in TracingEnvironment.spans:
            if span != MpTracingEnvironment.parent_span:
                span.finish()
            else:
                break

    time.sleep(FINISH_TIMEOUT)
    TracingEnvironment.tracer.close()
