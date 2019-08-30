'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 27, 2017
@author: Niels Lubbes

https://python-packaging.readthedocs.io/en/latest/minimal.html
https://pypi.python.org/pypi?%3Aaction=list_classifiers
'''


from setuptools import setup


setup( 
    name = 'ns_lattice',
    version = '4',
    description = 'Algorithms for computing in Neron-Severi lattice',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    keywords = 'Neron-Severi-lattice',
    url = 'http://github.com/niels-lubbes/ns_lattice',
    author = 'Niels Lubbes',
    license = 'MIT',
    package_dir = {'ns_lattice': 'src/ns_lattice'},
    packages = ['ns_lattice'],
    package_data = {'ns_lattice': ['ns_tools.sobj']},
    # include_package_data = True,
    install_requires = ['linear_series'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    entry_points = {
        'console_scripts': ['run-lattice=ns_lattice.__main__:main'],
    },
    zip_safe = False
    )
