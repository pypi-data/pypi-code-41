import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("requirements.txt") as f:
    install_requires = f.read().split()

setuptools.setup(
    name="infomaniakclient",
    version="0.0.3",
    author="Potrac Grognuz",
    author_email="potrac@grognuz.site",
    description="Infomaniak Newsletter API client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Potrac/infomaniakclient",
    keywords="infomaniak newsletter api client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
)