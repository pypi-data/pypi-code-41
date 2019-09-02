from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='pyaeneas',
    packages=['pyaeneas'],
    version='0.1',
    license='MIT',
    description='Aeneas fullnode API Python client',
    long_description=long_description,
    author='Andrii Matiiash',
    author_email='andmati743@gmail.com',
    url='https://github.com/AverHLV/pyaeneas',
    download_url='https://github.com/AverHLV/pyaeneas/archive/0.1.tar.gz',
    keywords=['ASYNC', 'AENEAS', 'CLIENT', 'BLOCKCHAIN'],

    install_requires=[
        'aiohttp',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
