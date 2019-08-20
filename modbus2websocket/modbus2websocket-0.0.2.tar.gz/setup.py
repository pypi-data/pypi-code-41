from setuptools import setup, find_packages

import sys
if (sys.version_info.major < 3) and (sys.version_info.minor <= 6):
    sys.exit('Sorry, Python 3.6 and 3.7 only supported')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="modbus2websocket",
    version='0.0.2',
    description='Modbus/TCP to websocket router.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='modbus tcp websocket asyncio socket',
    url='https://github.com/PakshNina/modbus2websocket',
    author='Nina Pakshina',
    author_email='ninucium@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pyModbusTCP',
        'websockets'
    ],
    include_package_data=True,
    zip_safe=False,   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    )
