# -*- coding: utf-8 -*-
import re

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Compose


class NewsLoader(ItemLoader):
    content = Compose(Join(), lambda s: s.strip())
    media = Compose(Join(), lambda s:s.strip())


