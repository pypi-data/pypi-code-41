import asyncio
from pymata_aio.pymata3 import PyMata3

def test_connection():
    try:
        board = PyMata3()
    # Board not plugged in - correct sketch or not
    except TypeError:
        assert False
    # incorrect sketch loaded
    except asyncio.futures.CancelledError:
        assert False
