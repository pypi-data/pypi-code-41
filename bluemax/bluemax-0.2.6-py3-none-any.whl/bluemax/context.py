"""
    This context is available either remote or local
    It is maintained by the manager.
"""
__all__ = ["current_user", "broadcast", "broadcast_on_success"]

import logging
import contextvars
import contextlib

LOGGER = logging.getLogger(__name__)

_USER_ = contextvars.ContextVar("_USER_")
_BROADCAST_ON_SUCCESS_ = contextvars.ContextVar("_BROADCAST_ON_SUCCESS_")

# one to rule them all
_MANAGER_ = None


def current_user():
    """ returns the user(actor) for this procedure call """
    return _USER_.get(None)


def broadcast(signal, message, filter_clients=None):
    """ This allows for the broadcast to client inline """
    _MANAGER_.broadcast(signal, message, filter_clients)


def broadcast_on_success(signal, message, filter_clients=None):
    """ This allows for the boradcast to client after func return """
    _BROADCAST_ON_SUCCESS_.get([]).append((signal, message, filter_clients))


def perform(qname, *args, **kwargs):
    """ Returns an awaitable of the result of calling qname """
    LOGGER.debug("calling manager %s with %s", _MANAGER_, qname)
    return _MANAGER_.perform(current_user(), qname, *args, **kwargs)


@contextlib.contextmanager
def user_call(user=None):
    """ With this we setup contextvars and reset """
    utoken = _USER_.set(user)
    btoken = _BROADCAST_ON_SUCCESS_.set([])
    try:
        yield
    finally:
        _USER_.reset(utoken)
        _BROADCAST_ON_SUCCESS_.reset(btoken)


def context_call(func, user=None, args=None, kwargs=None):
    """ Setup context and call """
    with user_call(user):
        result = func(*args, **kwargs)
        broadcasts = _BROADCAST_ON_SUCCESS_.get()
        if broadcasts:
            _MANAGER_.broadcast_later(broadcasts)
        return result


async def acontext_call(func, user=None, args=None, kwargs=None):
    """ Setup context and call async """
    with user_call(user):
        result = await func(*args, **kwargs)
        broadcasts = _BROADCAST_ON_SUCCESS_.get()
        if broadcasts:
            _MANAGER_.broadcast_later(broadcasts)
        return result
