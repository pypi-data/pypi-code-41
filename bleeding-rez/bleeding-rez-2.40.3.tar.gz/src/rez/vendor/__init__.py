import sys

if sys.version_info[0] == 2:
    from ._python2 import yaml
    from ._python2 import sortedcontainers
    from ._python2 import enum
else:
    from ._python3 import yaml
    from ._python3 import sortedcontainers
    import enum


sys.modules[__name__ + ".yaml"] = yaml
sys.modules[__name__ + ".sortedcontainers"] = sortedcontainers
sys.modules[__name__ + ".enum"] = enum
