from distutils.core import setup

setup(
    name='carson_logging',
    version='0.0.1',
    packages=['packages', 'bin'],
    license="Apache-2.0",

    author='Carson',
    author_email='jackparadise520a@gmail.com',

    scripts=['runner.py'],

    install_requires=[],

    url='https://github.com/CarsonSlovoka/carson-logging',
    description='easier to use original python provides a module of logging',
    long_description=open('README.rst').read(),
    keywords=['logging', 'log'],

    download_url='https://github.com/CarsonSlovoka/carson-logging/tarball/v0.0.0',

    zip_safe=False,
    classifiers=[  # https://pypi.org/classifiers/
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Operating System :: Microsoft',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
