import os

from pathlib import Path

import setuptools

from backup_utils import __version__, __author__

ROOT = Path(__file__).resolve().parent.parent

readme_path = Path(ROOT / "README.md")
if not readme_path.exists():
    readme_path = Path(os.getcwd()) / "README.md"

setuptools.setup(
    name="backup_utils",
    version=__version__,
    author=__author__.split(" <")[0],
    author_email=__author__.split(" <")[1].strip("<>"),
    description="The goal of the project is to simplify backup creation.",
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Oprax/backup-utils",
    packages=setuptools.find_packages(),
    license="MIT",
    entry_points={"console_scripts": ["backup-utils = backup_utils:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Operating System :: POSIX",
        "Topic :: System :: Archiving :: Backup",
        "Intended Audience :: System Administrators",
    ],
)
