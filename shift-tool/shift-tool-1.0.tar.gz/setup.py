from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='shift-tool',
    version='1.0',
    packages=['shift'], 
    description='Keyed text encoding',
    url='https://github.com/Ewpratten/shift',
    author='Evan Pratten',
    author_email='ewpratten@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ),
    entry_points={
        'console_scripts': [
            'shift = shift.__main__:main'
        ]
    })
