from setuptools import setup

from sphinx.setup_command import BuildDoc
cmdclass = {'build_sphinx': BuildDoc}

name = 'eadf'
version = '0.1'
author = 'S. Pawar, S. Semper'
release = '0.1'

setup(
    author=author,
    version=version,
    name=name,
    packages=[name],
    author_email='sebastian.semper@tu-ilmenau.de',
    description='Effective Aperture Distribution Function',
    url='https://eadf.readthedocs.io/en/latest/',
    license='Apache Software License',
    keywords='signal processing',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
    ],
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'source_dir': ('setup.py', 'doc/source'),
            'build_dir': ('setup.py', 'doc/build'),
        }
    },
)
