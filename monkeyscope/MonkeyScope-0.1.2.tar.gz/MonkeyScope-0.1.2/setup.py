from setuptools import setup, Extension
from Cython.Build import cythonize


with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="MonkeyScope",
    ext_modules=cythonize(
        Extension(
            name="MonkeyScope",
            sources=["MonkeyScope.pyx"],
            language=["c++"],
            extra_compile_args=["-std=gnu++17", "-O3"],
        ),
        compiler_directives={
            'embedsignature': True,
            'language_level': 3,
        },
    ),
    author="Robert Sharp",
    author_email="webmaster@sharpdesigndigital.com",
    url="https://sharpdesigndigital.com",
    requires=["Cython"],
    version="0.1.2",
    description="Distribution Stats & Timer for Testing Non-deterministic Value Generators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Free for non-commercial use",
    platforms=["Darwin", "Linux"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Cython",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "MonkeyScope", "distribution tests", "function timer", "performance testing", "statistical analysis",
    ],
    python_requires='>=3.7',
)
