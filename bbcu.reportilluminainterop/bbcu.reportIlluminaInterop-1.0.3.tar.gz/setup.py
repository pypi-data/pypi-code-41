from setuptools import setup, find_packages

with open('VERSION.txt', 'r') as version_file:
    version = version_file.read().strip()

requires = ['pandas==0.18.1', 'interop==1.1.4', 'tabulate']

setup(
    name='bbcu.reportIlluminaInterop',
    version=version,
    author='Refael Kohen',
    author_email='refael.kohen@gmail.com',
    packages=find_packages(),
    scripts=[
        'scripts/run-sav-stat.py',
    ],
    description='Create SAV statistics. Run in python 2.7',
    long_description=open('README.txt').read(),
    install_requires=requires,
    tests_require=requires + ['nose'],
    include_package_data=True,
    test_suite='nose.collector',
)
