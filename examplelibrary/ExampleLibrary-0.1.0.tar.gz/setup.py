from setuptools import setup, find_packages

setup(
    name='ExampleLibrary',
    version='0.1.0',
    url='https://github.com/asweigart/examplelibrary',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('A placeholder for the "examplelibrary" name on PyPI. This is not a real library.'),
    license='BSD',
    long_description='',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],
    keywords="example",
    classifiers=[],
)