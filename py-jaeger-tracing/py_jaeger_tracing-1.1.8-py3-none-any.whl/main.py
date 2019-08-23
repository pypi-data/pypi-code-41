import atexit
import functools
import logging
import traceback

import requests
from jaeger_client import Config
from opentracing import tags

from py_jaeger_tracing.global_variables import MpTracingEnvironment
from py_jaeger_tracing.global_variables import TracingEnvironment
from py_jaeger_tracing.patches.patches import TracingPatcher
from py_jaeger_tracing.shutdown import on_shutdown
from py_jaeger_tracing.utils.event_loop import patch_event_loop

DEFAULT_SERVICE_NAME = 'UnknownService'

DEFAULT_TRACER_CONFIG = {
    'sampler': {
        'type': 'const',
        'param': 1,
    },
    'logging': False,
}


class TracingStarter:
    @classmethod
    def _check_server_exists(cls, logger):
        try:
            requests.get(f'http://{TracingEnvironment.host}:{TracingEnvironment.port}')
        except requests.exceptions.ConnectionError:
            logger.warning('Tracing server is not found')

    @classmethod
    def disable_tracing_on_debug(cls):
        """Disable tracing if debug mode is on."""
        import sys

        if 'pydevd' in sys.modules or 'pdb' in sys.modules:
            print('Tracer was disabled')
            TracingEnvironment.is_tracer_enabled = False

    @classmethod
    def initialize(cls, service_name, config=None, logger=None, patches=None):
        patch_event_loop()
        if not TracingEnvironment.is_tracer_enabled:
            return

        logger = logger or logging.getLogger(__name__)
        config = config or DEFAULT_TRACER_CONFIG
        patches = patches or []
        cls._check_server_exists(logger)

        if TracingEnvironment.tracer is not None and len(TracingEnvironment.spans) > 0:
            MpTracingEnvironment.parent_span = TracingEnvironment.spans[-1]

        TracingEnvironment.service_name = service_name
        TracingEnvironment.config = config
        TracingEnvironment.logger = logger
        TracingEnvironment.patches = patches

        Config._initialized = None
        TracingEnvironment.tracer = Config(
            config=config,
            service_name=service_name,
            validate=True
        ).initialize_tracer()
        TracingPatcher.apply_patches(patches)

        atexit.register(on_shutdown)

    @classmethod
    def initialize_subprocess(cls, f):
        @functools.wraps(f)
        def wrapper_tracer(*args, **kwargs):
            TracingStarter.initialize(
                TracingEnvironment.service_name or DEFAULT_SERVICE_NAME,
                TracingEnvironment.config or DEFAULT_TRACER_CONFIG,
                TracingEnvironment.logger,
                TracingEnvironment.patches
            )

            label = f'{f.__module__}.{f.__name__}'

            if len(TracingEnvironment.spans) > 0:
                span = TracingEnvironment.tracer.start_span(label,
                                                            child_of=TracingEnvironment.spans[-1])
            else:
                span = TracingEnvironment.tracer.start_span(label)

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
                TracingStarter.finish()

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if TracingEnvironment.tracer:
                return wrapper_tracer(*args, **kwargs)
            else:
                return f(*args, **kwargs)

        return wrapper

    @classmethod
    def finish(cls):
        on_shutdown()
