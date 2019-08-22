#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 16:15:25 2019

@author: vbokharaie

This is just an auxilary function that helps break a class into several files
and put methods of the same class in different modules.


"""

# Lib.py

def add_methods_from(*modules):
    def decorator(Class):
        for module in modules:
            for method in getattr(module, "__methods__"):
                setattr(Class, method.__name__, method)
        return Class
    return decorator

def register_method(methods):
    def register_method(method):
        methods.append(method)
        return method # Unchanged
    return register_method