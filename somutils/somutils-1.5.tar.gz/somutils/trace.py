# -*- coding: utf-8 -*-

import decorator

doTrace=True
@decorator.decorator
def trace(function, *args) :
    """Decorates a function by tracing the begining and
    end of the function execution, if doTrace global is True"""

    if doTrace : print ("> "+function.__name__, args)
    result = function(*args)
    if doTrace : print ("< "+function.__name__, args, "->", result)
    return result

# vim: ts=4 sw=4 et
