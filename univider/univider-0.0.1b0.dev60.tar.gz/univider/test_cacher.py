# -*- coding: utf-8 -*-
from univider.cacher import Cacher

cacher = Cacher()

cacher.set('aaaaaaaaa','你好')

print cacher.get('aaaaaaaaa')

