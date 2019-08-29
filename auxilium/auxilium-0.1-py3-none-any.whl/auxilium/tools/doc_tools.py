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


from datetime import date
from textwrap import wrap
from os import walk, sep, getcwd, linesep
from os.path import join


def set_timestamp(pkg, rootdir=getcwd()):

    pkg = __import__(pkg) if isinstance(pkg, str) else pkg

    for subdir, dirs, files in walk(rootdir):
        for file in files:
            if file.endswith('py'):
                file = join(subdir, file)

                # read file lines into list
                f = open(file, 'r')
                lines = list(map(str.rstrip, f.readlines()))
                f.close()

                # set library date
                if file == rootdir + sep + pkg.__name__ + sep + '__init__.py':
                    for i, line in enumerate(lines):
                        if line.startswith('__date__ = '):
                            print("set %s.__date__ = %s" %( pkg.__name__, date.today().strftime('%A, %d %B %Y')))
                            lines[i] = "__date__ = '" + date.today().strftime('%A, %d %B %Y') + "'"
                            break

                    f = open(file, 'w')
                    f.write(linesep.join(lines))
                    f.write(linesep)  # last empty line
                    f.close()


def replace_headers(pkg, rootdir=getcwd(), test=False):
    pkg = __import__(pkg) if isinstance(pkg, str) else pkg

    new_lines = pkg.__name__,
    new_lines += '-' * len(pkg.__name__),
    new_lines += tuple(wrap(pkg.__doc__))
    new_lines += '',
    new_lines += "Author:   " + pkg.__author__,
    new_lines += "Version:  " + pkg.__version__ + ', copyright ' + pkg.__date__,
    new_lines += "Website:  " + pkg.__url__,
    new_lines += "License:  " + pkg.__license__ + " (see LICENSE file)",
    new_header = ["# -*- coding: utf-8 -*-", ''] + ['# ' + l for l in new_lines] + ['', '']

    for subdir, dirs, files in walk(rootdir):
        for file in files:
            if file.endswith('py'):
                file = join(subdir, file)
                print('\n*** process %s ***\n' % file)

                # read file lines into list
                f = open(file, 'r')
                lines = list(map(str.rstrip, f.readlines()))
                f.close()

                # remove old header
                removed = list()
                while lines and (not lines[0] or lines[0].startswith('#')):
                    removed.append(lines.pop(0).strip())

                # add new header
                new_lines = new_header + lines

                if test:
                    print('remove : ' + '\nremove : '.join(removed[:20]))
                    print('-----------------------------------------------------------------')
                    print('add    : ' + '\nadd    : '.join(new_lines[:20]))
                else:
                    print('\n'.join(new_lines[:20]))
                    f = open(file, 'w')
                    f.write(linesep.join(new_lines))
                    f.write(linesep)  # last empty line
                    f.close()


if __name__ == '__main__':
    # replace automated the header in source files
    pkg = __import__(getcwd().split(sep)[-1])
    set_timestamp(pkg)
    replace_headers(pkg)
