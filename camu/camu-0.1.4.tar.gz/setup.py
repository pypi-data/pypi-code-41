import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="camu",
    version="0.1.4",
    author="Nicolas Ruffini",
    author_email="ruffini@uni-mainz.de",
    description="A package for filtering candidate mutations for spontaneous mutation rate estimates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.rlp.net/nruffini/camufi/tree/master",
    packages=["camu", "detectFIO", "findDupAndLinked", "IGVSessions", "snapshotIGV", "preprocessing"],
    install_requires=['tqdm>=4.32.1', 'numpy>=1.16.2', 'pysam>=0.15.2'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
