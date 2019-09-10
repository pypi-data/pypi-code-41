import logging
from typing import Any, Callable

from microcosm.api import get_component_name
from microcosm.object_graph import ObjectGraph
from microcosm_logging.timing import elapsed_time


def training_initializer():
    """
    Register a microcosm component as a training initializer, so that its init
    method will automatically be called.  This function is designed to be used
    as a decorator on a factory.

    """
    def decorator(func: Callable[[ObjectGraph], Any]):
        def factory(graph):
            component = func(graph)
            graph.training_initializers.register(component)
            return component
        return factory
    return decorator


def _method_with_logging(original_method):
    def new_method(self, *args, **kwargs):
        bundle_name = get_component_name(self._graph, self)
        logging.info(
            f"Started method `{original_method.__name__}` of the `{bundle_name}`."
        )
        timing = {}
        with elapsed_time(timing):
            original_method(self, *args, **kwargs)
        logging.info(
            f"Completed method `{original_method.__name__}` of the `{bundle_name}` "
            f"after {timing['elapsed_time']/1000:.1f} seconds."
        )
    return new_method


def log_bundle_methods(cls):

    _init = cls.__init__

    def __init__(self, graph: ObjectGraph, **kwargs) -> None:
        _init(self, graph, **kwargs)
        self._graph = graph

    cls.__init__ = __init__
    cls.fit = _method_with_logging(cls.fit)
    cls.load = _method_with_logging(cls.load)
    cls.save = _method_with_logging(cls.save)

    return cls
