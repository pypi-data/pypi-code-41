# -*- coding: utf-8 -*-

# auxilium
# --------
# A Python project for an automated test and deploy toolkit - 100%
# reusable.
# 
# Author:   sonntagsgesicht
# Version:  0.1, copyright Thursday, 29 August 2019
# Website:  https://github.com/sonntagsgesicht/auxilium
# License:  Apache License 2.0 (see LICENSE file)


import os
import sys
import inspect
import types

replacements = dict()
replacements['mod'] = {}
replacements['const'] = {}
replacements['func'] = {}
replacements['attr'] = {}
replacements['meth'] = dict.fromkeys(('range()',))
replacements['exc'] = {}
replacements['obj'] = {}
replacements['class'] = dict.fromkeys(('int', 'float', 'str', 'tuple', 'list', 'dict'))

replacements['mod']['datetime'] = 'datetime <datetime>'
replacements['class']['datetime.datetime'] = 'datetime.datetime <datetime.datetime>'
replacements['class']['datetime.timedelta'] = 'datetime.timedelta <datetime.timedelta>'
replacements['class']['datetime.date'] = 'datetime.date <datetime.date>'
replacements['meth']['datetime.date.today()'] = 'datetime.date.today() <datetime.date.today>'

def replacements_from_pkg(replacements_in, pkg, spr=None):
    if spr is None:
        replacements_in['mod'][pkg.__name__] = None
        n = pkg.__name__ + '.'
    else:
        n = spr.__name__ + '.'
    for k, v in inspect.getmembers(pkg):
    #for k, v in [(name, getattr(auxilium, name)) for name in sorted(dir(auxilium))]:
        if not k.startswith('_') and inspect.getmodule(v) and inspect.getmodule(v).__name__.startswith(pkg.__name__):
            if inspect.ismodule(v):
                # mod -> 'datetime, datetime <datetime
                replacements_in['mod'][n + k] = '%s <%s>' % (n + k, n + k)
                replacements_in = replacements_from_pkg(replacements_in, v, pkg)
            elif inspect.isclass(v) and issubclass(v, Exception):
                # exc  -> 'ValueError', 'ValueError <ValueError>'
                replacements_in['exc'][k] = '%s <%s>' % (k, n + k)
            elif inspect.isclass(v):
                # cls  -> 'date', 'date <datetime.date>'        # isclass(x)
                replacements_in['class'][k] = '%s <%s>' % (k, n + k)
                # init -> 'date()', 'date() <datetime.date>'    # isclass(x)
                replacements_in['class'][k + '()'] = '%s() <%s>' % (k, n + k)
                if spr is None:
                    replacements_in = replacements_from_cls(replacements_in, v, pkg)
                else:
                    replacements_in = replacements_from_cls(replacements_in, v, spr)
            elif inspect.isfunction(v):
                # func -> 'foo()', 'auxilium.foo() <foo()>'
                replacements_in['func'][k + '()'] = '%s() <%s>' % (k, n + k)
            else:
                # attr -> 'DO', 'date.year <datetime.date.year>'
                replacements_in['attr'][k] = '%s <%s>' % (k, n + k)
    return replacements_in


def replacements_from_cls(replacements_in, cls, pkg=None):
    n = cls.__name__ + '.'
    p = (pkg.__name__ + '.') if pkg else ''
    for k, v in inspect.getmembers(cls):
        if not k.startswith('_'):
            if isinstance(v, types.MethodType) or isinstance(v, types.FunctionType) or inspect.ismethoddescriptor(v):
                # meth -> 'today()', 'date.today() <datetime.date.today>'
                replacements_in['meth'][n + k + '()'] = '%s() <%s>' % (n + k, p + n + k)
            elif inspect.isfunction(v):
                # meth -> 'today()', 'date.today() <datetime.date.today>'
                replacements_in['meth'][n + k + '()'] = '%s() <%s>' % (n + k, p + n + k)
            else:
                # attr -> 'year', 'date.year <datetime.date.year>'
                replacements_in['attr'][n + k] = '%s <%s>' % (n + k, p + n[:-1])
    return replacements_in


def replacements_str(replacements_in):
    _lines = []
    for c, d in replacements_in.items():
        for k, v in d.items():
            s = k if v is None else v
            _lines.append(".. |%s| replace:: :%s:`%s`" % (k, c, s))
    return """   x""".replace('x', (os.linesep + '   ').join(_lines))


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('../../'))  # needed to import auxilium
    sys.path.insert(0, os.path.abspath('.'))  # needed to import auxilium

    pkg = __import__(os.getcwd().split(os.sep)[-1])

    sys.path.insert(0, os.path.abspath('../../' + pkg.__name__))  # needed to import auxilium

    replacements = replacements_from_pkg(replacements, pkg)
    print(replacements_str(replacements))
