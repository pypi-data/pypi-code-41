from setuptools import setup, find_packages


setup(
    name='physical_dualism',
    version='1.0.1',
    url='https://github.com/petarmaric/physical_dualism',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Python library that approximates the natural frequency from '\
                'stress via physical dualism, and vice versa.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    platforms='any',
    py_modules=['physical_dualism'],
    install_requires=open('requirements.txt').read().splitlines(),
)
