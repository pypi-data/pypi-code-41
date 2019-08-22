# -*- coding: utf-8 -*-
# @Time     : 2019/5/16 16:49
# @Author   : Run
# @File     : __init__.py
# @Software : PyCharm

# from book.web_fiction import WebFictionSpider, check_calibre_installed
# from video.m3u8 import M3U8Spider, check_ffmpeg_installed
from RunSpiders.book.web_fiction import WebFictionSpider, check_calibre_installed
from RunSpiders.video.m3u8 import M3U8Spider, check_ffmpeg_installed