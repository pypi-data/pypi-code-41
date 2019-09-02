"""
    Proxy to procedures

    ...because it walks like a duck....

    should you wish to run locally::

        async with Moo('<package name>') as cow:
            result = await cow.add(2, 2)
            assert result == 4

"""

import logging
from bluemax import bring_up, get_settings
from bluemax.utils import qname_to_class

LOGGER = logging.getLogger(__name__)


class Moo:  # pylint: disable=R0903
    """ we want a proxy """

    def __init__(self, procedures, manager="bluemax.rpc:PoolRpc"):
        bring_up(procedures)
        rpc = qname_to_class(manager)
        self._rpc_ = rpc.rpc_for(get_settings("procedures"))

    def _stop_(self):
        """ call this to shutdown the rpc """
        return self._rpc_.shutdown()

    async def __aenter__(self):
        """ act as an async context manager """
        return self

    async def __aexit__(self, type_, value, traceback):
        """ act as an async context manager """
        await self._stop_()

    def __getattribute__(self, name):
        """ public attributes are proxies to procedures """
        LOGGER.debug("attribute %s", name)
        if name[0] == "_":
            return super().__getattribute__(name)
        if name in self._rpc_.procedures:

            def _wrapped_(*args, **kwargs):
                LOGGER.debug("calling %s(*%s, ***%s)", name, args, kwargs)
                return self._rpc_.perform(name, *args, **kwargs)

            return _wrapped_
        raise AttributeError(f"no such procedure: {name}")
