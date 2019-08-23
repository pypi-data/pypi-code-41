from distutils.core import setup
setup(
    name='handygeometry',
    packages=['handygeometry'],
    version='0.12',
    license='MIT',
    description='A collection of handy geometry functions.',
    author='ahmetserguns',
    author_email='ahmetserguns@gmail.com',
    url='https://github.com/ahmetserguns/geometry',
    download_url='https://github.com/ahmetserguns/geometry/archive/0.11.tar.gz',
    keywords=['geometry', 'easy', 'triangle', 'surface',
              'collection', 'angle', 'perimeter', 'volume'],
    install_requires=[],
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
