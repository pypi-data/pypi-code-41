from setuptools import find_packages, setup

setup(
    name='kiss_cache',
    packages=find_packages(),
    version='0.5.8',
    license='MIT',
    description='"Keep It Simple Stupid" Cache',
    author='Bergutov Ruslan',
    author_email='ruslanbergutov@gmail.com',
    url='https://github.com/HiveTraum/kiss_cache',
    download_url='https://github.com/HiveTraum/kiss_cache/archive/0.5.8.tar.gz',
    keywords=['cache', 'memoize', 'kiss'],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
