from setuptools import setup, find_packages

with open("DESCRIPTION.md", "r") as f:
    longdesc = f.read()

setup(
    name="BetterScratchAPI",
    version="0.1.2",
    description="Web API Interface for Scratch! (scratch.mit.edu)",
    long_description=longdesc,
    url="https://github.com/ItzMeWilliam/BetterScratchAPI",
    author="ItzMeWilliam",
    license="GPLv3+",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords="scratch api betterscratchapi requests scratch.mit.edu api.scratch.mit.edu",
    packages=find_packages(),
    install_requires="requests",
    python_requires=">=3.0"
    )
