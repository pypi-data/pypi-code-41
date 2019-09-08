import setuptools
from distutils.core import Extension
from distutils.core import setup


_package_description = """Interval Arithmetic Package for Kaucher's Interval Arithmetic
This Python package provides types and functions for Kaucher's Interval Arithmetic, named KaucherPy.
""".split("\n")


if __name__ == "__main__":
    setup(
        name="kaucherpy",
        version="0.1.0",
        description=_package_description[0],
        long_description="\n".join(_package_description[2:-1]),
        author="Lucas Mendes Tortelli, Dirceu Maraschin Jr.",
        author_email="lmtortelli@inf.ufpel.edu.br,dmaraschin@inf.ufpel.edu.br",
        license="GPL",
        url="https://github.com/lmtortelli/kaucherpy",
        platforms=[
            "Windows",
            "Linux"
        ],
        packages=[
            "kaucherpy",
            "kaucherpy.kaucher",
            "kaucherpy.core",
            "kaucherpy.support",
            "kaucherpy.utils"
        ],
        package_dir={
            "kaucherpy" : "src"
        },
        install_requires = [
                          'numpy >= 1.13.0',
                          'enum34',
                          ],

    )
