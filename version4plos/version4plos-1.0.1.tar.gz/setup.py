from setuptools import setup


setup(
    name='version4plos',
    version='1.0.1',
    url='https://github.com/petarmaric/version4plos',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Console app and Python API for automated tracking of PLOS '\
                'LaTeX template versions',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Utilities',
    ],
    py_modules=[
        'version4plos',
    ],
    entry_points={
        'console_scripts': [
            'version4plos=version4plos:main',
        ],
    },
    install_requires=[
        'lxml~=4.4',
        'requests~=2.22',
    ],
    extras_require={
        'dev': [
            'pylint~=1.9',
        ],
    },
)
