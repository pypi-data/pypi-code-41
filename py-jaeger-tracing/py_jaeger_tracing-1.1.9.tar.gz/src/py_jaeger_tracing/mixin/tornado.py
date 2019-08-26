import traceback

import tornado.web
from jaeger_client import Span
from opentracing import Format
from opentracing import tags

from py_jaeger_tracing.global_variables import TracingEnvironment


class TracerMixin:
    def __init__(self, *args, **kwargs):
        self._request_span: Span = None

    def initialize_tracer(self, request):
        if TracingEnvironment.tracer is not None:
            tracer = TracingEnvironment.tracer

            parent_span = tracer.extract(Format.HTTP_HEADERS, request.headers)

            self._request_span = tracer.start_span(
                operation_name=f'{request.method} {request.path}',
                child_of=parent_span
            )
            TracingEnvironment.spans.append(self._request_span)

            for k, v in {
                tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
                tags.HTTP_URL: request.path,
                tags.HTTP_METHOD: request.method,
                tags.PEER_HOST_IPV4: request.remote_ip,
                tags.COMPONENT: 'tornado',
            }.items():
                self._request_span.set_tag(k, v)

    def exception_tracer(self, status_code, **kwargs):
        exception, reason, tb = kwargs['exc_info']

        if TracingEnvironment.tracer is not None and self._request_span:
            self._request_span.set_tag(tags.HTTP_STATUS_CODE, status_code)
            self._request_span.set_tag(tags.ERROR, True)
            self._request_span.log_kv({
                'event': tags.ERROR,
                'error.object': exception,
                'error.traceback': traceback.format_tb(tb)
            })
            TracingEnvironment.spans.pop()


class BaseRequestHandler(tornado.web.RequestHandler, TracerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data_received(self, chunk):
        pass

    def initialize(self):
        self.initialize_tracer(self.request)

    def on_finish(self):
        if TracingEnvironment.tracer and len(TracingEnvironment.spans) > 0 and self._request_span is not None:
            TracingEnvironment.spans.pop()
            self._request_span.finish()

    def write_error(self, status_code, **kwargs):
        exception, reason, tb = kwargs['exc_info']
        self.exception_tracer(status_code, **kwargs)

        if isinstance(exception, ValueError):
            self.set_status(400)
        else:
            self.set_status(500)

        if self.settings.get('debug', False):
            self.write({
                'success': False,
                'response': {
                    'reason': exception.__name__,
                    'traceback': traceback.format_tb(tb)
                }
            })
        else:
            self.write({
                'success': False,
                'response': {
                    'reason': str(reason)
                }
            })

    def on_connection_close(self):
        if TracingEnvironment.tracer is not None and self._request_span is not None:
            self._request_span.set_tag(tags.ERROR, True)
            self._request_span.finish()
            TracingEnvironment.spans.pop()
