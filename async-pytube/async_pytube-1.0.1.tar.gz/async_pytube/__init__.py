# -*- coding: utf-8 -*-
#
"""
Async version of pytube
"""
__title__ = 'async_pytube'
__version__ = '1.0 (9.5.1)'
__author__ = 'Andrebcd4'


from async_pytube.logging import create_logger
from async_pytube.query import CaptionQuery
from async_pytube.query import StreamQuery
from async_pytube.streams import Stream
from async_pytube.captions import Caption
from async_pytube.playlist import Playlist
from async_pytube.__main__ import YouTube

logger = create_logger()
logger.info('%s v%s', __title__, __version__)
