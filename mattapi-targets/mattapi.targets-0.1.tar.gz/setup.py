# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import platform
from setuptools import setup, find_packages

PACKAGE_NAME = 'mattapi.targets'
PACKAGE_VERSION = '0.1'

INSTALL_REQUIRES = [
'mattapi>=0.92'
]

TESTS_REQUIRE = [
]

DEV_REQUIRES = [
]

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='Targets for Mozilla Iris',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing'
    ],
    keywords=['automation', 'testing'],
    author='Matt Wobensmith',
    author_email='itsmatt@pacbell.net',
    url='https://github.com/mwxfr/mattapi.targets',
    download_url='https://github.com/mwxfr/mattapi.targets/latest.tar.gz',
    license='MPL2',
    packages=find_packages(),
    python_requires='>=3.7.3',
    include_package_data=True,  # See MANIFEST.in
    zip_safe=False,
    use_2to3=False,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={'dev': DEV_REQUIRES},  # For `pip install -e .[dev]`
    entry_points={
        'console_scripts': [
            'target1 = targets.test.main:main',
            'target2 = mattapi.targets.test.main:main',
            'plz = plz:hi'
        ]
    }
)
