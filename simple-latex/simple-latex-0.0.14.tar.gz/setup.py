import setuptools

# defines __version__
exec(open('simple_latex/version.py').read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-latex",
    version=__version__,
    author="Engage",
    author_email="eli.j.selkin@gmail.com",
    description="A way to write LaTeX in python without being bound to existing higher level structures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hackla-engage/simple-latex",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[]
)
