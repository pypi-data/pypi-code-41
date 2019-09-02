"""
    Worker listens to a queue in redis and performs
    work as an Rpc Manager
"""
import asyncio
import logging
from bluemax.settings import get_settings
from bluemax.rpc import ContextRpc
from bluemax.utils import json_utils
from bluemax.performer import Performer
from .redis_pubsub import redis_publish, redis_cmd
from . import rd_session


LOGGER = logging.getLogger(__name__)

"""
    Main worker file. It subscribes to the
    redis queue and broadcasts activity
"""


class Worker(ContextRpc, Performer):
    """ A context rpc fed by redis """

    def __init__(self, *args, **kwargs):
        """ setup variables before run """
        ContextRpc.__init__(self, *args, **kwargs)
        Performer.__init__(self)
        # set off subscription
        self.handle_work()

    async def shutdown(self, wait=True):
        await ContextRpc.shutdown(self)

    @redis_cmd(key=get_settings("redis_work_q", "perform"), cmd="blpop", cmd_args=[0])
    async def handle_work(self, val=None):
        """ unpack the mesage and call perform """
        LOGGER.info("got work %s", val)
        if val is None:
            return
        content = json_utils.loads(val[1].decode("utf-8"))
        try:
            LOGGER.info("%r", content["qname"])
            result = await self.perform(
                content["user"], content["qname"], *content["args"], **content["kwargs"]
            )
            content["result"] = result
        except asyncio.CancelledError:
            LOGGER.info("cancelled")
            return
        except Exception as ex:  # pylint: disable=W0703
            content["error"] = {"code": -32000, "message": str(ex)}
        if content.get("reply"):
            pool = await rd_session.pool()
            await pool.execute("publish", content["reply"], json_utils.dumps(content))
            LOGGER.info("published reply %s", content)

    @redis_publish(key=get_settings("redis_broadcast_q", "broadcast"))
    def _broadcast_(self, signal, message, client_filter=None):
        """ will broadcast to redis """
        msg = json_utils.dumps((signal, message, client_filter))
        LOGGER.debug("broadcasted to redis: %s", msg)
        return msg


def main():
    """ Creates Worker and starts tornado """
    assert get_settings("redis_url")
    assert get_settings("procedures")
    worker = Worker.rpc_for(
        get_settings("procedures"),
        max_workers=get_settings("max_workers"),
        max_threads=get_settings("max_threads"),
    )
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(worker.shutdown())
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
