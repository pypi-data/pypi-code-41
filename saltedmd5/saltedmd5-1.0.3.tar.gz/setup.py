## Setup for Salted MD5 Hashing

import setuptools

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author='Nuttaphat Arunoprrayoch',
    author_email='nat236919@gmail.com',
    name='saltedmd5',
    license='MIT',
    description='saltedmd5 is a python package for performing md5 hashing with salt.',
    version='v1.0.3',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/nat236919/saltedmd5',
    packages=setuptools.find_packages(),
    python_requires=">=3.5",
    install_requires=[],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop'
    ],
)
