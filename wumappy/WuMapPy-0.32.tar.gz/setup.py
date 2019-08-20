# coding: utf8
"""
    wumappy
    -------

    Graphical user interface for sub-surface geophysical survey data processing

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""

import sys
import subprocess
import os
import glob
import re
from setuptools import setup, find_packages
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))

README = ''
CHANGES = ''
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    pass

REQUIREMENTS = [
    'matplotlib', # depends on linux package libfreetype6-dev libpng12-0-dev
    'QT.py',  # to manage all Qt bindings
    'numexpr',
    'geophpy>=0.32' # match the WuMapPy GUI version
   ]

## Checking python version and Qt binding to adjust dependencies ---------------
_ver = sys.version_info
is_py3 = (_ver[0] == 3)
is_py34 = (is_py3 and _ver[1] == 4)
is_py35 = (is_py3 and _ver[1] > 4)

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

Qt_binding = ''
if is_py34:

    is_Qt4 = 'PyQt4' in installed_packages
    is_Pyside = 'PySide' in installed_packages
    print('*** Qt4', is_Qt4)
    print('*** PySide', is_Pyside)

    if  not (is_Qt4 or is_Pyside):
        # Pyside is required for Python 34 and less 
        # depends on linux package qt4-dev-tools
        Qt_binding = ['PySide']
        REQUIREMENTS.extend(Qt_binding)

elif is_py35:

    is_Qt5 = 'PyQt5' in installed_packages
    is_Pyside2 = 'PySide2' in installed_packages
    #print('*** Qt5', is_Qt5)
    #print('*** PySide2', is_Pyside2)

    # PyQt5 compatibility not tested yet
    # --> Forcing PySide2
    #if not (is_Qt5 or is_Pyside2):  
    if not is_Pyside2:
        # Pyside2 is required for Python 35 and more
        Qt_binding = ['PySide2'] 
        REQUIREMENTS.extend(Qt_binding)

with open(os.path.join(os.path.dirname(__file__), 'wumappy',
                       '__init__.py')) as init_py:
    release = re.search("VERSION = '([^']+)'", init_py.read()).group(1)

# The short X.Y version.
version = release.rstrip('dev')

## Custom setuptool install command class ----------------------------
class CustomInstallCommand(install):
    ''' Class to make a custom installation command

    Custom command that builds the package html documentation before
    installing it.

    '''

    def run(self):
        # Building html doc
        print('Building package documentation')
        docspath= os.path.join(here, 'docs')
        os.chdir(docspath)
        os.system('make html')
        os.system('make clean')

        # Installing package
        print('Installing package')
        os.chdir(here)
        # Recommended call to 'install.run(self)' will ignores the
        # install_requirements.
        # The underlying bdist_egg is called instead.
        self.do_egg_install()
        ##install.run(self)  # ignores install_requirements


## Actual setuptools setup command  -------------------------------------------
setup(
    name='WuMapPy',
    version='0.32',
    license='GNU GPL v3',
    description='Graphical user interface for sub-surface geophysical survey data processing',
    long_description=README + '\n\n' + CHANGES,
    author='Lionel Darras, Philippe Marty, Quentin Vitale',
    author_email='lionel.darras@mom.fr',
    maintainer='Lionel Darras, Philippe Marty Quentin Vitale',
    maintainer_email='lionel.darras@mom.fr',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    data_files=[
        ('resources', ['wumappy/resources/wumappy.png']),
        ('examples', glob.iglob('wumappy/examples/**', recursive=True))
    ],
    entry_points={
        'console_scripts': [
            'wumappy = wumappy.__main__:main'
        ]
    },
    cmdclass={
        'install': CustomInstallCommand,  # using custom install command
    }
)
