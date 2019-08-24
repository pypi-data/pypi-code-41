#!/usr/bin/env python

class Program(object):
    """ """
    
    def __init__(self, name, current = None, latest=None):
        """ """

        self.name = str(name)

        if current is not None and current[:1] is not "v":
            self.current = "v{}".format(current)
        else:
            self.current = current

        self.latest = latest