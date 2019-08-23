import os
import shutil
import cProfile
from pathlib import Path
from typing import NamedTuple, List, Dict, Callable, Tuple, Iterator

from ..config import conf
from ..session import Session


class Test(NamedTuple):
    func: Callable[[Session], Iterator[str]]
    args: List[str] = []
    files: List[Tuple[Path, str]] = []


tests: Dict[str, Test] = {}


def test(function=None, *, args=[], files=[]):
    def decorator(func):
        tests[func.__name__] = Test(func, args, files)
        return func
    if function is None:
        return decorator
    return decorator(function)


class Input:
    session = None

    def __init__(self, test):
        self.stream = self.characters(test)
        self.queue = []

    def get(self):
        if self.queue:
            return self.queue.pop(0)
        c = next(self.stream)
        if len(c) == 1:
            print(c, end='')
        else:
            print(f'<{c}>', end='')
        return c

    def put(self, c):
        self.queue.append(c)

    def characters(self, test):
        for s in test(self.session):
            while s:
                if s[:2] == '^^':
                    yield '^'
                    s = s[2:]
                if s[0] == '^':
                    yield s[:2]
                    s = s[2:]
                elif s[:2] == '<<':
                    yield '<'
                    s = s[2:]
                elif s[0] == '<':
                    key, s = s[1:].split('>', 1)
                    yield key.replace('-', '_')
                elif s[0] == '\n':
                    s = s[1:]
                else:
                    yield s[0]
                    s = s[1:]
        yield '^q'


def run_tests(names):
    # Read in all tests:
    import spelltinkle.test.tests  # noqa

    dir = Path.home() / '.spelltinkle/self-test'
    if dir.is_dir():
        shutil.rmtree(dir)
    dir.mkdir(parents=True)
    os.chdir(dir)
    conf.home = dir
    conf.read()

    prof = cProfile.Profile()
    prof.enable()

    if not names:
        names = sorted(tests)
    for name in names:
        print(name)
        test = tests[name]
        scr = Screen(10, 60, Input(test.func))
        for name, txt in test.files:
            if '/' in name:
                dir = name.rsplit('/', 1)[0]
                os.makedirs(dir)
            with open(name, 'w') as fd:
                fd.write(txt)
        s = Session(test.args, scr, test=True)
        scr.stream.session = s
        error = s.run()
        print()
        if error:
            break

    prof.disable()
    prof.dump_stats('test.profile')

    if error:
        raise SystemExit('Test failed')


class Screen:
    def __init__(self, h, w, stream=None):
        self.h = h
        self.w = w
        self.stream = stream

    def subwin(self, a, b, c, d):
        return Screen(a, b)

    def erase(self):
        pass

    def refresh(self):
        pass

    def move(self, a, b):
        pass

    def write(self, line, colors):
        pass

    def input(self):
        return self.stream.get()
