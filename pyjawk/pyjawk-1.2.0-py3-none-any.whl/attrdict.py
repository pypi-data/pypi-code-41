#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger
# This code is released under the license described in the LICENSE file

from collections import OrderedDict

class AttrDict(OrderedDict): 
    '''Simple dictionary subclass that allows known keys to be fetched in attribute style'''
    def __getattr__(self, attr): 
        try: 
            return self[attr] 
        except KeyError: 
            return super.__getattr__(attr) 

    def __setattr__(self, attr, value): 
        self[attr] = value     

    def __str__(self):
        return '{{{}}}'.format(', '.join('{!r}: {!r}'.format(key, value) for key, value in self.items()))

    __repr__ = __str__
