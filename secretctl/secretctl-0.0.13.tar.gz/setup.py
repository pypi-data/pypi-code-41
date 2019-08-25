import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements=['invoke', 'boto3', 'pyyaml', 'requests', 'colorama', 'setuptools-git-version']

setup(
    name="secretctl",
    author="Nic Cheneweth",
    author_email="nic.cheneweth@thoughtworks.com",
    description="Command line tool for working with aws secrets manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ncheneweth/secretctl",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        'Development Status :: 3 - Alpha',
    ],
    python_requires='>=3.5',
    install_requires=requirements,
    setup_requires=['pytest-runner','setuptools-git-version'],
    version_format='{tag}.dev{commitcount}' if not os.environ.get('CIRCLE_TAG') else '{tag}',
    tests_require=['pytest', 'moto'],
    entry_points={
        'console_scripts': ['secretctl = secretctl.main:program.run']
    }
)
