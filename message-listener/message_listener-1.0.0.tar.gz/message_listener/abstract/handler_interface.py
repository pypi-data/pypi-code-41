#!/usr/bin/python3
# pylint: disable=I0011,R0913,R0902
"""Define Handler abstact"""


class Handler(object):
    """Handler abstract"""
    def __init__(self, worker):
        self.worker = worker

    def handle(self, message):
        """handle a message"""
        raise NotImplementedError("handle not implemented")
