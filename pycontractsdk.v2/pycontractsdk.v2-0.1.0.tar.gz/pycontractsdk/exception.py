# -*- coding: utf-8 -*-

class Error(Exception):
    pass

class InputError(Error):
    def __index__(self, expression, message):
        self.expression = expression
        self.message = message

    def __str__(self):
        return repr()