# -*- coding: utf-8 -*-
"""Puzzlestream test module.

contains test function wrapper
"""

functions = []


def test(func):
    """Test function wrapper.

    This wrapper marks a function in a module as a test function.
    Example usage::

        @test  
        def testFunctionExample(stream):  
            return isinstance(stream["example"], int)
    """
    functions.append(func)
    return func
