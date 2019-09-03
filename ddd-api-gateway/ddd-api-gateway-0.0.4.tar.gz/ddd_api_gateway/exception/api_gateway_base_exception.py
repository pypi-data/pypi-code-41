# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""


class ApiGWBaseException(Exception):

    def __init__(self, msg):
        super().__init__()
        print(msg)
