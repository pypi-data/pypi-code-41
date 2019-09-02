from __future__ import print_function

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__


# -------------------------------------------------------------------------------------------------
def print(*args, **kwargs):
    if "color" in kwargs:
        if(kwargs["color"] == "green"):
            return __builtin__.print("\033[1;36;1m", *args, "\033[1;32;0m", sep="", end="")
        elif(kwargs["color"] == "yellow"):
            return __builtin__.print("\033[1;33;1m", *args, "\033[1;32;0m", sep="", end="")
        elif(kwargs["color"] == "red"):
            return __builtin__.print("\033[1;31;1m", *args, "\033[1;32;0m", sep="", end="")
        else:
            __builtin__.print("ERR:" + kwargs['color'], sep="", end="")
            exit(1)
    else:
        return __builtin__.print(*args, **kwargs)
# -------------------------------------------------------------------------------------------------
