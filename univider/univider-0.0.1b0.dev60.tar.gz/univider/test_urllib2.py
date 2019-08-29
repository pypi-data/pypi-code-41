# -*- coding: utf-8 -*-
import urllib2

req = urllib2.Request(url="https://detail.tmall.com/item.htm?id=540638557308")

response = urllib2.urlopen(req)

html = response.read()

print html

