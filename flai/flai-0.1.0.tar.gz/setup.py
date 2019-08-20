
import setuptools

from setuptools import setup



with open('README.md', 'r') as f:

    long_description = f.read()



setup(

    url='https://github.com/moreal/flai',

    name='flai',

    version='0.1.0',

    long_description=long_description,

    long_description_content_type="text/markdown",

    description='flask like socket server framework',

    author='moreal',

    author_email='dev.moreal@gmail.com',

    packages=setuptools.find_packages(),

    include_package_data=True,

    install_requires=[],

    classifiers=[

        'Development Status :: 2 - Pre-Alpha',

        'Programming Language :: Python :: 3.7',

    ]

)