import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clean_cmake_project",
    version="0.0.3",
    author="FrenchCommando",
    author_email="martialren@gmail.com",
    description="A script to build cmake project for c++ using python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FrenchCommando/clean_cmake_project",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['cmake-python-project=clean_cmake_project.ProjectSkeleton:main'],
    }
)
