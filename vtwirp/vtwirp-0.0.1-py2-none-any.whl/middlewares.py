import time
import datetime

from verloopcontext.header import VERLOOP_CLIENT_ID_HEADER

from . import exceptions
from . import errors
from . import ctxkeys


def logger(ctx, request, handler):
    start = time.time()
    headers = ctx.get_headers()
    kwargs = {
            "start_time": datetime.datetime.now().isoformat(),
            "service": ctx.get(ctxkeys.SERVICE_NAME),
            "method":  ctx.get(ctxkeys.METHOD_NAME),
            "client_id": ctx.client_id,
            "entity_id": headers.entity_id,
            "caller_identity": headers.caller_identity,
        }
    ctx.set_logger(ctx.get_logger().bind(**kwargs))
    try:
        return handler(ctx, request)
    finally:
        resp_data = {
            "status_code": ctx.get(ctxkeys.RESPONSE_STATUS),
            "time_taken":int((time.time() - start) * 100000) / 100,
        }
        ctx.get_logger().info("twirp request processed", **resp_data)


def client_id_from_headers(ctx, request, handler):
    hdrs = ctx.get(ctxkeys.RAW_HEADERS)
    ctx.get_headers().update(hdrs)
    # will throw error
    try:
        ctx.client_id
    except KeyError:
        raise exceptions.RequiredArgument(argument=VERLOOP_CLIENT_ID_HEADER)
    return handler(ctx, request)