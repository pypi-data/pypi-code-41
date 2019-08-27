import setuptools
import version

with open("README.md", "r") as fh:
    long_description = 'Custom methodes for various data science, computer vision, and machine learning operations in python'#fh.read()

setuptools.setup(
    name = 'JLpy_utils_package',
    version= version.find_version('JLpy_utils_package', '__init__.py'),
    author="John T. Leonard",
    author_email="jtleona01@gmail.com",
    description='Custom methodes for various data science, computer vision, and machine learning operations in python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jlnerd/JLpy_utils_package.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

