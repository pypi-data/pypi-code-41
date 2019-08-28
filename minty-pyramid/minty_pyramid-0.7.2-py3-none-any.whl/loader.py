import logging
from uuid import uuid4

from minty import Base
from minty.cqrs import CQRS
from minty.infrastructure import InfrastructureFactory
from minty.logging.mdc import get_mdc, mdc
from pyramid.config import Configurator
from pyramid.events import NewResponse, subscriber

from .exception_handlers import (
    exception_cqrs_catch_all,
    exception_cqrs_conflict,
    exception_cqrs_forbidden,
    exception_cqrs_not_found,
    exception_cqrs_validation,
)
from .session_manager import SessionRetriever, session_manager_factory


@subscriber(NewResponse)
def new_response_callback(event):
    """Set default headers when a new response is created"""
    if not event.response.headers.get("cache-control"):
        event.response.headers.update({"cache-control": "no-store"})

    event.response.headers.update(
        {"request-id": str(event.request.request_id)}
    )


class Engine(Base):
    """Pyramid configurator."""

    __slots__ = [
        "config",
        "domains",
        "command_wrapper_middleware",
        "query_middleware",
    ]

    def __init__(
        self,
        domains: list,
        command_wrapper_middleware: list = None,
        query_middleware: list = None,
    ):
        if command_wrapper_middleware is None:
            command_wrapper_middleware = []
        if query_middleware is None:
            query_middleware = []
        self.command_wrapper_middleware = command_wrapper_middleware
        self.query_middleware = query_middleware
        self.domains = domains
        self.config = None

    def setup(self, global_config: dict, **settings) -> object:
        """Set up the application by loading the injecting the CQRS layer.

        :param global_config: Global configuration
        :type global_config: dict
        :return: Returns the Configurator from Pyramid
        :rtype: object
        """
        infra_factory = InfrastructureFactory(
            settings["minty_service.infrastructure.config_file"]
        )
        config = Configurator(settings=settings)

        cqrs = CQRS(
            domains=self.domains,
            infrastructure_factory=infra_factory,
            command_wrapper_middleware=self.command_wrapper_middleware,
            query_middleware=self.query_middleware,
        )

        config.add_request_method(
            lambda r: uuid4(), name="request_id", property=True, reify=True
        )

        config.add_request_method(
            lambda r: infra_factory,
            name="infrastructure_factory",
            property=True,
            reify=True,
        )

        config.include(_build_cqrs_setup(cqrs))
        if settings.get("session_manager", False):
            session_manager = session_manager_factory(
                infra_factory=infra_factory
            )
            config.include(
                _build_http_session_manager(
                    session_manager,
                    cookie_name=settings.get(
                        "session_cookie_name", "minty_session"
                    ),
                )
            )

        config.add_view(view=exception_cqrs_not_found, name="not_found")
        config.add_view(view=exception_cqrs_forbidden, name="forbidden")
        config.add_view(view=exception_cqrs_conflict, name="conflict")
        config.add_view(view=exception_cqrs_validation, name="validation")
        config.add_view(view=exception_cqrs_catch_all, name="catch_all")

        config.add_tween("minty_pyramid.loader.RequestTimer")
        config.add_tween("minty_pyramid.loader.RequestDataLogger")

        config.scan()
        self.config = config
        return config

    def main(self) -> object:
        """Run the application by calling the wsgi_app function of Pyramid.

        :raises ValueError: When setup is forgotten
        :return: wsgi app
        :rtype: object
        """
        if self.config is None:
            raise ValueError("Make sure you run setup before 'main'")

        self.logger.info("Creating WSGI application")

        return self.config.make_wsgi_app()


def _build_cqrs_setup(cqrs):
    """Create a callable for setting up the "CQRS" methods request objects.

    :param cqrs: A configured CQRS object
    :type cqrs: CQRS
    :return: A function, callable by Pyramid, to register the CQRS
        method(s)
    :rtype: callable
    """

    def setup_cqrs_request(config):
        """Add the CQRS accessors to the Pyramid request objects.

        :param config: Pyramid configurator instance
        :type config: Configurator
        :return: Nothing
        :rtype: None
        """

        def get_query_instance(request, domain: str, user_uuid: str):
            return cqrs.get_query_instance(
                correlation_id=request.request_id,
                domain=domain,
                context=request.host,
                user_uuid=user_uuid,
            )

        config.add_request_method(get_query_instance, "get_query_instance")

        def get_command_instance(request, domain: str, user_uuid: str):
            return cqrs.get_command_instance(
                correlation_id=request.request_id,
                domain=domain,
                context=request.host,
                user_uuid=user_uuid,
            )

        config.add_request_method(get_command_instance, "get_command_instance")

    return setup_cqrs_request


def _build_http_session_manager(
    session_manager: SessionRetriever, cookie_name: str = "minty_cookie"
):
    """Create a callable to set up the `retrieve_session` method on request objects.

    :param session_manager: A configured SessionRetriever object
    :type session_manager: SessionRetriever
    :param cookie_name: Name of the cookie the session-id is stored in
    :type cookie_name: str
    :return: A function, callable by Pyramid, to register the session_manager
        method(s)
    :rtype: callable
    """

    def setup_session_request(config):
        """Add the SessionRetriver accessors to the Pyramid request objects.

        :param config: Pyramid configurator instance
        :type config: Configurator
        :return: Nothing
        :rtype: None
        """

        def session_id(request):
            try:
                return request.cookies[cookie_name]
            except KeyError:
                return "<session cookie not found>"

        config.add_request_method(
            session_id, "session_id", property=True, reify=True
        )

        def retrieve_session(request):
            session = session_manager.retrieve(request.cookies[cookie_name])
            return session

        config.add_request_method(retrieve_session, "retrieve_session")

    return setup_session_request


class RequestTimer(Base):
    """Middleware / tween to log request time and count to statsd."""

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        """Log time and count to statsd before and after execution of handler.

        :param request: request
        :type request: class
        :return: response
        :rtype: class
        """
        timer = self.statsd.get_timer()
        timer.start()

        response = self.handler(request)

        try:
            req_name = request.matched_route.name
        except AttributeError:
            req_name = "unknown"

        timer.stop(f"{req_name}.time")

        self.statsd.get_counter().increment(
            f"{req_name}.{response.status_int}.count"
        )

        return response


def get_logging_info(request):
    logging_info = {}

    logging_info["hostname"] = request.host
    logging_info["request_id"] = request.request_id

    try:
        logging_info["session_id"] = request.session_id
    except AttributeError:
        logging_info["session_id"] = "<sessions not configured>"

    return logging_info


class RequestDataLogger(Base):
    """Tween to add request-specific information to log entries"""

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        logging_info = get_logging_info(request)
        with mdc(**logging_info):
            response = self.handler(request)

        return response


# Add a "req" key, containing the MDC to logging output in minty-pyramid
# applications.
old_factory = logging.getLogRecordFactory()


def log_record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.req = get_mdc()
    return record


logging.setLogRecordFactory(log_record_factory)
