def id(name):
    return {'Id': name}


def avg(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Avg': arg}


def sum(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Sum': arg}


def count(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Count': arg}


def last(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Last': arg}


def max(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Max': arg}


def min(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Min': arg}


def year(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Year': arg}


def month(arg):
    if isinstance(arg, str):
        arg = id(arg)
    return {'Month': arg}


def time(h, m, s):
    h, m, s = str(h), str(m), str(s)
    val = h.zfill(2) + ':' + m.zfill(2) + ':' + s.zfill(2)
    return {'Time': val}


def bar(lhs, rhs):
    if isinstance(lhs, str):
        lhs = id(lhs)
    return {'Bar': [lhs, rhs]}
