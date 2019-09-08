from setuptools import setup
from distutils.core import Extension
from distutils.core import setup


_package_description = ''' Interval Arithmetic package
This package provides types and functions for Maximum Accuracy Interval
Arithmetic.
'''.split("\n")


if __name__ == "__main__":
    setup(
        name="pyrdmia",
        version="0.1.0",
        description=_package_description[0],
        long_description="\n".join(_package_description[2:-1]),
        author="Dirceu Maraschin Jr.,Lucas Mendes Tortelli",
        author_email="lmtortelli@inf.ufpel.edu.br,dmaraschin@inf.ufpel.edu.br",
        license="GPL",
        url="https://github.com/DirceuMaraschin/PyRDMIA",
        platforms=[
            "Windows",
            "Linux"
        ],
        packages=[
            "pyrdmia",
            "pyrdmia.core",
            "pyrdmia.utils",
            "pyrdmia.support",
            "pyrdmia.regression"
        ],
        package_dir={
            "pyrdmia" : "src"
        },
        install_requires = [
                          "numpy >= 1.13.0",
                          "enum34",
                          ],

    )
