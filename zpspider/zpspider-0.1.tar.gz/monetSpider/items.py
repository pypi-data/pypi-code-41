# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class NewsItem(Item):
    collection = table = 'news'
    title = Field()
    content = Field()
    pub_time = Field()
    media = Field()
    URL = Field()
    TIMESTAMP = Field()
    missing_data = Field()
    download_fileurl = Field()
    download_imgurl = Field()

