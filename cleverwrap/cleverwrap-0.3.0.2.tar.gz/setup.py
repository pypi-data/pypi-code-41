import re

from setuptools import setup

import cleverwrap

install_requires = [
    'requests',
]

req_re = re.compile(r'([^=\s]+)(?:==|>=|<=)([^\s]+)')
reqs_file = open('requirements.txt').read().splitlines()


def parse_contstraints():
    d = {}
    for line in reqs_file:
        # Ignore options and comments
        if line.startswith(('#', '-')):
            continue

        if '#' in line:
            line = line.split('#')[0]

        match = req_re.match(line)

        if not match:
            continue

        name, ver = match.groups()
        d[name] = ver

    return d


constraints = parse_contstraints()


def get_constraints(reqs):
    for name in reqs:
        yield '{}=={}'.format(name, constraints[name])


def read_file(name):
    with open(name) as f:
        return f.read()


setup(
    name='cleverwrap',
    packages=['cleverwrap'],
    license='MIT',
    install_requires=get_constraints(install_requires),
    version='.'.join(str(n) for n in cleverwrap.__version__),
    description='A wrapper for the official cleverbot.com API',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Andrew Edwards',
    author_email='andrewthomasedwards@gmail.com',
    url='https://github.com/snoonetIRC/cleverwrap.py',
    keywords=['cleverbot', 'wrapper', 'clever'],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
)
