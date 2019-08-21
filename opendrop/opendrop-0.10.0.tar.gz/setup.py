from opendrop import __version__
from codecs import open
from os.path import abspath, dirname, join
from setuptools import find_packages, setup

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='opendrop',
    version=__version__,
    python_requires='>=3.6',
    description='An open Apple AirDrop implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/seemoo-lab/opendrop',
    project_urls={
        'Research Project': 'https://owlink.org',
        'Research Paper': 'https://usenix.org/conference/usenixsecurity19/presentation/stute',
        'Research Group': 'https://seemoo.de',
        'Source': 'https://github.com/seemoo-lab/opendrop',
    },
    author='The Open Wireless Link Project',
    author_email='mstute@seemoo.tu-darmstadt.de',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='cli',
    packages=find_packages(),
    package_data={
        'opendrop': ['certs/*.pem']
    },
    install_requires=['requests', 'fleep', 'ifaddr', 'Pillow',
                      'requests_toolbelt', 'ctypescrypto', 'libarchive-c'],
    entry_points={
        'console_scripts': [
            'opendrop=opendrop.cli:main',
        ],
    },
)
