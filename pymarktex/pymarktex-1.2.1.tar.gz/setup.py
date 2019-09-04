from setuptools import setup, find_packages

setup(
    name             = 'pymarktex',
    version          = '1.2.1',
    description      = 'Will convert a markdown text file to a fancy PDF document',
    license          = 'MIT',
    url              = 'http://github.com/xapple/pymarktex/',
    author           = 'Lucas Sinclair',
    author_email     = 'lucas.sinclair@me.com',
    packages         = find_packages(),
    scripts          = ['scripts/pymarktex'],
    install_requires = ['autopaths', 'plumbing', 'sh', 'pystache'],
    long_description = open('README.md').read(),
)