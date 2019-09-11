# -*- coding: utf-8 -*-
import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()


if __name__ == '__main__':
    setup(
        name='setuptools_freeze',
        author='Axel Juraske',
        author_email='axel.juraske@short-report.de',
        url='https://github.com/axju/setuptools_freeze',
        license='MIT',
        description='Integrate "pyinstaller" to "setuptools"',
        long_description=README,
        packages=['setuptools_freeze'],
        package_dir={'': 'src'},
        include_package_data=True,
        use_scm_version=True,
        install_requires=[
            'pyinstaller'
        ],
        setup_requires=[
            'setuptools_scm',
        ],
        entry_points={
            'distutils.commands': [
                'pyinstaller=setuptools_freeze.integration:PyInstallerCmd',
                'inno=setuptools_freeze.integration:InnoSetupCmd',
            ],
            'distutils.setup_keywords':[
                'guid=setuptools_freeze.integration:guid'
            ]
        }
    )
