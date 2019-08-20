import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='dotGraph',
    version='0.0.1',
    author="Bernhard W. Radermacher",
    author_email="bernhard@radermacher.us",
    description="Tool to create .dot/.gv files for Graphviz",
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)