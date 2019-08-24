import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reddit-wall",
    version="0.1.0",
    author="Jalen Adams",
    author_email="jalen@jalenkadams.me",
    description="Download wallpapers from subreddits and multireddits of your choosing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LeftySolara/reddit-wall",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "reddit-wall=main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Natural Language :: English"
    ],
)
