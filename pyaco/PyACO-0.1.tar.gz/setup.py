from setuptools import setup

requires = ["matplotlib"]

setup(
    name="PyACO",
    version="0.1",
    description="Ant Colony Optimization in python",
    url="https://github.com/Ganariya/PyACO",
    author="ganariya",
    license="MIT",
    keywords="ACO python",
    packages=[
        "PyACO"
    ],
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3.6"
    ]
)
