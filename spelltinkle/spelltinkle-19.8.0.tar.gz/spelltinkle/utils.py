import os
import os.path as op
import re


def untabify(line):
    if '\t' not in line:
        return line
    N = len(line)
    n = 0
    while n < N:
        if line[n] == '\t':
            m = 8 - n % 8
            line = line[:n] + ' ' * m + line[n + 1:]
            n += m
            N += m - 1
        else:
            n += 1
    return line


def isempty(line):
    return line == ' ' * len(line)

# re.match('(.*\S)(?= *)|( +)', line).group()


def tolines(fd):
    lines = []
    line = '\n'
    for n, line in enumerate(fd):
        line = untabify(line)
        for a in line[:-1]:
            assert ord(a) > 31, (line, n)
        if not isempty(line[:-1]):
            line = line[:-1].rstrip() + line[-1]
        lines.append(line[:-1])
    if line[-1] == '\n':
        lines.append('')
    else:
        lines[-1] = line
    return lines


def findword(line, c):
    while line[c - 1].isalnum():
        c -= 1
    return c


def find_files(x):
    x = re.compile('.*'.join(re.escape(word) for word in x.split(',')))
    matches = []
    for root, dirs, names in os.walk('.'):
        for name in names:
            if name.endswith('.pyc'):
                continue
            path = op.join(root, name)
            if x.search(path):
                matches.append(path)
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
    return matches
