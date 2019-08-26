import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="maksekeskus",
    version="0.0.4",
    author="Rao Zvorovski",
    author_email="rao.zvorovski@codeduf.eu",
    description="Library to use the Maksekeskus(Makecommerce) APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raoz/pymaksekeskus",
    packages=setuptools.find_packages(),
    install_requires = [
        'requests',
        'simplejson'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Office/Business :: Financial"
    ],
)
