import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="discomp",
	version="1.5.0",
    author="Dis.co ",
    author_email="service@dis.co",
    description="Dis.co multi-processing python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Iqoqo/iqoqomp",
    packages=setuptools.find_packages(),
    install_requires=[
        'dill>=0.2.9',
        'analytics-python'
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
