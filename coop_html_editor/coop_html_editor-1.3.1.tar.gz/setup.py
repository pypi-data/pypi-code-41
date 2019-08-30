# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('coop_html_editor').__version__

setup(
    name='coop_html_editor',
    version=VERSION,
    description='integration for Inline HTML editor',
    packages=find_packages(),
    include_package_data=True,
    author='Luc Jean',
    author_email='ljean@apidev.fr',
    license='BSD',
    long_description=open('README.rst').read(),
    url="https://github.com/ljean/coop_html_editor/",
    download_url="https://github.com/ljean/coop_html_editor/tarball/master",
    zip_safe=False,
    install_requires=['apidev_django-floppyforms', ],
)
