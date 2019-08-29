# -*- coding: utf-8 -*-
import socket
import urllib
import urlparse

# values = {
#     'X-Requested-With' : 'XMLHttpRequest',
#     'Referer' : 'https://www.baidu.com/s?wd=宽连十方'
# }
# data = urllib.urlencode(values)
#
# print data


# dict=urlparse.parse_qs("X-Requested-With=XMLHttpRequest&Referer=https%3A%2F%2Fwww.baidu.com%2Fs%3Fwd%3D%E5%AE%BD%E8%BF%9E%E5%8D%81%E6%96%B9", False)
# dict=urlparse.parse_qs("User-Agent=Mozilla%2F5.0+%28Windows+NT+6.1%3B+WOW64%3B+rv%3A32.0%29+Gecko%2F20100101+Firefox%2F32.0", False)
#
# print dict

node = socket.gethostname()
print node
