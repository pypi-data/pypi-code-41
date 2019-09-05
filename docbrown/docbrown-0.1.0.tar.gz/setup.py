import os
from setuptools import find_packages, setup

from docbrown import VERSION

try:
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')) as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = ''


setup(
    name='docbrown',
    version=VERSION,
    description='an empirical progress library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Konrad Mohrfeldt',
    author_email='konrad.mohrfeldt@farbdev.org',
    url='https://github.com/kmohrf/docbrown',
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    include_package_data=True,
    package_data={
        '': ['README.md', 'LICENSE']
    },
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
