# -*- coding: utf-8 -*-
"""Implements a simple wrapper around urlopen."""
from async_pytube.compat import urlopen
import aiohttp

async def get(
    url=None, headers=False,
    streaming=False, chunk_size=8 * 1024,
):
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :param bool headers:
        Only return the http headers.
    :param bool streaming:
        Returns the response body in chunks via a generator.
    :param int chunk_size:
        The size in bytes of each chunk.
    """

    #response = await _get(url)
    if streaming:
        return async_stream_response(url, chunk_size)
    elif headers:
        # https://github.com/nficano/pytube/issues/160
        info = await get_headers(url)
        return {k.lower(): v for k, v in info}
    response = await async_response(url)
    return response

def stream_response(response, chunk_size=8 * 1024):
    """Read the response in chunks."""
    while True:
        buf = response.read(chunk_size)
        if not buf:
            break
        yield buf


async def async_stream_response(url, chunk_size=8 * 1024):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            while True:
                buf = await response.content.read(chunk_size)
                if not buf:
                    break
                yield buf


async def async_response(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text(encoding='utf-8')


async def get_headers(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.headers.items()
