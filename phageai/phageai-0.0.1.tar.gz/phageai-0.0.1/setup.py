# Copyright (C) 2019 SLAVIC AI


import setuptools


with open('README.md') as f:
    README = f.read()


setuptools.setup(
    author='SLAVIC AI',
    author_email="contact@slavic.ai",
    name='phageai',
    license='MIT',
    description='PhageAI',
    version='v0.0.1',
    long_description=README,
    url='https://github.com/slavicai/phageai/',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['requests'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ]
)

