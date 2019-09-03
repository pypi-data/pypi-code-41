import setuptools

import snitch

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = [line.strip() for line in fh]

setuptools.setup(
    name="snitch-ci",
    version=snitch.__version__,
    author=snitch.__author__,
    author_email="gregory@millasseau.fr",
    description="An input event recorder and player for automatic testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://picocs.neutron.intra.irsn.fr/Picocs/snitch",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points={
        'console_scripts': ['snitch = snitch.__main__:main']
    }
)
