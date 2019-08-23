import codecs
from setuptools import setup
from glob import glob
import os.path as path

# Snippet taken from - http://goo.gl/BnjFzw
# It's to fix a bug for generating a Windows distribution on Linux systems.
# Linux doesn't have access to the "mbcs" encoding.
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    def wrapper(name, enc=ascii):
        return {True: enc}.get(name == 'mbcs')
    codecs.register(wrapper)

install_requires = ['pytz', 'beautifulsoup4', 'lxml', 'requests']

cwd = path.dirname(__file__)
longdesc = codecs.open(path.join(cwd, 'longdesc.rst'), 'r', 'ascii').read()

version = '0.0.0'
with codecs.open(path.join(cwd, 'nflgame/version.py'), 'r', 'ascii') as f:
    exec(f.read())
    version = __version__
assert version != '0.0.0'

setup(
    name='nflgame-redux',
    author='Andrew Gallant',
    author_email='d@derekadair.comm',
    version=version,
    license='UNLICENSE',
    description='An API to retrieve and read NFL Game Center JSON data. '
                'It can work with real-time data, which can be used for '
                'fantasy football.',
    long_description=longdesc,
    url='https://github.com/derek-adair/nflgame',
    classifiers=[
        'License :: Public Domain',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
    ],
    platforms='ANY',
    packages=['nflgame'],
    package_data={'nflgame': ['players.json', 'schedule.json',
                              'gamecenter-json/*.json.gz']},
    data_files=[('share/doc/nflgame', ['README.md', 'CHANGELOG', 'UNLICENSE',
                                       'longdesc.rst']),
                ('share/doc/nflgame/doc', glob('doc/nflgame/*.html'))],
    scripts=[
        'scripts/nflgame-update-players',
        'scripts/nflgame-update-schedule',
    ],
    install_requires=install_requires
)
