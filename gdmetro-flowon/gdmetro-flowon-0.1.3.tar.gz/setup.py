# -*- coding: utf-8 -*-
import os

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'gdflowon', '__about__.py'), 'r') as f:
    exec(f.read(), about)

__VERSION__ = about['VERSION']

requirements = []

test_requirements = ['mock', 'PyYAML==3.13']

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = setuptools.find_packages(exclude=['tests', 'tests.*', '*.log', 'venv'])
setuptools.setup(
    name='gdmetro-flowon',
    description="An automated production tool provided by the GeneDock team.",
    version=__VERSION__,
    author='GeneDock Contributor',
    author_email="raomengnan@genedock.com",
    maintainer='GeneDock Contributor',
    maintainer_email='liming@genedock.com',
    url='https://www.genedock.com',
    packages=packages,
    package_data={'': ['LICENSE', 'requirements.txt']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Customer Service',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    platforms=['Independent'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='tests'
)
