import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='rim',
     version='0.3.4',
     #  scripts=['rim'],
     author="Ivan Majic",
     author_email="imajicos@gmail.com",
     description="A package for calculating RIM between spatial objects",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
