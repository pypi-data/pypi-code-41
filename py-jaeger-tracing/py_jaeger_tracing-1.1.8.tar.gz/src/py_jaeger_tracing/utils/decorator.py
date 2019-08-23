import functools
import traceback

from opentracing import tags

from py_jaeger_tracing.global_variables import TracingEnvironment


def _tracing(f, operation_name, *args, **kwargs):
    f_signature = f'{f.__module__}.{f.__name__}({",".join(["?"] * len(args) + list(kwargs.keys()))})'

    operation_name = f'{f_signature}; {operation_name}'
    if len(TracingEnvironment.spans) > 0:
        span = TracingEnvironment.tracer.start_span(operation_name, child_of=TracingEnvironment.spans[-1])
    else:
        span = TracingEnvironment.tracer.start_span(operation_name)

    TracingEnvironment.spans.append(span)

    try:
        return f(*args, **kwargs)
    except Exception as e:
        span.set_tag(tags.ERROR, True)
        span.log_kv({
            'event': tags.ERROR,
            'error.object': e,
            'error.traceback': traceback.format_exc()
        })
        raise e
    finally:
        h_span = None
        while h_span != span:
            h_span = TracingEnvironment.spans.pop()
        span.finish()


class TracingDecorator:
    def __init__(self, operation_name=None):
        self._operation_name = operation_name or ''

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if TracingEnvironment.tracer:
                return _tracing(f, self._operation_name, *args, **kwargs)
            else:
                return f(*args, **kwargs)

        return wrapper
