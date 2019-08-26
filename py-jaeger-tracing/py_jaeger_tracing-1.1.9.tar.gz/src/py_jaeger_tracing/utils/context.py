import contextlib
import traceback

from opentracing import tags

from py_jaeger_tracing.global_variables import TracingEnvironment


@contextlib.contextmanager
def _tracing_context(name='', *, context_function=None):
    if context_function:
        operation_name = f'{context_function.__module__}.{context_function.__name__}: {name}'
    else:
        operation_name = name

    span = None
    try:
        if len(TracingEnvironment.spans) > 0:
            span = TracingEnvironment.tracer.start_span(operation_name, child_of=TracingEnvironment.spans[-1])
        else:
            span = TracingEnvironment.tracer.start_span(operation_name)

        TracingEnvironment.spans.append(span)
        yield
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


@contextlib.contextmanager
def tracing_context(name='', *, context_function=None):
    if TracingEnvironment.tracer:
        with _tracing_context(name, context_function=context_function):
            yield
    else:
        yield
