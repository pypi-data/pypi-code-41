import os
from setuptools import setup, find_packages


__VERSION__ = "0.1.0"

ROOT = os.path.dirname(__file__)

with open(os.path.join(ROOT, "README.md")) as f:
    long_description = f.read()

setup(
    name="CuteJoe",
    version=__VERSION__,
    license="MIT License",
    description="Commands to automate some release tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MatheusBrochi",
    author_email="matheusgbrochi@gmail.com",
    url="https://github.com/MatheusBrochi/CuteJoe",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    project_urls={
        'Changelog': 'https://github.com/MatheusBrochi/CuteJoe/tree/master/changelogs',
        'Issue Tracker': 'https://github.com/MatheusBrochi/CuteJoe/issues',
    },
    install_requires=(
        "Click~=7.0",
        "PyYAML~=5.1.2",
    ),
    extras_require={
        "test": (
            "pytest",
            "pytest-flake8",
            "pytest-cov",
        ),
    },
    entry_points={
        'console_scripts': [
            'cutejoe=cutejoe:cli'
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Documentation",
    ],
)
