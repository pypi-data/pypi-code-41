from setuptools import setup

from pybotman import __version__

setup(
    name='pybotman',
    version=__version__,
    description='Python API wrapper for botman bots',
    url='https://github.com/Flowelcat/pybotman',
    download_url=f'https://github.com/Flowelcat/pybotman/archive/v.{__version__}.tar.gz',
    author='Flowelcat',
    author_email='flowelcat@gmail.com',
    keywords=["botman", 'pybotman', 'botmanbot', 'botmanapi'],
    license='apache-2.0',
    packages=['pybotman'],
    install_requires=['requests'],
    python_requires='>3.6.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
