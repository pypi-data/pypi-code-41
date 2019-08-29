# -*- coding: utf-8 -*-
import zlib

str_l = "啊啊啊啊啊"

print len(str_l)

str_s = zlib.compress(str_l)

print len(str_s)

print zlib.decompress(str_s)


