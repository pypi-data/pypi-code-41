import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wordlike",
    version="0.0.2",
    author="Nathan Kieffer",
    author_email="nathankieffer@gmail.com",
    description="Generates pronounceable nonsense words using Markov chains.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nkieffer/wordlike",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
