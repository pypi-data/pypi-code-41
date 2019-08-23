import pathlib
import re

import setuptools


def version():
    here = pathlib.Path(__file__).parent.resolve()
    with open(here / 'tutti_aisthetics' / '__init__.py', 'r') as f:
        for line in f:
            if re.match('^__version__ = ', line):
                version_string = re.search(r"[0-9]+\.[0-9]+\.[0-9]+", line).group(0).strip()
                return version_string


def requirements():
    """Extract requirements from `requirements.txt.`"""

    reqs = []
    here = pathlib.Path(__file__).parent.resolve()

    with open(here / 'requirements.txt', 'r') as f:
        for line in f:
            if not re.match('^#', line):
                reqs.append(line.strip())

    return reqs


setuptools.setup(
    name='tutti_aisthetics',
    version=version(),
    description='A tutti.ch image asthetics AI scorer.',
    long_description='Package based on https://github.com/idealo/image-quality-assessment.',
    author='Oscar Saleta',
    author_email='oscar@tutti.ch',
    license='Proprietary',
    keywords=['nima', 'CNN', 'neural net', 'MobileNet', 'aesthetics'],
    packages=setuptools.find_packages(exclude=['build', 'dist', '*test*']),
    python_requires='>=3.5.2',
    install_requires=requirements(),
    zip_safe=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    package_data={
        'tutti_aisthetics': ['model/*.hdf5']
    },
    include_package_data=True
)
