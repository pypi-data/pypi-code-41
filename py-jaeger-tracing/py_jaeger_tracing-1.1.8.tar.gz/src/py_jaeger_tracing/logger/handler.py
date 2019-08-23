from logging import StreamHandler

from py_jaeger_tracing.global_variables import TracingEnvironment


class TracerHandler(StreamHandler):
    def emit(self, record):
        if TracingEnvironment.tracer and len(TracingEnvironment.spans) > 0:
            span = TracingEnvironment.spans[-1]
            span.log_kv({
                'event': f'logger.{record.levelname}',
                'text': self.format(record)
            })
