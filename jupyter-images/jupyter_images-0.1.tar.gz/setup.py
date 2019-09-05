import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name='jupyter_images',    # This is the name of your PyPI-package.
    version='0.1',
    url='https://github.com/ryanGT/jupyter_images',
    author='Ryan Krauss',
    author_email='ryanwkrauss@gmail.com',
    description="package for generating HTML code to put images in Jupyter notebooks, especially from google drive",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
