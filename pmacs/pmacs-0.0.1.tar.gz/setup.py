import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pmacs',
    version='0.0.1',
    author='Bart L. Brown',
    author_email='bartonlbrown@gmail.com',
    description='Python editing MACroS',
    long_description_content_type="text/markdown",
    url='https://github.com/bartlbrown/pmacs',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
