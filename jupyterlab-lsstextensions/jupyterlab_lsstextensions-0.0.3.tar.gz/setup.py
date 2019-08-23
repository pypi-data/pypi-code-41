"""
Setup Module to setup Python Handlers for LSST query templating
"""
import setuptools

setuptools.setup(
    name='jupyterlab_lsstextensions',
    version='0.0.3',
    packages=setuptools.find_packages(),
    install_requires=[
        'nbreport>=0.7.3rc1',
        'notebook',
    ],
    package_data={'jupyterlab_lsstextensions': ['*']},
)
