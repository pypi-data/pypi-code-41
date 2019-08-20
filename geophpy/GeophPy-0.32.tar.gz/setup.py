# coding: utf8
"""
    geophpy
    -------

    Tools for sub-surface geophysical survey data processing.

    :copyright: Copyright 2014-2019 Lionel Darras, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""
import os
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
    'netcdf4',    # depends on linux packages libhdf5-dev, libnetcdf-dev
    #'matplotlib==1.4.2', # depends on ???
    'matplotlib>=1.5',
    'numpy',
    'scipy',      # depends on ???
    'pillow',     # depends on linux packages libjpeg ...
    'pyshp',
    'simplekml',
    'utm',
    'Sphinx>=1.4.3' # depends on linux packages latexmk, dvipng
]

## Custom setuptool install command class ----------------------------
class CustomInstallCommand(install):
    '''
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

        ###
        ## Not really used in geophpy, should be placed in wumappy
        ###
        # Updating colormap icons
        print('Updating available colormaps')
        from geophpy import dataset

        icon_path = os.path.join(here, 'geophpy\plotting\colormapicons')
        mypath = icon_path
        icon_filelist = [ f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        cmap_list = dataset.colormap_getlist()

        for cmname in cmap_list:
            icon_name  = 'CMAP_' + cmname + '.png'
            if not os.path.exists(os.path.join(icon_path, icon_name)):
                dataset.colormap_make_icon(cmname, path=icon_path)
                print(icon_name)

        # Installing package
        print('Installing package')
        os.chdir(here)
        # Recommended call to 'install.run(self)' will ignores the
        # install_requirements.
        # The underlying bdist_egg is called instead.
        self.do_egg_install()
        ##install.run(self)  # ignores install_requirements


setup(
    name='GeophPy',
    version='0.32',
#    url='https://pypi.org/project/GeophPy/',
    license='GNU GPL v3',
    description='Tools for sub-surface geophysical survey data processing',
    long_description=README + '\n\n' + CHANGES,
    author='Lionel Darras, Philippe Marty & Quentin Vitale',
    author_email='lionel.darras@mom.fr',
    maintainer='Lionel Darras, Philippe Marty & Quentin Vitale',
    maintainer_email='lionel.darras@mom.fr',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    cmdclass={
        'install': CustomInstallCommand,  # custom install command
    }
)
