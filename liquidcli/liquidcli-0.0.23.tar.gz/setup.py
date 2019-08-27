import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

about = {}
with open(os.path.join(here, 'liquidcli', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setuptools.setup(
    name="liquidcli",
    version=about['__version__'],
    author="Suzuito",
    author_email="suzuito3@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suzuito/liquid-python",
    python_requires=">=3.7",
    packages=['liquidcli'],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
