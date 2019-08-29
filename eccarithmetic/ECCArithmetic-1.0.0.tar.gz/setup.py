from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ECCArithmetic',
    version='1.0.0',
    author="Parthkumar Rathod, Rakshit Joshi, Mahesh Hegde",
    author_email="parthcrathod@gmail.com, rakshitjoshi211997@gmail.com, maheshhegde113@gmail.com",
    description="Python Elliptic Curve Arithmetic Library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages('ECCArithmetic', exclude=['test_ec']),
    python_requires='>=3.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Security :: Cryptography"
    ],
    py_modules=["bigrange", "dlog", "ec", "ent", "test_ec"],
    package_dir={'': 'ECCArithmetic'},
)
