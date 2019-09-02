import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="linedoll",
    version="0.0.1a",
    author="lim",
    author_email="lim@bigfinding.com",
    description="A simple tool to create a micro api backend framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lim-lq/flask-vue-example",
    packages=setuptools.find_packages(),
    install_requires=[
        "click"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
