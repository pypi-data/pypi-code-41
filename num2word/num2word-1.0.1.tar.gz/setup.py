from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name = 'num2word',
    version = '1.0.1',
    description = 'Convert any number to word',
    py_modules = ['num2word'],
    package_dir = {'': 'src'},
    url = "https://github.com/MUKESHSIHAG/python_library_num2word",
    author = "Mukesh Kumar",
    author_email = "sihagmukesh22@gmail.com",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
    ],
)