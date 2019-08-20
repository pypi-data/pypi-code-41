import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proto_dist_ml",
    version="1.0.0",
    author="Benjamin Paassen",
    author_email="bpaassen@techfak.uni-bielefeld.de",
    description="Prototype-based Machine Learning on Distance Data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ub.uni-bielefeld.de/bpaassen/proto-dist-ml",
    packages=['proto_dist_ml'],
    install_requires=['numpy', 'scikit-learn', 'scipy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    keywords='relational-neural-gas learning-vector-quantization lvq clustering classification machine-learning distances',
)
