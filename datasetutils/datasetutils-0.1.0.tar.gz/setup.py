import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setuptools.setup(
     name='datasetutils',  
     version='0.1.0',
     author="Dmitry Afonin",
     author_email="raysofgoodness@gmail.com",
     description="A simple util to make your dataset flexable.",
     long_description=long_description,
     license="MIT",
     long_description_content_type="text/markdown",
     url="https://github.com/Trapov/dataset-utils",
     packages=setuptools.find_packages(),
     install_requires=REQUIREMENTS,
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )