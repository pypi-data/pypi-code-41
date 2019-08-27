import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="touchbar-lyric",
    version="0.0.1",
    author="Chenghao",
    author_email="mouchenghao@gmail.com",
    description="Show time-synced lyric with BTT!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChenghaoMou/touchbar-lyric",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
)
