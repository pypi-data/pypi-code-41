import os
import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

version_from_tag = '0.0.1'
if os.environ['CI_COMMIT_TAG']:
    if os.environ['CI_COMMIT_TAG'].count('.') == 2:
        version_from_tag = os.environ['CI_COMMIT_TAG']

setuptools.setup(
    name="ptscore",
    version=version_from_tag,
    author="Caesar Kabalan",
    author_email="caesar.kabalan@gmail.com",
    description="PassTheSecret core library containing back-end code for encryption and storage of secrets.",
    long_description=long_description,
    url="https://github.com/passthesecret/passthesecret-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)