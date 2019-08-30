#!/usr/bin/env python3

PACKAGE_DATA = {
    'friendly_name': 'RemotePdb Client',
    'name': 'remote-pdb-client',
    'version': '1.0.2',
    'url': 'https://github.com/MartyMacGyver/remote-pdb-client',
    'author': 'Martin F. Falatic',
    'author_email': 'martin@falatic.com',
    'copyright': 'Copyright (c) 2017-2019',
    'license': 'MIT License',
    'description': 'A client for the RemotePDB debugger',
    'keywords': 'remotepdb debugging pdb telnet',
    'classifiers': [
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 5 - Production/Stable',
    ],
    'packages': [
        'remotepdb_client',
    ],
    'entry_points': {
        'console_scripts': [
            'remotepdb_client=remotepdb_client.remotepdb_client:main',
        ],
    },
    'install_requires': [
        'prompt-toolkit>=2.0.0',
    ],
    'extras_require': {},
    'package_data': {},
    'data_files': [],
}
