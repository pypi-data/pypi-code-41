import distutils.spawn
import os.path
from setuptools import find_packages
from setuptools import setup
import shlex
import subprocess
import sys

install_requires = [
    'numpy',
    'opencv-python',
    'PyQt5'
]

if sys.argv[1] == 'release':
    if not distutils.spawn.find_executable('twine'):
        print(
            'Please install twine:\n\n\tpip install twine\n',
            file=sys.stderr,
        )
        sys.exit(1)

    commands = [
        'python setup.py sdist',
        'twine upload dist/labelme-{:s}.tar.gz'.format('0.0.1'),
    ]
    for cmd in commands:
        subprocess.check_call(shlex.split(cmd))
    sys.exit(0)


def get_long_description():
    with open('README.md', 'r') as f:
        long_description = f.read()
    return long_description


setup(
    name='labelseg',
    version='0.0.1',
    packages=find_packages(),
    description='label tool for semantic segmentation',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Frederic',
    author_email='fk1010098686@outlook.com',
    install_requires=install_requires,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    package_data={'labelseg': ['icons/*', ]},
    entry_points={
        'console_scripts': [
            'labelseg=labelseg.app:main',
        ],
    },
)
