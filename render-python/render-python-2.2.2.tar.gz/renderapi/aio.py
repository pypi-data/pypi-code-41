#!/usr/bin/env python
"""
asynchronous helper functions for python 3.7+ (because I'm lazy)
"""
import asyncio
import aiohttp

try:
    import ujson as json
except ImportError:
    import json

from renderapi.render import format_preamble, renderaccess
from renderapi.tilespec import TileSpec
import renderapi

DEFAULT_CONCURRENCY = 2


async def get_json(session, request_url, params=None, **kwargs):
    """get_json wrapper for requests to handle errors

    Parameters
    ----------
    session : requests.session.Session
        requests session
    request_url : str
        url
    params : dict
        requests parameters
    stream: bool
        requests whether to stream
    kwargs: dict
        kwargs to shout into the dark
    Returns
    -------
    dict
        json response from server

    Raises
    ------
    RenderError
        if cannot get json successfully
    """
    r = await session.request('GET', request_url, params=params)
    # r.raise_for_status()
    # if r.status != 200:
    #     message = "request to {} returned error code {} with message {}"
    #     raise RenderError(message.format(r.url, r.status_code, r.text))
    j = await r.json(loads=json.loads)
    try:
        return j
    except Exception as e:
        raise RenderError(r.text)


@renderaccess
async def get_tile_specs_from_z(stack, z, host=None, port=None,
                          owner=None, project=None, session=None,
                          render=None, **kwargs):
    """Get all TileSpecs in a specific z values. Returns referenced transforms.

    :func:`renderapi.render.renderaccess` decorated function

    Parameters
    ----------
    stack : str
        render stack
    z : float
        render z
    render : renderapi.render.Render
        render connect object
    session : requests.sessions.Session
        sessions object to connect with

    Returns
    -------
    :obj:`list` of :class:`TileSpec`
        list of TileSpec objects from that stack at that z
    """
    request_url = format_preamble(
        host, port, owner, project, stack) + '/z/%f/tile-specs' % (z)
    tilespecs_json = await get_json(session, request_url)

    if len(tilespecs_json) == 0:
        return None
    else:
        return [TileSpec(json=tilespec_json)
                for tilespec_json in tilespecs_json]


async def run_function_async_over_arg(
        argidx, f, *args, reduction_func=None, concurrency=None, **kwargs):
    concurrency = DEFAULT_CONCURRENCY if concurrency is None else concurrency
    reduction_func = (lambda x: x if reduction_func is None  # noqa: E731
                      else reduction_func)

    if not isinstance(args[argidx], collections.Sequence) or isinstance(args[argidx], str):
        raise RenderError("cannot index over {} {}".format(
            type(args[argidx]), args[argidx]))

    def get_newargs(args, newa, aidx):
        return args[:aidx] + (newa,) + args[aidx+1:]

    async with asyncio.Semaphore(concurrency):
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            tasks = [f(*get_newargs(*args, newa, argidx), **kwargs)
                     for newa in args[argidx]]
            result = await asyncio.gather(*tasks)
    return reduction_func(result)


async def run_function_async_over_args(
        argidxs, f, *args, reduction_func=None, concurrency=None, **kwargs):
    concurrency = DEFAULT_CONCURRENCY if concurrency is None else concurrency
    reduction_func = (lambda x: x if reduction_func is None  # noqa: E731
                      else reduction_func)
    raise NotImplementedError("well, crap.")


async def run_get_tile_specs_from_zs(
        stack, zs, *args,  concurrency=None, **kwargs):
    concurrency = DEFAULT_CONCURRENCY if concurrency is None else concurrency
    async with asyncio.Semaphore(concurrency):
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            tasks = [get_tile_specs_from_z(
                stack, z, *args,
                **dict(kwargs, session=session)) for z in zs]
            result = await asyncio.gather(*tasks)
    return [i for l in result for i in l]


def get_tile_specs_from_zs(*args, **kwargs):
    # return asyncio.run(run_get_tile_specs_from_zs(*args, **kwargs))
