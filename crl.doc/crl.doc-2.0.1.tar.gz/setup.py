import os
import sys
import importlib
from setuptools import setup, find_packages


class WorksOnlyWithPython3(Exception):
    pass


if sys.version_info.major < 3 or sys.version_info.minor < 6:
    s = "Current version of Crl-Doc works only with on python 3.6 and onwards.\n \
         Either update your systems or use older version."
    raise WorksOnlyWithPython3(s)


VERSIONFILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'src', 'crl', 'doc', '_version.py')


def get_version():
    spec = importlib.util.spec_from_file_location('_version.py', VERSIONFILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_version()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='crl.doc',
    version=get_version(),
    author='Petri Huovinen',
    author_email='petri.huovinen@nokia.com',
    description='Documenation tools for Common Robot Libraries',
    install_requires=['lxml',
                      'jinja2',
                      'robotframework',
                      'sphinx'],
    python_requires='>=3.6.*',
    long_description=read('README.rst'),
    license='BSD-3-Clause',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Documentation :: Sphinx',
                 'Environment :: Console',
                 'Framework :: Robot Framework'],
    keywords='robotframework documentation',
    url='https://github.com/nokia/crl-doc',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['crl'],
    entry_points={
        'console_scripts': [
            'crl_doc_generate_rst = crl.doc.cmdline:cmdline']}
)
